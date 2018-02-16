import json

class Resources(object):
    guisettings_items = 'res/guisettings_items.json'

    def load(self):
        with open('res/itemschema.json', 'r') as fp:
            self.itemschema = json.load(fp)
        with open(self.guisettings_items, 'r') as fp:
            self.itemgroup = json.load(fp)
        with open('res/guisettings_titles.json', 'r') as fp:
            self.titlesdesc = json.load(fp)
        with open('res/guisettings_selectors.json', 'r') as fp:
            self.selectorsdesc = json.load(fp)

g_resources = Resources()

TIERS = [ str(tier) for tier in range(1, 10 + 1) ]
TIERS_LABEL = { '1':'I', '2':'II', '3':'III', '4':'IV', '5':'V', '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X'}
TIERS_LIST = [ TIERS_LABEL[t] for t in TIERS ]

WG_TYPES = [ 'lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG' ]
TYPES_MAP = { 'lightTank':'LT', 'mediumTank':'MT', 'heavyTank':'HT', 'AT-SPG':'TD', 'SPG':'SPG' }
TYPES = [ TYPES_MAP[t] for t in WG_TYPES ]

