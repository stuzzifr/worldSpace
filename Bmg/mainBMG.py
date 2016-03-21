from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pdb
import Graph

db = pdb.set_trace


class Win():

    def __init__(self, parent=None):

        val = {'Cash': [[0, 10],
               [1, 110],
               [2, 130],
               [3, 30],
               ]
               }

        self.setGraph(val)

    def setGraph(self, val):

        app = QApplication([])
        graph = Graph.Curves(val)
        print 'objectName', graph.objectName()
        app.exec_()


if __name__ == '__main__':
    obj = Win()
