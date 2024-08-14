#token guard to prevent excessive token use
import tiktoken
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenGuard:
    def __init__(self, model_name, max_tokens):
        self.encoder = tiktoken.encoding_for_model(model_name)
        self.max_tokens = max_tokens
        self.tokens_used = 0
        logger.info(f"TokenGuard initialized for model {model_name} with max tokens {max_tokens}")

    def count_tokens(self, text):
        token_count = len(self.encoder(text))
        logger.info(f"Token count for text: {token_count}")
        return token_count
    
    def check_tokens(self, input_text, estimated_output_tokens):
        input_tokens = self.count_tokens(input_text)
        total_tokens = self.tokens_used + input_tokens + estimated_output_tokens
        logger.info(f"Total tokens: {total_tokens}, Max tokens: {self.max_tokens}")

        if total_tokens > self.max_tokens:
            raise ValueError("Exceeded token limit. Total tokens: {total_tokens}, estimated output={estimated_output_tokens}, total={total_tokens}")
        
        return input_tokens
    
    def update_used_tokens(self, input_tokens, output_tokens):
        self.tokens_used += input_tokens + output_tokens

        return self.max_tokens - self.tokens_used