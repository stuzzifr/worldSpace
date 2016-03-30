from PyQt4.QtGui import *
from PyQt4.QtCore import *
import random, os, math, shutil, subprocess
import pdb

db = pdb.set_trace


class Curves(QWidget, QObject):
    prev = QPoint()
    prevSize = QSize()
    previous = False

    returned = pyqtSignal(str)

    def __init__(self, values=None, colors=None, mode='curve', datas=None, parent=None):
        QWidget.__init__(self, parent)

        self.setMouseTracking(True)
        self.mode = mode
        self.numGrid, self.border = 25, 25
        self.clampx, self.clampy = 0, 0
        self.closestPoint = QPoint(0, 0)
        self.hoverPoly = QPolygon()
        self.hoverCloud = QPainterPath()
        self.hoverItem = None
        self.datas = datas
        self.values = values
        self.colors = colors
        self.curves = list()
        self.pairs = dict()

        self.setSaturation()
        self.setInside()
        self.setSize()
        self.setStyl()

        self.setMouseTracking(True)
        self.show()

    def setSaturation(self):
        coef = .8
        for key, color in self.colors.items():
            color.setHsvF(
                color.hueF(), (color.saturationF() * coef), color.valueF() * coef)

    def setInside(self):
        ''' add values before and after to create a closed poly '''

        for key, value in self.values.items():

            self.values[key].insert(0, 0)
            self.values[key].insert(0, value[0])

            self.values[key].append(value[-2])
            self.values[key].append(0)

    def setSize(self):

        for values in self.values.values():
            for value in values[::2]:
                if self.clampx < value:
                    self.clampx = value

            for value in values[1::2]:
                if self.clampy < value:
                    self.clampy = value

        self.setGeometry(1200, 1500, 600, 280)
        self.unit = self.size().width()/self.numGrid

    def getSum(self, key):
        sum = 0
        for pos in self.values[key][1::2]:
            sum += pos
        return sum

    def getAverage(self, key):
        return self.getSum(key) / ((len(self.values[key])) * .5)

    def getLow(self, key):
        low = self.clampy
        for pos in self.values[key][1::2]:
            if pos < low:
                low = pos

        return low

    def getHigh(self, key):
        high = 0
        for pos in self.values[key][1::2]:
            if pos > high:
                high = pos

        return high

    def setStyl(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def distance(self, A, B):
        return math.sqrt(math.pow((A.x()-B.x()), 2) + math.pow((A.y()-B.y()), 2))

    def closeEvent(self, event):
        path = os.path.dirname(self.datas[-1].thumbLoc)
        if os.path.exists(path):
            shutil.rmtree(path)

    def mouseReleaseEvent(self, event):
        self.previous = False

    # def resizeEvent(self, event):
    #     self.numGrid = int(self.width() * .1)

    def resizeEvent(self, event):
        self.update()

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.MidButton:
            if not self.previous:
                self.prev = event.globalPos()
                self.offset = event.pos()
                self.previous = True
                return

            out = event.globalPos() - self.prev
            self.move(self.prev - self.offset + out)

        if event.buttons() == Qt.RightButton:
            if not self.previous:
                self.prev = event.globalPos()
                self.prevSize = self.size()
                self.previous = True
                return

            out = event.globalPos() - self.prev
            self.resize(
                self.prevSize.width() + out.x(), self.prevSize.height() + out.y())

        for key, values in self.pairs.items():

            if values[0].containsPoint(event.pos(), Qt.OddEvenFill):
                p = 0
                shortest = 900
                self.hoverPoly = values[0]
                while p < 1.0:
                    pCurrent = values[1].pointAtPercent(p)
                    fThisDistance = self.distance(pCurrent, event.pos())
                    if fThisDistance < shortest:
                        shortest = fThisDistance
                        self.closestPoint = pCurrent
                    p += .01

                self.update()

        for i in xrange(len(self.clouds)):
            if self.clouds[i].contains(event.pos()):
                self.hoverCloud = self.clouds[i]
                self.hoverItem = self.datas[i]
                self.update()
                break

            self.hoverItem = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def mousePressEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            if self.hoverItem:
                subprocess.call('firefox %s' % self.hoverItem.url, shell=True)

        if event.buttons() == Qt.RightButton:
            print 'right'

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)
        self.coef = (self.height() - self.border) / float(self.clampy)

        # -- BACKGROUND
        gradColor = QColor(0, 30, 150)
        gradient = QRadialGradient(self.width() * .5, self.height() * .5, self.height() * 1, self.width() * .5, self.height() * .5)
        gradient.setColorAt(0, gradColor.lighter(210))
        gradient.setColorAt(1, gradColor.darker(390))
        painter.setBrush(gradient)
        painter.drawRect(0, 0, self.width(), self.height())

        # # -- DAMIER
        for v in xrange(self.numGrid):
            for h in xrange(self.numGrid):
                random.seed(h)

                chestColor = QColor(48, 52, 58, 205).darker(
                    random.uniform(100, 110))
                if v % 2 == 0:
                    painter.setBrush(QBrush(chestColor.darker(113)))
                else:
                    painter.setBrush(QBrush(chestColor))
                painter.setPen(QPen(QBrush(chestColor), 1))
                painter.drawRect(
                    h * self.unit, v * self.unit, self.unit-2, self.unit-2)

        # -- GRIDS
        penColor = QColor(190, 190, 190, 40)
        for v in xrange(self.numGrid):
            # -- THICK
            if v % 10 == 0:
                painter.setPen(QPen(penColor.lighter(190), .8, Qt.DashLine))
            else:
                painter.setPen(QPen(penColor.darker(150), 1.8))
            painter.drawLine(v * self.unit, 0, v * self.unit, self.height())
            painter.drawLine(0, v * self.unit, self.width(), v * self.unit)

            # -- THIN
            painter.setPen(QPen(penColor.lighter(350), .61))
            painter.drawLine(v * self.unit, 0, v * self.unit, self.height())
            painter.drawLine(0, v * self.unit, self.width(), v * self.unit)

        if self.mode == 'curve':
            self.paintCurve(painter)

        if self.mode == 'cloud':
            self.paintCloud(painter)

    def paintCloud(self, painter):

        self.clouds = list()
        for key, values in self.values.items():

            for i in xrange(2, len(values)-4, 2):
                move = QPoint(values[i] * self.unit, self.height() - (values[i+1] * self.coef))
                self.clouds.append(QPainterPath())
                self.clouds[-1].addEllipse(move, 2, 2)

                color = self.colors[key]
                if self.hoverCloud == self.clouds[-1]:
                    color.lighter(430)

                painter.setPen(QPen(color, 1.3))
                painter.drawPath(self.clouds[-1])

            # -- thumb
            if self.hoverItem:

                s = 100
                pixmap = QPixmap(s, s)
                pixmap.load(self.hoverItem.thumbLoc, 'jpg')
                painter.drawPixmap(self.width() - s - self.border, self.border, s, s, pixmap)

                legends = QPainterPath()
                font = QFont('FreeSans', 10, QFont.Light)

                step = 16
                legends = QPainterPath()
                legends.addText(self.width()-s - self.border, self.border + s + step, font, 'Price: {:,} Eurs'.format(self.hoverItem.price))
                legends.addText(self.width()-s - self.border, legends.boundingRect().bottom() + step, font, 'Rentabilite: {:.2f}'.format(self.hoverItem.ratio))
                legends.addText(self.width()-s - self.border, legends.boundingRect().bottom() + step, font, 'Ratio: {:.0f}'.format(self.hoverItem.ratio))
                legends.addText(self.width()-s - self.border, legends.boundingRect().bottom() + step, font, 'Surface: {}'.format(self.hoverItem.surface))
                legends.addText(self.width()-s - self.border, legends.boundingRect().bottom() + step, font, 'Pieces: {}'.format(self.hoverItem.pieces))
                legends.addText(self.width()-s - self.border, legends.boundingRect().bottom() + step, font, 'Ville: {}'.format(self.hoverItem.ville))
                legends.addText(self.width()-s - self.border, legends.boundingRect().bottom() + step, font, 'Date: {}'.format(self.hoverItem.date))
                # font.setPointSize(8)
                # txt = self.hoverItem.desc
                # txt = '\n'.join(txt.split('.'))
                # legends.addText(0, self.height() - step, font, '{}'.format(txt))
                # legends.addText(0, step, font, '{}'.format(txt))

                painter.setPen(QPen(QColor(255, 255, 255, 155), .61))
                painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
                painter.drawPath(legends)

    def paintCurve(self, painter):

        # -- POLYS
        width = 3
        self.polys = list()
        for key, inside in self.values.items():
            color = self.colors[key]
            poly = QPolygonF()
            for i in xrange(0, len(inside), 2):
                x = inside[i] * self.unit
                y = self.height() - (inside[i+1] * self.coef)

                poly << QPointF(x, y)
                painter.setBrush(color.darker(215))
                painter.drawRect(x + (width * .5), y, width, inside[i+1])

            self.polys.append(poly)
            self.pairs.setdefault(key, [poly, ''])

            gradient = QLinearGradient(0, self.height() - self.clampy, 0, self.size().height())

            if self.hoverPoly == poly:
                gradient.setColorAt(0, color.lighter(150))
            else:
                gradient.setColorAt(0, color)

            color.setAlpha(20)
            gradient.setColorAt(1, color.darker(220))
            painter.setBrush(QBrush(gradient))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawPolygon(poly)

        # -- CURVES
        self.curves = list()
        for key, values in self.values.items():
            curve = QPainterPath()
            self.curves.append(curve)
            color = self.colors[key]
            self.pairs[key][-1] = curve
            color.setAlpha(155)

            for i in xrange(2, len(values)-4, 2):

                move = QPoint(values[i] * self.unit, self.height() - (values[i+1] * self.coef))
                line = QPoint(values[i+2] * self.unit, self.height() - (values[i+3] * self.coef))

                pourcent = ((self.height()-line.y()) - (self.height() - move.y())) / float(self.height() - move.y()) * 100
                midPoint = move + ((line - move) * .5)
                sign = '+' if pourcent > 0 else '-'
                painter.setFont(QFont('FreeSans', 8.5, QFont.Light))
                painter.drawText(
                    midPoint, '{}{:0>.1f}%'.format(sign, abs(pourcent)))

                self.curves[-1].moveTo(move)
                self.curves[-1].lineTo(line)

                painter.setPen(
                    QPen(QBrush(color.lighter(150)), 1.5, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                painter.setBrush(QBrush(color))

            posLegend = self.curves[-1].currentPosition()
            painter.setFont(QFont('Impact', 13, QFont.Black))
            painter.drawText(posLegend + QPoint(5, 5), key)
            painter.drawPath(curve)

        # -- COORDONNEES
        painter.setFont(QFont('FreeSans', 8, QFont.Light))
        painter.setPen(QPen(QBrush(QColor(200, 200, 200, 200)), 1, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        for v in xrange(self.numGrid):
            # -- vertical
            painter.drawText(3, self.height() - (self.unit * v * self.coef), str(self.unit * v))
            # -- horizontal
            painter.drawText(v * self.unit, self.height(), str(v))

        # -- LEGENDS
        step = 10
        x = self.width() * .85
        legends = QPainterPath()
        font = QFont('FreeSans', 8, QFont.Light)
        for key in self.values.keys():
            legends.addText(x, legends.boundingRect().bottom() + step * 2, font, '{}'.format(key.upper()))
            legends.addText(x, legends.boundingRect().bottom() + step, font, 'avg: {: >10.1f}'.format(self.getAverage(key)))
            legends.addText(x, legends.boundingRect().bottom() + step, font, 'low: {: >10.1f}'.format(self.getLow(key)))
            legends.addText(x, legends.boundingRect().bottom() + step, font, 'hig: {: >10.1f}'.format(self.getHigh(key)))
            legends.addText(x, legends.boundingRect().bottom() + step, font, 'sum: {: >10.1f}'.format(self.getSum(key)))

            painter.setPen(QPen(QColor(self.colors[key]).lighter(150)))
            painter.drawPath(legends)

        # -- CLOSEST
        rad = 15
        painter.setPen(QPen(QColor(235, 235, 240, 200), 1))
        painter.drawPie(self.closestPoint.x() - (rad * .5), self.closestPoint.y() - (rad * .5), rad, rad, 30 * 16, 120 * 16)

        # -- x
        text = '{:.1f}'.format(self.closestPoint.x() / self.unit)
        painter.drawText(self.closestPoint + QPointF(rad, 0), text)

        # -- y
        y = self.height() - (self.closestPoint.y())
        text = '{:.1f}'.format(y)
        painter.drawText(self.closestPoint + QPointF(rad, rad), text)
