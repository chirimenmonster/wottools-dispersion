# wottools-dispersion
## environment
+ Python3
+ World of Tanks

## GUI
### usage

`python gui.py [-d <WoT_game_folder>]`

## screenshot
![image](https://user-images.githubusercontent.com/11075065/36062614-3dbf6e8e-0eb3-11e8-97bc-133baef1d1df.png)

## commandline tool
### usage

vehicleinfo.py [-h] [-d BASE_DIR] [-s SCRIPTS_DIR] [-g GUI_DIR]
                      [--secret] [--gui-items GUI_ITEMS] [--vehicle VEHICLE]
                      [--csv] [--list-nation] [--list-tier] [--list-type]
                      [--list-module LIST_MODULE] [--params SHOW_PARAMS]
                      [--suppress-unique] [--suppress-header]
                      [--prefer-userstring]

### example

+ list vehicles.  arg of option `--vehicle` may pattern NATION:TIER:TYPE.
`::` for all vehicles.

```
$ ./vehicleinfo.py --vehicle ussr:8:mt
{'vehicle:index': 'R20_T-44'}
{'vehicle:index': 'R60_Object416'}
{'vehicle:index': 'R112_T54_45_FL'}
{'vehicle:index': 'R20_T-44_FL'}
{'vehicle:index': 'R127_T44_100_U'}
{'vehicle:index': 'R146_STG_Tday'}
{'vehicle:index': 'R146_STG'}
{'vehicle:index': 'R122_T44_100B'}
{'vehicle:index': 'R112_T54_45'}
{'vehicle:index': 'R122_T44_100'}
{'vehicle:index': 'R127_T44_100_P'}
```

+ list available module pattern.  arg of option `--list-module` may be chassis, turret, engine, radio, gun, shell.

```
$ ./vehicleinfo.py --vehicle R20_T-44 --list-module gun
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44', 'gun:index': '_85mm_ZiS_S-53'}
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44', 'gun:index': '_85mm_D5T-85BM'}
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44-100', 'gun:index': '_85mm_ZiS_S-53'}
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44-100', 'gun:index': '_85mm_D5T-85BM'}
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44-100', 'gun:index': '_100mm_D10T'}
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44-100', 'gun:index': '_100mm_LB-1'}
{'vehicle:index': 'R20_T-44', 'turret:index': 'T-44-100', 'gun:index': '_122mm_D-25-44'}
```

+ show shell gravity without spg.  removed duplicate lines.

```
$ ./vehicleinfo.py --vehicle ::lt,mt,td,ht --list-module shell --params shell:gravity --csv
shell:gravity
9.81
```
