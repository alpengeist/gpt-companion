import openai
import os


def get_apikey():
    return os.getenv('OPENAI_KEY')


def completion(prefix="", text="", temperature=0.7, model="ext-davinci-003", max_tokens=1000):
    prompt = prefix + text
    print(f"model={model}, temperature={temperature}\n{prompt}")
    try:
        return openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )["choices"][0]["text"]
    except openai.error.OpenAIError as e:
        return f"{e=}"


def models():
    try:
        m = openai.Model.list()
        print(m)
    except openai.error.OpenAIError as e:
        return f"{e=}"


openai.api_key = get_apikey()
