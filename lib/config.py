import argparse
import os

from lib.resources import g_resources

BASE_DIRS = [ 'C:/Games/World_of_Tanks', 'C:/Games/World_of_Tanks_ASIA' ]

class Config:
    BASE_DIR = 'C:/Games/World_of_Tanks'
    PKG_RELPATH = 'res/packages'
    LOCALE_RELPATH = 'res'
    VEHICLES = 'vehicles'
    GUI_SETTINGS = 'gui'
    DATA = {
        VEHICLES: {
            'vpath':        'scripts/item_defs/vehicles',
            'packed':       'scripts.pkg',
            'extracted':    None
        },
        GUI_SETTINGS: {
            'vpath':        'gui',
            'packed':       'gui.pkg',
            'extracted':    None
        }
    }
    moduleSpecified = {
        'chassis':  -1,
        'turret':   -1,
        'engine':   -1,
        'radio':    -1,
        'gun':      -1,
        'shell':    0
    }


g_config = Config()

def parseArgument(mode=None):
    for d in BASE_DIRS:
        if os.path.isdir(d):
            g_config.BASE_DIR = d
            break

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='BASE_DIR', help='specify <WoT_game_folder>')
    parser.add_argument('-s', dest='SCRIPTS_DIR', help='scripts folder extracted.  ex. "C:/git/wot.scripts/scripts"')
    parser.add_argument('-g', dest='GUI_DIR', help='gui folder extracted.  ex. "./test/gui"')
    parser.add_argument('--secret', action='store_true', help='include secret tanks')
    parser.add_argument('--gui-items', dest='gui_items', help='change guisettings_items.json')

    if mode != 'cui':
        parser.add_argument('--vehicle', dest='vehicle', help='vehicle name.  ex. "R80_KV1"')
    else:
        parser.add_argument('--vehicle', dest='vehicle', help='vehicle name or filter NATION:TIER:TYPE.  ex. "R80_KV1" or "germany:9:HT"')

    if mode == 'cui':
        parser.add_argument('--csv', dest='csvoutput', action='store_true', help='output CSV')
        parser.add_argument('--list-nation', action='store_true', help='show nations')
        parser.add_argument('--list-tier', action='store_true', help='show tiers')
        parser.add_argument('--list-type', action='store_true', help='show vehicle types')
        parser.add_argument('--list-module', dest='list_module', help='list modules.  ex. "gun" or "engine,radio')
        parser.add_argument('--params', dest='show_params', help='parameter names to show.  ex. "shell:speed,shell:gravity"')
        parser.add_argument('--suppress-unique', action='store_true', dest='suppress_unique', help='suppress remove duplicate')
        parser.add_argument('--suppress-header', action='store_true', dest='suppress_header', help='suppress output csv header')

    parser.parse_args(namespace=g_config)
    if g_config.SCRIPTS_DIR:
        g_config.DATA[g_config.VEHICLES]['extracted'] = g_config.SCRIPTS_DIR
    if g_config.GUI_DIR:
        g_config.DATA[g_config.GUI_SETTINGS]['extracted'] = g_config.GUI_DIR

    if g_config.gui_items:
        g_resources.guisettings_items = g_config.gui_items
    g_resources.load()

