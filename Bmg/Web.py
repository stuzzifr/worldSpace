# -*- coding: utf-8 -*-
import urllib, re, os
import pdb
import subprocess

db = pdb.set_trace


class Bien(object):

    isValid = True

    def __init__(self, id=None):
        self.id = id
        pass

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
        return 'http:' + self._thumb

    @property
    def thumbLoc(self):
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
        return float(self.price) / int(self.surface)


def getLinks(site='bonCoin'):

    links = list()
    for i in range(1, 2):
        address = 'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/seine_saint_denis/?o={}&ps=1&pe=4&ret=2'.format(i)
        print address

        sock = urllib.urlopen(address)
        html = sock.read()
        sock.close()

        rawLinks = re.findall(r'href="(.+)" title', html)
        ids = re.findall(r'ad_listid" : "(\d+)', html)

        if ids:
            for i in xrange(len(ids)):
                for link in rawLinks:
                    if ids[i] in link:
                        links.append(link)

    return links


def getDatas(links, site='bonCoin'):

    if not links:
        print 'no links found'
        return

    biens = list()

    for link in links:
        url = 'http:%s' % link
        sock = urllib.urlopen(url)
        html = sock.read()
        sock.close()

        biens.append(Bien())
        price = re.search(r'prix : "(\d+)', html)
        ville = re.findall(r'PostalAddress">(.+) \d', html)
        date = re.search(r'Mise en ligne le (\d+ \w+)', html)
        thumb = re.search(r'images_thumbs\[0\] = "(.+)"', html)
        pieces = re.search(r'pieces : "(\d)"', html)
        surface = re.search(r'surface : "(\d+)"', html)
        desc = re.search(r'"description" content="(.+)\>', html)

        thumb = '' if not thumb else thumb.group(1)

        try:
            biens[-1].setInfos(url, price.group(1), surface.group(1),
                               pieces.group(1), date.group(1), desc.group(1),
                               thumb, ville[0])

        except:

            print 'fail ', link

    return biens
