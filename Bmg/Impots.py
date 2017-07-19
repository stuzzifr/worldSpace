import math
import time
import pdb
db = pdb.set_trace

CSG = 15.5
bareme =[[9700,.14], [26791,.30], [71826,.41], [152108,.45] ]

class Revenu():
    ''' Donne l'impot sur le revenu en fonction des quotes parts et revenu net '''

    def __init__(self, revenu, quotePart):
        self._revenu = revenu
        self._quotePart = quotePart
        self.process()

    @property
    def quotePart(self):
        return self._quotePart

    @property
    def revenu(self):
        return self._revenu

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, value):
        self._total = value

    @property
    def tmi(self):
        return self._tmi

    def process(self):

        revenuGlob = self.revenu *.9
        self.quotient = revenuGlob / self.quotePart

        amount = int()
        for i,tranche in enumerate(bareme):

            if self.quotient < bareme[i][0]:
                self._tmi = (bareme[i-1][1])*100
                break

            if self.quotient > bareme[i+1][0]:
                amount += (bareme[i+1][0] - bareme[i][0]) * bareme[i][1]

            else:
                amount += (self.quotient - bareme[i][0]) * bareme[i][1]

        self.total = amount * self.quotePart


    def __str__(self):
        ratio = (self.total / float(self.revenu)) * 100
        return 'Impots {:>,.2f}\t\tImposition {:.2f}%\t\tTMI {}%'.format(self.total, ratio, self.tmi)


class Foncier():

    ''' Donne l'impot Foncier + SCG en fonction du revenu foncier apres deduction '''

    def __init__(self, impotRev, foncier):
        self.impotRev = impotRev
        self.foncier = foncier

        self.process()

    def __str__(self):
        return 'impot foncier {:.2f}\t\ttaxeFonciere {:.2f}\t\tCSG {:.2f}'.format(self.total, self.taxefoncier, self.csg)

    @property
    def csg(self):
        return self._csg

    @property
    def taxefoncier(self):
        return self._taxefoncier

    @property
    def total(self):
        return self._total

    def getIndex(self):

        for i, tmi in enumerate(bareme):
            if self.impotRev.tmi == (tmi[1])*100:
                return i

    def process(self):

        quotient = self.foncier / self.impotRev.quotePart
        quotientSum = quotient + self.impotRev.quotient

        index = self.getIndex()
        thisbareme = bareme[index:]

        first = True
        amount = int()
        for i, tranche in enumerate(thisbareme):

            if first:
                diff = (thisbareme[i+1][0] - self.impotRev.quotient)

                if  quotient < diff: amount += quotient * thisbareme[0][1]
                else: amount += (quotient - self.impotRev.quotient) * thisbareme[0][1]

                first = False
                continue

            if quotientSum < thisbareme[i][0]:
                break

            if quotientSum > thisbareme[i+1][0]:
                amount += (thisbareme[i+1][0] - quotientSum) * thisbareme[i][1]

            else:
                amount += (quotientSum - thisbareme[i][0]) * thisbareme[i][1]

        self._taxefoncier = amount * self.impotRev.quotePart
        self._csg= self.foncier * (CSG/100.0)
        self._total = self.taxefoncier + self.csg
