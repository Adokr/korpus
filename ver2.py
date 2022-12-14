import copy
import csv
import xml.etree.ElementTree as ET

tree = ET.parse('../Składnica-frazowa-200319/NKJP_1M_4scal-NIE/morph_38-p/morph_38.63-s.xml')
#NKJP_1M_4scal-NIE/morph_38-p/morph_38.63-s.xml
#NKJP_1M_1102000011/morph_1-p/morph_1.6-s.xml
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
                for y in getParent(x).iter('children'):
                    if y.get('chosen') == 'true':
                        for z in y.iter('child'):
                            if z.get('head') == 'true' and z.get('nid') == x.get('nid'):
                                print(z.attrib)
                                wynik.append(x)
    return wynik

def getParent(node):
    return parent_map.get(node)

def getChildren(node):
    return children_map.get(node)
def getSiblings(node):
    return getChildren(getParent(node))



def getSpojnikValue(node):
    return getChildren(node)[0].find('terminal').find('orth').text
def getTagSpojnika(node):
    return getChildren(node)[0].find('terminal').find('f').text
def getKategoriaKoordynacji(node):
    kategorie = []
    for x in getSiblings(node):
        for y in x.iter('category'):
            kategorie.append(y.text)
    rozne_kategorie = set(kategorie)
    rozne_kategorie.discard('spójnik')
    assert len(rozne_kategorie) == 1
    return next(iter(rozne_kategorie))
def getKategoriaRodzicaKoordynacji(node):
    return getParent(getParent(node)).find('nonterminal').find('category').text

def getNadrzednik(node):
    #x = None
    #y = None
    a = node
    b = None
    # zrób funkcję żeby się dało łatwo znajdować get children get child i takie tam
    # tutaj trzeba while'a wrzucić żeby cofał się póki się skończy "szare"
    for x in getParent(a).iter('children'):
        if x.get('chosen') == 'true':
            for y in x.iter('child'):
                if y.get('nid') == a.get('nid'):
                    if y.get('head') == 'true':
                        a = getParent(a)
    print(getParent(a).attrib)
    for x in a.iter('children'):
        if x.get('chosen') == 'true':
            for y in x.iter('child'):
                if y.get('head') == 'true':
                    for wow in root.iter('node'):
                        if wow.get('nid') == y.get('nid'):
                            b = wow
    while b.find('terminal') == None:
        for x in b.iter('children'):
            if x.get('chosen') == 'true':
                for y in x.iter('child'):
                    if y.get('head') == 'true':
                        for wow in root.iter('node'):
                            if wow.get('nid') == y.get('nid'):
                                b = wow
    return b



    """dziadek = getParent(getParent(node))
    if len(getSiblings(dziadek)) == 1:
        x = getSiblings(dziadek)[0].find('nonterminal').find('category').text
    else:
        for child in getChildren(getParent(dziadek)):
            if child != dziadek:
                while getChildren(child) is not None:
                    child = getChildren(child)[0]
                y = child
        x = y
        return x
        """
def getPozycjaNadrzednika(node):
  #  tab = getCaleZdanie().split()
 #   for x in tab:
#        if x
    return
def getTagNadrzednka(node):
    return

def getKategoriaNadrzednika(node):
    return getParent(node).find('nonterminal').find('category').text
def getWordCount(node):
    return
def getSylablesCount(node):
    return
def getCharCount(node):
    return
def getCaleZdanie():
    return root.find('text').text

def setInfo(x):
        informacje[1] = getNadrzednik(x).find('terminal').find('orth').text
        informacje[2] = getTagSpojnika(getParent(getNadrzednik(x)))
        informacje[3] = getKategoriaNadrzednika(getNadrzednik(x))
        informacje[4] = getKategoriaNadrzednika(getParent(getNadrzednik(x)))
        informacje[5] = getSpojnikValue(x)
        informacje[6] = getTagSpojnika(x)
        informacje[7] = getKategoriaKoordynacji(x)
        informacje[8] = getKategoriaRodzicaKoordynacji(x)

spojniki = getSpojniki()
for x in spojniki:
    setInfo(x)
    print(getSpojnikValue(x))
    wyniki.append(copy.deepcopy(informacje))


print(wyniki)
