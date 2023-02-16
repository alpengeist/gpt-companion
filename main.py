import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import keyboard
import config
import gpt


def replace_text(widget, text):
    widget.replace('1.0', tk.END, text)


def set_temperature(v):
    v = round(float(v) ,2)
    v_temperature.set(f'{v}')


def set_max_tokens(v):
    v = round(float(v) / 10.0) * 10     # increment in 10s
    if v == 0:
        v = 1
    v_max_tokens.set(str(v))


def paste_clipboard():
    text = root.clipboard_get()
    replace_text(txt_input, text)


def gpt_completion():
    text = txt_input.get('1.0', tk.END)
    prefix = config.text(cbb_actions.get())
    replace_text(txt_output, f'{prefix}\nworking on it...')
    txt_output.update()
    res = gpt.completion(prefix=prefix, text=text, temperature=float(v_temperature.get()),
                         model=cbb_models.get(), max_tokens=int(v_max_tokens.get()))
    replace_text(txt_output, res)


def paste_and_complete():
    # Give app time to settle from hotkey
    time.sleep(config.HOTKEY_WAIT or 1)
    # print('sending ctrl+c')
    # Force source app to copy to clipboard and wait a little
    keyboard.send(config.COPY_KEY or 'ctrl+c')
    time.sleep(config.HOTKEY_WAIT or 1)
    try:
        paste_clipboard()
    except tk.TclError:
        replace_text(txt_output,'Sorry, clipboard "copy" operation failed in source application.'
                                ' Maybe it is too slow to react or uses the hotkey for something else.')
    if v_autocall.get():
        gpt_completion()


root = tk.Tk()
root.title('GPT Companion')
ttk.Style().configure('.', font=('Helvetica', 10))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


# Master frame
frame = ttk.Frame(root, padding=10, borderwidth=2, width=800, height=500)
frame.grid(column=0, row=0, columnspan=3, sticky='nsew')
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

# INPUT and OUTPUT text fields
txt_input = scrolledtext.ScrolledText(frame, width=100, wrap=tk.WORD, relief=tk.FLAT)
replace_text(txt_input, 'Copy text to clipboard and press <Paste> button, or use hotkey ' + config.HOTKEY)
txt_input.columnconfigure(0, weight=1)
txt_input.rowconfigure(0, weight=1)
txt_output = scrolledtext.ScrolledText(frame, wrap=tk.WORD, relief=tk.FLAT)
txt_output.columnconfigure(0, weight=1)
txt_output.rowconfigure(2, weight=1)

# Action box
actionbox = ttk.Frame(frame)
btn_paste = ttk.Button(actionbox, text='Paste', command=paste_clipboard)
btn_gpt = ttk.Button(actionbox, text='Call GPT', command=gpt_completion)
v_action = tk.StringVar()
# action menu
cbb_actions = ttk.Combobox(actionbox, values=config.choices(), font=('Helvetica', 10))
cbb_actions.state(['readonly'])
cbb_actions.set(config.default())
# hotkey autocall option
v_autocall = tk.IntVar()
v_autocall.set(config.AUTOCALL)
btn_autocall = ttk.Checkbutton(actionbox, variable=v_autocall, text='Auto call with hotkey ' + config.HOTKEY)

# Model parameters box
modelbox = ttk.Frame(frame)
# model menu
lbl_models = ttk.Label(modelbox, text='Model:')
cbb_models = ttk.Combobox(modelbox, values=config.MODELS, font=('Helvetica', 10))
cbb_models.state(['readonly'])
cbb_models.set(config.MODELS[0])

# temperature display
v_temperature = tk.StringVar()
v_temperature.set(str(config.TEMPERATURE))
lbl_temperature = ttk.Label(modelbox, text='Temperature:')
scl_temperature = ttk.Scale(modelbox, from_=0, to=1, value=config.TEMPERATURE, command=set_temperature)
lbl_temperature_value = ttk.Label(modelbox, textvariable=v_temperature, width=4)

# max_tokens display
v_max_tokens = tk.StringVar()
v_max_tokens.set(str(config.MAX_TOKENS))
lbl_max_tokens = ttk.Label(modelbox, text='Maximum Output Tokens (Words):')
scl_max_tokens = ttk.Scale(modelbox, from_=1, to=4000, value=config.MAX_TOKENS, command=set_max_tokens, length=150)
lbl_max_tokens_value = ttk.Label(modelbox, textvariable=v_max_tokens, width=6)

# modelbox layout
lbl_models.grid(row=0, column=0, sticky='e')
cbb_models.grid(row=0, column=1, columnspan=1, padx=5, sticky='e')
lbl_temperature.grid(row=0, column=2, sticky='e')
scl_temperature.grid(row=0, column=3, sticky='w')
lbl_temperature_value.grid(row=0, column=4, padx=5, sticky='e')
lbl_max_tokens.grid(row=0, column=5, padx=5, sticky='e')
scl_max_tokens.grid(row=0, column=6, columnspan=2, sticky='ew')
lbl_max_tokens_value.grid(row=0, column=8, padx=5, sticky='e')

# actionbox layout
btn_paste.grid(row=0)
cbb_actions.grid(row=0, column=1, sticky='ns', padx=10, pady=5)
btn_gpt.grid(row=0, column=2, padx=5, pady=5)
btn_autocall.grid(row=0, column=3, padx=5)

# master frame layout
txt_input.grid(row=0, column=0, columnspan=3, sticky='nsew')
actionbox.grid(row=1, column=0, sticky='w', pady=5)
modelbox.grid(row=2, column=0, sticky='w', pady=5)
txt_output.grid(row=3, columnspan=3, sticky='nsew')

keyboard.add_hotkey(config.HOTKEY, paste_and_complete)

if __name__ == '__main__':
    if not os.getenv('OPENAI_KEY'):
        print('Missing environment variable OPENAI_KEY')
        exit(1)
    root.mainloop()