import copy
import csv
import xml.etree.ElementTree as ET
import os


#NKJP_1M_4scal-NIE/morph_38-p/morph_38.63-s.xml niebinarna koordynacj
#NKJP_1M_1102000011/morph_1-p/morph_1.6-s.xml działa
#NKJP_1M_4scal-KOT/morph_1-p/morph_1.51-s.xml niebinarna koordynacja (nie działa)
#NKJP_1M_1202900065/morph_2-p/morph_2.15-s działa
#NKJP_1M_1202900065/morph_2-p/morph_2.53-s


def getActuallTree(node, dict):
    root = node
    for x in node.iter('node'):
        if x.get('chosen') == 'true':
            for p in x.iter('children'):
                if p.get('chosen') == 'true':
                    for c in p.iter('child'):
                        for y in root.iter('node'):
                            if y.attrib['nid'] == c.get('nid'):
                                dict[y] = x
    return dict
def getSpojniki(parent_map):
    wynik = []
    for x in parent_map.keys():
        for category in x.iter('category'):
            if category.text == "spójnik":
                for y in getParent(x, parent_map).iter('children'):
                    if y.get('chosen') == 'true':
                        for z in y.iter('child'):
                            if z.get('head') == 'true' and z.get('nid') == x.get('nid'):
                                #print(z.attrib)
                                if len(x.find("children").findall("child")) == 1:
                                    wynik.append(x)
    return wynik

def getParent(node, parent_map):
    return parent_map.get(node)

def getChildren(node, children_map):
    return children_map.get(node)
def getSiblings(node, parent_map, children_map):
    wynik = getChildren(getParent(node, parent_map), children_map)
    rozne_wyniki = set(wynik)
    rozne_wyniki.discard(getParent(node, parent_map))
    xd = []
    for x in rozne_wyniki:
        if x.get("nid") != node.get("nid"):
            xd.append(x)
    return xd

def getSpojnikValue(node, children_map):
    return getChildren(node, children_map)[0].find('terminal').find('orth').text
def getTagSpojnika(node, children_map):
    return getChildren(node, children_map)[0].find('terminal').find('f').text
def getKategoriaKoordynacji(node, parent_map, children_map):
    kategorie = []
    for x in getSiblings(node, parent_map, children_map):
        for y in x.iter('category'):
            kategorie.append(y.text)
    rozne_kategorie = set(kategorie)
    rozne_kategorie.discard('spójnik')
    rozne_kategorie.discard("znakkonca")
    #assert len(rozne_kategorie) == 1
    return next(iter(rozne_kategorie))
def getKategoriaRodzicaKoordynacji(node, parent_map):
    return getParent(getParent(node, parent_map), parent_map).find('nonterminal').find('category').text

def getNodeWhereGreyEnds(node, root, parent_map): #idąc od góry drzewa znajduje pierwszy node, w którym zaczyna się szare
    a = getParent(node, parent_map)
    b = node
    while a == getParent(b, parent_map) and a != findNode(0, root):
        for x in a.iter('children'):
            if x.get('chosen') == 'true':
                for y in x.iter('child'):
                    if y.get('nid') == b.get('nid'):
                        a = getParent(a, parent_map)
                        if y.get('head') == 'true':
                            b = getParent(b, parent_map)
    return b
def findSzareTerminalAttribute(node, root): #przeszukuje poddrzewa po szarym, aż znajdzie atrybut 'terminal'
    a = node
    for x in a.iter("children"):
        if x.get("chosen") == "true":
            for y in x.iter("child"):
                if y.get("head") == "true":
                    a = findSzareTerminalAttribute(findNode(y.get("nid"), root), root)
    return a
def findTerminalAttributes(node, root, wynik):
    a = node
    #wynik = []
    if a.find("terminal") is None:
        for x in a.iter("children"):
            if x.get("chosen") == "true":
                for y in x.iter("child"):
                    z = findTerminalAttributes(findNode(y.get("nid"), root), root, wynik)

                    while type(z) == list:
                        z = z[0]
                    wynik.append(z)
    else:
        wynik.append(node)
    #print("wynik:")
    #for x in wynik:
     #   print(x.attrib)
    secior = set(wynik)
    wynik = list(secior)
    return wynik
def findNode(nid, root):
    for x in root.iter("node"):
        if x.get("nid") == str(nid):
            return x

def getNadrzednik(node, root, parent_map):
    return findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(node, root, parent_map), parent_map), root)
def getPozycjaNadrzednika(nodeNadrzednik, nodeSpojnik, root):
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

def getKategoriaNadrzednika(node, parent_map):
    return getParent(node, parent_map).find('nonterminal').find('category').text
def getWordCount(node, root): #podajemy node na tym samym poziomie co node z "category" == "spojnik"
    return len(findTerminalAttributes(node, root, []))
def getSylablesCount(node):
    return
def getCharCount(node, root):
    return len(getCzlon(node, root))
def getCzlon(node, root):
    wynik = []
    """for x in findTerminalAttributes(node, root):
        print(f"x: {x}")
        for y in x[0]:
            #print(y)
     #       print(z)
            while type(y) == list:
                y = y[0]
    #        print(f"y: {z.attrib}")
        wynik.append(y.find("terminal").find("orth").text)"""
    #print(findTerminalAttributes(node, root, []))
    for x in findTerminalAttributes(node, root, []):
        wynik.append(x.find("terminal").find("orth").text)
    #        print(f"y: {z.attrib}")
    #wynik = sortuj(wynik, root.find("text").text)
    a = " ".join(wynik)
    #print(a)
    return a
"""def sortuj(doPosortowania, wgTegoSortuj):
    wgTegoSortuj = wgTegoSortuj[0:-1] # usuwanie znaku interpunkcyjnego
    klucz = {c: i for i, c in enumerate(wgTegoSortuj.split())}
    #print(klucz)
    wyniki = sorted(doPosortowania, key=klucz.get)
    return wyniki"""
def getCzlonyKoordynacji(dlCzlon1, dlCzlon2, root, spójnik):
    caleZdanie = root.find("text").text
    gdzieSpojnik = caleZdanie.split().index(spójnik)
    #print(dlCzlon1, dlCzlon2)
    czlon1 = caleZdanie.split()[caleZdanie.split().index(spójnik)-dlCzlon1:caleZdanie.split().index(spójnik)]
    czlon2 = caleZdanie.split()[caleZdanie.split().index(spójnik)+1: caleZdanie.split().index(spójnik)+dlCzlon2+1]
    #print(f"funckja czlon1: {czlon1}\nczlon2: {czlon2}")
    return czlon1, czlon2
def setInfo(tab, root, spójnik, parent_map, children_map):
        rodzenstwo = getSiblings(spójnik, parent_map, children_map)
        dlugoscCzlon1 = getWordCount(rodzenstwo[0], root)
        dlugoscCzlon2 = getWordCount(rodzenstwo[1], root)
        czlon1, czlon2 = getCzlonyKoordynacji(dlugoscCzlon1, dlugoscCzlon2, root, getSpojnikValue(spójnik, children_map))
        #print(f"czlon1: {czlon1}\nczlon2: {czlon2}")
        if len(czlon1) != dlugoscCzlon1 or len(czlon2) != dlugoscCzlon2:
            czlon1, czlon2 = getCzlonyKoordynacji(dlugoscCzlon2, dlugoscCzlon1, root, getSpojnikValue(spójnik, children_map))
            rodzenstwo[0], rodzenstwo[1] = rodzenstwo[1], rodzenstwo[0]
            #print(czlon1, czlon2)
        czlon1 = " ".join(czlon1)
        czlon2 = " ".join(czlon2)
        print(czlon1, czlon2)
        if list(czlon2.split()[-1])[-1] in [".", "?","!"]:
            #lul = list(czlon2.split()[-1])[0:-1]
            #print("".join(lul))
            czlon2 = czlon2[0:-1]
            #print(czlon2)
            #czlon2 = czlon2.join(lul)
        print(czlon2)

        """czlon1 = ''
        czlon2 = ''
        for i in getCzlon(rodzenstwo[0], root):
            if i != " ":
                czlon1 += i
            else:
                break
        for i in getCzlon(rodzenstwo[1], root):
            if i != " ":
                czlon2 += i
            else:
                break
        czlony = [czlon1, czlon2]
        czlony = sortuj(czlony, root.find("text").text)
        if czlon1 == czlony[1]:
            rodzenstwo[0], rodzenstwo[1] = rodzenstwo[1], rodzenstwo[0]
        print(czlony)"""
        tab[0] = getPozycjaNadrzednika(getNadrzednik(spójnik, root, parent_map).find('terminal').find('orth').text, getSpojnikValue(spójnik, children_map), root)
        tab[1] = getNadrzednik(spójnik, root, parent_map).find('terminal').find('orth').text
        tab[2] = getTagSpojnika(getParent(getNadrzednik(spójnik, root, parent_map), parent_map), children_map)
        tab[3] = getKategoriaNadrzednika(getNadrzednik(spójnik, root, parent_map), parent_map)
        tab[4] = getKategoriaNadrzednika(getParent(getNadrzednik(spójnik, root, parent_map), parent_map), parent_map)
        tab[5] = getSpojnikValue(spójnik, children_map)
        tab[6] = getTagSpojnika(spójnik, children_map)
        tab[7] = getKategoriaKoordynacji(spójnik, parent_map, children_map)
        tab[8] = getKategoriaRodzicaKoordynacji(spójnik, parent_map)
        tab[9] = len(czlon1.split())
        #for i in getSiblings(spójnik, parent_map, children_map):
         #   print(i.attrib)
        tab[10] = None#sylaby
        tab[11] = len(czlon1)
        tab[12] = czlon1
        tab[13] = getNodeWhereGreyEnds(rodzenstwo[0], root, parent_map).find("nonterminal").find("category").text
        tab[14] = len(czlon2.split())
        tab[15] = None#sylaby
        tab[16] = len(czlon2)
        tab[17] = czlon2
        tab[18] = getNodeWhereGreyEnds(rodzenstwo[1], root, parent_map).find("nonterminal").find("category").text
        tab[19] = root.find("text").text
        tab[20] = root.get("sent_id")
        return tab

def writeToFile(tab):
    puste = True
    if tab == []:
        puste = True #PLIKI BEZ SPÓJNIKów
    else:
        with open("./data.csv", "r") as g:
            reader = csv.reader(g)
            for i, _ in enumerate(reader):
                if i:
                    puste = False

        with open("./data.csv", "a") as f:
            header = ["Pozycja Nadrzędnika", "Nadrzędnik", "Tag Nadrzędnika", "Kategoria Nadrzędnika",
                      "Kategoria Rodzica Nadrzędnika", "Spójnik",
                      "Tag Spójnika", "Kategoria Koordynacji", "Kategoria Rodzica Koordynacji",
                      "Słowa Pierwszego Członu",
                      "Sylaby Pierwszego Członu",
                      "Znaki Pierwszego Członu", "Pierwszy Człon", "Kategoria Pierwszego Członu",
                      "Słowa Drugiego Członu",
                      "Sylaby Drugiego Członu",
                      "Znaki Drugiego Członu", "Drugi Człon", "Kategoria Drugiego Członu", "Całe Zdanie", "Sent_id"]
            writer = csv.DictWriter(f, fieldnames=header)
            if puste:
                writer.writeheader()
            writer.writerow({"Pozycja Nadrzędnika": tab[0][0],
                             "Nadrzędnik": tab[0][1],
                             "Tag Nadrzędnika": tab[0][2],
                             "Kategoria Nadrzędnika": tab[0][3],
                             "Kategoria Rodzica Nadrzędnika": tab[0][4],
                             "Spójnik": tab[0][5],
                             "Tag Spójnika": tab[0][6],
                             "Kategoria Koordynacji": tab[0][7],
                             "Kategoria Rodzica Koordynacji": tab[0][8],
                             "Słowa Pierwszego Członu": tab[0][9],
                             "Sylaby Pierwszego Członu": tab[0][10],
                             "Znaki Pierwszego Członu": tab[0][11],
                             "Pierwszy Człon": tab[0][12],
                             "Kategoria Pierwszego Członu": tab[0][13],
                             "Słowa Drugiego Członu": tab[0][14],
                             "Sylaby Drugiego Członu": tab[0][15],
                             "Znaki Drugiego Członu": tab[0][16],
                             "Drugi Człon": tab[0][17],
                             "Kategoria Drugiego Członu": tab[0][18],
                             "Całe Zdanie": tab[0][19],
                             "Sent_id": tab[0][20]
                             })
            writer.writerow({})
            writer.writerow({})

#writeToFile(wyniki)
def main():
    i = 0
    with open("./data.csv", "w", newline=''):
        print("")
    path = ["../Składnica-frazowa-200319/NKJP_1M_2002000131/morph_2-p/morph_2.20-s.xml",
            "../Składnica-frazowa-200319/NKJP_1M_1303900001/morph_314-p/morph_314.49-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_1103000012/morph_1-p/morph_1.26-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_1202000009/morph_196-p/morph_196.14-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_2002000176/morph_5-p/morph_5.62-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_2004000005/morph_8-p/morph_8.81-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_1305000000631/morph_1-p/morph_1.52-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_1202910000003/morph_10-p/morph_10.20-s.xml",
"../Składnica-frazowa-200319/NKJP_1M_SzejnertCzarny/morph_5-p/morph_5.50-s.xml"]
    for i in path:
        openFile(i)
    """i = 0
    with open("./data.csv", "w", newline=''):
        print("")
    path = '../Składnica-frazowa-200319'
    for folder in os.listdir(path):
        czyKolejnyFolder = True
        pathwithfolder = os.path.join(path, folder)
        for anotherfolder in os.listdir(pathwithfolder):
            pathwithanotherfolder = os.path.join(pathwithfolder, anotherfolder)
            for filename in os.listdir(pathwithanotherfolder):
                if filename != ".xml":
                    #print(os.path.join(pathwithanotherfolder, filename))
                    fullname = os.path.join(pathwithanotherfolder, filename)
                    openFile(fullname)
                    czyKolejnyFolder = False
                    i += 1""" #to jest main chyba taki ostateczny, że przeszukuje wszytskie foldery i w ogóle
def openFile(path):
    with open(path, "r"):
        writeToFile(analizeFile(path))
def czyDrzewoFull(root):
    return root.find("answer-data").find("base-answer").get("type") == "FULL"
def analizeFile(path):
    parent_map = {}  # słownik, który które każdemu węzłu przyporządkowuje rodzica; kluczami są wszystkie <node>, których atrybut 'chosen' = true; opr
    children_map = {}
    informacje = [None] * 21
    wyniki = []
    #print(path)
    tree = ET.parse(path)
    root = tree.getroot()
    if czyDrzewoFull(root):
        print(root.get("sent_id"))
        node_root = root.find('node')
        assert node_root.get('nid') == '0'
        parent_map = getActuallTree(root, parent_map)  # nid = 0 to zawsze korzeń
        parent_map[node_root] = node_root

        for k, v in parent_map.items():
            children_map[v] = children_map.get(v, []) + [k]

        spojniki = getSpojniki(parent_map)
        if spojniki != []:
            for x in spojniki:
                #setInfo(informacje, root, x)
                if len(getSiblings(x, parent_map, children_map)) == 2:
                    #print(getSiblings(x, parent_map, children_map))
                    wyniki.append(copy.deepcopy(setInfo(informacje, root, x, parent_map, children_map)))
    return wyniki
#filePath = '../Składnica-frazowa-200319/NKJP_1M_1102000011/morph_1-p/morph_1.6-s.xml'
#tree = ET.parse(filePath)
#root = tree.getroot()
#node_root = root.find('node')
#assert node_root.get('nid') == '0'
#parent_map = {}  # słownik, który które każdemu węzłu przyporządkowuje rodzica; kluczami są wszystkie <node>, których atrybut 'chosen' = true; opr
#children_map = {}
#informacje = [None] * 20
#wyniki = []

#parent_map[node_root] = node_root
#getActuallTree(root)  # nid = 0 to zawsze korzeń
#for k, v in parent_map.items():
   # children_map[v] = children_map.get(v, []) + [k]

#spojniki = getSpojniki()
#for x in spojniki:
 #   setInfo()
  #  print(getSpojnikValue(x))
   # wyniki.append(copy.deepcopy(informacje))


main()

### ../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_6-p/morph_6.9-s.xml co tu co koordynuje 121 wiersz w .csv
#../Składnica-frazowa-200319/NKJP_1M_1202000010/morph_53-p/morph_53.61-s.xml    brak nadrzędnika?


"""
NKJP_1M_2002000131/morph_2-p/morph_2.20-s
NKJP_1M_1303900001/morph_314-p/morph_314.49-s
NKJP_1M_1103000012/morph_1-p/morph_1.26-s
NKJP_1M_1202000009/morph_196-p/morph_196.14-s
NKJP_1M_2002000176/morph_5-p/morph_5.62-s
NKJP_1M_2004000005/morph_8-p/morph_8.81-s
NKJP_1M_1305000000631/morph_1-p/morph_1.52-s
NKJP_1M_1202910000003/morph_10-p/morph_10.20-s
NKJP_1M_SzejnertCzarny/morph_5-p/morph_5.50-s
"""