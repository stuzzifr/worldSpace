import time


class AssuranceV():

    def __init__(self, start, year=20, pot=0, taux=3.05):
        '''
        Param: pot, argent remise chaque annee
        '''

        self._start = start
        self._year = year
        self._taux = taux
        self._pot = pot
        self._fraisE = .80
        self._fraisG = .475

    @property
    def pot(self):
        return self._pot

    @property
    def year(self):
        return self._year

    @property
    def start(self):
        return self._start

    @property
    def taux(self):
        return float(self._taux)

    @property
    def fraisE(self):
        return self._fraisE

    @property
    def fraisG(self):
        return self._fraisG

    @fraisG.setter
    def fraisG(self, value):
        self._fraisG = value

    @fraisE.setter
    def fraisE(self, value):
        self._fraisE = value

    def fraisEntree(self, value):
        out = value - (value * self.fraisE/100)
        return out

    def fraisGestion(self, value):
        out = value - (value * self.fraisG/100)
        return out

    def __str__(self):

        out = ''
        capital = self.fraisEntree(self.start)
        interet = float()
        sumInt = float()

        for i in range(self.year):
            interet = capital * (self.taux / 100)
            interet = self.fraisGestion(interet)
            sumInt += interet
            capital += interet
            capital += (self.pot * 12)
            date = int(time.strftime('%Y')) + i + 1
            ratio = sumInt * 100 / self.start

            out += ('\nyear: {inc:<2}: {year: <6}\t'
                    'capital: {cap: ,.0f}\t'
                    'interet: {inte: ,.0f}\t'
                    'ratio: {rat: <6.2f}%'.format(inc=i+1,
                                                  rat=ratio,
                                                  year=date,
                                                  cap=capital,
                                                  inte=sumInt,)
                    )

        return out
