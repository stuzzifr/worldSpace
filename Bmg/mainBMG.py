from PyQt4.QtGui import *
from PyQt4.QtCore import *

from Pret import *
from Epargne import *
from Impots import *
from Regime import *
from Study import *

import Graph
import Web

values = {'Cash': [0, 10,
                   1, 110,
                   2, 130,
                   3, 80,
                   4, 160,
                   6, 60,
                   9, 80,
                   ],

          'Capital': [0, 3,
                      1, 50,
                      2, 60,
                      3, 20,
                      4, 80,
                      7, 20,
                      10, 30,
                      ],
          }

colors = {'Cash': QColor(255, 0, 0),
          'Capital': QColor(255, 0, 255),
          }


class BLoom():

    def __init__(self, parent=None):
        pass

    def displayCloud(self):

        links = Web.getLinks()
        biens = Web.getDatas(links)
        print 'biens ', biens
        Web.setRenta(biens)

        cloud = {'cloud': []}
        for bien in biens:
            cloud['cloud'].extend([bien.datef, bien.renta])

        colors = {'cloud': QColor(200, 200, 255, 80)}
        self.setGraph(cloud, datas=biens, mode='cloud', colors=colors)

    def displayGraph(self, val, col=None):
        if not col:
            col = dict()
            for i in val.keys():
                col.setdefault(i, QColor(100, 100, 100))

        self.setGraph(val, col, mode='curve')

    def setGraph(self, values, colors=None, mode=None, datas=None):

        if not colors:
            colors = {'cloud': QColor(255, 255, 255, 90)}

        app = QApplication([])
        graph = Graph.Curves(values, colors, mode, datas)
        graph.objectName()
        app.exec_()

if __name__ == '__main__':
    # obj = BLoom()
    # obj.displayCloud()
    # obj.displayGraph(values)

    av = AssuranceV(start=100000, year=8, taux=8, pot=0)
    print av

    pret = Classique(cout=120000, taux=1.50, annees=20, loyer=900,
                     charges=128, fonciere=156, ass=2680, occupation=12,
                     travaux=0, notaire=0, apport=0
                     )

    regime = Regime(pret, 'BICreel')
    # print pret
    # print regime
#
    # impot = Revenu(revenu=126770, quotePart=2.5)
    # foncier = Foncier(impot, foncier=5400)

    # obj = Renta(prix=129000, surface=45, travaux=10000, loyer=1000 )
    # print obj.getCost( )
