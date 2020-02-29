
import argparse
import sys


class Config:
    version = '0.3.2'
    gui = False
    PKG_RELPATH = 'res/packages'
    LOCALE_RELPATH = 'res'
    basedir = None
    scriptsdir = None
    guidir = None
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


def parseArgument(mode=None):

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--base', dest='basedir', help='specify <WoT_game_folder>')
    parser.add_argument('-s', '--scripts', dest='scriptsdir', help='WoT scripts folder extracted.  ex. "C:/git/wot.scripts/scripts"')
    parser.add_argument('-g', '--gui', dest='guidir', help='WoT gui folder extracted.  ex. "./test/data/res/gui"')
    parser.add_argument('-L', '--locale', dest='localedir', help='locale folder, with "text".  ex. "<WoT_game_folder>/res"')
    parser.add_argument('-S', '--schema', dest='schema', metavar='SCHEMAFILE', help='change "itemschema.json".  default is "res/itemschema.json"')
    parser.add_argument('-v', action='store_true', dest='show_version', help='show version')

    if mode != 'cui':
        parser.add_argument('--vehicle', dest='vehicle', help='vehicle name.  ex. "R80_KV1"')
    else:
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--nation', action='store_true', dest='list_nation', help='show nations')
        group.add_argument('--tier', action='store_true', dest='list_tier', help='show tiers')
        group.add_argument('--type', action='store_true', dest='list_type', help='show vehicle types')
        group.add_argument('--tag', action='store_const', const='.', dest='list_tag', help='show all tags')
        group.add_argument('--tag-pattern', dest='list_tag', metavar='REGEX', help='show tags matched regex')
        parser.add_argument('vehicle', help='vehicle name or filter NATION:TIER:TYPE.  ex. "R80_KV1" or "germany:9:HT"')

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--csv', dest='output_csv', action='store_true', help='output CSV')
        group.add_argument('--json', dest='output_json', action='store_true', help='output JSON')

        parser.add_argument('--module', dest='list_module', metavar='MODULE_LIST', help='list modules.  ex. "gun" or "engine,radio')
        parser.add_argument('--show', dest='show_params', metavar='TAGS', help='parameter names to show.  ex. "shell:speed,shell:gravity"')
        parser.add_argument('--headers', dest='show_headers', metavar='TAGS', help='header names to show.')
        parser.add_argument('--sort', dest='sort', metavar='TAGS', help='parameter names to sort.')
        parser.add_argument('--suppress-unique', action='store_true', dest='suppress_unique', help='suppress remove duplicate')
        parser.add_argument('--suppress-header', action='store_true', dest='suppress_header', help='suppress output csv header')
        parser.add_argument('--suppress-empty', action='store_true', dest='suppress_empty', help='suppress output recodes with empty parameter')

    config = Config()
    config.gui = mode == 'gui'
    parser.parse_args(namespace=config)
    
    if config.show_version:
        print(config.version)
        sys.exit()

    return config
