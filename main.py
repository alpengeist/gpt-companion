import os
import time
import ttkbootstrap as ttk
import tkinter as tk
import pynput

import config
import remotectrl as remote
import gpt

BTN_WIDTH = 10
GPT_READY = 'READY'
GPT_RUNNING = 'RUNNING'
mouse_pos = ()
prompt_active = False

def change_profile(unused):
    cbb_profiles['values'] = config.profile_choices()
    menu_actions.delete(0, tk.END)
    config.select(cbb_profiles.get())
    build_action_menu(menu_actions)
    cbb_models['values'] = config.models()
    cbb_models.set(cbb_models['values'][0])
    cbb_actions['values'] = config.action_choices()
    v_action.set(config.action_first())
    v_temperature.set(config.temperature())
    v_autocall.set(config.autocall())
    v_use_popup.set(config.action_popup())
    v_max_tokens.set(config.max_tokens())


def replace_text(widget, text):
    widget.delete('1.0', tk.END)
    widget.insert('1.0', text)
    if widget == txt_input:
        set_wordcount(v_input_counter, text)
    if widget == txt_output:
        set_wordcount(v_output_counter, text)


def get_output():
    return txt_output.get('1.0', tk.END)


def set_wordcount(v, text):
    v.set(str(len(text.split())))


def update_output_counter():
    set_wordcount(v_output_counter, txt_output.get('1.0', tk.END))


def update_input_counter():
    set_wordcount(v_input_counter, txt_input.get('1.0', tk.END))


def set_message(text):
    sysmessage['text'] = text


def set_temperature(v):
    v = round(float(v), 2)
    v_temperature.set(v)


def set_max_tokens(v):
    v = round(float(v) / 25.0) * 25
    if v == 0:
        v = 1
    v_max_tokens.set(int(v))


def paste_clipboard():
    try:
        replace_text(txt_input, remote.get_clipboard(root))
    except tk.TclError:
        replace_text(txt_output, 'Sorry, clipboard "copy" operation failed in source application.'
                                 ' Maybe it is too slow to react or uses the hotkey for something else.')


def action_completion():
    gpt_completion(config.action_text(cbb_actions.get())
)

def prompt_completion(user_prompt):
    prompt = f'''Your task is to work on the presented text using the provided instructions.
    Respond in the language of the instruction unless a different language is asked for.
    <text>
    $text
    </text>
    <instructions>
    {user_prompt}
    </instructions>
    '''
    gpt_completion(prompt)

def gpt_completion(prompt):
    set_message('')
    text = txt_input.get('1.0', tk.END)
    replace_text(txt_output, '')
    update_input_counter()
    progress_gpt['text'] = GPT_RUNNING
    frame.update()
    try:
        chunks = gpt.chat_completion(
            prompt=prompt, text=text, temperature=v_temperature.get(),
            model=cbb_models.get(), max_tokens=int(v_max_tokens.get()),
            instruction=config.instruction())
        txt_output.delete('1.0', tk.END)
        # collect the response from GPT live into the output box
        for c in chunks:
            t = c.choices[0].delta.content or ''
            txt_output.insert(tk.END, t)
            txt_output.see(tk.END)
            txt_output.update()
        # if switched on, write the output content to where the current keyboard focus is
        if v_write_back.get():
            write_back()
    except Exception as e:
        replace_text(txt_output, f'{e=}')
    finally:
        progress_gpt['text'] = GPT_READY
        update_output_counter()


def write_back():
    if v_autocall.get():
        if not remote.write_text(root, get_output()):
            set_message('The application with keyboard focus is not editable, better switch off "Write back"')


def paste_and_complete():
    remote.send_copy_key()
    paste_clipboard()
    if v_autocall.get():
        action_completion()

def prompt_and_complete(prompt):
    remote.send_copy_key()
    paste_clipboard()
    prompt_completion(prompt)

def build_action_menu(m):
    def menu_action_command(cmd):
        hide_action_menu()
        cbb_actions.set(cmd)
        paste_and_complete()

    m.add_command(label="-Close-")  # dummy command to be able to close menu without effect
    m.add_separator()
    for action in config.action_choices():
        # a=action makes sure we get the value of action, not the variable
        m.add_command(label=action, command=lambda a=action: menu_action_command(a))


def pop_action_menu():
    menu_actions.post(mouse_pos[0], mouse_pos[1])


def hide_action_menu():
    menu_actions.unpost()
    menu_actions.grab_release()

def display_prompt_entry():
    """Display a popup entry field to enter a prompt for GPT completion."""
    # Create a small popup window
    global prompt_active
    if prompt_active:
        return
    prompt_active = True
    popup = tk.Toplevel(root)
    popup.title("Prompt for selected text")
    popup.resizable(True, True)
    popup.attributes('-topmost', True)
    popup.lift()
    # Make it appear near the mouse position
    popup.geometry(f"+{mouse_pos[0]}+{mouse_pos[1]}")
    # Create an entry field
    prompt_entry = tk.Entry(popup, width=80)
    prompt_entry.pack(pady=10, padx=10, fill=tk.X, expand=True)
    popup.grab_set()
    popup.after(100, lambda: popup.focus_set())

    def close(event=None):
        global prompt_active
        prompt_active = False
        popup.destroy()

    def on_enter(event):
        prompt_text = prompt_entry.get()
        close()
        # after the popup is closed, the previously active app with the selected text will get focus again.
        if prompt_text.strip():
            prompt_and_complete(prompt_text)


    prompt_entry.bind("<Return>", on_enter)
    popup.bind("<Escape>", close)
    popup.protocol("WM_DELETE_WINDOW", close)


    # Add a Cancel button
    # cancel_button = tk.Button(popup, text="Cancel", command=popup.destroy)
    # cancel_button.pack(pady=5)

    # Ensure entry gets focus - do this after all UI elements are created
    prompt_entry.focus_set()
    # Additional measure to force focus
    popup.after(100, lambda: prompt_entry.focus_force())


def mouse_moved(x, y):
    global mouse_pos
    # strangely enough, macOS sends mouse positions as float
    mouse_pos = (int(x), int(y))


def bind_keyboard_and_mouse():
    mlistener = pynput.mouse.Listener(on_move=mouse_moved)
    mlistener.start()
    # due to a race condition in a non-threadsafe macOS implementation a short delay is required
    time.sleep(1)

    def release(k):
        hotkey.release(klistener.canonical(k))
        hotkey2.release(klistener.canonical(k))

    def press(k):
        hotkey.press(klistener.canonical(k))
        hotkey2.press(klistener.canonical(k))

    # Popups don't go well with pynput HotKey because they snatch all the key releases.
    # This messes up the internal state management of the HotKey instance. We help him by releasing the keys.
    def action_menu():
        for k in hotkey_parsed:
            release(k)
        if v_use_popup.get():
            pop_action_menu()
        else:
            paste_and_complete()

    def prompt():
        # for k in hotkey2_parsed:
        #     release(k)
        display_prompt_entry()

    hotkey_parsed = pynput.keyboard.HotKey.parse(config.hotkey())
    hotkey = pynput.keyboard.HotKey(hotkey_parsed, action_menu)
    hotkey2_parsed = pynput.keyboard.HotKey.parse(config.hotkey2())
    hotkey2 = pynput.keyboard.HotKey(hotkey2_parsed, prompt)

    klistener = pynput.keyboard.Listener(on_press=press, on_release=release)
    klistener.start()


def reload_profiles():
    config.read_all_profiles()
    change_profile(None)


def create_wordcount_label(parent, text):
    wordcount = ttk.Frame(parent)
    lbl_wordcount = ttk.Label(wordcount, text=text, bootstyle='light')
    v_wordcount = tk.StringVar(value='0')
    lbl_wordcount_value = ttk.Label(wordcount, textvariable=v_wordcount, bootstyle='light')
    lbl_wordcount.grid(row=0, column=0, sticky="w")
    lbl_wordcount_value.grid(row=0, column=1, sticky="w")
    return wordcount, v_wordcount


root = ttk.Window(themename='darkly')
if config.on_top():
    root.attributes('-topmost', 1)
root.title('Text Companion')
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
tk.font.nametofont('TkTextFont').configure(size=config.font_size())     # combo boxes
tk.font.nametofont('TkDefaultFont').configure(size=config.font_size())  # everything else

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
txt_input.bind('<Control-Return>', lambda e: action_completion())

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
btn_gpt = ttk.Button(actionbox, text='RUN', command=action_completion, width=BTN_WIDTH, bootstyle='success')
# action menu
lbl_action = ttk.Label(actionbox, text='Action:')
v_action = tk.StringVar()
cbb_actions = ttk.Combobox(actionbox, values=config.action_choices(), textvariable=v_action)
cbb_actions.state(['readonly'])
cbb_actions.set(config.action_first())

# option box
optionbox = ttk.Frame(actionbox)
# hotkey autocall option
v_autocall = tk.IntVar(value=config.autocall())
btn_autocall = ttk.Checkbutton(optionbox, variable=v_autocall, text='Auto call')
# popup menu option
v_use_popup = tk.IntVar(value=config.action_popup())
btn_use_popup = ttk.Checkbutton(optionbox, variable=v_use_popup, text='Action popup')
v_write_back = tk.IntVar(value=False)
btn_write_back = ttk.Checkbutton(optionbox, variable=v_write_back, text='Write back')
#option box layout
btn_use_popup.grid(row=0, column=0)
btn_autocall.grid(row=0, column=1, padx=15)
btn_write_back.grid(row=0, column=2)

# actionbox layout
lbl_action.grid(row=0, column=0, sticky='w')
cbb_actions.grid(row=0, column=1, sticky='e', padx=5, pady=5)
btn_paste.grid(row=0, column=2)
btn_gpt.grid(row=0, column=3, padx=5, pady=5)
optionbox.grid(row=0, column=4, padx=10)

# Model parameters box
modelbox = ttk.Frame(frame)
# model menu
lbl_models = ttk.Label(modelbox, text='Model:')
cbb_models = ttk.Combobox(modelbox, values=config.models())
cbb_models.state(['readonly'])
cbb_models.set(config.models()[0])
# temperature display
v_temperature = tk.DoubleVar(value=config.temperature())
lbl_temperature = ttk.Label(modelbox, text='Temperature:')
scl_temperature = ttk.Scale(modelbox, from_=0, to=1, variable=v_temperature, command=set_temperature)
lbl_temperature_value = ttk.Label(modelbox, textvariable=v_temperature, width=4)
# max_tokens display
v_max_tokens = tk.IntVar(value=config.max_tokens())
lbl_max_tokens = ttk.Label(modelbox, text='Max output tokens:')
scl_max_tokens = ttk.Scale(modelbox, from_=1, to=4000, variable=v_max_tokens, command=set_max_tokens, length=250)
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
progress_gpt.grid(row=6, column=0, columnspan=3, sticky='w', pady=20)
outputbox.grid(row=7, columnspan=3, sticky='ewns')
frame.rowconfigure(7, weight=1)
output_counter.grid(row=8, column=0, sticky='e', pady=(5, 10))
sysmessage = ttk.Label(frame, bootstyle='danger')
sysmessage.grid(row=8, column=0, sticky='w')

replace_text(txt_input,
f'''Copy text to clipboard and press <Paste> button, or use hotkey {config.hotkey()} for action popup.
Use hotkey {config.hotkey2()} for immediate prompting.
You can also type text here and press Ctrl+Enter to prompt the Companion.
''')
replace_text(txt_output, "Companion's output goes here.")

menu_actions = tk.Menu(root, tearoff=0)
build_action_menu(menu_actions)
bind_keyboard_and_mouse()

if __name__ == '__main__':
    if not os.getenv('OPENAI_API_KEY'):
        print('Missing environment variable OPENAI_API_KEY')
        exit(1)
    root.mainloop()
