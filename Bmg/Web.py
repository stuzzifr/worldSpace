# -*- coding: utf-8 -*-
import urllib, re, os
import pdb

db = pdb.set_trace


class Bien(object):

    isValid = True

    def __init__(self):
        self._rentAvg = 0

    def setInfos(self, url, price, surface, pieces, date, desc, thumb, ville):
        if 'viager' in desc.lower():
            self.isValid = False

        self._url = url
        self._price = price
        self._surface = surface
        self._pieces = pieces
        self._date = date
        self._desc = desc
        self._thumb = thumb
        self._ville = ville

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
        if 'fevrier' in date: month = 2
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
        if reg: day = 31 / float(reg.group(1))

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

    print 'getting links...'
    links = list()
    for i in range(1, 99):
        # -- http://www.leboncoin.fr/annonces/offres/aquitaine/dordogne/
        address = 'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/seine_saint_denis/?o={}&ps=1&pe=4&ret=2'.format(i)
        try:
            sock = urllib.urlopen(address)
        except IOError:
            print '%s does not exists' % address
            break

        html = sock.read()
        sock.close()

        rawLinks = re.findall(r'href="(.+)" title', html)
        ids = re.findall(r'ad_listid" : "(\d+)', html)

        if ids:
            for i in xrange(len(ids)):
                for link in rawLinks:
                    if ids[i] in link:
                        links.append(link)

        # print 'extracting %s' % address
    return links


def getDatas(links, site='bonCoin'):

    if not links:
        print 'no links found'
        return

    biens = list()

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

        if None in [price, ville, date, pieces, surface]:
            biens.pop()
            print 'skip ', url
            continue

        biens[-1].setInfos(url, price, surface, pieces, date, desc, thumb, ville)

        if not biens[-1].isValid:
            biens.pop()
            continue

        if i % 25 == 0:
            print 'getDatas {:0>2.0f}%'.format((i*100.0/(len(links))))

    return biens


def setRenta(biens, site='bonCoin'):
    # surface = [20, 100] sqs sqe numItems
    # pieces = [1, 4] ros roe
    # type = [2] = appart ret
    # will miss region, ville

    url = str()
    for i, bien in enumerate(biens):
        surfacemin, surfacemax = getSurfaceRange(bien.surface)

        if bien.pieces == 0:
            url = '''http://www.leboncoin.fr/locations/offres/ile_de_france/seine_saint_denis/?th=1&sqs={}&sqe={}&ret=2
            '''.format(surfacemin, surfacemax)

        else:
            url = '''http://www.leboncoin.fr/locations/offres/ile_de_france/seine_saint_denis/?o=1&sqs={}&sqe={}&ros={}&roe={}&ret=2
            '''.format(surfacemin, surfacemax, bien.pieces, bien.pieces)

        try:
            sock = urllib.urlopen(url)
        except IOError:
            print '%s url doesnt exsts' % url
            continue

        html = sock.read()
        sock.close()

        rents = re.findall(r'item_price">([\d ]+)', html)
        rents = [rent.replace(' ', '')for rent in rents]

        avg = 0.0
        for rent in rents:
            avg += int(rent)

        if rents:
            avg /= len(rents)
            bien.setRenta((avg * 12 * 100) / bien.price)
            bien.setRentAvg(avg)

        else:
            bien.setRenta(0)
            print 'cannot find rent average of %s, skipped', url

        if i % 25 == 0:
            print 'setCloud {:0>2.0f}%'.format((i*100.0/(len(biens))))


def getSurfaceRange(surface, site='bonCoin'):

    smin, smax = 1, 2

    if surface > 20 and surface < 25: smin, smax = 2, 3
    if surface > 25 and surface < 29: smin, smax = 3, 4
    if surface > 30 and surface < 34: smin, smax = 4, 5
    if surface > 35 and surface < 39: smin, smax = 5, 6
    if surface > 40 and surface < 49: smin, smax = 6, 7
    if surface > 50 and surface < 59: smin, smax = 7, 8
    if surface > 60 and surface < 69: smin, smax = 8, 9
    if surface > 70 and surface < 79: smin, smax = 9, 10
    if surface > 80 and surface < 89: smin, smax = 10, 11
    if surface > 90 and surface < 99: smin, smax = 11, 12

    return smin, smax

