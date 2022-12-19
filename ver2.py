import copy
import csv
import xml.etree.ElementTree as ET

tree = ET.parse('../Składnica-frazowa-200319/NKJP_1M_1102000011/morph_1-p/morph_1.6-s.xml')
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
    wynik = getChildren(getParent(node))
    xd = []
    for x in wynik:
        if x.get("nid") != node.get("nid"):
            xd.append(x)
    return xd

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

def getNodeWhereGreyEnds(node): #idąc od góry drzewa znajduje pierwszy node, w którym zaczyna się szare
    a = getParent(node)
    b = node
    while a == getParent(b):
        for x in a.iter('children'):
            if x.get('chosen') == 'true':
                for y in x.iter('child'):
                    if y.get('nid') == b.get('nid'):
                        a = getParent(a)
                        if y.get('head') == 'true':
                            b = getParent(b)
    return b
def findSzareTerminalAttribute(node): #przeszukuje poddrzewa po szarym, aż znajdzie atrybut 'terminal'
    a = node
    for x in a.iter("children"):
        if x.get("chosen") == "true":
            for y in x.iter("child"):
                if y.get("head") == "true":
                    a = findSzareTerminalAttribute(findNode(y.get("nid")))
    return a
def findTerminalAttributes(node):
    a = node
    wynik = []
    if a.find("terminal") is None:
        for x in a.iter("children"):
            if x.get("chosen") == "true":
                for y in x.iter("child"):
                    wynik.append(findTerminalAttributes(findNode(y.get("nid"))))
    else:
        wynik.append(node)
        return wynik

    return wynik
def findNode(nid):
    for x in root.iter("node"):
        if x.get("nid") == str(nid):
            return x

def getNadrzednik(node):
    return findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(node)))
def getPozycjaNadrzednika(nodeNadrzednik, nodeSpojnik):
    tab = root.find("text").text.split()
    czyZnalazles = False
    pozycja = "0"
    for slowo in tab:
        if not czyZnalazles:
            if slowo == nodeNadrzednik:
                czyZnalazles = True
                pozycja = "L"
            elif slowo == nodeSpojnik:
                czyZnalazles = True
                pozycja = "R"
    return pozycja

def getTagNadrzednka(node):
    return

def getKategoriaNadrzednika(node):
    return getParent(node).find('nonterminal').find('category').text
def getWordCount(node): #podajemy node na tym samym poziomie co node z "category" == "spojnik"
    return len(findTerminalAttributes(node))

   #wynik = []
   # for x in findTerminalAttributes(node):
    #    while type(x) == list:
     #       x = x[0]
      #  wynik.append(x.find("terminal").find("orth").text)
    #a = " ".join(wynik)

def getSylablesCount(node):
    return
def getCharCount(node):
    return len(getCzlon(node))

def getCzlon(node):
    wynik = []
    for x in findTerminalAttributes(node):
        while type(x) == list:
           x = x[0]
        wynik.append(x.find("terminal").find("orth").text)
    a = " ".join(wynik)
    return a

def setInfo(x):
        informacje[0] = getPozycjaNadrzednika(getNadrzednik(x).find('terminal').find('orth').text, getSpojnikValue(x))
        informacje[1] = getNadrzednik(x).find('terminal').find('orth').text
        informacje[2] = getTagSpojnika(getParent(getNadrzednik(x)))
        informacje[3] = getKategoriaNadrzednika(getNadrzednik(x))
        informacje[4] = getKategoriaNadrzednika(getParent(getNadrzednik(x)))
        informacje[5] = getSpojnikValue(x)
        informacje[6] = getTagSpojnika(x)
        informacje[7] = getKategoriaKoordynacji(x)
        informacje[8] = getKategoriaRodzicaKoordynacji(x)
        informacje[9] = getWordCount(getSiblings(x)[0])
        informacje[10]
        informacje[11] = getCharCount(getSiblings(x)[0])
        informacje[12] = getCzlon(getSiblings(x)[0])
        informacje[13] = 
        informacje[14]
spojniki = getSpojniki()
for x in spojniki:
    setInfo(x)
    print(getSpojnikValue(x))
    wyniki.append(copy.deepcopy(informacje))

for x in getSiblings(spojniki[0]):
    print(x.attrib)
print(wyniki)
