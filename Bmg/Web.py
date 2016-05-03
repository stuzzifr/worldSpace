# -*- coding: utf-8 -*-
import urllib, re, os
import pdb

db = pdb.set_trace

# DEPARTEMENT = 'aquitaine/dordogne/'
DEPARTEMENT = 'ile_de_france/seine_saint_denis'
VILLE = 'Noisy-le-Sec 93130'


class Bien(object):

    isViager = True
    isValid = True

    def __init__(self):
        self._rentAvg = 0

    def setInfos(self, url, price, surface, pieces, date, desc, thumb, ville):
        if 'viager' in desc.lower():
            self.isViager = False

        if 'viagier' in desc.lower():
            self.isViager = False

        self._url = url
        self._price = price
        self._surface = surface
        self._pieces = pieces
        self._date = date
        self._desc = desc
        self._thumb = thumb
        self._ville = ville

    def setInvalid(self):
        self.isValid = False
        self.setRentAvg(0)
        self.setRenta(1)

    def setRentAvg(self, avg):
        self._rentAvg = avg

    def setRenta(self, renta):
        self._renta = renta

    @property
    def rentAvg(self):
        return self._rentAvg

    @property
    def renta(self):
        return self._renta

    @property
    def url(self):
        return self._url

    @property
    def date(self):
        return self._date

    @property
    def datef(self):
        date = self.date
        month = int()
        day = float()

        if 'janvier' in date: month = 1
        if 'f' in date: month = 2
        if 'mars' in date: month = 3
        if 'avril' in date: month = 4
        if 'mai' in date: month = 5
        if 'juin' in date: month = 6
        if 'juillet' in date: month = 7
        if 'aout' in date: month = 8
        if 'septembre' in date: month = 9
        if 'octobre' in date: month = 10
        if 'novembre' in date: month = 11
        if 'decembre' in date: month = 12

        reg = re.search(r'(\d+)', date)
        if reg: day = float(reg.group(1)) / 31.0

        print date, day+month
        return day + month

    @property
    def price(self):
        return int(self._price)

    @property
    def thumb(self):
        if not self._thumb:
            return

        return 'http:' + self._thumb

    @property
    def thumbLoc(self):
        if not self.thumb:
            return

        path = os.path.join(os.getcwd(), 'thumb')
        if not os.path.exists(path):
            os.mkdir(path)

        destination = os.path.join(path, os.path.basename(self.thumb))

        url = urllib.URLopener()
        url.retrieve(self.thumb, destination)

        return destination

    @property
    def pieces(self):
        return int(self._pieces)

    @property
    def surface(self):
        return int(self._surface)

    @property
    def desc(self):
        return self._desc

    @property
    def ville(self):
        return self._ville

    @property
    def ratio(self):
        if not int(self.surface):
            return 0

        return float(self.price) / int(self.surface)


def getLinks(site='bonCoin'):

    piecemin = 2
    piecemax = 3
    links = list()
    if site == 'bonCoin':
        for i in range(1, 99):
            address = 'http://www.leboncoin.fr/ventes_immobilieres/offres/{}/?o={}&location={}&ps={}&pe={}&ret=2'.format(DEPARTEMENT, i, VILLE, piecemin, piecemax)

            try:
                sock = urllib.urlopen(address)
            except IOError:
                print '%s does not exists' % address
                continue

            html = sock.read()
            sock.close()

            rawLinks = re.findall(r'href="(.+)" title', html)
            ids = re.findall(r'ad_listid" : "(\d+)', html)

            if ids:
                for o in xrange(len(ids)):
                    for link in rawLinks:
                        if ids[o] in link:
                            links.append(link)

            else:
                break

            print 'parsing leBonCoin {}'.format(i)

    if site == 'pap':
        print 'parsing pap {}'.format(i)

    return links


def getDatas(links, site='bonCoin'):

    if not links:
        raise Exception('no links found')
        return

    biens = list()

    # for i, link in enumerate(links[:8]):
    for i, link in enumerate(links):
        url = 'http:%s' % link
        sock = urllib.urlopen(url)
        html = sock.read()
        sock.close()

        biens.append(Bien())
        price = re.search(r'prix : "([\d ]+)', html)
        ville = re.findall(r'PostalAddress">(.+) \d', html)
        date = re.search(r'Mise en ligne le (\d+ \w+)', html)
        thumb = re.search(r'images_thumbs\[0\] = "(.+)"', html)
        pieces = re.search(r'pieces : "(\d)"', html)
        surface = re.search(r'surface : "(\d+)"', html)
        desc = re.search(r'"description" content="(.+)\>', html)

        price = 0 if not price else price.group(1)
        surface = 0 if not surface else surface.group(1)
        pieces = 0 if not pieces else pieces.group(1)
        date = '' if not date else date.group(1)
        desc = 0 if not desc else desc.group(1)
        thumb = '' if not thumb else thumb.group(1)
        ville = 'Unknown' if not ville else ville[0]

        biens[-1].setInfos(url, price, surface, pieces, date, desc, thumb, ville)

        if not biens[-1].isViager:
            biens.pop()
            continue

        if i % 10 == 0:
            percent = i*100.0/(len(links))
            print 'getDatas {:0>2.0f}% |{: <50}|'.format(percent, '.' * int(percent * .5))

    if not biens:
        raise Exception('no biens found, make sure the url are valid')

    print '%d properties found' % len(biens)
    return biens


def setRenta(biens, site='bonCoin'):
    # boncoin
    # surface = [20, 100] sqs sqe numItems
    # pieces = [1, 4] ros roe
    # type = [2] = appart ret
    # will miss region, ville

    # pap
    # http://www.pap.fr/annonce/vente-appartements-saint-denis-93-g43705-a-partir-du-2-pieces-entre-55000-et-99000-euros-entre-21-et-33-m2
    # surface =

    url = str()
    if site == 'pap':
        pass


    if site == 'bonCoin':
        for i, bien in enumerate(biens):

            surfacemin, surfacemax = getSurfaceRange(bien.surface)
            if bien.pieces == 0:
                url = '''http://www.leboncoin.fr/locations/offres/{}/?th=1&location={}&sqs={}&sqe={}&ret=2
                '''.format(DEPARTEMENT, bien.ville, surfacemin, surfacemax)

            else:
                url = '''http://www.leboncoin.fr/locations/offres/{}/?th=1&location={}&sqs={}&sqe={}&ros={}&roe={}&ret=2
                '''.format(DEPARTEMENT, bien.ville, surfacemin, surfacemax, bien.pieces, bien.pieces, bien.ville)

            try:
                sock = urllib.urlopen(url)
            except IOError:
                print '%s url doesnt exsts' % url
                continue

            html = sock.read()
            sock.close()

            rents = re.findall(r'item_price">([\d ]+)', html)

            avg = 0.0
            for rent in rents:
                rent = rent.replace(' ', '')
                avg += int(rent)

            if rents:
                avg /= len(rents)
                bien.setRentAvg(avg)
                bien.setRenta((avg * 12 * 100) / bien.price)

            else:
                bien.setInvalid()
                # print 'cannot find rent average', url

            if i % 10 == 0:
                percent = (i*100.0/(len(biens)))
                print 'average rent {:0>2.0f}% |{: <50}|'.format(percent, '.' * int(percent * .5))

        print '%d pages analysed' % len(biens)


def getSurfaceRange(surface, site='bonCoin'):

    if surface < 20: return 1, 2
    if surface > 20 and surface < 25: return 2, 3
    if surface > 25 and surface < 29: return 3, 4
    if surface > 30 and surface < 34: return 4, 5
    if surface > 35 and surface < 39: return 5, 6
    if surface > 40 and surface < 49: return 6, 7
    if surface > 50 and surface < 59: return 7, 8
    if surface > 60 and surface < 69: return 8, 9
    if surface > 70 and surface < 79: return 9, 10
    if surface > 80 and surface < 89: return 10, 11
    if surface > 90 and surface < 99: return 11, 12

    else: return 1, 2
