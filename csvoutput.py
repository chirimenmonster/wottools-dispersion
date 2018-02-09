
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

def fetchItemdef():
    with open('itemdef.json', 'r') as fp:
        data = json.load(fp)
    return data


def createMessage(strage, param, items):
    dataList = fetchItemdef()
    
    output = io.StringIO(newline='')
    writer = csv.writer(output, dialect='excel', lineterminator='\n')

    for node in [ 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
        writer.writerow([ node, *strage.getDescription(node, param) ])

    for target in items:
        category, node = target.split(':')
        unit = dataList[category][node]['unit']
        writer.writerow([ node, strage.find(category, node, param), unit ])

    return output.getvalue()

items = fetchItemdef()

if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    fetchItemdef()
