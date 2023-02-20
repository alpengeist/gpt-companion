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

## Prerequisites
Python 3.11

## Platforms

Tested and developed under Windows 11

## Installation
`pip install -r requirements.txt`

The **keyboard** module, which is required for the hot key handling, works under Linux as well. MacOS is experimental.

## Run

`python3 main.py`

The program must be run in its directory, otherwise the configuration profiles will not be found.

## Configuration
The environment variable OPENAI_KEY must contain your OpenAI API key.

The program is configured through profile files in TOML format. The default profile is **profile-default.toml**.
Custom profiles are collected during startup by reading all files with the .toml extension.
  
To define a new profile:
* Create a new .toml file in the program's directory
* Use the default profile as a template for the syntax of the properties.
* Mandatory: *settings.name*
* Optional: *settings.models*
* Optional: *actions*

## Future Ideas
* Optional: Issue a paste keyboard command after GPT is finished. This could integrate GPT seamlessly in any text application.