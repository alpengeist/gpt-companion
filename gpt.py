import openai
import os


def call_gpt(prefix="", text="", temperature=0.7, model="ext-davinci-003", max_tokens=1000):
    openai.api_key = os.getenv('OPENAI_KEY')
    prompt = prefix + text
    print(f"model={model}, temperature={temperature}\n{prompt}")
    try:
        return openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )["choices"][0]["text"]
    except openai.error.RateLimitError as e:
        return f"{e.user_message}"
