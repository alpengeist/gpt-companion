import tomllib
import glob

profiles = {}


def default():
    return profiles['default']


def select(name):
    profiles['__selected'] = profiles[name]


def selected():
    return profiles['__selected']


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


def read_config_profile(filename):
    with open(filename, 'rb') as prof:
        return tomllib.load(prof)


def read_all_profiles():
    profiles['default'] = read_config_profile('profile-default.toml')
    select('default')
    files = glob.glob('*.toml')
    files.sort()
    for f in files:
        if f != 'profile-default':
            print('reading profile ' + f)
            profile = read_config_profile(f)
            profiles[profile['settings']['name']] = profile


read_all_profiles()
