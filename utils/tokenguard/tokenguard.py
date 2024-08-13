#token guard to prevent excessive token use
import tiktoken

class TokenGuard:
    def __init__(self, model_name, max_tokens):
        self.encoder = tiktoken.encoding_for_model(model_name)
        self.max_tokens = max_tokens
        self.tokens_used = 0

    def count_tokens(self, text):
        return len(self.encoder(text))
    
    def check_tokens(self, input_text, estimated_output_tokens):
        input_tokens = self.count_tokens(input_text)
        total_tokens = self.tokens_used + input_tokens + estimated_output_tokens

        if total_tokens > self.max_tokens:
            raise ValueError("Exceeded token limit. Total tokens: {total_tokens}, Max tokens: {self.max_tokens}")
        
        return input_tokens
    
    def update_used_tokens(self, input_tokens, output_tokens):
        self.tokens_used += input_tokens + output_tokens

        return self.max_tokens - self.tokens_used