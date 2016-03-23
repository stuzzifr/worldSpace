from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pdb
import Graph

db = pdb.set_trace


class Win():

    def __init__(self, parent=None):

        self.val = {'Cash': [0, 10,
                             1, 110,
                             2, 130,
                             3, 30,
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

        self.colors = {'Cash': QColor(255, 0, 0),
                       'Capital': QColor(255, 0, 255),
                       }

        self.setGraph()

    def setGraph(self):

        app = QApplication([])
        graph = Graph.Curves(self.val, self.colors)
        graph.objectName()
        app.exec_()


if __name__ == '__main__':
    obj = Win()
