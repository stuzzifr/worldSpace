# -*- coding: utf-8 -*-
import urllib
import re


class Bien(object):

    def __init__(self, id):
        self.id = id

    def setInfos(self, url, price, surface, pieces, date, desc, image):
        'set ratio in here'

    @property
    def url(self):
        return self._url

    @property
    def date(self):
        return self._date

    @property
    def price(self):
        return self._price

    @property
    def image(self):
        return self._image

    @property
    def pieces(self):
        return self._pieces

    @property
    def surface(self):
        return self._surface

    @property
    def desc(self):
        return self._desc

    @property
    def ratio(self):
        return self._ratio


address = 'http://www.leboncoin.fr/ventes_immobilieres/offres/ile_de_france/seine_saint_denis/?th=1&ps=1&pe=4&ret=2'

sock = urllib.urlopen(address)
html = sock.read()
sock.close()

# titles = re.findall(r'imgAlt="(.+);\s', html)
prices = re.findall(r'item_price">(\d+ \d+)', html)
rawLinks = re.findall(r'href="(.+)" title', html)
ids = re.findall(r'ad_listid" : "(\d+)', html)

infos = list()
if prices:
    for i in xrange(ids):
        for link in rawLinks:
            if ids[i] in link:
                this = link

    print '{} Eurs {} {}'.format(prices[i], ids[i], this)
