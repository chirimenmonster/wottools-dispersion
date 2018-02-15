import re
from xml.etree import ElementTree
from lib.resources import g_resources
from lib.translate import g_translate as translate
from lib.utils import readXmlData

class FindEntry(object):

    def __init__(self):
        self.__itemschema = g_resources.itemschema
        self.__xmltree = {}
        self.__functions = {
            'sum':  self.__functionSum,
            'or':   self.__functionOr
        }

    def find(self, node, param):
        schema = self.__itemschema[node]
        param = self.__getModifiedParam(node, param)
        result = None
        for r in schema['resources']:
            result = self.__getRawData(r, param)
            if result is not None:
                break
        if result is None:
            return None
        result = self.__convertType(schema, result)
        if 'map' in schema:
            result = self.__getMappedData(schema['map'], result)
        return result

    def __getXmlTree(self, resource, param):
        param = param.copy()
        if 'vehicle_file' in param:
            param['vehicle'] = param['vehicle_file']
        file = self.__substitute(resource['file'], param)
        if not file:
            return None
        if file not in self.__xmltree:
            domain, target = file.split('/', 1)
            self.__xmltree[file] = readXmlData(domain, target)
        root = self.__xmltree[file]
        return root

    def __findNode(self, resource, param):
        root = self.__getXmlTree(resource, param)
        if root is None:
            return None
        if 'xpath' in resource:
            value = self.__getNodesXpath(root, resource['xpath'], param)
        elif 'custom' in resource:
            if resource['custom'] == 'getNationsOrder()':
                value = self.__getNodesCustomGetNationsOrder(root)
            else:
                print('__findNode: not implement func: {}'.format(resource['custom']))
                raise ValueError
        else:
            print('__findNode: missing method: {}'.format(resource))
            raise ValueError
        return value

    def __substitute(self, format, param):
        for match in re.finditer('\{[^}]+\}', format):
            key = match.group()[1:-1]
            if param.get(key, None) is None:
                return None
        return format.format(**param)

    def __getModifiedParam(self, node, param):
        schema = self.__itemschema[node]
        param = param.copy()
        if param.get('siege', None) == 'siege':
            if not node == 'vehicle:siegeMode' and self.find('vehicle:siegeMode', param):
                param['vehicle_file'] = param['vehicle'] + '_siege_mode'
        if 'addparams' in schema:
            for p in schema['addparams']:
                value = self.find(p['value'], param)
                param[p['xtag']] = value
        return param

    def __getRawData(self, resource, param):
        result = None
        if 'file' in resource:
            result = self.__findNode(resource, param)
        elif 'immediate' in resource:
            result = resource['immediate']
        elif 'func' in resource:
            if resource['func'] in self.__functions:
                result = self.__functions[resource['func']](resource['args'], param)
            else:
                raise ValueError('unknown resource function: {}'.format(resource['func']))
        else:
            raise ValueError('missing valid resource: {}'.format(resource))
        return result

    def __convertType(self, schema, data):
        result = None
        if 'value' in schema:
            if schema['value'] == 'nodename':
                result = data.tag
            elif schema['value'] == 'nodelist':
                result = data
            elif schema['value'] == 'float':
                result = float(data.text)
            else:
                print('unknown value keyword: {}'.format(schema['value']))
                raise ValueError
        else:
            if isinstance(data, ElementTree.Element):
                result = data.text
            else:
                result = data
        return result

    def __getMappedData(self, map, data):
        if map == 'gettext':
            data = translate(data)
        elif map == 'roman':
            data = TIERS_LABEL[data]
        elif isinstance(map, dict):
            data = [ map[v] for v in data.split() if v in map ]
            data = data.pop(0) if data else None
        else:
            match = re.match('\[(\d)\]', str(map))
            if match:
                data = data.split()[int(match.group(1))]
            else:
                raise ValueError('unknown map method: {}'.map)
        return data

    def __getNodesXpath(self, root, template, param):
        xpath = self.__substitute(template, param)
        if xpath is None:
            return None
        nodes = root.find(xpath)
        return nodes

    def __getNodesCustomGetNationsOrder(self, root):
        for child in root.findall('settings'):
            if child.findtext('name') == 'nations_order':
                return [ i.text for i in child.findall('value') ]
        return None

    def __functionSum(self, args, param):
        result = 0
        for arg in args:
            value = self.find(arg, param)
            if value is None:
                return None
            value = float(value)
            result += value
        return result
            
    def __functionOr(self, args, param):
        result = None
        for arg in args:
            result = self.find(arg, param)
            if result:
                break
        return result

class FindFormattedEntry(FindEntry):

    def getText(self, schema, param):
        node = schema['value']
        if isinstance(node, list):
            nodes = node
        else:
            nodes = [ node ]
        values = []
        for node in nodes:
            value = self.find(node, param)
            value = self.__consider(value, schema.get('consider', None))
            values.append(value)
        text = self.__format(values, schema.get('format', None))
        if text is None:
            text = ''
        return text

    def __consider(self, node, consider):
        if node is None:
            return None
        if consider is None:
            pass
        elif consider == 'float':
            node = float(node)
        else:
            print('consider type not implement: {}'.format(consider))
            raise ValueError
        return node

    def __format(self, nodes, template):
        if nodes is None or nodes == []:
            return None
        nodes = nodes.copy()
        if template is not None:
            matches = [ m for m in re.finditer('\{[^}]*\}', template) ]
            list = range(len(matches))
            for i in range(len(matches))[::-1]:
                m = matches[i]
                if nodes[i] is None:
                    template = template[:m.start()] + template[m.end():]
                    del nodes[i]
            text = template.format(*nodes)
        else:
            for i in range(len(nodes))[::-1]:
                if nodes[i] is None:
                    del nodes[i]
            text = ' '.join(nodes)
        return text