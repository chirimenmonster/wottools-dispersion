
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

#import gui
#dataorder = []
#for column in gui.itemGroup:
#    for row in column:
#        dataorder += row['items']


def fetchItemdef():
    with open('itemdef.json', 'r') as fp:
        data = json.load(fp)
    return data


def createMessage(strage, param, items):
    info = {}
    info['vehicle'] = strage.fetchVehicleInfo(param['nation'], param['vehicle'])
    info['chassis'] = strage.fetchChassisInfo(param['nation'], param['vehicle'], param['chassis'])
    info['turret'] = strage.fetchTurretInfo(param['nation'], param['vehicle'], param['turret'])
    info['gun'] = strage.fetchGunInfo(param['nation'], param['vehicle'], param['turret'], param['gun'])
    info['shell'] = strage.fetchShellInfo(param['nation'], param['gun'], param['shell'])

    dataList = fetchItemdef()
    
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    for category in [ 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
        data = [ category ] + [ info[category][name] for name in labeldesc[category] ]
        writer.writerow(data)

    for target in items:
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
