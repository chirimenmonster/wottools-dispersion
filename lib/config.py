import argparse

from lib.resources import g_resources


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

g_config = Config()

def parseArgument(mode=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='BASE_DIR', help='specify <WoT_game_folder>')
    parser.add_argument('-s', dest='SCRIPTS_DIR', help='scripts folder extracted.  ex. "C:\git\wot.scripts\scripts"')
    parser.add_argument('-g', dest='GUI_DIR', help='gui folder extracted.  ex. ".\test\gui"')
    parser.add_argument('--secret', action='store_true', help='include secret tanks')
    parser.add_argument('--gui-items', dest='gui_items', help='change guisettings_items.json')
    
    if mode == 'test':
        parser.add_argument('--list', dest='pattern', help='show vehicle list for NATION:TIER:TYPE.  ex. "germany:9:HT"')
        parser.add_argument('--list-nation', action='store_true', help='show nations')
        parser.add_argument('--list-tier', action='store_true', help='show tiers')
        parser.add_argument('--list-type', action='store_true', help='show vehicle types')
        parser.add_argument('--list-chassis', dest='vehicle_chassis', help='list chassis for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-turret', dest='vehicle_turret', help='list turret for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-engine', dest='vehicle_engine', help='list engine for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-radio', dest='vehicle_radio', help='list radio for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-gun', dest='vehicle_gun', help='list gun for vehicle and turret.  ex. "R80_KV1:Turret_2_KV1"')
        parser.add_argument('--list-shell', dest='gun_shell', help='list shell for gun and turret.  ex. "ussr:_85mm_F-30"')

        parser.add_argument('--info', dest='vehicle', help='view info for vehicle.  ex. "R80_KV1:Chassis_KV1_2:Turret_2_KV1:V-2K:_10RK:_85mm_F-30:_85mm_UBR-365K"')

    parser.parse_args(namespace=g_config)
    if g_config.SCRIPTS_DIR:
        g_config.DATA[g_config.VEHICLES]['extracted'] = g_config.SCRIPTS_DIR
    if g_config.GUI_DIR:
        g_config.DATA[g_config.GUI_SETTINGS]['extracted'] = g_config.GUI_DIR

    if g_config.gui_items:
        g_resources.guisettings_items = g_config.gui_items
    g_resources.load()

