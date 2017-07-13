import sys
from pdb import set_trace as db


class Renta(object):

    def __init__(self, prix, surface, travaux=0, loyer=None, fonciere=900):

        self.prix = prix
        self.surface = surface
        self.travaux = travaux
        self.loyer = loyer
        self.fonciere = fonciere

        self.getRenta()
        self.getDigit()

    def getDigit(self):

        prixBrut = self.getRevenu() / 0.1
        prixNet = (prixBrut * 92) / 100

        print 'prixNet for 2 digits ',  prixNet

        return prixNet

    def getRenta(self):

        cost = self.getCost()
        revenu = self.getRevenu()

        renta = (revenu / cost) * 100

        prixM = self.prix/self.surface
        print 'renta {:>20.2f}%\nprix/m2 {:>20}'.format(renta, prixM)

    def getRevenu(self):
        '''revenu annuel apres taxe '''

        revenu = self.loyer * 12.0
        revenu -= self.fonciere

        return revenu

    def getCost(self):
        ''' print 'cout total avec notaire '''

        notaire = self.prix * .08
        cost = self.prix + self.travaux + notaire

        return cost
