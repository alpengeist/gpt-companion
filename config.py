import copy
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


def name():
    return selected()['settings']['name']


def models():
    return selected()['settings']['models']


def action_choices():
    return [k for k in selected()['actions'].keys()]


def action_first():
    return next(iter(selected()['actions']))


def action_text(choice):
    return selected()['actions'][choice] if choice in selected()['actions'] else ''


def default():
    return profiles['Default']


def hotkey():
    return default()['startup']['hotkey']


def hotkey_wait():
    return default()['startup']['hotkey_wait']


def copy_key():
    return default()['startup']['copy_key']


def temperature():
    return default()['startup']['temperature']


def autocall():
    return default()['startup']['autocall']


def max_tokens():
    return default()['startup']['max_tokens']


def validate_profile(p):
    if 'settings' not in p or 'name' not in p['settings']:
        raise ValueError('missing mandatory property settings.name')
    if 'settings' not in p or 'models' not in p['settings'] or len(p['settings']['models']) == 0:
        raise ValueError('missing or empty mandatory property settings.models')
    if 'actions' not in p or len(p['actions']) == 0:
        raise ValueError('missing or empty mandatory property settings.actions')


# read custom profile and overwrite the default values
def read_config_profile(filename):
    with open(filename, 'rb') as prof:
        prof = tomllib.load(prof)
    return prof


def read_all_profiles():
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
