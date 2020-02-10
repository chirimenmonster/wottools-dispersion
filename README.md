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

vehicleinfo.py [-h] [-d BASEDIR] [-s SCRIPTSDIR] [-g GUIDIR]
                      [--schema SCHEMA] [--gui-items GUI_ITEMS]
                      [--nation | --tier | --type | --vehicle LIST_VEHICLE]
                      [--csv | --json] [--list-module LIST_MODULE]
                      [--show SHOW_PARAMS] [--headers SHOW_HEADERS]
                      [--sort SORT] [--suppress-unique] [--suppress-header]
                      [--suppress-empty] [--prefer-userstring]


### example

+ list vehicles.  arg of option `--vehicle` may pattern NATION:TIER:TYPE.
`::` for all vehicles.

```
$ ./vehicleinfo.py --vehicle ussr:8:mt:all
 Nation    Tier    Type  Secret      Id Index                           UserString
   ussr       8      MT              17 R20_T-44                        T-44
   ussr       8      MT              52 R60_Object416                   Object 416
   ussr       8      MT  secret     152 R20_T-44_IGR                    T-44
   ussr       8      MT             171 R112_T54_45_FL                  T-54 first prototype FL
   ussr       8      MT             172 R20_T-44_FL                     T-44 FL
   ussr       8      MT  secret     180 R127_T44_100_K                  Т-44-100 (К)
   ussr       8      MT             181 R127_T44_100_U                  Т-44-100 (У)
   ussr       8      MT             185 R146_STG_Tday                   STG Guard
   ussr       8      MT             186 R146_STG                        STG
   ussr       8      MT             191 R122_T44_100B                   T-44-100 (B)
   ussr       8      MT             234 R112_T54_45                     T-54 first prototype
   ussr       8      MT             242 R122_T44_100                    Т-44-100
   ussr       8      MT             246 R127_T44_100_P                  T-44-100 (R)
```

+ list available module pattern.  arg of option `--list-module` may be chassis, turret, engine, radio, gun, shell.

```
$ ./vehicleinfo.py --vehicle G16_PzVIB_Tiger_II --list-module gun
Vehicle                         Turret                                 Gun
G16_PzVIB_Tiger_II              PzVIB_Porsche_Turm                     _88mm_KwK_43_L71
G16_PzVIB_Tiger_II              PzVIB_Porsche_Turm                     _105mm_KwK45_L52
G16_PzVIB_Tiger_II              PzVIB_Porsche_Turm                     _105mm_KwK46_L68
G16_PzVIB_Tiger_II              PzVIB_Heinschel_Turm                   _88mm_KwK_43_L71
G16_PzVIB_Tiger_II              PzVIB_Heinschel_Turm                   _105mm_KwK45_L52
G16_PzVIB_Tiger_II              PzVIB_Heinschel_Turm                   _105mm_KwK46_L68
```

+ show shell gravity without spg.  removed duplicate lines.

```
$ ./vehicleinfo.py --vehicle ::lt,mt,td,ht --list-module shell --show shell:gravity --csv
shell:gravity
9.81
```

+ show secret vehicles.  fource parameter on --vehicles may be "secret", "all" or none.

```
$ ./vehicleinfo.py --vehicle germany:10::secret
 Nation    Tier    Type  Secret      Id Index                           UserString
germany      10      HT  secret     159 G42_Maus_IGR                    Maus
germany      10      HT  secret     168 G134_PzKpfw_VII_bob             Pz.Kpfw. VII BB
germany      10      TD  secret      66 G98_Waffentrager_E100           Waffenträger auf E 100
germany      10      TD  secret     190 G98_Waffentrager_E100_P         Waffenträger auf E 100 (P)
```
