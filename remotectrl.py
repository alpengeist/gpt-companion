import time
from pynput.keyboard import Key, Controller
import sys
import config
import tkinter as tk

cliptext = ''


def get_clipboard(root):
    global cliptext
    cliptext = root.clipboard_get()
    return cliptext


def is_editable(root, probe_key):
    c = Controller()
    # type one key and kill any assistant popup that might appear in editors
    c.press(probe_key)
    c.release(probe_key)
    c.press(Key.esc)
    c.release(Key.esc)
    # Select the character just typed, copy it to clipboard, check whether the clipboard content is this character.
    # In editable applications, the single key will overwrite the current selection, which has been copied over
    # to the Companion for Completion.
    with c.pressed(Key.shift):
        c.press(Key.left)
    try:
        send_copy_key()
        ct = root.clipboard_get()
        return ct == probe_key
    except tk.Tcl:
        return False


def write_text(root, text):
    if is_editable(root, text[0]):
        c = Controller()
        c.type(text)
        return True
    else:
        return False


def send_copy_key():
    # Give app time to settle from hotkey
    time.sleep(config.hotkey_wait())
    # Force source app to copy to clipboard and wait a little
    c = Controller()
    if sys.platform == 'darwin':
        # something seems to be fishy with Key.cmd as argument
        with c.pressed(Key.cmd.value):
            c.press('c')
            c.release('c')
    else:
        with c.pressed(Key.ctrl):
            c.press('c')
            c.release('c')
    time.sleep(config.hotkey_wait())
