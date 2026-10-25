"""Offline application compatibility checks for the security dependency update.

Run this module explicitly; legacy Firecrawl diagnostics perform live requests.
"""

import importlib
import os
import re
import socket
import unittest
from contextlib import ExitStack
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch

from pypdf import PdfReader, PdfWriter
from pypdf.errors import LimitReachedError


class ApplicationCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patches = ExitStack()
        cls.addClassCleanup(cls.patches.close)
        cls.patches.enter_context(patch.dict(os.environ, {
            "OPENAI_API_KEY": "offline-test-not-a-real-key",
            "FIRECRAWL_API_KEY": "offline-test-not-a-real-key",
        }, clear=True))
        cls.patches.enter_context(patch("dotenv.load_dotenv", return_value=False))
        cls.patches.enter_context(patch("nltk.download", return_value=True))
        cls.patches.enter_context(patch.object(
            socket.socket, "connect",
            side_effect=AssertionError("Offline tests must not contact a service"),
        ))
        cls.module = importlib.import_module("app")
        cls.client = cls.module.app.test_client()

    def setUp(self):
        self.module.cache.clear()
        self.module.limiter.reset()

    def test_home_and_static_routes(self):
        with self.client.get("/") as response:
            self.assertEqual(response.status_code, 200)
        with self.client.get("/public/styles.css") as response:
            self.assertEqual(response.status_code, 200)

    def test_pdf_route_preserves_article_text(self):
        response = self.client.post("/generate_pdf", json={
            "title": "Offline article", "content": "Offline article\nOrdinary body text",
            "imageUrl": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertIn("Ordinary body text", PdfReader(BytesIO(response.data)).pages[0].extract_text())

    def test_invalid_content_still_rejected(self):
        response = self.client.post("/generate_pdf", json={"content": ""})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/query", json={
            "model": "unknown", "content": "Article", "query": "What is this?",
        })
        self.assertEqual(response.status_code, 400)

    def test_firecrawl_sdk_preserves_request_and_response_contract(self):
        # Exercise the real SDK and application adapter, mocking only HTTP I/O.
        reply = Mock(status_code=200)
        reply.json.return_value = {"success": True, "data": {
            "markdown": "# Offline title\nArticle body", "metadata": {"title": "Fallback"},
        }}
        with patch("firecrawl.firecrawl.requests.post", return_value=reply) as post:
            result = self.module.fetch_and_format_content("https://example.invalid/article")
        self.assertEqual(result.title, "Offline title")
        self.assertIn("Article body", result.content)
        self.assertEqual(post.call_args.kwargs["json"]["formats"], ["markdown"])
        self.assertIs(post.call_args.kwargs["json"]["onlyMainContent"], True)
        self.assertTrue(post.call_args.args[0].endswith("/v1/scrape"))

    def test_rag_query_with_real_index_and_offline_models(self):
        from llama_index.core import Settings
        from llama_index.core.embeddings import MockEmbedding
        from llama_index.core.llms import MockLLM
        from llama_index.core.node_parser import SentenceSplitter

        old_parser = Settings.node_parser
        old_tokenizer = Settings.tokenizer
        self.addCleanup(setattr, Settings, "node_parser", old_parser)
        self.addCleanup(setattr, Settings, "tokenizer", old_tokenizer)
        Settings.tokenizer = lambda text: list(text.encode("utf-8"))
        Settings.node_parser = SentenceSplitter(
            chunk_size=256, chunk_overlap=16, tokenizer=Settings.tokenizer,
            chunking_tokenizer_fn=lambda text: [text],
        )
        with patch.object(self.module.indexUtils, "OpenAI", return_value=MockLLM(max_tokens=8)), \
                patch.object(self.module.indexUtils, "OpenAIEmbedding", return_value=MockEmbedding(embed_dim=8)), \
                patch.object(self.module.query_validator, "validate_query", return_value=SimpleNamespace(is_valid=True)):
            response = self.client.post("/query", json={
                "model": "gpt-4o-mini", "content": "Reader indexes article text.",
                "query": "What does Reader index?", "title": "Reader",
            })
        self.assertEqual(response.status_code, 200, response.get_json())
        self.assertTrue(response.get_json()["result"])


class PdfParserSecurityTests(unittest.TestCase):
    @staticmethod
    def make_pdf():
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        stream = BytesIO()
        writer.write(stream)
        return stream.getvalue()

    def test_excessive_xref_size_is_rejected(self):
        data = self.make_pdf()
        for declared_size in (b"999999999", b"99999999999999999999"):
            with self.subTest(declared_size=declared_size):
                malformed, count = re.subn(
                    rb"xref\n0 \d+\n", b"xref\n0 " + declared_size + b"\n", data, count=1,
                )
                self.assertEqual(count, 1)
                with self.assertRaises(LimitReachedError):
                    PdfReader(BytesIO(malformed), strict=True)

    def test_repeated_bad_xrefs_reuse_single_recovery_scan(self):
        import pypdf._reader

        data = self.make_pdf()
        # Preserve line lengths and PDF object offsets while corrupting entries.
        malformed, count = re.subn(rb"\d{10} 00000 n ", b"bad0000000 00000 n ", data)
        self.assertGreater(count, 1)
        with patch("pypdf._reader.get_stream_data", wraps=pypdf._reader.get_stream_data) as read_all:
            reader = PdfReader(BytesIO(malformed), strict=False)
        self.assertEqual(read_all.call_count, 1)
        self.assertEqual(len(reader.pages), 1)

    def test_valid_pdf_still_reads(self):
        self.assertEqual(len(PdfReader(BytesIO(self.make_pdf()), strict=True).pages), 1)


if __name__ == "__main__":
    unittest.main()
