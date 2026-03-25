import tiktoken


class TokenCounter:
    def __init__(self, model_name):
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base for models not recognized by tiktoken
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: list[str]) -> int:
        return len(self.encoding.encode_batch(text))

    def count_messages(self, messages: list) -> int:
        '''
          计算对话消息的 token 数量
        '''
        total_tokens = 0
        for message in messages:
            total_tokens += self.count_tokens(message["content"])
            total_tokens += 4
        return total_tokens


class TokenLimiter:
    def __init__(self,
                 max_input_tokens: int = 100,
                 max_output_tokens: int = 200,
                 model_limit=128000):
        self.max_input_tokens = max_input_tokens
        self.max_output_tokens = max_output_tokens
        self.model_limit = model_limit

    def check_input(self, input_tokens):
        if input_tokens > self.max_input_tokens:
            raise ValueError(
                f"Input tokens exceed limit: {input_tokens} > {self.max_input_tokens}"
            )

    def check_total(self, input_tokens, output_tokens):
        total = input_tokens + output_tokens

        if total > self.model_limit:
            raise ValueError(
                f"Total tokens exceed model limit: {total} > {self.model_limit}"
            )


if __name__ == "__main__":
    counter = TokenCounter("stepfun/step-3.5-flash:free")
    print(counter.count_tokens("你好 world, 你好世界"))
    print(counter.count_messages(
        [{"role": "user", "content": "你好 world, 你好世界"}]))

    limiter = TokenLimiter()
    limiter.check_input(counter.count_tokens("你好 world, 你好世界"))
    limiter.check_total(counter.count_tokens("你好 world, 你好世界"),
                        counter.count_messages(
                            [{"role": "user", "content": "你好 world, 你好世界"}]))
