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
    stary = getParent(node, parent_map)
    wynik = getChildren(stary, children_map)
    rozne_wyniki = set(wynik)
    rozne_wyniki.discard(node)#(getParent(node, parent_map)) #tu chyba discard(node)
    if stary in rozne_wyniki:
        rozne_wyniki.discard(stary)
    xd = []
    czyPauza=0
    przec= None
    pozostałeSpójniki = []
    for x in rozne_wyniki:
        if x.get("nid") != node.get("nid") and x.find("nonterminal").find("category").text not in ("znakkonca", "pauza", "przec", "spójnik"):
            xd.append(x)
        if x.find("nonterminal").find("category").text == "pauza":
            czyPauza=1
        if x.find("nonterminal").find("category").text == "przec":
            przec = x
        if x.find("nonterminal").find("category").text == "spójnik":
            pozostałeSpójniki.append(x)
    return xd, czyPauza, przec, pozostałeSpójniki

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
def getSylablesCount(node):
    return
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
    #for i in zbiory:
     #   if len(i) == 3:
      #      print(i)
    return ileTakich == 0, zbiory
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
    #print(wynik)
    if '"' in wynik or '„' in wynik:
        tmpCzlon = []
        przeskok = False
        for i in range(len(wynik)):
            if not przeskok:
                if wynik[i] in ['"', '„'] and not czyCudzyslowOtwarty:
                    tmp = wynik[i]
                    tmp += wynik[i+1]
                    tmpCzlon.append(tmp)
                    przeskok = True
                    czyCudzyslowOtwarty = True
                elif wynik[i] in ['"', '„']:
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
    ociec = getParent(node, parent_map)
    if sprawdzIleTokenowNadrzednik(node, parent_map) > 1:
        for x in ociec.iter("children"):
            if x.get("chosen") == "true":
                for y in x.iter("child"):
                    if y.get("head") == "true":
                        tab.append(findNode(y.get("nid"), root))
        for x in tab:
            tagiPodwojneGlowy.append(findSzareTerminalAttribute(x, root).find("terminal").find("f").text)
            podwojnaGlowa.append(findSzareTerminalAttribute(x, root).find("terminal").find("orth").text)
    else:
        podwojnaGlowa.append(findSzareTerminalAttribute(node, root).find("terminal").find("orth").text)
    return podwojnaGlowa, tagiPodwojneGlowy

def setInfo(tab, root, spójnik, parent_map, children_map, czyNonBinary):
        spojnik_wartosc = getSpojnikValue(spójnik, children_map)
        rodzenstwo, nic, przec, pozostaleSpójniki = getSiblings(spójnik, parent_map, children_map)
        if not czyNonBinary:
            tab[10] = 2
            if int(rodzenstwo[0].get("from")) > int(rodzenstwo[1].get("from")):
                rodzenstwo[0], rodzenstwo[1] = rodzenstwo[1], rodzenstwo[0]
        else:
            tab[10] = len(rodzenstwo)
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

        if przec is not None:
            if int(przec.get("from")) < int(spójnik.get("from")):
                if int(przec.get("from")) > int(rodzenstwo[0].get("from")):
                    czlon1 += findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                else:
                    tmpczlon1 = findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                    tmpczlon1 += czlon1
                    czlon1 = tmpczlon1
                tab[17] = 1
                tab[26] = 0
            elif (int(przec.get("from"))+1 != int(pozostaleSpójniki[0].get("from"))):
                if int(przec.get("from")) > int(rodzenstwo[1].get("from")):
                    czlon2 += findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                else:
                    tmpczlon2 = findSzareTerminalAttribute(przec, root).find("terminal").find("orth").text
                    tmpczlon2 += czlon2
                    czlon2 = tmpczlon2
                tab[26] = 1
                tab[17] = 0
            else:
                tab[17] = 0
                tab[26] = 0

            if pozostaleSpójniki != []:
                print(root.get("sent_id"))
                if int(przec.get('from')) == int(pozostaleSpójniki[0].get("from")) - 1:
                    tab[5] = spojnik_wartosc + '...' + getSpojnikValue(przec, children_map) + ' '
                    tab[5] += " ".join(getInfoPodwyjnychGlow(getChildren(pozostaleSpójniki[0], children_map)[0], root, parent_map)[0])
            else:
                tab[5] = spojnik_wartosc
        else:
            tab[17] = 0
            tab[26] = 0
            tab[5] = spojnik_wartosc

        if findSzareTerminalAttribute(getParent(getNodeWhereGreyEnds(spójnik, root, parent_map), parent_map), root) != getChildren(spójnik, children_map)[0] and not czyPrzerwaWSzarym(spójnik, root, parent_map, children_map):
            if sprawdzIleTokenowNadrzednik(getNadrzednik(spójnik, root, parent_map, children_map), parent_map) > 1:
                t1, t2 = getInfoPodwyjnychGlow(getNadrzednik(spójnik, root, parent_map, children_map), root, parent_map)
                tab[1] = "~".join(t1)
                tab[2] = "~".join(t2)
                tab[31] = "tak"

            else:
                tab[1] = getNadrzednik(spójnik, root, parent_map, children_map).find('terminal').find('orth').text
                tab[2] = getTagSpojnika(getNadrzednik(spójnik, root, parent_map, children_map), parent_map)
            tab[0] = getPozycjaNadrzednika(getNadrzednik(spójnik, root, parent_map, children_map), spójnik)
            tab[3] = getKategoriaNadrzednika(getNadrzednik(spójnik, root, parent_map, children_map), parent_map)
            tab[4] = getKategoriaNadrzednika(getParent(getNadrzednik(spójnik, root, parent_map, children_map), parent_map), parent_map)
            tab[9] = getPrzodek(spójnik, root, parent_map)
        else:
            tab[0] = 0
        if sprawdzIleTokenowNadrzednik(findSzareTerminalAttribute(rodzenstwo[0], root), parent_map) > 1:
            t1, t2 = getInfoPodwyjnychGlow(findSzareTerminalAttribute(rodzenstwo[0], root), root, parent_map)
            tab[13] = "~".join(t1)
            tab[14] = "~".join(t2)
        else:
            tab[13] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("orth").text
            tab[14] = findSzareTerminalAttribute(rodzenstwo[0], root).find("terminal").find("f").text

        if sprawdzIleTokenowNadrzednik(findSzareTerminalAttribute(rodzenstwo[1], root), parent_map) > 1:
            t1, t2 = getInfoPodwyjnychGlow(findSzareTerminalAttribute(rodzenstwo[1], root), root, parent_map)
            tab[22] = "~".join(t1)
            tab[23] = "~".join(t2)
        else:
            tab[22] = findSzareTerminalAttribute(rodzenstwo[1], root).find("terminal").find("orth").text
            tab[23] = findSzareTerminalAttribute(rodzenstwo[1], root).find("terminal").find("f").text
        #tab[5] = getSpojnikValue(spójnik, children_map)
        tab[6] = getTagSpojnika(spójnik, children_map)
        tab[7] = getKategoriaKoordynacji(spójnik, parent_map, children_map)
        tab[8] = getKategoriaRodzicaKoordynacji(spójnik, parent_map)
        tab[17] += len(findTerminalAttributes(rodzenstwo[0], root, [], parent_map))
        tab[16] = len(czlon1.split())
        tab[18] = syl1
        tab[19] = len(czlon1)
        tab[11] = czlon1
        tab[12] = getNodeWhereGreyEnds(rodzenstwo[0], root, parent_map).find("nonterminal").find("category").text
        tab[15] = getParent(findSzareTerminalAttribute(rodzenstwo[0], root), parent_map).find("nonterminal").find("category").text
        tab[26] += len(findTerminalAttributes(rodzenstwo[1], root, [], parent_map))
        tab[25] = len(czlon2.split())
        tab[27] = syl2
        tab[28] = len(czlon2)
        tab[20] = czlon2
        tab[21] = getNodeWhereGreyEnds(rodzenstwo[1], root, parent_map).find("nonterminal").find("category").text
        tab[24] = getParent(findSzareTerminalAttribute(rodzenstwo[1], root), parent_map).find("nonterminal").find("category").text
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
            header = ["governor.position", "governor.word", "governor.tag", "governor.category",
                      "governors.parent.category", "conjunction.word",
                      "conjunction.tag", "coordination.category", "coordinations.parent.category",
                      "antecedent.category", "no.conjuncts", "L.conjunct", "L.category", "L.head.word",
                      "L.head.tag", "L.head.category", "L.words", "L.tokens", "L.syllables",
                      "L.chars", "R.conjunct", "R.category", "R.head.word", "R.head.tag",
                      "R.head.category", "R.words", "R.tokens", "R.syllables", "R.chars",
                      "sentence", "sent_id", "double.governor"]
            writer = csv.DictWriter(f, fieldnames=header)
            if puste:
                writer.writeheader()
            for i in range(len(tab)):
                writer.writerow({"governor.position": tab[i][0],
                                 "governor.word": tab[i][1],
                                 "governor.tag": tab[i][2],
                                 "governor.category": tab[i][3],
                                 "governors.parent.category": tab[i][4],
                                 "conjunction.word": tab[i][5],
                                 "conjunction.tag": tab[i][6],
                                 "coordination.category": tab[i][7],
                                 "coordinations.parent.category": tab[i][8],
                                 "antecedent.category": tab[i][9],
                                 "L.tokens": tab[i][17], #17
                                 "L.words": tab[i][16], #16
                                 "L.syllables": tab[i][18], #18
                                 "L.chars": tab[i][19], #19
                                 "L.conjunct": tab[i][11], #11
                                 "L.category": tab[i][12], #12
                                 "L.head.word": tab[i][13], #13
                                 "L.head.tag": tab[i][14], #14
                                 "L.head.category": tab[i][15], #15
                                 "R.tokens": tab[i][26], #26
                                 "R.words": tab[i][25], #25
                                 "R.syllables": tab[i][27], #27
                                 "R.chars": tab[i][28], #28
                                 "R.conjunct": tab[i][20], #20
                                 "R.category": tab[i][21], #21
                                 "R.head.word": tab[i][22], #22
                                 "R.head.tag": tab[i][23], #23
                                 "R.head.category": tab[i][24], #24
                                 "no.conjuncts": tab[i][10], #10
                                 "sentence": tab[i][29], #29
                                 "sent_id": tab[i][30], #30
                                 "double.governor": tab[i][31] #31
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

    with open("./data.csv", "w", newline=''):
        print("")
    path = '../Składnica-frazowa-200319'
    for folder in os.listdir(path):
        pathwithfolder = os.path.join(path, folder)
        for anotherfolder in os.listdir(pathwithfolder):
            pathwithanotherfolder = os.path.join(pathwithfolder, anotherfolder)
            for filename in os.listdir(pathwithanotherfolder):
                #if filename != ".xml" and filename != "morph_5.37-s.xml":
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
    #if root.find("answer-data").find("base-answer").get("type") == "NOT_SENTENCE":
     #   print(root.get("sent_id"))
      #  print(root.find("answer-data").find("base-answer").get("type"))
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
                liczbarodzeństwa = len(getSiblings(x, parent_map, children_map)[0])
                if liczbarodzeństwa == 2:
                    informacje = [None] * 32
                    wyniki.append(copy.deepcopy(setInfo(informacje, root, x, parent_map, children_map, False)))
                elif liczbarodzeństwa > 2:
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

#FULL TREE


#SPOTKANIE 13.02
#format drzew nie pozwala wyciągnac informacji na temat koordynacji gdy spójnikiem jest 'zaś'; spójniki inkorporacyjne
#jaki test do chi kwadrat
#kubełki w wykresach
#własne statystyki spróbować zrobić
#spis treści pracy licencjackiej zrobić
#spotkanie 6.03 o 16:00 <- jeśli nie to napisać
