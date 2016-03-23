from PyQt4.QtGui import *
from PyQt4.QtCore import *
import pdb, random
db = pdb.set_trace


class Curves(QWidget, QObject):

    returned = pyqtSignal(str)

    def __init__(self, values=None, colors=None, parent=None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)
        self.values = values
        self.curves = list()
        self.numGrid = 25
        self.border = 25
        self.colors = colors
        self.pairs = dict()
        self.clampx = 0
        self.clampy = 0

        self.setInside()
        self.setSize()
        self.setConnections()
        self.setStyl()

        self.setMouseTracking(True)
        self.show()

    def setInside(self):

        for key, value in self.values.items():

            self.values[key].insert(0, 0)
            self.values[key].insert(0, value[0])

            self.values[key].append(value[-2])
            self.values[key].append(0)

    def setSize(self):

        for values in self.values.values():
            for value in values[::2]:
                if self.clampx < value: self.clampx = value

            for value in values[1::2]:
                if self.clampy < value: self.clampy = value

        self.setGeometry(2500, 1500, 600, self.clampy + self.border)
        self.unit = self.size().width()/self.numGrid

    def setStyl(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def resizeEvent(self, event):
        self.update()

    def mouseMoveEvent(self, event):

        for key, values in self.pairs.items():

            if values[0].containsPoint(event.pos(), Qt.OddEvenFill):
                self.hoverPoly = values[0]
                print key, QPolygon(values[0])
                # print 'percent: ', values[-1].pointAtPercent(values[-1].length() / (event.pos().x() / self.unit))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            print 'left'

        if event.buttons() == Qt.RightButton:
            print 'right'

        self.update()

    def setConnections(self):
        pass

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)

        # -- BACKGROUND
        gradColor = QColor(10, 10, 250)
        gradient = QRadialGradient(self.width() * .5, self.height() * .5, self.height(), self.width() * .5, self.height() * .5)
        gradient.setColorAt(0, gradColor.lighter(120))
        gradient.setColorAt(1, gradColor.darker(230))
        painter.setBrush(gradient)
        painter.drawRect(0, 0, self.width(), self.height())

        # -- DAMIER
        for v in xrange(self.numGrid):
            for h in xrange(self.numGrid):
                random.seed(h)
                chestColor = QColor(48, 52, 58, 205).darker(random.uniform(100, 110))
                painter.setBrush(QBrush(chestColor))
                painter.setPen(QPen(QBrush(chestColor), 1))
                painter.drawRect(h * self.unit, v * self.unit, self.unit-1, self.unit-1)

        # -- GRIDS
        penColor = QColor(130, 140, 170, 4)
        for v in xrange(self.numGrid):
            for h in xrange(self.numGrid):
                # -- thick
                painter.setPen(QPen(penColor.darker(150), 4))
                painter.drawLine(v * self.unit, 0, v * self.unit, self.height())
                painter.drawLine(0, h * self.unit, self.width(), h * self.unit)

                # -- thin
                painter.setPen(QPen(penColor.lighter(250), .4))
                painter.drawLine(v * self.unit, 0, v * self.unit, self.height())
                painter.drawLine(0, h * self.unit, self.width(), h * self.unit)

        # -- POLYS
        self.polys = list()
        for key, inside in self.values.items():
            color = self.colors[key]
            poly = QPolygonF()
            for i in xrange(0, len(inside), 2):
                poly << QPointF(inside[i] * self.unit, self.size().height() - inside[i+1])
            self.polys.append(poly)
            self.pairs.setdefault(key, [poly, ''])

            gradient = QLinearGradient(0, self.height() - self.clampy, 0, self.size().height())
            gradient.setColorAt(0, color)
            color.setAlpha(20)
            gradient.setColorAt(1, color.darker(220))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawPolygon(poly)

        # -- CURVES
        painter.setFont(QFont('Impact', 13, QFont.Black))
        self.curves = list()
        for key, values in self.values.items():
            curve = QPainterPath()
            self.curves.append(curve)
            color = self.colors[key]
            self.pairs[key][-1] = curve
            color.setAlpha(155)

            for i in xrange(2, len(values)-4, 2):
                move = QPoint(values[i] * self.unit, self.size().height() - values[i+1])
                line = QPoint(values[i+2] * self.unit, self.size().height() - values[i+3])

                self.curves[-1].moveTo(move)
                self.curves[-1].lineTo(line)

                painter.setPen(QPen(QBrush(color.lighter(150)), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.setBrush(QBrush(color))

            posLegend = self.curves[-1].currentPosition()
            painter.drawText(posLegend + QPoint(5, 5), key)
            painter.drawPath(curve)

        # -- COORDONNEES
        painter.setFont(QFont('FreeSans', 8, QFont.Light))
        painter.setPen(QPen(QBrush(QColor(200, 200, 200, 200)), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        for v in xrange(self.numGrid):
            painter.drawText(3, self.height() - (self.unit * v), str(self.unit * v))
            painter.drawText(v * self.unit, self.height(), str(v))

            # text = QPainterPath()
            # text.addText(0, 0, font, str(v))
            # painter.rotate(45)
            # text.translate(QPointF(v * self.unit, self.height()))
            # painter.drawPath(text)
            # painter.rotate(-45)

        # -- LEGENDS
        painter.setFont(QFont('Impact', 9, QFont.Black))
        painter.drawText(self.width() * .9, self.height() * .1, ':close')
        painter.drawText(self.width() * .9, self.height() * .2, ':avg')
        painter.drawText(self.width() * .9, self.height() * .3, ':low')
        painter.drawText(self.width() * .9, self.height() * .4, ':high')


