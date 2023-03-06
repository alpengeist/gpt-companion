import openai
import os

import config


def get_apikey():
    return os.getenv('OPENAI_KEY')


def completion(prefix='', text='', temperature=0.7, model='ext-davinci-003', max_tokens=1000):
    prompt = prefix + text
    print(f"model={model}, temperature={temperature}\n{prompt}")
    try:
        for ev in openai.Completion.create(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        ):
            yield ev['choices'][0]['text']
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"{e=}")


def chat_completion(prefix='', text='', temperature=0.7, model='gpt-3.5-turbo', max_tokens=1000):
    messages = [
        {'role': 'system', 'content': 'Be precise and concise'},  # general instruction to the chat
        {'role': 'user', 'content': prefix + text}
    ]
    print(f"model={model}, temperature={temperature}\n{messages}")
    try:
        ev = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False     # streaming is broken as of v0.27
        )
        return [ev['choices'][0]['message']['content']]
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"{e=}")


def models():
    try:
        m = openai.Model.list()
        print(m)
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"{e=}")


openai.api_key = get_apikey()
