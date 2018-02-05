
import io
import csv

labeldesc = {
    'vehicle':  [ 'name', 'id', 'shortUserString', 'description' ],
    'chassis':  [ 'name', 'tag' ],
    'turret':   [ 'name', 'tag' ],
    'gun':      [ 'name', 'tag' ],
    'shell':    [ 'name', 'tag' ],
}

datadesc = [
    [ 'gun',        'reloadTime',           's' ],
    [ 'gun',        'aimingTime',           's' ],
    [ 'gun',        'shotDispersionRadius', 'm' ],
    [ 'chassis',    'vehicleMovement',      ''  ],
    [ 'chassis',    'vehicleRotation',      ''  ],
    [ 'gun',        'turretRotation',       ''  ],
    [ 'gun',        'afterShot',            ''  ],
    [ 'gun',        'whileGunDamaged',      ''  ],
    [ 'shell',      'damage_armor',         ''  ],
    [ 'shell',      'damage_devices',       ''  ],
]


def createMessage(strage, nation, vehicle, chassis, turret, gun, shell):
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    info = {}
    info['vehicle'] = strage.fetchVehicleInfo(nation, vehicle)
    info['chassis'] = strage.fetchChassisInfo(nation, vehicle, chassis)
    info['turret'] = strage.fetchTurretInfo(nation, vehicle, turret)
    info['gun'] = strage.fetchGunInfo(nation, vehicle, turret, gun)
    info['shell'] = strage.fetchShellInfo(nation, gun, shell)

    for category in [ 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
        data = [ category ] + [ strage[category][name] for name in labeldesc[category] ]
        writer.writerow(data)

    for category, name, unit in datadesc:
        writer.writerow([ name, strage[category][name], unit ])

    return output.getvalue()
