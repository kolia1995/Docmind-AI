from src.core.settings import settings
from groq import Groq
import time

class GroqProvider:
    def __init__(
        self,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        top_p: float = 0.9,
        model_name: str = settings.LLM_GROQ_NAME,
        api_key: str = settings.LLM_GROQ_KEY,
        cache_enabled: bool = True,
        rate_limit_per_minute: int = 60,
    ):
        if not api_key:
            raise ValueError("Missing Groq API key")

        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p

        self.client = Groq(api_key=api_key)

        self.usage_status = {"requests": 0, "tokens_used": 0}

        self.cache_enabled = cache_enabled
        self.cache = {}

        self.rate_limit_per_minute = rate_limit_per_minute
        self.last_call_timestamp = 0

    def _rate_limit(self):
        now = time.time()
        wait_time = max(
            0,
            60 / self.rate_limit_per_minute - (now - self.last_call_timestamp)
        )

        if wait_time > 0:
            time.sleep(wait_time)

        self.last_call_timestamp = time.time()

    def _cache_lookup(self, prompt: str):
        if self.cache_enabled:
            return self.cache.get(prompt)
        return None

    def _cache_store(self, prompt: str, response: str):
        if self.cache_enabled:
            self.cache[prompt] = response

    def generate(self, prompt: str):
        self._rate_limit()

        cached = self._cache_lookup(prompt)
        if cached:
            return cached
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=self.max_tokens,
        )

        text = response.choices[0].message.content

        self._cache_store(prompt, text)

        self.usage_status["requests"] += 1
        self.usage_status["tokens_used"] += len(prompt) + len(text)

        return text