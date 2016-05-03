import math
import time

class Classique():

    fluxY = {
             'Revenu Y': list(),
             'TresoBrut Y': list(),
             'TresoNet Y': list(),
             }

    fluxM = {
             'Loyer M': list(),
             'Mensualites M': list(),
             'Interet M': list(),
             'Capital M': list(),
             }

    sheet = dict()

    def __init__(self, cout, taux, annees, loyer, charges, fonciere, ass=1266, occupation=12):
        self._occupation = occupation
        self._fonciere = fonciere
        self._charges = charges
        self._cout = cout
        self._loyer = loyer
        self._taux = taux / 100.0 / 12.000
        self._annees = annees
        self.ass = ass
        self.process()

    @property
    def occupation(self):
        return self._occupation

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
        return self._echeances

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

        # self.cout += self.ass
        mois = self.annees * 12
        mensualite = self.cout * (self.taux / (1 - math.pow((1+self.taux),-mois)))

        self._echeances = mois
        self._mens = mensualite
        self.ratio = self.mens / self.loyer * 100
        self.rentabilite = (self.loyer * 12.0) / self.cout * 100.0

    def __str__(self):

        diff = self.loyer - self.mens
        ratio = self.mens / self.loyer * 100
        netCharge = ((self.loyer * self.occupation) / 12.0) - self.charges - (self.fonciere/12.0) - (self.ass/self.echeances)
        treso = netCharge - self.mens
        revenu = (self.loyer * 11)
        imposable = revenu - ((self.sumInteret / float(self.echeances)) * 12) - (self.ass/self.echeances) # autres charges deductibles?
        impot = imposable * (.30 + .155)

        net = (treso * 12) - impot
        rentabilite = (self.loyer * 12.0) / self.cout * 100.0

        out = '''
        loyer:       {loyer:>10,.0f}
        Mensualites: {mens:>10,.0f}
        pondere:     {pond:>10,.0f}
        ratio:      {ratio:>10,.0f}%

        netCharge:   {netc:>10,.0f} (taxeFonciere, ass, charges)
        tresorerie:  {trez:>10,.0f} (net avant impot & CSG)

        CoutGlobal:  {cout:>10,.0f} (hors ass)
        Somme Int:   {intt:>10,.0f} (global)

        revenu:      {rev:>10,.0f}
        imposable:   {impos:>10,.0f}
        impot:       {imp:>10,.0f} (manque travaux)
        net:         {net:>10,.0f}
        rentabilite:{rent:>10,.2f}%
        '''.format(pond=self.pond,
                 mens=self.mens,
                 loyer=self.loyer,
                 diff=diff,
                 ratio=ratio,
                 netc=netCharge,
                 trez=treso,
                 cout=self.coutGlobal,
                 intt=self.sumInteret,
                 rev=revenu,
                 impos=imposable,
                 imp=impot,
                 net=net,
                 rent=rentabilite )


        return out

class Simu():

    def __init__(self, pret):

        annuCapital = annuRevenu = annuInteret = annuNetCharge = 0

        year = int(time.strftime('%Y')) + 1
        restantDu = pret.cout
        reimbursed = False
        sumInterets = 0
        month = 1

        while True:

            interet = restantDu * (pret.taux)
            capital = pret.mens - interet
            annuCapital += capital
            restantDu -= capital

            if pret.annees == month/12 : reimbursed = True
            if pret.annees  + 5 == (month/12):
                total = pret.cout + sumInterets + pret.ass
                print 'year {:>2.1f} interets:{:>3,.0f} total:{:>8,.2f} ratio:{:.2f}% renta:{:.2f}%\n'.format(month/12.0, sumInterets, total, pret.ratio, pret.rentabilite)
                break

            print '{:>3} restantDu: {:>.0f}     interet: {:>2,.1f}     capital: {:>3,.0f}'.format(month, restantDu, interet, capital)
            annuRevenu += (pret.loyer * pret.occupation) / 12.0

            # -- MONTH
            pret.fluxM['Loyer M'].extend([month, pret.loyer])
            pret.fluxM['Mensualites M'].extend([month, pret.mens])
            pret.fluxM['Interet M'].extend([month, interet])
            pret.fluxM['Capital M'].extend([month, capital])

            annuInteret += interet
            annuNetCharge += ((pret.loyer * pret.occupation) / 12.0) - (pret.ass/pret.echeances*12.0) - (pret.fonciere/12.0)

            # -- YEAR
            if not month % 12:

                # pret.fluxY['Revenu Y'].extend([year, annuRevenu])
                # pret.fluxY['TresoBrut Y'].extend([year, annuNetCharge])
                # pret.fluxY['TresoNet Y'].extend([year, net])
                # ********************************************
                if not reimbursed:
                    annuTresoBrut = annuNetCharge - (pret.mens * 12) # -- avant impots
                    imposable = annuNetCharge - annuInteret

                else:
                    annuTresoBrut = annuNetCharge + (pret.ass) # -- avant impots
                    imposable = annuNetCharge
                    restantDu = 0

                impot = imposable * (.30 + .155)

                annuTresoNet = annuTresoBrut - impot # -- apres impots

                annuRevenu, annuNetCharge, annuTresoBrut, annuTresoNet, restantDu = map(int, [annuRevenu, annuNetCharge, annuTresoBrut, annuTresoNet, restantDu])
                pret.sheet.setdefault(year, [annuRevenu, annuNetCharge, annuTresoBrut, annuTresoNet])

                annuCapital = annuRevenu = annuInteret = annuNetCharge = 0
                year += 1

            sumInterets += interet
            month += 1

# revenu foncier imposable
# treso hors impot + CSG
# treso net