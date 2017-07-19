import math
import time

outClassique ='{} -->> revenu: {}\t\tnetCharge: {}\t\ttresoBrut: {}\t\ttresoNet: {}\t\timpot: {}\t\tchargeDedc: {}\n'

class Classique():

    fluxY = {
             'Revenu Y': list(),
             'TresoBrut Y': list(),
             'TresoNet Y': list(),
             'Impot Y': list(),
             }

    fluxM = {
             'Loyer M': list(),
             'Mensualites M': list(),
             'Interet M': list(),
             'Capital M': list(),
             }

    sheet = dict()

    def __init__(self, cout, taux, annees, loyer, charges, fonciere, ass=1266,
                occupation=12, travaux = 0, notaire = 0, apport=0):
        self._occupation = occupation
        self._fonciere = fonciere
        self._charges = charges
        self._cout = cout - apport
        self._loyer = loyer
        self._taux = taux / 100.0 / 12.000
        self._annees = annees
        self._ass = ass
        self._travaux = travaux
        self._notaire = notaire
        self.process()

    @property
    def notaire(self):
        if not self._notaire:
            return (self.cout - self.travaux) *.085
        return self._notaire

    @property
    def occupation(self):
        return self._occupation

    @property
    def travaux(self):
        return self._travaux

    @property
    def fonciere(self):
        return self._fonciere

    @property
    def charges(self):
        return self._charges

    @property
    def loyer(self):
        return self._loyer

    @property
    def annees(self):
        return self._annees

    @property
    def cout(self):
        return self._cout

    @property
    def taux(self):
        return self._taux

    @property
    def echeances(self):
        return float(self._echeances)

    @property
    def ass(self):
        return self._ass

    @property
    def mens(self):
        return self._mens

    @property
    def pond(self):
        return float(self.mens * 100 / 70.0)

    @property
    def coutGlobal(self):
        return self.mens * self.echeances

    @property
    def sumInteret(self):
        return self.coutGlobal - self.cout

    def process(self):
        ''' param: cout as money ask, taux as percentage, annees '''

        mois = self.annees * 12
        mensualite = self.cout * (self.taux / (1 - math.pow((1+self.taux),-mois)))

        self._echeances = mois
        self._mens = mensualite
        self.ratio = self.mens / self.loyer * 100
        self.rentabilite = (self.loyer * 12.0) / self.cout * 100.0

    def __str__(self):

        out = '''         # -- netCharge = loyer - (charges + taxe fonciere)
         # -- tresoBrut = netCharge - traite
         # -- tresoNet = tresoBrut - impot\n'''

        for year, values in self.sheet.items():
            out += outClassique.format(year, *values)
        return out
