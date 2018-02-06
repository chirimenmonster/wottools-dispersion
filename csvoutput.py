
import io
import csv
import json

labeldesc = {
    'vehicle':  [ 'name', 'id', 'shortUserString', 'description' ],
    'chassis':  [ 'name', 'tag' ],
    'turret':   [ 'name', 'tag' ],
    'gun':      [ 'name', 'tag' ],
    'shell':    [ 'name', 'tag' ],
}

dataorder = [ 'gun:reloadTime', 'gun:aimingTime', 'gun:shotDispersionRadius',
    'chassis:vehicleMovement', 'chassis:vehicleRotation',
    'gun:turretRotation', 'gun:afterShot', 'gun:whileGunDamaged',
    'shell:damage_armor', 'shell:damage_devices'
]

def fetchItemdef():
    with open('itemdef.json', 'r') as fp:
        data = json.load(fp)
    return data


def createMessage(strage, nation, vehicle, chassis, turret, gun, shell):
    info = {}
    info['vehicle'] = strage.fetchVehicleInfo(nation, vehicle)
    info['chassis'] = strage.fetchChassisInfo(nation, vehicle, chassis)
    info['turret'] = strage.fetchTurretInfo(nation, vehicle, turret)
    info['gun'] = strage.fetchGunInfo(nation, vehicle, turret, gun)
    info['shell'] = strage.fetchShellInfo(nation, gun, shell)

    dataList = fetchItemdef()
    
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    for category in [ 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
        data = [ category ] + [ info[category][name] for name in labeldesc[category] ]
        writer.writerow(data)

    for target in dataorder:
        category, node = target.split(':')
        unit = dataList[category][node]['unit']
        writer.writerow([ node, info[category][node], unit ])

    return output.getvalue()

items = fetchItemdef()

if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    fetchItemdef()
