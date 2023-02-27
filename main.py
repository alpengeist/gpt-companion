import os
import time
import ttkbootstrap as ttk
import tkinter as tk
# ttkboostratp ScrolledText messes up a few things, including key binding.
# We stay with ye good ole scrolledtext
from tkinter import scrolledtext
import keyboard
import mouse
import config
import gpt


def change_profile(e):
    menu_actions.delete(0, len(config.action_choices())+1)
    config.select(cbb_profiles.get())
    build_action_menu(menu_actions)
    cbb_models.configure(values=config.models())
    cbb_models.set(config.models()[0])
    cbb_actions.configure(values=config.action_choices())
    v_action.set(config.action_first())


def replace_text(widget, text):
    widget.delete('1.0', tk.END)
    widget.insert('1.0', text)
    if widget == txt_input:
        set_tokencount(text)


def set_tokencount(text):
    v_tokencount.set(str(len(text.split())))


def set_temperature(v):
    v = round(float(v), 2)
    v_temperature.set(f'{v}')


def set_max_tokens(v):
    v = round(float(v) / 10.0) * 10  # increment in 10s
    if v == 0:
        v = 1
    v_max_tokens.set(str(v))


def paste_clipboard():
    text = root.clipboard_get()
    replace_text(txt_input, text)


def gpt_completion():
    text = txt_input.get('1.0', tk.END)
    prefix = config.action_text(cbb_actions.get())
    replace_text(txt_output, 'working on it...')
    txt_output.update()
    try:
        progress_gpt.step(5)
        frame.update()
        res = gpt.completion(prefix=prefix, text=text, temperature=float(v_temperature.get()),
                             model=cbb_models.get(), max_tokens=int(v_max_tokens.get()))
        txt_output.delete('1.0', tk.END)
        for event in res:
            txt_output.insert(tk.END, event['choices'][0]['text'])
            txt_output.see(tk.END)
            progress_gpt.step()
            txt_output.update()
    finally:
        progress_gpt['value']=0


def paste_and_complete():
    # Give app time to settle from hotkey
    time.sleep(config.hotkey_wait())
    # print('sending ctrl+c')
    # Force source app to copy to clipboard and wait a little
    keyboard.send(config.copy_key())
    time.sleep(config.hotkey_wait())
    try:
        paste_clipboard()
    except tk.TclError:
        replace_text(txt_output, 'Sorry, clipboard "copy" operation failed in source application.'
                                 ' Maybe it is too slow to react or uses the hotkey for something else.')
    if v_autocall.get():
        gpt_completion()


def build_action_menu(m):
    def menu_action_command(cmd):
        cbb_actions.set(cmd)
        paste_and_complete()
        hide_action_menu()

    m.add_command(label="-Close-")  # dummy command to be able to close menu without effect
    m.add_separator()
    for action in config.action_choices():
        # a=action makes sure we get the value of action, not the variable
        m.add_command(label=action, command=lambda a=action: menu_action_command(a))


def pop_action_menu():
    pos = mouse.get_position()
    menu_actions.post(pos[0], pos[1])
    menu_actions.focus_set()


def hide_action_menu():
    menu_actions.unpost()
    menu_actions.grab_release()


def hotkey_pressed():
    if config.startup()['action_popup']:
        pop_action_menu()
    else:
        paste_and_complete()


root = ttk.Window(themename='darkly')
if config.startup()['on_top']:
    root.attributes('-topmost',1)
root.title('GPT Companion')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Master frame
frame = ttk.Frame(root, padding=10, borderwidth=2, width=800, height=500)
frame.grid(column=0, row=0, columnspan=3, sticky='nsew')
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

# INPUT and OUTPUT text fields
txt_input = scrolledtext.ScrolledText(frame, width=100, height=10, wrap=tk.WORD, relief=tk.FLAT)
txt_input.columnconfigure(0, weight=1)
txt_input.rowconfigure(0, weight=1)
txt_input.bind('<Control-Return>', lambda e: gpt_completion())

txt_output = scrolledtext.ScrolledText(frame, height=10, wrap=tk.WORD, relief=tk.FLAT)
txt_output.columnconfigure(0, weight=1)
txt_output.rowconfigure(2, weight=1)

# token counter
tokencount = ttk.Frame(frame)
lbl_tokencount = ttk.Label(tokencount, text="Input Token Count:")
v_tokencount = tk.StringVar()
v_tokencount.set("0")
lbl_tokencount_value = ttk.Label(tokencount, textvariable=v_tokencount)
lbl_tokencount.grid(row=0, column=0, sticky="w")
lbl_tokencount_value.grid(row=0, column=1, sticky="w")

# Profile menu
profilebox = ttk.Frame(frame)
lbl_profiles = ttk.Label(profilebox, text='Profile:')
cbb_profiles = ttk.Combobox(profilebox, values=config.profile_choices())
cbb_profiles.state(['readonly'])
cbb_profiles.set(config.name())
cbb_profiles.bind('<<ComboboxSelected>>', change_profile)
lbl_profiles.grid(row=0, column=0, sticky='w')
cbb_profiles.grid(row=0, column=1, padx=5, sticky='e')

# Action box
actionbox = ttk.Frame(frame)
btn_paste = ttk.Button(actionbox, text='Paste', command=paste_clipboard, bootstyle='secondary')
btn_gpt = ttk.Button(actionbox, text='Call GPT', command=gpt_completion)
# action menu
lbl_action = ttk.Label(actionbox, text='Action:')
v_action = tk.StringVar()
cbb_actions = ttk.Combobox(actionbox, values=config.action_choices(), textvariable=v_action, bootstyle='primary')
cbb_actions.state(['readonly'])
cbb_actions.set(config.action_first())
# hotkey autocall option
v_autocall = tk.IntVar()
v_autocall.set(config.autocall())
btn_autocall = ttk.Checkbutton(actionbox, variable=v_autocall, text='Auto call with hotkey ' + config.hotkey())
# actionbox layout
lbl_action.grid(row=0, column=0)
cbb_actions.grid(row=0, column=1, sticky='ns', padx=5, pady=5)
btn_paste.grid(row=0, column=2)
btn_gpt.grid(row=0, column=3, padx=5, pady=5)
btn_autocall.grid(row=0, column=4, padx=5)

# Model parameters box
modelbox = ttk.Frame(frame)
# model menu
lbl_models = ttk.Label(modelbox, text='Model:')
cbb_models = ttk.Combobox(modelbox, values=config.models())
cbb_models.state(['readonly'])
cbb_models.set(config.models()[0])
# temperature display
v_temperature = tk.StringVar()
v_temperature.set(str(config.temperature()))
lbl_temperature = ttk.Label(modelbox, text='Temperature:')
scl_temperature = ttk.Scale(modelbox, from_=0, to=1, value=config.temperature(), command=set_temperature)
lbl_temperature_value = ttk.Label(modelbox, textvariable=v_temperature, width=4)
# max_tokens display
v_max_tokens = tk.StringVar()
v_max_tokens.set(str(config.max_tokens()))
lbl_max_tokens = ttk.Label(modelbox, text='Maximum Output Tokens (Words):')
scl_max_tokens = ttk.Scale(modelbox, from_=1, to=4000, value=config.max_tokens(), command=set_max_tokens, length=150)
lbl_max_tokens_value = ttk.Label(modelbox, textvariable=v_max_tokens, width=6)
# modelbox layout
lbl_models.grid(row=0, column=0, sticky='e')
cbb_models.grid(row=0, column=1, padx=5, sticky='e')
lbl_temperature.grid(row=0, column=2, sticky='e')
scl_temperature.grid(row=0, column=3, padx=5, sticky='w')
lbl_temperature_value.grid(row=0, column=4, padx=5, sticky='e')
lbl_max_tokens.grid(row=0, column=5, padx=5, sticky='e')
scl_max_tokens.grid(row=0, column=6, columnspan=2, sticky='ew')
lbl_max_tokens_value.grid(row=0, column=8, padx=5, sticky='e')

# master frame layout
txt_input.grid(row=0, column=0, columnspan=3, sticky='nsew')
tokencount.grid(row=1, column=0, sticky='w', pady=(5, 10))
profilebox.grid(row=2, column=0, sticky='w', pady=5)
modelbox.grid(row=3, column=0, sticky='w', pady=5)
actionbox.grid(row=4, column=0, sticky='w', pady=5)
txt_output.grid(row=5, columnspan=3, sticky='nsew')
progress_gpt = ttk.Progressbar(frame, mode='indeterminate')
progress_gpt.grid(row=6, column=0, columnspan=3, sticky='ew', pady=10)

replace_text(txt_input, 'Copy text to clipboard and press <Paste> button, or use hotkey ' + config.hotkey()
             + '\nYou can also type text here and press Ctrl+Enter to run GPT.')

menu_actions = tk.Menu(root, tearoff=0)
build_action_menu(menu_actions)
keyboard.add_hotkey(config.hotkey(), hotkey_pressed)

if __name__ == '__main__':
    if not os.getenv('OPENAI_KEY'):
        print('Missing environment variable OPENAI_KEY')
        exit(1)
    root.mainloop()