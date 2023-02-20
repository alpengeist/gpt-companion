import copy
import tomllib
import glob

_selected = {}
profiles = {'Default': {'settings': {}}}


def default():
    return profiles['Default']


def select(pname):
    global _selected
    _selected = profiles[pname]


def selected():
    return _selected


def profile_choices():
    return [k for k in profiles.keys()]


def name():
    return selected()['settings']['name']


def action_choices():
    return [k for k in selected()['actions'].keys()]


def action_default():
    return next(iter(selected()['actions']))  # first entry


def action_text(choice):
    return selected()['actions'][choice] if choice in selected()['actions'] else ''


def hotkey():
    return selected()['settings']['hotkey']


def hotkey_wait():
    return selected()['settings']['hotkey_wait']


def copy_key():
    return selected()['settings']['copy_key']


def temperature():
    return selected()['settings']['temperature']


def models():
    return selected()['settings']['models']


def autocall():
    return selected()['settings']['autocall']


def max_tokens():
    return selected()['settings']['max_tokens']


# read custom profile and overwrite the default values
def read_config_profile(filename):
    with open(filename, 'rb') as prof:
        result = copy.deepcopy(default())
        custom = tomllib.load(prof)
        result['actions'] = custom['actions']  # actions are completely overwritten
        for k in custom['settings']:  # settings get merged
            result['settings'][k] = custom['settings'][k]
        return result


def read_all_profiles():
    profiles['Default'] = read_config_profile('profile-default.toml')
    select('Default')
    files = glob.glob('*.toml')
    files.sort()
    for f in files:
        if f != 'profile-default':
            print('reading profile ' + f)
            profile = read_config_profile(f)
            profiles[profile['settings']['name']] = profile


read_all_profiles()
