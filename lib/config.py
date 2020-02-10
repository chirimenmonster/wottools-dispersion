
import argparse
import os

TIERS = [ str(tier) for tier in range(1, 10 + 1) ]
TIERS_LABEL = { '1':'I', '2':'II', '3':'III', '4':'IV', '5':'V', '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X'}
TIERS_LIST = [ TIERS_LABEL[t] for t in TIERS ]

WG_TYPES = [ 'lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG' ]
TYPES_MAP = { 'lightTank':'LT', 'mediumTank':'MT', 'heavyTank':'HT', 'AT-SPG':'TD', 'SPG':'SPG' }
TYPES = [ TYPES_MAP[t] for t in WG_TYPES ]


class Config:
    gui = False
    PKG_RELPATH = 'res/packages'
    LOCALE_RELPATH = 'res'
    VEHICLES = 'vehicles'
    GUI_SETTINGS = 'gui'
    SCRIPTS_DIR = None
    GUI_DIR = None
    basedir = None
    pkgdir = None
    scriptspkg = None
    guipkg = None
    localedir = None
    schema = None
    suppress_unique = False
    suppress_empty = False
    csvoutput = False
    outputjson = False
    sort = None
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

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='basedir', help='specify <WoT_game_folder>')
    parser.add_argument('-s', dest='scriptsdir', help='scripts folder extracted.  ex. "C:/git/wot.scripts/scripts"')
    parser.add_argument('-g', dest='guidir', help='gui folder extracted.  ex. "./test/gui"')
    parser.add_argument('--schema', dest='schema', help='change itemschema.json')
    parser.add_argument('--gui-items', dest='gui_items', help='change guisettings_items.json')

    if mode != 'cui':
        parser.add_argument('--vehicle', dest='vehicle', help='vehicle name.  ex. "R80_KV1"')
    else:
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--nation', action='store_true', dest='list_nation', help='show nations')
        group.add_argument('--tier', action='store_true', dest='list_tier', help='show tiers')
        group.add_argument('--type', action='store_true', dest='list_type', help='show vehicle types')
        group.add_argument('--vehicle', dest='list_vehicle', help='vehicle name or filter NATION:TIER:TYPE.  ex. "R80_KV1" or "germany:9:HT"')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--csv', dest='csvoutput', action='store_true', help='output CSV')
        group.add_argument('--json', dest='outputjson', action='store_true', help='output JSON')

        parser.add_argument('--list-module', dest='list_module', help='list modules.  ex. "gun" or "engine,radio')
        parser.add_argument('--show', dest='show_params', help='parameter names to show.  ex. "shell:speed,shell:gravity"')
        parser.add_argument('--headers', dest='show_headers', help='header names to show.')
        parser.add_argument('--sort', dest='sort', help='parameter names to sort.')
        parser.add_argument('--suppress-unique', action='store_true', dest='suppress_unique', help='suppress remove duplicate')
        parser.add_argument('--suppress-header', action='store_true', dest='suppress_header', help='suppress output csv header')
        parser.add_argument('--suppress-empty', action='store_true', dest='suppress_empty', help='suppress output recodes with empty parameter')
        parser.add_argument('--prefer-userstring', action='store_const', const='userString', default='index', dest='indextag', help='prefer userString')

    parser.parse_args(namespace=g_config)
    if g_config.SCRIPTS_DIR:
        g_config.DATA[g_config.VEHICLES]['extracted'] = g_config.SCRIPTS_DIR
    if g_config.GUI_DIR:
        g_config.DATA[g_config.GUI_SETTINGS]['extracted'] = g_config.GUI_DIR
