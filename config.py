# key = Text in dropdown box
# value = prefix for the GPT prompt
actions = {
    "Summarize": "sum up the text:\n",
    "Readability": "optimize the readability:\n",
    "Explain Word": "explain the word ",
    "Alternative Words": "name altenative words for:\n",
    "Typical Sentence": "write a typical sentence with:\n",
    "Opposite": "name the opposite of:\n",
    "To German": "translate to German:\n",
    "To English": "translate to English:\n",
    "Pass-through": ""
}
MODELS = ["text-davinci-003", "text-curie-001", "text-babbage-001", "text-ada-001"]
TEMPERATURE = 0.7
MAX_TOKENS = 1000
# start value of the corresponding checkbox in the UI. 1 = call GPT immediately after pasting the text
AUTOCALL = 0
COPY_KEY = "ctrl+c"
HOTKEY = "alt+ctrl+g"
# Apps have to digest the hotkeys first before they can copy selected text. This takes a little time.
# After the waiting time the companion sends COPY_KEY keypress to the app.
# If you notice that selected text is not copied, try increasing the time or another hotkey.
HOTKEY_WAIT = 1     # seconds


def choices():
    return [k for k in actions.keys()]


def default():
    return next(iter(actions))  # first entry


def text(choice):
    return actions[choice] if choice in actions else ""
