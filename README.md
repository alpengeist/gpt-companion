# GPT Companion

<img alt="Companion App" src="doc/app.png" width="75%" height="75%"/>

Are you familiar with DeepL's desktop tool for on the fly translations?
The GPT Companion tool works in similar ways. You select some text in a source
application and press the configurable hotkey crtl-alt-g. The Companion will
call GPT for you and display the result.

Put your preferred GPT text processing actions (prompts) into profiles, which you can switch between at runtime.
For example, you could have a profile for English, one for German, one for fun stuff, etc.
An action did not work as expected? A new action comes to mind? Just edit the profile, press the _Reload_ button and run GPT again.

Once the hotkey is pressed and *Action popup* is switched on, it displays a menu at the
current mouse position. The next image depicts a text selection in Wikipedia and
the menu after pressing the hotkey. Once an action is selected, the Companion makes the browser copy the selection
into the clipboard, and then it fetches the clipboard content. 
- If *Auto call* is switched on, it calls GPT immediately.
- If *Write back* is switched on, the output gets typed into the application that has keyboard focus.

<img alt="action popup" src="doc/popup.png" width="30%" height="30%"/>

The Companion can be configured to stay on top of all windows.

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

1. Install py2pp with `pip install py2app`
2. Create macOS app bundle with `python setup.py py2app -A` [^1]
3. Start the macOS bundle in dist folder
4. Enable "Input Monitoring" in System > Privacy & Security > Input Monitoring for GPT Companion ([Platform limitations — pynput 1.7.6 documentation](https://pynput.readthedocs.io/en/latest/limitations.html))

[^1]: Alias mode (the -A or --alias option) instructs py2app to build an application bundle that uses your source and data files in-place. It does not create standalone applications, and the applications built in alias mode are not portable to other machines.

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

## More about the *write back* feature 
To edit text in-place, switch on *Write back*. After the GPT response is complete, the Companion will first
try to type, select, and copy the first character. Then it checks whether the clipboard contains excactly this
character. In that case, the application with keyboard focus is editable.

This probing technique is pretty safe. If the source app is read-only, not much can go bad. It is just one key followed
by shift-left and ctrl-c (cmd-c on Mac). 

Still, you need to be patient while the Companion is running and not move the focus someplace else.

**Things get a little nasty when GPT takes forever to respond. As the API has no means to interrupt the current request,
you should kill the Companion first, before changing focus to another app.**