from PyQt4.QtGui import *
from PyQt4.QtCore import *
import math, pdb
db = pdb.set_trace


class Curves(QWidget, QObject):

    returned = pyqtSignal(str)

    def __init__(self, values=None, parent=None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.values = values
        self.curves = list()
        self.numGrid = 25
        self.clampx = 0
        self.clampy = 0

        self.setSize()
        self.setConnections()
        self.setStyl()

        self.show()

    def setSize(self):

        for key, values in self.values.items():
            for value in values:
                if self.clampx < value[0]: self.clampx = value[0]
                if self.clampy < value[1]: self.clampy = value[1]

        self.setGeometry(2000, 1400, 900, 400)
        self.unit = self.size().width()/self.numGrid
        print 'clampx', self.clampx
        print 'clampy', self.clampy

    def setStyl(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def focusOutEvent(self, event):
        print 'outFocus', event

    def resizeEvent(self, event):
        self.update()

    def mousePressEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            print 'left', event.pos()

        if event.buttons() == Qt.RightButton:
            print 'right', event.pos()

    def setConnections(self):
        pass

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        # painter.setPen(QPen(QBrush(gridColor), 1))

        # -- grids
        # aligns = ['vertical', 'horizont']
        # for align in aligns:
        for v in xrange(self.numGrid):
            for h in xrange(self.numGrid):
                gridColor = QColor(20, 33, 39, 200 * (.5 + (math.sin(h) * .3)))
                painter.setBrush(QBrush(gridColor))
                # painter.drawRect(h * self.unit, v * self.unit, self.unit-3, self.unit-3)

        # -- CURVES
        color = QColor(130, 134, 140, 200)

        poly = QPolygonF()
        for value in self.values.values()[0]:
            poly << QPointF(value[0] * self.unit, value[1] * self.unit)

        painter.drawPolygon(poly)

        # for key, values in self.values.items():
        #     curve = QPainterPath()
        #     self.curves.append(curve)

        #     for i in xrange(1, len(values)):
        #         move = QPoint(values[i-1][0] * self.unit, self.size().height() - values[i-1][1])
        #         line = QPoint(values[i][0] * self.unit, self.size().height() - values[i][1])

        #         self.curves[-1].moveTo(move)
        #         self.curves[-1].lineTo(line)

        #         painter.setPen(QPen(QBrush(color.lighter(250)), 2))
        #         painter.setBrush(QBrush(color))

        #         painter.drawPath(curve)

        #     tail = QPainterPath()
        #     tail.moveTo(self.curves[-1].currentPosition())
        #     tail.lineTo(QPoint(self.curves[-1].currentPosition().x(), self.size().height()))
        #     painter.drawPath(tail)

        #     end = QPainterPath()
        #     end.moveTo(tail.currentPosition())
        #     end.lineTo(QPoint(0, self.size().height()))

        #     painter.drawPath(end)

        # font = QFont('FreeSans', 20, QFont.Black)
        # -- BORDER

