from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pdb
import Graph
import Web

db = pdb.set_trace


class Win():

    def __init__(self, parent=None):

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

        links = Web.getLinks()
        biens = Web.getDatas(links)
        Web.setRenta(biens)

        cloud = {'cloud': []}
        for bien in biens:
            # -- change bien.price to renta
            cloud['cloud'].extend([bien.datef, bien.price])

        self.setGraph(cloud, datas=biens)
        # self.setGraph(values, colors)

    def setGraph(self, values, colors=None, datas=None):

        if not colors:
            colors = {'cloud': QColor(255, 255, 0)}

        app = QApplication([])
        graph = Graph.Curves(values, colors, 'cloud', datas)
        # graph = Graph.Curves(values, colors, 'curve')
        graph.objectName()
        app.exec_()


if __name__ == '__main__':
    obj = Win()
