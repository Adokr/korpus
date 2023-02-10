import copy
import csv
import xml.etree.ElementTree as ET
import os
import pyphen
import num2words

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
                                if len(x.find("children").findall("child")) == 1 and findNode(x.find("children").find("child").get("nid"), root).find("terminal").find("f").text != "comp":
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
    czyPauza=0
    przec= None
    for x in rozne_wyniki:
        if x.get("nid") != node.get("nid") and x.find("nonterminal").find("category").text not in ("znakkonca", "pauza", "przec", "spójnik"):
            xd.append(x)
        if x.find("nonterminal").find("category").text == "pauza":
                czyPauza=1
        if x.find("nonterminal").find("category").text == "przec":
                przec = x
    return xd, czyPauza, przec

def getSpojnikValue(node, children_map):
    return getChildren(node, children_map)[0].find('terminal').find('orth').text
def getTagSpojnika(node, children_map):
    #for i in getChildren(node, children_map):
     #   print(f"aha: {i.get('nid')}") czemu tutaj jest node wśrod dzieciuchów...
    if node.find("terminal") is None:
        if getChildren(node, children_map)[0].find("terminal") is None:
            return getTagSpojnika(getChildren(node, children_map)[0], children_map)
                #getChildren(getChildren(node, children_map)[0], children_map)[0].find("terminal").find('f').text
        else:
            return getChildren(node, children_map)[0].find('terminal').find('f').text
    else:
        return node.find("terminal").find("f").text
def getKategoriaKoordynacji(node, parent_map, children_map):
    kategorie = []
    for x in getSiblings(node, parent_map, children_map)[0]:
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
        #if getParent(a, parent_map).find("nonterminal").find("category").text != "przec":
        wynik.append(node)
    secior = set(wynik)
    wynik = list(secior)
    return wynik
def findNode(nid, root):
    for x in root.iter("node"):
        if x.get("nid") == str(nid):
            return x

def getNadrzednik(node, root, parent_map, children_map):
    nadrzednik = findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(node, root, parent_map), parent_map), root)
    return nadrzednik
def getPozycjaNadrzednika(nodeNadrzednik, nodeSpojnik):
    pozycja = 0
    if int(nodeNadrzednik.get("from")) < int(nodeSpojnik.get("from")):
        pozycja = "L"
    elif int(nodeNadrzednik.get("from")) > int(nodeSpojnik.get("from")):
        pozycja = "R"
    #print(f"pozycja: {pozycja}")
    return pozycja
def sprawdzIleTokenowNadrzednik(node, parent_map):
    ociec = getParent(node, parent_map)
    count = 0
    for x in ociec.iter("children"):
        if x.get("chosen") == "true":
            for y in x.iter("child"):
               if y.get("head") == "true":
                   count += 1
    return count
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
    for x in findTerminalAttributes(node, root, [], parent_map):
        wynik.append(x.find("terminal").find("orth").text)
    a = " ".join(wynik)
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
    for i in zbiory:
        if len(i) == 3:
            print(i)
    return ileTakich == 0, zbiory

def podwojneGlowyWCzlonieKoordynacji(nodeCzlonu, nodePodwojnejGlowy, root, parent_map):
    for i in nodePodwojnejGlowy:
        if findNode(i, root) in findTerminalAttributes(nodeCzlonu, root, [], parent_map):
            return True
    return False
def posortuj(tab):
    kolejnosc = []
    lepszakolejnosc = []
    wynik = [None] * len(tab)
    for i in tab:
        kolejnosc.append(int(i.get("from")))
    for i in kolejnosc:
        lepszakolejnosc.append(i - (max(kolejnosc) - 1))
    for i in range(len(tab)):
        wynik[lepszakolejnosc[i]] = tab[i].find("terminal").find("orth").text
    return wynik
def getLepszeCzlonyKoordynacji(root, spójnik, parent_map, children_map):
    rodzenstwoSpojnika = getSiblings(spójnik, parent_map, children_map)[0]
    pierwsze = rodzenstwoSpojnika[0]
    ostatnie = rodzenstwoSpojnika[0]
    for x in rodzenstwoSpojnika:
        if int(x.get("from")) < int(pierwsze.get("from")):
            pierwsze = x
        if int(x.get("from")) > int(ostatnie.get("from")):
            ostatnie = x
    rodzenstwoSpojnika[0], rodzenstwoSpojnika[1] = pierwsze, ostatnie

    czlon1 = rodzenstwoSpojnika[0]
    czlon2 = rodzenstwoSpojnika[1]
    if int(rodzenstwoSpojnika[0].get("from")) > int(rodzenstwoSpojnika[1].get("from")):
        czlon1 = rodzenstwoSpojnika[1]
        czlon2 = rodzenstwoSpojnika[0]

    indeksyCzlon1 = list(range(int(czlon1.get("from")), int(czlon1.get("to"))))
    indeksyCzlon2 = list(range(int(czlon2.get("from")), int(czlon2.get("to"))))
    glowi = []
    glowi2 = []
    p, podwojneGlowy = czyTylkoPojedynczeGlowy(root)
    if not p:
        for i in podwojneGlowy:
            for j in i:
                glowi.append(j)
        for i in podwojneGlowy:
            glowi2.append(i[0])
    #print(glowi)
    slowaCzlon1 = []
    slowaCzlon2 = []
    tmp = []
    kolejnosc = []
    for i in indeksyCzlon1:
        for j in root.findall("node"):
            if int(j.get("from")) == i and int(j.get("to")) == i+1 and j.get("chosen") == "true":
                if j.find("terminal") is not None:
                    if j.get("nid") not in glowi:
                        slowaCzlon1.append(j.find("terminal").find("orth").text)
                    elif j.get("nid") in glowi2:
                        for k in findTerminalAttributes(getParent(j, parent_map), root, [], parent_map):
                            #tmp.append(k.find("terminal").find("orth").text)
                            kolejnosc.append(k)
                        #tmp = posortuj(kolejnosc)
                        #slowo = "".join(posortuj(kolejnosc))
                        slowaCzlon1.append("".join(posortuj(kolejnosc)))
                        #tmp = []
                        kolejnosc = []
    for i in indeksyCzlon2:
        for j in root.findall("node"):
            if int(j.get("from")) == i and int(j.get("to")) == i + 1 and j.get("chosen") == "true":
                if j.find("terminal") is not None:
                    if j.get("nid") not in glowi:
                        slowaCzlon2.append(j.find("terminal").find("orth").text)
                    elif j.get("nid") in glowi2:
                        for k in findTerminalAttributes(getParent(j, parent_map), root, [], parent_map):
                            #tmp.append(k.find("terminal").find("orth").text)
                            kolejnosc.append(k)
                        #tmp = posortuj(kolejnosc)
                        #slowo = "".join(posortuj(kolejnosc))
                        slowaCzlon2.append("".join(posortuj(kolejnosc)))
                        #tmp = []
                        kolejnosc = []

    a1 = " ".join(slowaCzlon1)
    a2 = " ".join(slowaCzlon2)
    #print(a1)
    a1 = ogarnijInterpunkcje(a1)
    a2 = ogarnijInterpunkcje(a2)
    return a1, a2
def ogarnijInterpunkcje(czlon):
    wynik = []
    czyCudzyslowOtwarty = False
    for i in czlon.split():
        if i == "," and wynik != []:
            tmp = wynik[-1]
            del wynik[-1]
            tmp += ","
            wynik.append(tmp)
        else:
            wynik.append(i)
    if '"' in wynik:
        tmpCzlon = []
        przeskok = False
        for i in range(len(wynik)):
            if not przeskok:
                if wynik[i] == '"' and not czyCudzyslowOtwarty:
                    tmp = wynik[i]
                    tmp += wynik[i+1]
                    tmpCzlon.append(tmp)
                    przeskok = True
                    czyCudzyslowOtwarty = True
                elif wynik[i] == '"':
                    tmp = tmpCzlon[-1]
                    del tmpCzlon[-1]
                    tmp += '"'
                    tmpCzlon.append(tmp)
                    czyCudzyslowOtwarty = False
                else:
                    tmpCzlon.append(wynik[i])
            else:
                przeskok = False
        #print(f"lol: {tmpCzlon}")
        wynik = tmpCzlon
    return " ".join(wynik)

def czyPrzerwaWSzarym(node, root, parent_map, children_map):
    wynik = True
    if getNadrzednik(node, root, parent_map, children_map).find("terminal") is None:
        for i in getNadrzednik(node, root, parent_map, children_map).iter("children"):
            if i.get("chosen") == "true":
                for j in i.iter("child"):
                    if j.get("head") == "true":
                        wynik = False
    else:
        wynik = False
    return wynik
def getPrzodek(nodeKoordynacji, root, parent_map): #pierwszy wspólny węzeł nadrzędnika i koordynacji
    return getParent(getNodeWhereGreyEnds(nodeKoordynacji, root, parent_map), parent_map).find("nonterminal").find("category").text
def num_words(tks):
    tks2 = [tokens for tokens in tks]
    for i in range(len(tks2)):
        if tks2[i].isnumeric():
            tks2[i] = num2words.num2words(tks2[i], lang="pl")
    return tks2

def syllables(text):
    dic = pyphen.Pyphen(lang="pl_PL")
    n= 1
    tildes = dic.inserted(text, "~")
    for i in tildes:
        if  i =="~":
            n +=1
    return n, tildes

def getInfoPodwyjnychGlow(node, root, parent_map):
    tab = []
    podwojnaGlowa = []
    tagiPodwojneGlowy = []
    if sprawdzIleTokenowNadrzednik(node, parent_map) > 1:
        ociec = getParent(node, parent_map)
        for x in ociec.iter("children"):
            if x.get("chosen") == "true":
                for y in x.iter("child"):
                    if y.get("head") == "true":
                        tab.append(findNode(y.get("nid"), root))
        for x in tab:
            tagiPodwojneGlowy.append(findSzareTerminalAttribute(x, root).find("terminal").find("f").text)
            podwojnaGlowa.append(findSzareTerminalAttribute(x, root).find("terminal").find("orth").text)
    return podwojnaGlowa, tagiPodwojneGlowy

def setInfo(tab, root, spójnik, parent_map, children_map, czyNonBinary):

        if not czyNonBinary:
            tab[28] = 2
            rodzenstwo = getSiblings(spójnik, parent_map, children_map)[0]
            if int(rodzenstwo[0].get("from")) > int(rodzenstwo[1].get("from")):
                rodzenstwo[0], rodzenstwo[1] = rodzenstwo[1], rodzenstwo[0]
        else:
            rodzenstwo = getSiblings(spójnik, parent_map, children_map)[0]
            tab[28] = len(rodzenstwo)
            pierwsze = rodzenstwo[0]
            ostatnie = rodzenstwo[0]
            for x in rodzenstwo:
                if int(x.get("from")) < int(pierwsze.get("from")):
                    pierwsze = x
                if int(x.get("from")) > int(ostatnie.get("from")):
                    ostatnie = x
            rodzenstwo[0], rodzenstwo[1] = pierwsze, ostatnie
        czlon1, czlon2 = getLepszeCzlonyKoordynacji(root, spójnik, parent_map, children_map)
        wordsTab1 = num_words(czlon1.split())
        wordsTab2 = num_words(czlon2.split())
        syl1 = 0
        syl2 = 0
        for i in wordsTab1:
            syl1 += syllables(i)[0]
        for i in wordsTab2:
            syl2 += syllables(i)[0]

        przec = getSiblings(spójnik, parent_map, children_map)[2]

        if przec is not None:
            if int(przec.get("from")) < int(spójnik.get("from")):
                if int(przec.get("from")) > int(rodzenstwo[0].get("from")):
                    czlon1 += findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                else:
                    tmpczlon1 = findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                    tmpczlon1 += czlon1
                    czlon1 = tmpczlon1
                tab[10] = 1
                tab[19] = 0
            else:
                if int(przec.get("from")) > int(rodzenstwo[1].get("from")):
                    czlon2 += findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                else:
                    tmpczlon2 = findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                    tmpczlon2 += czlon2
                    czlon2 = tmpczlon2
                tab[19] = 1
                tab[10] = 0
        else:
            tab[10] = 0
            tab[19] = 0
        if findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(spójnik, root, parent_map), parent_map), root) != getChildren(spójnik, children_map)[0] and not czyPrzerwaWSzarym(spójnik, root, parent_map, children_map):
            if sprawdzIleTokenowNadrzednik(getNadrzednik(spójnik, root, parent_map, children_map), parent_map) > 1:
                t1, t2 = getInfoPodwyjnychGlow(getNadrzednik(spójnik, root, parent_map, children_map), root, parent_map)
                tab[1] = "|".join(t1)
                tab[2] = "|".join(t2)
                tab[31] = "tak"

            else:
                tab[1] = getNadrzednik(spójnik, root, parent_map, children_map).find('terminal').find('orth').text
                tab[2] = getTagSpojnika(getNadrzednik(spójnik, root, parent_map, children_map), parent_map)
            tab[0] = getPozycjaNadrzednika(getNadrzednik(spójnik, root, parent_map, children_map), spójnik)
            #print(tab[1])
            tab[3] = getKategoriaNadrzednika(getNadrzednik(spójnik, root, parent_map, children_map), parent_map)
            tab[4] = getKategoriaNadrzednika(getParent(getNadrzednik(spójnik, root, parent_map, children_map), parent_map), parent_map)
            tab[9] = getPrzodek(spójnik, root, parent_map)
        else:
            tab[0] = 0
        if sprawdzIleTokenowNadrzednik(findSzareTerminalAttribute(rodzenstwo[0], root), parent_map) > 1:
            t1, t2 = getInfoPodwyjnychGlow(findSzareTerminalAttribute(rodzenstwo[0], root), root, parent_map)
            tab[16] = "|".join(t1)
            tab[17] = "|".join(t2)
        else:
            tab[16] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("orth").text
            tab[17] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("f").text

        if sprawdzIleTokenowNadrzednik(findSzareTerminalAttribute(rodzenstwo[1], root), parent_map) > 1:
            t1, t2 = getInfoPodwyjnychGlow(findSzareTerminalAttribute(rodzenstwo[1], root), root, parent_map)
            tab[25] = "|".join(t1)
            tab[26] = "|".join(t2)
        else:
            tab[25] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("orth").text
            tab[26] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("f").text
        tab[5] = getSpojnikValue(spójnik, children_map)
        tab[6] = getTagSpojnika(spójnik, children_map)
        tab[7] = getKategoriaKoordynacji(spójnik, parent_map, children_map)
        tab[8] = getKategoriaRodzicaKoordynacji(spójnik, parent_map)
        tab[10] += len(findTerminalAttributes(rodzenstwo[0], root, [], parent_map))
        tab[11] = len(czlon1.split())
        tab[12] = syl1
        tab[13] = len(czlon1)
        tab[14] = czlon1
        tab[15] = getNodeWhereGreyEnds(rodzenstwo[0], root, parent_map).find("nonterminal").find("category").text
        #tab[16] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("orth").text
        #tab[17] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("f").text
        tab[18] = getParent(findSzareTerminalAttribute(rodzenstwo[0], root), parent_map).find("nonterminal").find("category").text
        tab[19] += len(findTerminalAttributes(rodzenstwo[1], root, [], parent_map))
        tab[20] = len(czlon2.split())
        tab[21] = syl2
        tab[22] = len(czlon2)
        tab[23] = czlon2
        tab[24] = getNodeWhereGreyEnds(rodzenstwo[1], root, parent_map).find("nonterminal").find("category").text
        #tab[25] = findSzareTerminalAttribute(rodzenstwo[1], root).find("terminal").find("orth").text
        #tab[26] = findSzareTerminalAttribute(rodzenstwo[1], root).find("terminal").find("f").text
        tab[27] = getParent(findSzareTerminalAttribute(rodzenstwo[1], root), parent_map).find("nonterminal").find("category").text
        tab[29] = root.find("text").text
        tab[30] = root.get("sent_id")
        return tab

def writeToFile(tab):
    puste = True
    if tab == []:
        puste = True #PLIKI BEZ SPÓJNIKów
        return 0
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
                      "Przodek","Tokeny Pierwszego Członu", "Słowa Pierwszego Członu", "Sylaby Pierwszego Członu",
                      "Znaki Pierwszego Członu", "Pierwszy Człon", "Kategoria Pierwszego Członu",
                      "Głowa Pierwszego Członu", "Tag Głowy Pierwszego Członu",
                      "Kategoria Głowy Pierwszego Członu","Tokeny Drugiego Członu", "Słowa Drugiego Członu",
                      "Sylaby Drugiego Członu", "Znaki Drugiego Członu", "Drugi Człon",
                      "Kategoria Drugiego Członu", "Głowa Drugiego Członu",
                      "Tag Głowy Drugiego Członu", "Kategoria Głowy Drugiego Członu", "Liczba członów koordynacji",
                      "Całe Zdanie", "Sent_id", "czypodwójnynadrzędnik"]
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
                                 "Przodek": tab[i][9],
                                 "Tokeny Pierwszego Członu": tab[i][10],
                                 "Słowa Pierwszego Członu": tab[i][11],
                                 "Sylaby Pierwszego Członu": tab[i][12],
                                 "Znaki Pierwszego Członu": tab[i][13],
                                 "Pierwszy Człon": tab[i][14],
                                 "Kategoria Pierwszego Członu": tab[i][15],
                                 "Głowa Pierwszego Członu": tab[i][16],
                                 "Tag Głowy Pierwszego Członu": tab[i][17],
                                 "Kategoria Głowy Pierwszego Członu": tab[i][18],
                                 "Tokeny Drugiego Członu": tab[i][19],
                                 "Słowa Drugiego Członu": tab[i][20],
                                 "Sylaby Drugiego Członu": tab[i][21],
                                 "Znaki Drugiego Członu": tab[i][22],
                                 "Drugi Człon": tab[i][23],
                                 "Kategoria Drugiego Członu": tab[i][24],
                                 "Głowa Drugiego Członu": tab[i][25],
                                 "Tag Głowy Drugiego Członu": tab[i][26],
                                 "Kategoria Głowy Drugiego Członu": tab[i][27],
                                 "Liczba członów koordynacji": tab[i][28],
                                 "Całe Zdanie": tab[i][29],
                                 "Sent_id": tab[i][30],
                                 "czypodwójnynadrzędnik": tab[i][31]
                                 })
            return len(tab)
#writeToFile(wyniki)
def main():
    i = 0
    ileAnaliz = 0
    ileNiebinarnych = 0
    ilePauz = 0
    ilePełnych = 0
    with open("./data.csv", "w", newline=''):
        print("")
    #openFile("../Składnica-frazowa-200319/NKJP_1M_1202000010/morph_70-p/morph_70.24-s.xml")
    #openFile("../Składnica-frazowa-200319/NKJP_1M_3104000000106/morph_1-p/morph_1.34-s.xml")
    with open("./data.csv", "w", newline=''):
        print("")
    path = '../Składnica-frazowa-200319'
    for folder in os.listdir(path):
        pathwithfolder = os.path.join(path, folder)
        for anotherfolder in os.listdir(pathwithfolder):
            pathwithanotherfolder = os.path.join(pathwithfolder, anotherfolder)
            for filename in os.listdir(pathwithanotherfolder):
                if filename != ".xml" and filename != "morph_5.37-s.xml":
                    #print(os.path.join(pathwithanotherfolder, filename))
                    fullname = os.path.join(pathwithanotherfolder, filename)
                    pauz, analiza, niebinarne, fulltrees = openFile(fullname)
                    ilePauz += pauz
                    ileAnaliz += analiza
                    ileNiebinarnych += niebinarne
                    ilePełnych += fulltrees
                    i += 1 #to jest main chyba taki ostateczny, że przeszukuje wszytskie foldery i w ogóle
    print(f"liczbaPauz: {ilePauz}")
    print(f"ile zdań z koordycjami przeaanalizowanymi: {ileAnaliz}")
    print(f"ile koordynacji niebinarnych (nieprzeanalizowane): {ileNiebinarnych}")
    print(f"ile fullTrees:  {ilePełnych}")
    print(f"ile zdań ogółem: {i}")
def openFile(path):
    ileAnaliz=0
    with open(path, "r"):
        x, y, z, a = analizeFile(path)
        ileAnaliz = writeToFile(x)
        return y, ileAnaliz, z, a
def czyDrzewoFull(root):
    #print(root.find("answer-data").find("base-answer").get("type"))
    return root.find("answer-data").find("base-answer").get("type") == "FULL"
def analizeFile(path):
    parent_map = {}  # słownik, który które każdemu węzłu przyporządkowuje rodzica; kluczami są wszystkie <node>, których atrybut 'chosen' = true; opr
    children_map = {}
    #print(path)
    wyniki = []
    tree = ET.parse(path)
    root = tree.getroot()
    ilePauz=0
    ileNiebinarnych=0
    ilePełnych =0
    if czyDrzewoFull(root):
        ilePełnych +=1
        print(root.get("sent_id"))
        node_root = root.find('node')
        assert node_root.get('nid') == '0'
        parent_map = getActuallTree(root, parent_map)  # nid = 0 to zawsze korzeń
        parent_map[node_root] = node_root

        for k, v in parent_map.items():
            children_map[v] = children_map.get(v, []) + [k]

        spojniki = getSpojniki(parent_map, root)
        if spojniki != []:
            for x in spojniki:
                #setInfo(informacje, root, x)
                ilePauz += getSiblings(x, parent_map, children_map)[1]
                if len(getSiblings(x, parent_map, children_map)[0]) == 2:
                    #print(getSiblings(x, parent_map, children_map))
                    informacje = [None] * 32
                    wyniki.append(copy.deepcopy(setInfo(informacje, root, x, parent_map, children_map, False)))
                elif len(getSiblings(x, parent_map, children_map)[0]) > 2:
                    ileNiebinarnych+=1
                    informacje = [None] * 32
                    wyniki.append(copy.deepcopy(setInfo(informacje, root, x, parent_map, children_map, True)))


    return wyniki, ilePauz, ileNiebinarnych, ilePełnych

main()

#nadrzędnik ze złej strony NAPRAWIĆ [zrobione]
#spójnik nie comp, ale może być interp np [chyba zrobione]
#psuje się jak są dwa interpunkcyjne znaki obok sb
#kim są rodzice koordynacji albo nadrzędników??? dodatkowa kolumna "przodek" [działa]
#2428 róznych
#zliczanie tokenów[zrobione]

#powtórzyć to co w artykule, ale dla języka polskiego

#na 25.01
#NKJP_1M_2004000041/morph_6-p/morph_6.12-s.xml <- czy taką koordynacj chcemy uwzględniać (w getSiblings filtracja)? pauza + zdanie
#

#NKJP_1M_2004000059/morph_3-p/morph_3.78-s.xml <- tokeny pierwsego członu źle, bo nie uwzględna ','
#liczbaPauz: 93
#przeanalizowanych koordynacji: 3718
#przeanalizowanych zdań z koordynacjami: 3089
#ile Full Trees: ~11930
#ile zdań ogółem: ~19989

#żeby 'przec' uwzględniał w członach [CHYBA GIT]
#sylaby dodać od Kamila [DONE]
#podwójne nadrzędniki [DONE]
#dodać niebinarne koordynacje (pierwszy i ostatni człon)[CHYBA GIT]
#usunąć wiersze puste[DONE]

#do końca lutego
#statystyki w R na podstawie artykułu który mam na mejlu

#WĄTPLIWOŚCI:
#NKJP_1M_1302910000004/morph_47-p/morph_47.71-s <- tag 'nie' w nadrzędniku jest inne niż w drzewie na stronie (qub v part)
#ogólnie tag 'part' jest jako 'qub' w tyych plikach

#dodane podwójne głowy członów i ich tagi