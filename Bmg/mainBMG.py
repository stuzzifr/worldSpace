from PyQt4.QtGui import *
from PyQt4.QtCore import *
import Graph, Web
import pdb

db = pdb.set_trace

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
        Web.setRenta(biens)

        cloud = {'cloud': []}
        for bien in biens:
            cloud['cloud'].extend([bien.datef, bien.renta])

        colors = {'cloud':QColor(255, 255, 255, 100)}
        self.setGraph(cloud, datas=biens, mode='cloud', color= colors)

    def displayGraph(self):
        self.setGraph(values, colors, mode='curve')

    def setGraph(self, values, colors=None, mode=None, datas=None):

        if not colors:
            colors = {'cloud': QColor(255, 255, 255, 190)}

        app = QApplication([])
        graph = Graph.Curves(values, colors, mode, datas)
        graph.objectName()
        app.exec_()


if __name__ == '__main__':
    obj = BLoom()
    obj.displayCloud()
    # obj.displayGraph()
