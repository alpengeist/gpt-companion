# GPT-3 Companion

## What it does

Are you familiar with DeepL's desktop tool for on the fly translations?
The GPT companion tool works in similar ways.

Select text in any application and send it to the companion via hot key. 
Configure your favorite GPT-3 text processing tasks and let the companion call
GPT-3 for you.

The companion is more convenient than using ChatGPT or OpenAI Playground
where you'll have to copy&paste the text yourself and fiddle with the
same prompts over and over again. You never have to leave the source application. Just run the companion, put it aside and feed it with text.

## Installation
`pip install -r requirements.txt`

It has been developed with Python 3.10 and the Tk UI under Windows. The **keyboard**
module, which is required for the hot key handling, works under Linux as well. MacOS is experimental.

## Configuration
The environment variable OPENAI_KEY must contain your OpenAI API key.

To configure your favorite commands or change the hot key, edit the **config.py** file.
It is very simple and straightforward.

## Future Ideas
* The config is in the code. Not ideal of course for non-developers and in case this
project gains a couple of users. I haven't decided the format, yet.
* Optional: Issue a paste keyboard command after GPT is finished. This will integrate GPT seamlessly in any text application.
