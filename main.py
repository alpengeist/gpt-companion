import os
import time
import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import *

import keyboard

import config
import gpt


def set_temperature(v):
    v = round(float(v),2)
    v_temp_text.set(f"{v}")


def paste_clipboard():
    text = root.clipboard_get()
    txt_input.replace("1.0", tk.END, text)


def call_gpt():
    text = txt_input.get("1.0", tk.END)
    prefix = config.text(opt_actions.get())
    txt_output.replace("1.0", tk.END, f"{prefix}\nworking on it...")
    txt_output.update()
    res = gpt.call_gpt(prefix=prefix, text=text, temperature=float(v_temp_text.get()),
                       model=opt_models.get(), max_tokens=config.MAX_TOKENS)
    txt_output.replace("1.0", tk.END, res)


def paste_and_call():
    # Give app time to settle from hotkey
    time.sleep(config.HOTKEY_WAIT or 1)
    # print("sending ctrl+c")
    # Force source app to copy to clipboard and wait a little
    keyboard.send(config.COPY_KEY or "ctrl+c")
    time.sleep(config.HOTKEY_WAIT or 1)
    try:
        paste_clipboard()
    except TclError:
        txt_output.replace("1.0", tk.END, "Sorry, clipboard 'copy' operation failed in source application."
                                          " Maybe it is too slow to react or uses the hotkey for something else.")
    if v_autocall.get():
        call_gpt()


root = Tk()
root.title("GPT Companion")
ttk.Style().configure('.', font=('Helvetica', 10))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


# Master frame
frame = ttk.Frame(root, padding=10, borderwidth=2, width=800, height=500)
frame.grid(column=0, row=0, columnspan=3, sticky="nsew")
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

# INPUT and OUTPUT text fields
txt_input = ScrolledText(frame, width=100, wrap=tk.WORD, relief=tk.FLAT)
txt_input.insert("1.0", "Copy text to clipboard and press <Paste> button, or use hotkey " + config.HOTKEY)
txt_input.columnconfigure(0, weight=1)
txt_input.rowconfigure(0, weight=1)
txt_output = ScrolledText(frame, wrap=tk.WORD, relief=tk.FLAT)
txt_output.columnconfigure(0, weight=1)
txt_output.rowconfigure(2, weight=1)

# Action box
actionbox = Frame(frame)
btn_paste = Button(actionbox, text="Paste", command=paste_clipboard)
btn_gpt = Button(actionbox, text="Call GPT", command=call_gpt)
v_action = tk.StringVar()
# action menu
opt_actions = ttk.Combobox(actionbox, values=config.choices(), font=('Helvetica', 10))
opt_actions.state(["readonly"])
opt_actions.set(config.default())
# hotkey autocall option
v_autocall = tk.IntVar()
v_autocall.set(config.AUTOCALL)
btn_autocall = ttk.Checkbutton(actionbox, variable=v_autocall, text="Auto call with hotkey " + config.HOTKEY)

# Model parameters box
modelbox = ttk.Frame(frame)
# model menu
lbl_models = ttk.Label(modelbox, text="Model:")
opt_models = ttk.Combobox(modelbox, values=config.MODELS, font=('Helvetica', 10))
opt_models.state(["readonly"])
opt_models.set(config.MODELS[0])
# temperature display
v_temp_text = tk.StringVar()
v_temp_text.set(f"{config.TEMPERATURE}")
lbl_temp = ttk.Label(modelbox, textvariable=v_temp_text)
# slider label
lbl_temp_scale = ttk.Label(modelbox, text="Temperature:")
scl_temp = ttk.Scale(modelbox, from_=0, to=1, value=config.TEMPERATURE, command=set_temperature)

# modelbox layout
lbl_models.grid(row=0, column=0, sticky="e")
opt_models.grid(row=0, column=1, columnspan=1, padx=5, sticky="e")
lbl_temp_scale.grid(row=0, column=2, sticky="e")
scl_temp.grid(row=0, column=3, sticky="w")
lbl_temp.grid(row=0, column=4, sticky="e")

# actionbox layout
btn_paste.grid(row=0)
opt_actions.grid(row=0, column=1, sticky="ns", padx=10, pady=5)
btn_gpt.grid(row=0, column=2, padx=5, pady=5)
btn_autocall.grid(row=0, column=3, padx=5)

# master frame layout
txt_input.grid(row=0, column=0, columnspan=3, sticky="nsew")
actionbox.grid(row=1, column=0, sticky="w", pady=5)
modelbox.grid(row=2, column=0, sticky="w", pady=5)
txt_output.grid(row=3, columnspan=3, sticky="nsew")

keyboard.add_hotkey(config.HOTKEY, paste_and_call)

if __name__ == '__main__':
    if not os.getenv('OPENAI_KEY'):
        print("Missing environment variable OPENAI_KEY")
        exit(1)
    root.mainloop()