import os
import sys
import time
import ttkbootstrap as ttk
import tkinter as tk
import pynput
# import keyboard
import config
import gpt


def change_profile(e):
    menu_actions.delete(0, len(config.action_choices()) + 1)
    config.select(cbb_profiles.get())
    build_action_menu(menu_actions)
    cbb_models.configure(values=config.all_models())
    cbb_models.set(config.all_models()[0])
    cbb_actions.configure(values=config.action_choices())
    v_action.set(config.action_first())


def replace_text(widget, text):
    widget.delete('1.0', tk.END)
    widget.insert('1.0', text)
    if widget == txt_input:
        set_wordcount(v_input_counter, text)
    if widget == txt_output:
        set_wordcount(v_output_counter, text)


def set_wordcount(v, text):
    v.set(str(len(text.split())))


def update_output_counter():
    set_wordcount(v_output_counter, txt_output.get('1.0', tk.END))


def update_input_counter():
    set_wordcount(v_input_counter, txt_input.get('1.0', tk.END))


def set_temperature(v):
    v = round(float(v), 2)
    v_temperature.set(f'{v}')


def set_max_tokens(v):
    v = round(float(v) / 25.0) * 25
    if v == 0:
        v = 1
    v_max_tokens.set(str(v))


def paste_clipboard():
    try:
        text = root.clipboard_get()
        replace_text(txt_input, text)
    except tk.TclError:
        replace_text(txt_output, 'Sorry, clipboard "copy" operation failed in source application.'
                                 ' Maybe it is too slow to react or uses the hotkey for something else.')


def gpt_completion():
    text = txt_input.get('1.0', tk.END)
    prefix = config.action_text(cbb_actions.get())
    replace_text(txt_output, '')
    update_input_counter()
    frame.update()
    try:
        progress_gpt['text'] = GPT_RUNNING
        frame.update()
        model = cbb_models.get()
        if model in config.chat_models():
            res = gpt.chat_completion(
                prefix=prefix, text=text, temperature=float(v_temperature.get()),
                model=cbb_models.get(), max_tokens=int(v_max_tokens.get()),
                instruction=config.chat_instruction())
        else:
            res = gpt.completion(
                prefix=prefix, text=text, temperature=float(v_temperature.get()),
                model=cbb_models.get(), max_tokens=int(v_max_tokens.get()))
        txt_output.delete('1.0', tk.END)
        for t in res:
            txt_output.insert(tk.END, t)
            txt_output.see(tk.END)
            txt_output.update()
    except RuntimeError as e:
        replace_text(txt_output, f'{e=}')
    finally:
        progress_gpt['text'] = GPT_READY
        update_output_counter()


def paste_and_complete():
    # Give app time to settle from hotkey
    time.sleep(config.hotkey_wait())
    # Force source app to copy to clipboard and wait a little
    # keyboard.send('ctrl+c')
    c = pynput.keyboard.Controller()
    if sys.platform == 'darwin':
        with c.pressed(pynput.keyboard.Key.cmd):
            c.press('c')
            c.release('c')
            c.release(pynput.keyboard.Key.cmd)
    else:
        with c.pressed(pynput.keyboard.Key.ctrl):
            c.press('c')
            c.release('c')
            c.release(pynput.keyboard.Key.ctrl)
    time.sleep(config.hotkey_wait())
    paste_clipboard()
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
    menu_actions.post(mouse_pos[0], mouse_pos[1])
    # menu_actions.focus_set()


def hide_action_menu():
    menu_actions.unpost()
    menu_actions.grab_release()


def mouse_moved(x, y):
    global mouse_pos
    mouse_pos = (x, y)


def hotkey_pressed():
    if config.action_popup():
        pop_action_menu()
    else:
        paste_and_complete()


def bind_keyboard_and_mouse():
    # if sys.platform != 'darwin':
    mlistener = pynput.mouse.Listener(on_move=mouse_moved)
    mlistener.start()
    # due to a race condition in a non-threadsafe macOS implementation a short delay is required
    time.sleep(1)

    # keyboard.add_hotkey(config.hotkey(), pop_action_menu)

    def release(k):
        # print(f'release {k}')
        hotkey.release(klistener.canonical(k))

    def press(k):
        # print(f'press {k}')
        hotkey.press(klistener.canonical(k))

    # Popups don't go well with pynput HotKey because they snatch all the key releases.
    # This messes up the internal state management of the HotKey instance. We help him by releasing the keys.
    def activate():
        for k in pk:
            release(k)
        pop_action_menu()

    pk = pynput.keyboard.HotKey.parse(config.hotkey())
    hotkey = pynput.keyboard.HotKey(pk, activate)
    klistener = pynput.keyboard.Listener(on_press=press, on_release=release)
    klistener.start()


def reload_profiles():
    config.read_all_profiles()
    change_profile(None)


def create_wordcount_label(parent, text):
    wordcount = ttk.Frame(parent)
    lbl_wordcount = ttk.Label(wordcount, text=text, bootstyle='light')
    v_wordcount = tk.StringVar()
    v_wordcount.set("0")
    lbl_wordcount_value = ttk.Label(wordcount, textvariable=v_wordcount, bootstyle='light')
    lbl_wordcount.grid(row=0, column=0, sticky="w")
    lbl_wordcount_value.grid(row=0, column=1, sticky="w")
    return wordcount, v_wordcount


BTN_WIDTH = 10
GPT_READY = 'GPT is ready.'
GPT_RUNNING = 'GPT is working...'
mouse_pos = ()

root = ttk.Window(themename='darkly')
if config.startup()['on_top']:
    root.attributes('-topmost', 1)
root.title('GPT Companion')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Master frame
frame = ttk.Frame(root, padding=10, borderwidth=2, width=800, height=500)
frame.grid(column=0, row=0, columnspan=3, sticky='nsew')
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

# INPUT and OUTPUT text fields
# The ScrolledText widget does not support the ^A key (select_range), so forget it.
# Attaching a scrollbar to a text widget is not so difficult after all.
# The ttkbootstrap scrollbar in the dark theme is almost invisible. We stay with the Tk scrollbar.
inputbox = ttk.Frame(frame)
txt_input = ttk.Text(inputbox, height=10, wrap=tk.WORD, relief=tk.FLAT)
scroll_input = ttk.Scrollbar(inputbox, orient=tk.VERTICAL, command=txt_input.yview, bootstyle='light')
txt_input.config(yscrollcommand=scroll_input.set)
txt_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_input.pack(side=tk.RIGHT, fill=tk.Y)
txt_input.bind('<Control-Return>', lambda e: gpt_completion())

input_counter, v_input_counter = create_wordcount_label(frame, 'Input word count:')

outputbox = ttk.Frame(frame)
txt_output = ttk.Text(outputbox, height=10, wrap=tk.WORD, relief=tk.FLAT)
scroll_output = ttk.Scrollbar(outputbox, orient=tk.VERTICAL, command=txt_output.yview, bootstyle='light')
txt_output.config(yscrollcommand=scroll_output.set)
txt_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll_output.pack(side=tk.RIGHT, fill=tk.Y)

output_counter, v_output_counter = create_wordcount_label(frame, 'Output word count:')

# Profile menu
profilebox = ttk.Frame(frame)
lbl_profiles = ttk.Label(profilebox, text='Profile:')
cbb_profiles = ttk.Combobox(profilebox, values=config.profile_choices())
cbb_profiles.state(['readonly'])
cbb_profiles.set(config.name())
cbb_profiles.bind('<<ComboboxSelected>>', change_profile)
btn_reload = ttk.Button(profilebox, text='Reload', width=BTN_WIDTH, command=reload_profiles)
lbl_profiles.grid(row=0, column=0, sticky='w')
cbb_profiles.grid(row=0, column=1, padx=5, sticky='e')
btn_reload.grid(row=0, column=2)

# Action box
actionbox = ttk.Frame(frame)
btn_paste = ttk.Button(actionbox, text='Paste', command=paste_clipboard, width=BTN_WIDTH)
btn_gpt = ttk.Button(actionbox, text='Call GPT', command=gpt_completion, width=BTN_WIDTH, bootstyle='success')
# action menu
lbl_action = ttk.Label(actionbox, text='Action:')
v_action = tk.StringVar()
cbb_actions = ttk.Combobox(actionbox, values=config.action_choices(), textvariable=v_action)
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
cbb_models = ttk.Combobox(modelbox, values=config.all_models())
cbb_models.state(['readonly'])
cbb_models.set(config.all_models()[0])
# temperature display
v_temperature = tk.StringVar()
v_temperature.set(str(config.temperature()))
lbl_temperature = ttk.Label(modelbox, text='Temperature:')
scl_temperature = ttk.Scale(modelbox, from_=0, to=1, value=config.temperature(), command=set_temperature)
lbl_temperature_value = ttk.Label(modelbox, textvariable=v_temperature, width=4)
# max_tokens display
v_max_tokens = tk.StringVar()
v_max_tokens.set(str(config.max_tokens()))
lbl_max_tokens = ttk.Label(modelbox, text='Max output tokens:')
scl_max_tokens = ttk.Scale(modelbox, from_=1, to=4000, value=config.max_tokens(), command=set_max_tokens, length=250)
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
inputbox.grid(row=0, column=0, sticky='nsew')
frame.rowconfigure(0, weight=0)
input_counter.grid(row=1, column=0, sticky='e', pady=(5, 10))
profilebox.grid(row=2, column=0, sticky='w', pady=5)
modelbox.grid(row=3, column=0, sticky='w', pady=5)
actionbox.grid(row=4, column=0, sticky='w', pady=5)
progress_gpt = ttk.Label(frame, bootstyle='info', text=GPT_READY)
progress_gpt.grid(row=5, column=0, columnspan=3, sticky='w', pady=10)
outputbox.grid(row=6, columnspan=3, sticky='ewns')
frame.rowconfigure(6, weight=1)
output_counter.grid(row=7, column=0, sticky='e', pady=(5, 10))

replace_text(txt_input, 'Copy text to clipboard and press <Paste> button, or use hotkey ' + config.hotkey()
             + '\nYou can also type text here and press Ctrl+Enter to run GPT.')
replace_text(txt_output, 'GPT output goes here.')

menu_actions = tk.Menu(root, tearoff=0)
build_action_menu(menu_actions)
bind_keyboard_and_mouse()

if __name__ == '__main__':
    if not os.getenv('OPENAI_KEY'):
        print('Missing environment variable OPENAI_KEY')
        exit(1)
    root.mainloop()
