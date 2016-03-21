from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Win(QWidget, QObject):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setMouseTracking(True)

        self.paint = False
        self.show()

    def mousePressEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            self.pos = event.pos()
            self.path = QPainterPath(self.pos)
            self.paint = True
            self.update()

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.LeftButton:
            self.pos = event.pos()
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.HighQualityAntialiasing)

        painter.setBrush(QColor(30, 30, 50, 255))
        painter.drawRect(QRectF(0, 0, 800, 800))

        color = QColor(255, 255, 255, 200)

        if self.paint:

            self.path.lineTo(self.pos)

            painter.setPen(QPen(QColor(color), .8))
            painter.drawPath(self.path)

def launch():

    app = QApplication([])
    obj = Win()
    # obj.resize(800,800)
    obj.setGeometry(900, 0, 500, 500)

    app.exec_()

if __name__ == '__main__':
    launch()
