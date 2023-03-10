# GPT Companion

<img alt="Companion App" src="doc/app.png" width="75%" height="75%"/>

Are you familiar with DeepL's desktop tool for on the fly translations?
The GPT Companion tool works in similar ways. You select some text in a source
application and press the configurable hotkey crtl-alt-g. The Companion will
call GPT for you and display the result.

Put your preferred GPT text processing actions (prompts) into profiles, which you can switch between at runtime.
For example, you could have a profile for English, one for German, one for fun stuff, etc.
An action did not work as expected? A new action comes to mind? Just edit the profile, press the _Reload_ button and run GPT again.

With the hotkey it can display a popup menu with the actions at the
mouse position in any application. This feature is configurable.

<img alt="action popup" src="doc/popup.png" width="30%" height="30%"/>

The app can also stay on top of all windows, which is also configurable.

For working on text documents, the Companion is more convenient than using ChatGPT or OpenAI Playground
where you'll have to copy&paste text snippets yourself and fiddle with the
same prompts over and over again. Just run the Companion, put it aside and feed it with text.

## OpenAI Chat Models

The Companion can use the chat models, however not in a chat-like fashion -  nobody needs yet another chatbot. 
The OpenAI API has a specific endpoint for chat models, which works differently than the other models.
The companion keeps no history of the "dialog" with the model, which would be required to make it "chatty".

The chat models must be listed separately in a profile config. See __profile-default.toml__ about how to do it.

## Prerequisites

Python 3.11

## Platforms

Developed and tested under Windows 11. Tested under macOS Ventura 13.

## Installation

`pip install -r requirements.txt`

### macOS
To allow the Companion read the keyboard and mouse on macOS, please see the section _macOS_ under [Platform limitations — pynput 1.7.6 documentation](https://pynput.readthedocs.io/en/latest/limitations.html). 

**Without that, the automated copy&paste from the app to the Companion will not work.**

The python executable must be white-listed in the security settings under _Enable access for assistive devices_.
If you feel uncomfortable with white-listing the whole Python installation,
I suggest you create and white-list a virtual Python environment, which has its own copy of Python 
and install the Companion there.

## Configuration

The environment variable OPENAI_KEY must contain your OpenAI API key.

The program is configured through profile files in TOML format. The default profile is **profile-default.toml**.
Custom profiles are collected during startup by reading all files with the .toml extension.

To define a new profile:

* Create a new .toml file in the program's directory
* Use the default profile as a template for the syntax of the properties.
* Mandatory: *settings.name*
* Mandatory: *actions*

## Run

`python3 main.py`

The program must be run in its directory, otherwise the configuration profiles will not be found.

## Potential Features

In some use cases, it may seem useful to paste the GPT output back into the source text.
However, this is a very dangerous feature, because the focus must not be taken away
from the text while GPT is running.
The application lacks the capability to identify the origin of the text or determine 
if the source application is currently in an editable input mode. That would require deep OS integration. 


