"""Offline behavioral regressions for Reader's security dependency updates.

Run with ``python -m unittest tests.test_security_dependencies -v`` after
installing requirements.txt. These tests need neither API keys nor NLTK data.
They deliberately do not import app.py or initialize the indexing clients.
"""

import hashlib
import importlib.util
import io
from pathlib import Path
import re
import ssl
import sys
import types
import unittest
from unittest.mock import Mock, call, patch
from uuid import uuid4

import certifi
from anyio.abc import ByteStream
from anyio.streams.tls import TLSStream
from fsspec.implementations.memory import MemoryFileSystem
from fsspec.implementations.reference import ReferenceFileSystem
from jinja2.exceptions import SecurityError
from PIL import Image
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_reader_image_and_pdf_utils():
    """Load the real utility code without utils.__init__ importing the LLM SDKs.

    Only the package import boundary is isolated. Pillow, ReportLab, requests,
    pypdf, and both application utility modules are real installed code. Restore
    sys.modules afterwards so this isolation cannot affect other test modules.
    """
    image_utils = _load_module(
        "_reader_security_image_utils", "utils/fetch/imageUtils.py"
    )
    utils_package = types.ModuleType("utils")
    utils_package.__path__ = [str(ROOT / "utils")]
    fetch_package = types.ModuleType("utils.fetch")
    fetch_package.__path__ = [str(ROOT / "utils/fetch")]
    fetch_package.imageUtils = image_utils
    utils_package.fetch = fetch_package
    aliases = {
        "utils": utils_package,
        "utils.fetch": fetch_package,
        "utils.fetch.imageUtils": image_utils,
    }
    missing = object()
    previous = {name: sys.modules.get(name, missing) for name in aliases}
    try:
        sys.modules.update(aliases)
        pdf_utils = _load_module(
            "_reader_security_pdf_utils", "utils/generate/pdfUtils.py"
        )
    finally:
        # Restore just our aliases, not newly imported ReportLab submodules.
        # Removing those would create inconsistent class identities on reimport.
        for name, value in previous.items():
            if value is missing:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    return image_utils, pdf_utils


class ReaderImageAndPdfCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image_utils, cls.pdf_utils = _load_reader_image_and_pdf_utils()

    @staticmethod
    def _image_bytes(image_format, size):
        buffer = io.BytesIO()
        with Image.new("RGB", size, color=(30, 90, 160)) as image:
            image.save(buffer, format=image_format)
        return buffer.getvalue()

    @staticmethod
    def _response(image_bytes):
        # A fresh stream per request matches requests' real response behavior.
        return types.SimpleNamespace(
            content=image_bytes, raw=io.BytesIO(image_bytes)
        )

    def test_png_and_jpeg_dimensions_and_display_width(self):
        for image_format in ("PNG", "JPEG"):
            for size, expected_display in (
                ((192, 96), (144.0, 72.0)),
                ((960, 480), (432.0, 216.0)),
            ):
                with self.subTest(image_format=image_format, size=size):
                    data = self._image_bytes(image_format, size)
                    url = "https://images.example.invalid/article-image"
                    with patch.object(
                        self.image_utils.requests,
                        "get",
                        side_effect=lambda *args, **kwargs: self._response(data),
                    ) as get:
                        self.assertEqual(
                            self.image_utils._get_image_size_from_url(url), size
                        )
                        self.assertEqual(
                            self.image_utils.get_image_display_size(url),
                            expected_display,
                        )
                    self.assertEqual(get.call_args_list, [call(url), call(url)])

    def test_text_only_pdf_contains_title_and_body_without_network(self):
        for image_url in (None, ""):
            with self.subTest(image_url=image_url):
                with patch.object(
                    self.pdf_utils.requests,
                    "get",
                    side_effect=AssertionError("Text-only PDF must not fetch URLs"),
                ) as get:
                    output = self.pdf_utils.generate_pdf(
                        "Offline article\nFirst paragraph.\n\nSecond paragraph.",
                        image_url,
                    )
                get.assert_not_called()
                self.assertEqual(output.tell(), 0)
                self.assertTrue(output.getvalue().startswith(b"%PDF-"))
                reader = PdfReader(output)
                self.assertEqual(len(reader.pages), 1)
                text = reader.pages[0].extract_text()
                for expected in (
                    "Offline article", "First paragraph.", "Second paragraph."
                ):
                    self.assertIn(expected, text)

    def test_pdf_embeds_real_png_and_jpeg_images(self):
        for image_format in ("PNG", "JPEG"):
            with self.subTest(image_format=image_format):
                data = self._image_bytes(image_format, (192, 96))
                url = "https://images.example.invalid/article-image"
                with patch.object(
                    self.pdf_utils.requests,
                    "get",
                    side_effect=lambda *args, **kwargs: self._response(data),
                ) as get:
                    output = self.pdf_utils.generate_pdf(
                        "Illustrated article\nBody survives the dependency upgrade.",
                        url,
                    )
                self.assertEqual(
                    get.call_args_list, [call(url, stream=True), call(url)]
                )
                reader = PdfReader(output)
                self.assertEqual(len(reader.pages), 1)
                page = reader.pages[0]
                self.assertIn("Illustrated article", page.extract_text())
                self.assertIn("Body survives", page.extract_text())
                xobjects = page["/Resources"]["/XObject"].get_object()
                embedded_images = [
                    value.get_object() for value in xobjects.values()
                    if value.get_object().get("/Subtype") == "/Image"
                ]
                self.assertEqual(len(embedded_images), 1)
                self.assertEqual(embedded_images[0]["/Width"], 192)
                self.assertEqual(embedded_images[0]["/Height"], 96)
                self.assertTrue(embedded_images[0].get_data())


class CertifiTrustBundleTests(unittest.TestCase):
    def test_compromised_emsign_g3_root_is_not_bundled(self):
        # GHSA-6q48-6c7w-9gw2: identify the certificate by its DER SHA-256,
        # not by a removable PEM comment or a package version string.
        # Inspect only certifi's bundle: host SSL contexts can preload extra CAs.
        compromised_root_sha256 = (
            "86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b"
        )
        pem = Path(certifi.where()).read_text(encoding="ascii")
        certificates = re.findall(
            r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",
            pem,
            flags=re.DOTALL,
        )
        self.assertGreater(len(certificates), 100, "CA bundle must not be empty")
        fingerprints = {
            hashlib.sha256(ssl.PEM_cert_to_DER_cert(cert)).hexdigest()
            for cert in certificates
        }
        self.assertNotIn(
            compromised_root_sha256,
            fingerprints,
            "certifi still trusts emSign ECC Root CA - G3",
        )


class FsspecTemplateSandboxTests(unittest.TestCase):
    # Harmless introspection probes: never execute commands or access files.
    # Exercise attribute, item, and attr-filter spellings of the same boundary.
    UNSAFE_TEMPLATES = (
        "{{ ''.__class__.__mro__ }}",
        "{{ ''['__class__']['__mro__'] }}",
        "{{ (''|attr('__class__'))() }}",
    )

    def setUp(self):
        self.memory = MemoryFileSystem()
        self.prefix = "/reader-security-" + uuid4().hex
        self.base = "memory:/" + self.prefix
        self.memory.pipe_file(self.prefix + "/data", b"abcdef")
        self.addCleanup(self.memory.rm, self.prefix, recursive=True)

    def _filesystem(self, spec, *, simple_templates=False):
        return ReferenceFileSystem(
            spec, simple_templates=simple_templates, fs=self.memory
        )

    @unittest.expectedFailure
    def test_default_template_mode_rejects_attribute_traversal(self):
        # Known upstream limitation, also present in fsspec 2026.9.0: the
        # default str.format path can traverse a named-template callable's
        # globals. Reader does not use ReferenceFileSystem. Keep the desired
        # security property visible instead of claiming every mode is fixed.
        # Probe only a public module name, never environment data or files.
        with self.assertRaises(SecurityError):
            self._filesystem({
                "version": 1,
                "templates": {"probe": "{{ ignored }}"},
                "refs": {"probe": ["memory:///{{probe.__globals__[__name__]}}"]},
            }, simple_templates=True)

    def test_reference_urls_reject_unsafe_introspection(self):
        for payload in self.UNSAFE_TEMPLATES:
            with self.subTest(payload=payload), self.assertRaises(SecurityError):
                self._filesystem({
                    "version": 1,
                    "templates": {"base": self.base},
                    "refs": {"unsafe": [payload]},
                })

    def test_named_templates_reject_unsafe_introspection(self):
        for payload in self.UNSAFE_TEMPLATES:
            with self.subTest(payload=payload), self.assertRaises(SecurityError):
                self._filesystem({
                    "version": 1,
                    "templates": {"location": payload},
                    "refs": {"unsafe": ["{{ location() }}"]},
                })

    def test_all_generator_fields_reject_unsafe_introspection(self):
        for field in ("key", "url", "offset", "length"):
            for payload in self.UNSAFE_TEMPLATES:
                with self.subTest(field=field, payload=payload):
                    generator = {
                        "key": "chunk{{ i }}",
                        "url": "{{ base }}/data",
                        "offset": "0",
                        "length": "1",
                        "dimensions": {"i": [0]},
                    }
                    generator[field] = payload
                    with self.assertRaises(SecurityError):
                        self._filesystem({
                            "version": 1,
                            "templates": {"base": self.base},
                            "gen": [generator],
                        })

    def test_simple_variables_still_resolve_and_read_byte_ranges(self):
        for simple_templates in (True, False):
            with self.subTest(simple_templates=simple_templates):
                fs = self._filesystem({
                    "version": 1,
                    "templates": {"base": self.base},
                    "refs": {"slice": ["{{base}}/data", 1, 3]},
                }, simple_templates=simple_templates)
                self.assertEqual(fs.cat_file("slice"), b"bcd")

    def test_safe_named_templates_still_resolve(self):
        fs = self._filesystem({
            "version": 1,
            "templates": {
                "base": self.base,
                "location": "{{ base }}/data",
            },
            "refs": {"file": ["{{ location(base=base) }}"]},
        })
        self.assertEqual(fs.cat_file("file"), b"abcdef")

    def test_safe_generators_still_read_expected_chunks(self):
        fs = self._filesystem({
            "version": 1,
            "templates": {"base": self.base},
            "gen": [{
                "key": "chunk{{ i }}",
                "url": "{{ base }}/data",
                "offset": "{{ i * 2 }}",
                "length": "2",
                "dimensions": {"i": {"stop": 3}},
            }],
        })
        self.assertEqual(set(fs.references), {"chunk0", "chunk1", "chunk2"})
        self.assertEqual(
            [fs.cat_file("chunk" + str(i)) for i in range(3)],
            [b"ab", b"cd", b"ef"],
        )


class _NoNetworkByteStream(ByteStream):
    """A byte stream that fails if a mocked TLS handshake attempts any I/O."""

    def __init__(self):
        self.closed = False

    async def send(self, item):
        raise AssertionError("TLS regression test must not send network data")

    async def receive(self, max_bytes=65536):
        raise AssertionError("TLS regression test must not receive network data")

    async def send_eof(self):
        raise AssertionError("TLS regression test must not send EOF")

    async def aclose(self):
        self.closed = True


class AnyioTlsHostnameTests(unittest.IsolatedAsyncioTestCase):
    async def test_wrap_preserves_idna2008_hostname_identity(self):
        # IDNA 2003 collapses faß.de into fass.de, changing the peer identity.
        # Assert what the real TLS wrapper passes into SSLContext, not just what
        # the idna package computes. Only SSL object construction/handshake is
        # mocked; AnyIO's name resolution and TLS wrapper execute normally.
        for hostname, expected in (
            ("faß.de", b"xn--fa-hia.de"),
            ("fass.de", b"fass.de"),
            ("example.com", b"example.com"),
        ):
            with self.subTest(hostname=hostname):
                transport = _NoNetworkByteStream()
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ssl_object = Mock(spec=ssl.SSLObject)
                ssl_object.do_handshake.return_value = None
                with patch.object(
                    ssl.SSLContext, "wrap_bio", return_value=ssl_object
                ) as wrap_bio:
                    stream = await TLSStream.wrap(
                        transport,
                        hostname=hostname,
                        ssl_context=context,
                        standard_compatible=False,
                    )
                wrap_bio.assert_called_once()
                args, kwargs = wrap_bio.call_args
                self.assertEqual(len(args), 2)
                self.assertTrue(all(isinstance(arg, ssl.MemoryBIO) for arg in args))
                self.assertEqual(kwargs["server_hostname"], expected)
                self.assertFalse(kwargs["server_side"])
                ssl_object.do_handshake.assert_called_once_with()
                self.assertIs(stream.transport_stream, transport)
                await stream.aclose()
                self.assertTrue(transport.closed)


if __name__ == "__main__":
    unittest.main()
