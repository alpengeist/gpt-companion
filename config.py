import tomllib
import glob

_selected = {}
profiles = {}


def empty_profile():
    return {'name': 'empty', 'settings': {'models:[]'}, 'actions': [{'pass-through': ''}]}


def select(pname):
    global _selected
    if pname not in profiles:
        raise 'unknown profile {pname}'
    _selected = profiles[pname]


def selected():
    return _selected


def profile_choices():
    return [k for k in profiles.keys()]


def get_with_fallback(section, prop):
    if section in selected():
        return selected()[section].get(prop, default_profile()[section][prop])
    else:
        return default_profile()[section][prop]


def name():
    return selected()['settings']['name']


def models():
    return get_with_fallback('settings', 'models')


def chat_models():
    return get_with_fallback('settings', 'chat_models')


def all_models():
    return chat_models() + models()


def chat_instruction():
    return get_with_fallback('settings', 'chat_instruction')


def temperature():
    return get_with_fallback('settings', 'temperature')


def max_tokens():
    return get_with_fallback('settings', 'max_tokens')


def action_choices():
    return [k for k in selected()['actions'].keys()]


def action_first():
    return next(iter(selected()['actions']))


def action_text(choice):
    return selected()['actions'].get(choice, '')


def default_profile():
    return profiles['Default']


def startup():
    return default_profile()['startup']


def action_popup():
    return startup()['action_popup']


def autocall():
    return startup()['autocall']


def on_top():
    return startup()['on_top']


def hotkey():
    return startup()['hotkey']


def hotkey_wait():
    return startup()['hotkey_wait']


def font_size():
    return startup()['font_size']


def validate_profile(p):
    if not p.get('settings', {}).get('name'):
        raise ValueError('missing mandatory property settings.name')
    if p['settings']['name'] in profiles:
        raise ValueError('duplicate profile name')
    if not p.get('actions'):
        raise ValueError('missing or empty mandatory property settings.actions')


# read custom profile and overwrite the default values
def read_config_profile(filename):
    with open(filename, 'rb') as prof:
        prof = tomllib.load(prof)
    return prof


def read_all_profiles():
    profiles.clear()
    files = glob.glob('*.toml')
    files.sort()
    for f in files:
        if f != 'profile-default':
            print('reading profile ' + f)
            profile = read_config_profile(f)
            try:
                validate_profile(profile)
            except ValueError as e:
                print(f'Error in profile {f}, file skipped: {e}')
            else:
                profiles[profile['settings']['name']] = profile
    if 'Default' not in profiles:
        raise 'Default profile not found. Make sure to run the program in the installation directory'
    select('Default')


read_all_profiles()
