from logging import getLogger, DEBUG
import re
from xml.etree import ElementTree

from lib.resources import g_resources
from lib.translate import g_translate as translate
from lib.utils import readXmlData

logger = getLogger(__name__)
logger.setLevel(DEBUG)

class FindEntry(object):

    def __init__(self):
        self.__itemschema = g_resources.itemschema
        self.__xmltree = {}
        self.__functions = {
            'sum':  self.__functionSum,
            'mul':  self.__functionMul,
            'div':  self.__functionDiv,
            'or':   self.__functionOr,
            'join': self.__functionJoin
        }

    def find(self, node, param):
        index = None
        match = re.match(r'(.*)\[(\d+)\]', node)
        if match:
            node = match.group(1)
            index = int(match.group(2))
        try:
            schema = self.__itemschema[node]
        except:
            logger.error('FindEntry.find(): bad key: "{}"'.format(node))
            raise
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
        if index is not None:
            if not isinstance(result, list) and not isinstance(result, ElementTree.Element):
                logger.error('find: spceify index, but node is not list: {}'.format(node))
                logger.error('type: {}'.format(result))
                raise ValueError
            result = result[index] if len(result) > index else None
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
                logger.error('__findNode: not implement func: {}'.format(resource['custom']))
                raise ValueError
        else:
            logger.error('__findNode: missing method: {}'.format(resource))
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
                if isinstance(value, ElementTree.Element):
                    value = value.tag
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
                logger.error('unknown value keyword: {}'.format(schema['value']))
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
        elif map == 'split':
            data = data.split()
        elif isinstance(map, dict):
            data = [ map[v] for v in data.split() if v in map ]
            data = data.pop(0) if data else None
        else:
            match = re.match('\[(\d)\]', str(map))
            if match:
                index = int(match.group(1))
                if isinstance(data, list):
                    if index >= len(data):
                        data = None
                    else:
                        data = data[index]
                else:
                    data = data.split()[index]
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
        for child in root.findall('setting'):
            if child.findtext('name') == 'nations_order':
                return [ i.text for i in child.findall('value/item') ]
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

    def __functionMul(self, args, param):
        result = 1.0
        for arg in args:
            value = self.find(arg, param)
            if value is None:
                return None
            value = float(value)
            result *= value
        return result

    def __functionDiv(self, args, param):
        result = self.find(args[0], param)
        result = float(result)
        for arg in args[1:]:
            value = self.find(arg, param)
            if value is None:
                return None
            value = float(value)
            result /= value
        return result
    
    def __functionOr(self, args, param):
        result = None
        for arg in args:
            result = self.find(arg, param)
            if result:
                break
        return result

    def __functionJoin(self, args, param):
        result = []
        for arg in args:
            value = self.find(arg, param)
            if isinstance(value, list):
                result.extend(value)
            else:
                result.append(value)
        return result


class FindFormattedEntry(FindEntry):

    def getText(self, schema, param):
        node = schema['value']
        if isinstance(node, list):
            value = [ self.find(n, param) for n in node ]
        else:
            value = self.find(node, param)
        if not isinstance(value, list):
            value = [ value ]
        value = [ self.__consider(v, schema.get('consider', None)) for v in value ]
        value = [ self.__factor(v, schema.get('factor', None)) for v in value ]
        if schema.get('format', None):
            text = self.__format(value, schema.get('format', None))
        else:
            text = self.__join(value, schema.get('join', None))       
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
            logger.error('consider type not implement: {}'.format(consider))
            raise ValueError
        return node

    def __factor(self, nodes, factor):
        if factor is None or nodes is None or nodes == []:
            return nodes
        if isinstance(nodes, list):
            result = [ node * factor for node in nodes ]
        else:
            result = nodes * factor
        return result

    def __format(self, nodes, template):
        if nodes is None or nodes == []:
            return None
        nodes = nodes.copy()
        matches = [ m for m in re.finditer('\{[^}]*\}', template) ]
        list = range(len(matches))
        for i in range(len(matches))[::-1]:
            m = matches[i]
            if nodes[i] is None:
                template = template[:m.start()] + template[m.end():]
                del nodes[i]
        text = template.format(*nodes)
        return text

    def __join(self, nodes, sep):
        if nodes is None or nodes == []:
            return None
        nodes = nodes.copy()
        if sep is None:
            sep = ' '
        for i in range(len(nodes))[::-1]:
            if nodes[i] is None:
                del nodes[i]
        text = sep.join(nodes)
        return text
