import csv
import xml.etree.ElementTree as ET

tree = ET.parse('../Składnica-frazowa-200319/NKJP_1M_4scal-NIE/morph_38-p/morph_38.63-s.xml')
root = tree.getroot()
node_root  = root.find('node')
assert node_root.get('nid') == '0'
parent_map = {} #słownik, który które każdemu węzłu przyporządkowuje rodzica; kluczami są wszystkie <node>, których atrybut 'chosen' = true; opr
children_map = {}
informacje = [None] * 21
wyniki = []

def getActuallTree(node):
    for x in node.iter('node'):
        if x.get('chosen') == 'true':
            for p in x.iter('children'):
                if p.get('chosen') == 'true':
                    for c in p.iter('child'):
                        for y in root.iter('node'):
                            if y.attrib['nid'] == c.get('nid'):
                                parent_map[y] = x

parent_map[node_root] = node_root
getActuallTree(root) #nid = 0 to zawsze korzeń
for k, v in parent_map.items():
    children_map[v] = children_map.get(v, []) + [k]

def getSpojniki():
    wynik = []
    for x in parent_map.keys():
        for category in x.iter('category'):
            if category.text == "spójnik":
                wynik.append(x)
    return wynik

def getParent(node):
    return parent_map.get(node)

def getChildren(node):
    return children_map.get(node)
def getSiblings(node):
    return getChildren(getParent(node))

spojniki = getSpojniki()
print(spojniki[0].get('nid'), spojniki[1].get('nid'))

def getSpojnikValue(node):
    return getChildren(spojniki[0])[0].find('terminal').find('orth').text
def getTagSpojnika(node):
    return getChildren(spojniki[0])[0].find('terminal').find('f').text
def getKategoriaKoordynacji(node):
    kategorie = []
    for x in getSiblings(node):
        for y in x.iter('category'):
            kategorie.append(y.text)
    rozne_kategorie = set(kategorie)
    rozne_kategorie.discard('spójnik')
    assert len(rozne_kategorie) == 1
    return next(iter(rozne_kategorie))

print(spojniki[0].get('nid'))
print(getKategoriaKoordynacji(spojniki[0]))

