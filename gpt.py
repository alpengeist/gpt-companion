from openai import OpenAI
from string import Template


def format_prompt(prompt, text) -> str:
    if '$text' in prompt:
        t = Template(prompt)
        return t.substitute(text=text)
    else:
        return prompt + text


def chat_completion(prompt='', text='', temperature=0.7, model='gpt-4.1-mini', max_tokens=1000,
                    instruction='Be precise and concise'):
    messages = [
        {'role': 'system', 'content': instruction },  # general instruction to the chat
        {'role': 'user', 'content': format_prompt(prompt, text)}
    ]
    print(f"model={model}, temperature={temperature}\n{messages}")
    return client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True
    )


client = OpenAI()
