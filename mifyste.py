"""minimal steam grid generator"""

import textwrap
import os
import sys
import shutil
import platform
from pathlib import Path
import steam.utils.appcache
import PySimpleGUI as sg
from PIL import Image, ImageFont, ImageDraw

def resource_path():
    """ Get resource path to work with PyInstaller OneFile """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return base_path

def get_steam_path():
    """Return the pathname of the Steam root directory or empty String."""
    user_platform = platform.system()
    if user_platform == "Linux":
        home_dir = str(Path.home())
        if os.path.exists(home_dir + "/.local/share/Steam/"):
            return home_dir + "/.local/share/Steam/"

    if user_platform == "Windows":
        try:
            import winreg
            hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\WOW6432Node\\Valve\\Steam")
            steam_path_found = winreg.QueryValueEx(hkey, 'InstallPath')[0]
            return steam_path_found
        except OSError:
            return ""

    if user_platform == "Darwin":
        if os.path.exists("~/Library/Application Support/Steam/"):
            home_dir = str(Path.home())
            if os.path.exists(home_dir + "/Library/Application Support/Steam/"):
                return home_dir + "/Library/Application Support/Steam/"
    return ""

def clear_steamcache(steampath):
    """Clears Library cache"""
    shutil.rmtree(steampath + '/appcache/librarycache/')

def get_users(steampath):
    """Returns a list of users in Steam subdirectory userdata"""
    if os.path.exists(steampath + "/userdata/"):
        users = os.listdir(steampath + "/userdata/")
        if '0' in users:
            users.remove('0')
        user_list = []
        for user in users:
            user_config = steampath + '/userdata/' + user + '/' + "config/localconfig.vdf"
            if os.path.exists(user_config):
                with open(user_config, 'rb') as file:
                    data = file.read().decode()
                    persona_name = data.split('"PersonaName"')
                    persona_name = persona_name[1].split('"')[1].strip()
                user_list.append((persona_name, '@', user))
        return user_list
    return [""]

def get_hmax(gamefont):
    """Get the maximum height of the given font"""
    testimg = Image.new("RGBA",(1,1))
    all_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    imgedit = ImageDraw.Draw(testimg)
    _, _, _, hmax = imgedit.textbbox((0, 0), all_chars, gamefont)
    return hmax

def get_games(gridpath, steampath):
    """Gather all games"""
    games = set()

    with open(steampath + "/appcache/appinfo.vdf", "rb") as file:
        data = steam.utils.appcache.parse_appinfo(file)
        for elem in data[1]:
            try:
                tracked_elements = ['Beta', 'Video', 'Tool', 'Game', 'game', 'Application']
                if elem['data']['appinfo']['common']['type'] in tracked_elements:
                    games.add((elem['appid'], elem['data']['appinfo']['common']['name']))
            except KeyError:
                pass

    if os.path.exists(gridpath + "/../shortcuts.vdf"):
        with open(gridpath + "/../shortcuts.vdf", "rb") as file:
            data = steam.utils.appcache.binary_load(file)
            for elem in data["shortcuts"].values():
                games.add((str(int(elem['appid']) + 4294967296),elem['appName']))

    return games

def run_minify(gridpath, steampath, overwrite, clearcache):
    """The main image generation & cleanup function"""
    gridpath = gridpath.replace("\\", "/") + '/'
    if not os.path.exists(gridpath):
        try:
            os.mkdir(gridpath)
        except FileNotFoundError:
            window['-STATUS-'].update("Could not create grid directory.")
            return
    games = get_games(gridpath, steampath)
    counter_processed = 0

    total_games = str(len(games))
    while len(games)!=0:
        game = games.pop()
        appid = str(game[0])
        text = game[1]
        imgoptions = [("bg.png", 24, ".png", 25),("pbg.png",44,"p.png", 16)]

        if not os.path.exists(gridpath+appid+".json") or overwrite:
            for imgoption in imgoptions:
                gamefont = ImageFont.truetype(
                                    resource_path() + "/resources/fffforwa.ttf",
                                    imgoption[1],
                )

                hmax = get_hmax(gamefont)
                img = Image.open(resource_path() + "/resources/" + imgoption[0])
                width, height = img.size
                imgedit = ImageDraw.Draw(img)
                wrappedtext = textwrap.wrap(text, width=imgoption[3])

                pad = hmax/3
                currenth = (height/2) - pad - ((len(wrappedtext) - 1)*2*pad)

                for line in wrappedtext:
                    _, _, w_1, _ = imgedit.textbbox((0, 0), line, gamefont)
                    imgedit.text(((width-w_1)/2,currenth), line, (208,211,212), font = gamefont)
                    currenth = currenth + hmax + pad

                img.save(gridpath+appid+imgoption[2])

            testimg = Image.new("RGBA",(1,1))
            imgedit = ImageDraw.Draw(testimg)
            gamefont = ImageFont.truetype(resource_path() + "/resources/fffforwa.ttf", 64)
            _, _, w_1, h_1 = imgedit.textbbox((0, 0),text,gamefont)
            img = Image.new("RGBA",(w_1,h_1+10))
            imgedit = ImageDraw.Draw(img)
            imgedit.text((0,10), text, (208,211,212), font = gamefont)
            img.save(gridpath+appid+"_logo.png")
            shutil.copy(resource_path() + "/resources/centerlogo.json",gridpath+appid+".json")
            shutil.copy(resource_path() + "/resources/herobg.png",gridpath+appid+"_hero.png")
            counter_processed += 1
            window['-STATUS-'].update(f'{counter_processed} of {total_games} games processed.')
            window.refresh()
            

    window['-STATUS-'].update(f'{counter_processed*5} files have been added to {gridpath}')
    if clear_steamcache:
        window['-STATUS-'].update(f'Cleaning steam library cache.')
        clear_steamcache(steampath)
        window['-STATUS-'].update(f'{counter_processed*5} added and cache cleaned!')

STEAMPATH = get_steam_path()
if STEAMPATH == "":
    STATUS = 'Autodetection failed, manual input required.'

USER = get_users(STEAMPATH)
if USER == [""]:
    STATUS = 'Autodetection failed, manual input required.'
else:
    STATUS = 'Please select a user.'

sg.theme('DarkGrey8')

col_one = [
            [sg.Text(STATUS, key='-STATUS-')],
            [
                sg.Text('Enter Steam path:'),
                sg.In(
                        default_text=STEAMPATH,
                        size=(50,1),
                        enable_events=True,
                        key='-INPUT_STEAMPATH-',
                ),
                sg.FolderBrowse(),
            ],
            [
                sg.Text('Select User: '),
                sg.Combo(USER,size=49, key='-INPUT_USER-', default_value=USER[0], readonly=True,),
                sg.Button('< Refresh >', key='-REFRESH_USERS-'),
            ],
            [
                sg.Checkbox('Overwrite current files', key='-INPUT_OVERWRITE-'),
                sg.Checkbox('Clear Cache', key='-INPUT_CLEARCACHE-'),
            ],
            [sg.Button('<< Create grid files >>', key='-CREATE_GRID-')],
]

layout = [[sg.Column(col_one, element_justification='c')]]
window = sg.Window('mifyste', layout, resizable=True,)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == '-CREATE_GRID-':
        window['-STATUS-'].update('Fetching appid & names... Please wait.')
        if values['-INPUT_USER-'] == "":
            window['-STATUS-'].update('User must not be empty.')
        else:
            grpa = f'{values["-INPUT_STEAMPATH-"]}/userdata/{values["-INPUT_USER-"][2]}/config/grid'
            window.refresh()
            run_minify(grpa, 
                       values["-INPUT_STEAMPATH-"], 
                       values["-INPUT_OVERWRITE-"], 
                       values["-INPUT_CLEARCACHE-"])

    if event == '-REFRESH_USERS-':
        STEAMPATH = values['-INPUT_STEAMPATH-']
        USER = get_users(STEAMPATH)
        if USER == [""]:
            window['-STATUS-'].update('No users found.')
        else:
            window['-STATUS-'].update('Select a user and create grid files.')
        window['-INPUT_USER-'].update(values = USER)
