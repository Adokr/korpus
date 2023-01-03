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
def getSpojniki(parent_map, root):
    wynik = []
    for x in parent_map.keys():
        for category in x.iter('category'):
            if category.text == "spójnik":
                for y in getParent(x, parent_map).iter('children'):
                    if y.get('chosen') == 'true':
                        for z in y.iter('child'):
                            if z.get('head') == 'true' and z.get('nid') == x.get('nid'):
                                #print(z.attrib)
                                if len(x.find("children").findall("child")) == 1 and findNode(x.find("children").find("child").get("nid"), root).find("terminal").find("f").text == "conj":
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
        if x.get("nid") != node.get("nid") and x.find("nonterminal").find("category").text != "znakkonca" and x.find("nonterminal").find("category").text != "pauza":
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
def findTerminalAttributes(node, root, wynik, parent_map):
    a = node
    #wynik = []
    if a.find("terminal") is None:
        for x in a.iter("children"):
            if x.get("chosen") == "true":
                for y in x.iter("child"):
                    z = findTerminalAttributes(findNode(y.get("nid"), root), root, wynik, parent_map)

                    if len(z) > 0:
                        while type(z) == list:
                            z = z[0]
                        wynik.append(z)
    else:
        if getParent(a, parent_map).find("nonterminal").find("category").text != "przec":
            wynik.append(node)
    #print("wynik:")
    #for x in wynik:
     #   print(x.attrib)
    secior = set(wynik)
    wynik = list(secior)
   # for i in root.iter("node"):
    #    if int(i.get("from")) + 2 == int(root.find("startnode").get("to")):
     #       if i.find("terminal") is not None:
      #          for j in root.iter("node"):
       #             if j.find("terminal") is None:
        #                if j.find("nonterminal").find("category").text == "znakkonca" and j.get("chosen") == "true":
         #                   wynik[wynik.index(findNode(i.get("nid"), root).find("terminal").find("orth").text)].append(findNode(j.find("children").find("child").get("nid"), root).find("terminal").find("orth").text)
    return wynik
def findNode(nid, root):
    for x in root.iter("node"):
        if x.get("nid") == str(nid):
            return x

def getNadrzednik(node, root, parent_map, children_map):
    nadrzednik = findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(node, root, parent_map), parent_map), root)
    return nadrzednik
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
def getWordCount(node, root, parent_map): #podajemy node na tym samym poziomie co node z "category" == "spojnik"
    return len(findTerminalAttributes(node, root, [], parent_map))
def getSylablesCount(node):
    return
def getCharCount(node, root, parent_map):
    return len(getCzlon(node, root, parent_map))
def getCzlon(node, root, parent_map):
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
    for x in findTerminalAttributes(node, root, [], parent_map):
        wynik.append(x.find("terminal").find("orth").text)
    #        print(f"y: {z.attrib}")
    #wynik = sortuj(wynik, root.find("text").text)
    a = " ".join(wynik)
    #print(a)
    return a
def czyTylkoPojedynczeGlowy(root):
    ileTakich = 0
    zbiory = []
    for i in root.iter("node"):
        if i.get("chosen") == "true":
            for j in i.iter("children"):
                if j.get("chosen") == "true":
                    count = 0
                    tab = []
                    for k in j.iter("child"):
                        if k.get("head") == "true":
                            count += 1
                            tab.append(k.get("nid"))
                    if count > 1:
                        ileTakich += 1
                        zbiory.append(tab)
    return ileTakich == 0, zbiory

def podwojneGlowyWCzlonieKoordynacji(nodeCzlonu, nodePodwojnejGlowy, root, parent_map):
    for i in nodePodwojnejGlowy:
        if findNode(i, root) in findTerminalAttributes(nodeCzlonu, root, [], parent_map):
            return True
    return False

def sortuj(doPosortowania, wgTegoSortuj, root, czyKoniecZdania):
    lepszeWgTegoSortuj = []
    lepszeDoPosortowania = []
    for i in wgTegoSortuj.split():
        if list(i.split()[-1])[-1] in [".", "?", "!", ",", ";", '"']:
            k = copy.deepcopy(i[-1])
            i = i[0:-1]
            lepszeWgTegoSortuj.append(i)
            lepszeWgTegoSortuj.append(k)
        else:
            lepszeWgTegoSortuj.append(i)
    for i in doPosortowania.split():
        if list(i.split()[-1]) in [".", "?", "!", ",", ";", '"']:
            i = i[0:-1]
        lepszeDoPosortowania.append(i)
    #print(lepszeWgTegoSortuj)
    """doPosortowania = doPosortowania.split()
    print(doPosortowania)
    if czyKoniecZdania:
        for i in root.iter("node"):
            if int(i.get("from")) + 2 == int(root.find("startnode").get("to")):
                if i.find("terminal") is not None:
                    for j in root.iter("node"):
                        if j.find("terminal") is None:
                            if j.find("nonterminal").find("category").text == "znakkonca" and j.get("chosen") == "true":
                                ktore = doPosortowania.index(findNode(i.get("nid"), root).find("terminal").find("orth").text)
                                print(ktore)
                                doPosortowania[ktore] = doPosortowania[ktore] + (findNode(j.find("children").find("child").get("nid"), root).find("terminal").find("orth").text)
                                print(doPosortowania[ktore])"""
    #wgTegoSortuj = wgTegoSortuj[0:-1] # usuwanie znaku interpunkcyjnego
    klucz = {c: i for i, c in enumerate(lepszeWgTegoSortuj)}
    wyniki = sorted(lepszeDoPosortowania, key=klucz.get)
    return wyniki
def getCzlonyKoordynacji(dlCzlon1, dlCzlon2, root, indeksSpojnika):
    caleZdanie = root.find("text").text
    lepszeCaleZdanie = []
    for i in caleZdanie.split():
        if list(i.split()[-1])[-1] in [".", "?", "!", ",", ";", '"']:
            k = copy.deepcopy(i[-1])
            i = i[0:-1]
            lepszeCaleZdanie.append(i)
            lepszeCaleZdanie.append(k)
        elif list(i.split()[-1])[0] in ['"']:
            k = copy.deepcopy(i[0])
            i = i[1:]
            lepszeCaleZdanie.append(k)
            lepszeCaleZdanie.append(i)
        else:
            lepszeCaleZdanie.append(i)

    """k = 0
    for i in range(len(czlon1)):
        for j in range(len(czlon2)):
            if lepszeCaleZdanie.index(czlon2[j]) < lepszeCaleZdanie.index(czlon1[i]):
                k += 1
    if k == dlCzlon1 * dlCzlon2:
        dlCzlon1, dlCzlon2 = dlCzlon2, dlCzlon1"""

    #print(f"s: {spójnik}")
    #gdzieSpojnik = lepszeCaleZdanie.index(spójnik)
    #print(gdzieSpojnik)
    gdzieSpojnik = int(indeksSpojnika)
    #print(gdzieSpojnik)
    czlon1 = lepszeCaleZdanie[gdzieSpojnik-dlCzlon1:gdzieSpojnik]
    czlon2 = lepszeCaleZdanie[gdzieSpojnik+1:gdzieSpojnik+dlCzlon2+1]
    print(f"funckja czlon1: {czlon1}\nczlon2: {czlon2}")
    ileZnakowInter1 = 0
    ileZnakowInter2 = 0
    lepszyCzlon1 = copy.deepcopy(czlon1)
    lepszyCzlon2 = copy.deepcopy(czlon2)
    for i in range(len(czlon1)):
        if czlon1[i] in [",", ".", ";", '"']:
            ileZnakowInter1 += 1
            lepszyCzlon1[i-1] = lepszyCzlon1[i-1] + lepszyCzlon1[i]
            lepszyCzlon1.pop(i)
    for i in range(ileZnakowInter1):
        lepszyCzlon1.append(lepszeCaleZdanie[gdzieSpojnik+i])
    for i in range(len(czlon2)):
        if czlon2[i] in [",", ".", ";", '"']:
            ileZnakowInter2 += 1
            lepszyCzlon2[i - 1] = lepszyCzlon2[i - 1] + lepszyCzlon2[i]
            lepszyCzlon2.pop(i)
    for i in range(ileZnakowInter2):
        lepszyCzlon2.append(lepszeCaleZdanie[gdzieSpojnik+dlCzlon2+i+1])
    print(f"funckja czlon1: {lepszyCzlon1}\nczlon2: {lepszyCzlon2}")
    return lepszyCzlon1, lepszyCzlon2
def setInfo(tab, root, spójnik, parent_map, children_map):
        if getSpojnikValue(spójnik, children_map) == "," or getTagSpojnika(spójnik, children_map) != "conj":
            return tab
        #print(spójnik.attrib)
        rodzenstwo = getSiblings(spójnik, parent_map, children_map)
        if int(rodzenstwo[0].get("from")) > int(rodzenstwo[1].get("from")):
            rodzenstwo[0], rodzenstwo[1] = rodzenstwo[1], rodzenstwo[0]
        dlugoscCzlon1 = getWordCount(rodzenstwo[0], root, parent_map)
        dlugoscCzlon2 = getWordCount(rodzenstwo[1], root, parent_map)
        #print(rodzenstwo[0].attrib)
        #print(rodzenstwo[1].attrib)
        #czyKoniecZdania = False
        #print("rodz0: " + getCzlon(getNodeWhereGreyEnds(rodzenstwo[0], root, parent_map), root), root.find("text").text)
        #print("rodz1:" + getCzlon(getNodeWhereGreyEnds(rodzenstwo[1], root, parent_map), root), root.find("text").text)
        #czlon1 = sortuj(getCzlon(getNodeWhereGreyEnds(rodzenstwo[0], root, parent_map), root, parent_map), root.find("text").text, root, False)
        #czlon2 = sortuj(getCzlon(getNodeWhereGreyEnds(rodzenstwo[1], root, parent_map), root, parent_map), root.find("text").text, root, czyKoniecZdania)
        #print(f"czlon1sortuj: {czlon1}\nczlon2sortuj: {czlon2}")
     #   print(podwojneGlowyWCzlonieKoordynacji(rodzenstwo[0], czyTylkoPojedynczeGlowy(root)[1][0], root, parent_map))
        whereSpójnik = int(spójnik.get("from"))
        if not czyTylkoPojedynczeGlowy(root)[0]:
            for i in range(len(czyTylkoPojedynczeGlowy(root)[1])):
                if int(findNode(czyTylkoPojedynczeGlowy(root)[1][i][0], root).get("from")) < int(spójnik.get("from")):
                    whereSpójnik -= 1
                    if podwojneGlowyWCzlonieKoordynacji(rodzenstwo[0], czyTylkoPojedynczeGlowy(root)[1][i], root, parent_map):
                        dlugoscCzlon1 -= 1
                else:
                    if podwojneGlowyWCzlonieKoordynacji(rodzenstwo[1], czyTylkoPojedynczeGlowy(root)[1][i], root, parent_map):
                        dlugoscCzlon2 -= 1
        czlon1, czlon2 = getCzlonyKoordynacji(dlugoscCzlon1, dlugoscCzlon2, root, whereSpójnik)
        czlon1 = " ".join(czlon1)
        czlon2 = " ".join(czlon2)
        #print(f"czlon1: {czlon1}\nczlon2: {czlon2}")
        if findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(spójnik, root, parent_map), parent_map), root) != getChildren(spójnik, children_map)[0]:
            tab[0] = getPozycjaNadrzednika(getNadrzednik(spójnik, root, parent_map, children_map).find('terminal').find('orth').text, getSpojnikValue(spójnik, children_map), root)
            tab[1] = getNadrzednik(spójnik, root, parent_map, children_map).find('terminal').find('orth').text
            tab[2] = getTagSpojnika(getParent(getNadrzednik(spójnik, root, parent_map, children_map), parent_map), children_map)
            tab[3] = getKategoriaNadrzednika(getNadrzednik(spójnik, root, parent_map, children_map), parent_map)
            tab[4] = getKategoriaNadrzednika(getParent(getNadrzednik(spójnik, root, parent_map, children_map), parent_map), parent_map)
        else:
            tab[0] = 0
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
            for i in range(len(tab)):
                writer.writerow({"Pozycja Nadrzędnika": tab[i][0],
                                 "Nadrzędnik": tab[i][1],
                                 "Tag Nadrzędnika": tab[i][2],
                                 "Kategoria Nadrzędnika": tab[i][3],
                                 "Kategoria Rodzica Nadrzędnika": tab[i][4],
                                 "Spójnik": tab[i][5],
                                 "Tag Spójnika": tab[i][6],
                                 "Kategoria Koordynacji": tab[i][7],
                                 "Kategoria Rodzica Koordynacji": tab[i][8],
                                 "Słowa Pierwszego Członu": tab[i][9],
                                 "Sylaby Pierwszego Członu": tab[i][10],
                                 "Znaki Pierwszego Członu": tab[i][11],
                                 "Pierwszy Człon": tab[i][12],
                                 "Kategoria Pierwszego Członu": tab[i][13],
                                 "Słowa Drugiego Członu": tab[i][14],
                                 "Sylaby Drugiego Członu": tab[i][15],
                                 "Znaki Drugiego Członu": tab[i][16],
                                 "Drugi Człon": tab[i][17],
                                 "Kategoria Drugiego Członu": tab[i][18],
                                 "Całe Zdanie": tab[i][19],
                                 "Sent_id": tab[i][20]
                                 })
            writer.writerow({})
            writer.writerow({})

#writeToFile(wyniki)
def main():
    i = 0
    with open("./data.csv", "w", newline=''):
        print("")
    #path = ["../Składnica-frazowa-200319/NKJP_1M_2004000000312/morph_18-p/morph_18.28-s.xml"]
            #"../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_2-p/morph_2.27-s.xml"]
    # ../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_4-p/morph_4.20-s.xml"]
    # ../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_2-p/morph_2.27-s.xml"]
            #../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_4-p/morph_4.20-s.xml"]
            #../Składnica-frazowa-200319/NKJP_1M_2002000082/morph_3-p/morph_3.62-s.xml"]
    #NKJP_1M_1305000001001/morph_1-p/morph_1.41-s
    #NKJP_1M_1202000010/morph_98-p/morph_98.47-s
    # ../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_2-p/morph_2.27-s.xml"]
        #"../Składnica-frazowa-200319/NKJP_1M_2002000131/morph_2-p/morph_2.20-s.xml",
        #"../Składnica-frazowa-200319/NKJP_1M_1303900001/morph_314-p/morph_314.49-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_1103000012/morph_1-p/morph_1.26-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_1202000009/morph_196-p/morph_196.14-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_2002000176/morph_5-p/morph_5.62-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_2004000005/morph_8-p/morph_8.81-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_1305000000631/morph_1-p/morph_1.52-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_1202910000003/morph_10-p/morph_10.20-s.xml",
#"../Składnica-frazowa-200319/NKJP_1M_SzejnertCzarny/morph_5-p/morph_5.50-s.xml"]
   # for i in path:
    #    openFile(i)

    with open("./data.csv", "w", newline=''):
        print("")
    path = '../Składnica-frazowa-200319'
    for folder in os.listdir(path):
        czyKolejnyFolder = True
        pathwithfolder = os.path.join(path, folder)
        for anotherfolder in os.listdir(pathwithfolder):
            pathwithanotherfolder = os.path.join(pathwithfolder, anotherfolder)
            for filename in os.listdir(pathwithanotherfolder):
                if filename != ".xml" and filename != "morph_53.61-s.xml" and i<300:
                    #print(os.path.join(pathwithanotherfolder, filename))
                    fullname = os.path.join(pathwithanotherfolder, filename)
                    openFile(fullname)
                    czyKolejnyFolder = False
                    i += 1 #to jest main chyba taki ostateczny, że przeszukuje wszytskie foldery i w ogóle
def openFile(path):
    with open(path, "r"):
        writeToFile(analizeFile(path))
def czyDrzewoFull(root):
    return root.find("answer-data").find("base-answer").get("type") == "FULL"
def analizeFile(path):
    parent_map = {}  # słownik, który które każdemu węzłu przyporządkowuje rodzica; kluczami są wszystkie <node>, których atrybut 'chosen' = true; opr
    children_map = {}
    #print(path)
    wyniki = []
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

        spojniki = getSpojniki(parent_map, root)
        #spojnikiValues = []
        #for i in spojniki:
        #    spojnikiValues.append(getSpojnikValue(i, children_map))
        #if len(set(spojnikiValues)) != len(spojnikiValues):
        #   for i in spojnikiValues:
        #       if spojnikiValues.count(i) > 1:
        #            indexes = [index for index, element in enumerate(root.find("text").text.split()) if element == i]
        if spojniki != []:
            for x in spojniki:
                #setInfo(informacje, root, x)
                if len(getSiblings(x, parent_map, children_map)) == 2:
                    #print(getSiblings(x, parent_map, children_map))
                    informacje = [None] * 21
                    wyniki.append(copy.deepcopy(setInfo(informacje, root, x, parent_map, children_map)))
    return wyniki

main()

### ../Składnica-frazowa-200319/NKJP_1M_0402000008/morph_6-p/morph_6.9-s.xml co tu co koordynuje 121 wiersz w .csv
#../Składnica-frazowa-200319/NKJP_1M_1202000010/morph_53-p/morph_53.61-s.xml    brak nadrzędnika?
# NKJP_1M_1202000010/morph_53-p/morph_53.61-s.xml <- przerwa w szarym??? złe drzewo chyba
#NKJP_1M_1102000000027/morph_2-p/morph_2.63-s.xml <- czy dobry nadrzędnik
# NKJP_1M_0402000008/morph_4-p/morph_4.78-s.xml <- czy dobry nadrzędnik? czy może nie powinno go nie ma

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