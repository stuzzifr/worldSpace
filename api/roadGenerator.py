from maya.OpenMaya import *

import maya.OpenMayaUI as apiUI
import maya.cmds as cmds

from swiss.ui.qt.QtCore import *
from swiss.ui.qt.QtGui import *
from swiss.ui.qt.QtWidgets import *


def debug(p):

    groupLocator = 'loc_Grp'
    if not cmds.objExists(groupLocator):
        cmds.createNode('transform', name=groupLocator)

    for i in range(p.length()):
        loc = cmds.spaceLocator(p=(p[i].x, p[i].y, p[i].z))[0]
        cmds.parent(loc, groupLocator)

        for axis in ['localScaleX', 'localScaleY', 'localScaleZ']:
            cmds.setAttr('%s.%s' % (loc, axis), 1)


class Mesh(object):

    def __init__(self, name):

        self._dag = MDagPath()
        sel = MSelectionList()
        obj = MObject()

        sel.add(name)
        sel.getDagPath(0, self._dag, obj)
        self._fn = MFnMesh(self._dag)

        self.bbox = BBox(name)

    @property
    def fnMesh(self):
        return self._fn

    @property
    def dag(self):
        return self._dag

    @property
    def touch(self):
        """ where the wheel touch the floor, same as BoundingB.bottomCenter
        returns MPoint()
        """
        closest = MPoint()
        center = self.bbox.center

        dante = MPoint(center.x,
                       center.y + self.bbox.height,
                       center.z)

        self.fnMesh.getClosestPoint(dante,
                                    closest,
                                    MSpace.kWorld)

        return closest

    @property
    def pos(self):
        """gives the center of the object
        returns MPoint()
        """
        return self.bbox.center

    @dag.setter
    def dag(self, value):
        self._dag = value


class BBox(object):
    """alternative for cmds"""

    def __init__(self, name):
        self.name = name

    @property
    def center(self):

        bbox = cmds.xform(self.name, bb=True, ws=True, q=True)

        return MPoint((bbox[3] + bbox[0]) * .5,
                      (bbox[4] + bbox[1]) * .5,
                      (bbox[5] + bbox[2]) * .5
                      )

    @property
    def height(self):
        """
        Get the height of the bounding box
        returns MVector
        """

        bbox = cmds.xform(self.name, bb=True, ws=True, q=True)

        min = MPoint((bbox[3] + bbox[0]) * .5,
                     bbox[1],
                     (bbox[5] + bbox[2]) * .5
                     )

        max = MPoint((bbox[3] + bbox[0]) * .5,
                     bbox[4],
                     (bbox[5] + bbox[2]) * .5
                     )
        return (min.y - max.y)


class Road(object):

    def __init__(self, name):
        self._road = MFnMesh()
        self._name = ''
        self._meshObj = MObject()

    @property
    def fnMesh(self):
        return self._road

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):

        fnDag = MFnDagNode(self._meshObj)
        shape = fnDag.fullPathName()
        transform = cmds.listRelatives(shape, parent=True, type='transform')

        if not transform:
            raise Exception('cannot find %s transform' % shape)

        newname = cmds.rename(transform, name)
        self._name = newname


    def addPoly(self, points):
        """Add Polygon to an existing functionSet
           points: position point in ccw as MPointArray
        """

        # debug(points)
        self._meshObj = self.fnMesh.addPolygon(points, True)

    def assignShader(self, shaderGrp):

        cmds.sets(self.name, e=True, forceElement=shaderGrp)
        print 'assigning %s to %s' % (shaderGrp, self.name)

    def flip(self):

        cmds.polyNormal(self.name, normalMode=0)

class Gen(object):

    def __init__(self, leftWheel, rightWheel):
        """
        LeftWheel: name of the leftone as Str()
        rifhtWheel: name of the rightone as Str()
        """

        self.left = Mesh(leftWheel)
        self.right = Mesh(rightWheel)

    def tesselation(self, start, end, step):
        """
        """

        out = list()
        append = out.append
        while start < end:
            res = start + step
            append(res)
            start += step

        return out


    def build(self, start=0, end=100, step=10, lWidth=1, rWidth=1, output='roadMesh'):
        """Main function for creating the road
        """

        road = Road(output)
        cmds.currentTime(start)
        span = self.tesselation(start, end, step)

        pCLeft = self.left.touch
        pCRight = self.right.touch

        vec = pCLeft - pCRight

        pL = self.left.touch + vec * lWidth
        pR = self.right.touch - vec * rWidth

        for currentTime in span:

            cmds.currentTime(currentTime)
            vec = pCLeft - pCRight


            # -- centerLane mesh construction
            pArr = MPointArray()
            pArr.append(pCRight)
            pArr.append(pCLeft)
            pArr.append(self.left.touch)
            pArr.append(self.right.touch)

            road.addPoly(pArr)


            # -- leftLane mesh construction
            vec = self.left.touch - self.right.touch
            pFL = self.left.touch + vec * lWidth

            pArr = MPointArray()
            pArr.append(pCLeft)
            pArr.append(pL)
            pArr.append(pFL)
            pArr.append(self.left.touch)

            if lWidth:
                road.addPoly(pArr)


            # -- rightLane mesh construction
            pFR = self.right.touch - vec * rWidth
            pArr = MPointArray()
            pArr.append(pR)
            pArr.append(pCRight)
            pArr.append(self.right.touch)
            pArr.append(pFR)

            if rWidth:
                road.addPoly(pArr)

            pL = pFL
            pR = pFR
            pCLeft = self.left.touch
            pCRight = self.right.touch


        road.name = output
        road.assignShader('initialShadingGroup')
        road.flip()
        cmds.select(output)


class Win(QMainWindow, QObject):

    def __init__(self):
        QMainWindow.__init__(self)

        central = QWidget(self)
        mainLayout = QVBoxLayout(central)
        gridLay = QGridLayout()

        frameLab = QLabel("Frame Interpolation:")
        widthLLab = QLabel("Left Extrusion:")
        widthRLab = QLabel("Right Extrusion:")
        outpuLab = QLabel("Output Name:")

        startLab = QLabel("Start Frame:")
        endLab = QLabel("End Frane:")

        self.leftBut = QPushButton('Left Wheel')
        self.rigthBut = QPushButton('Right Wheel')

        self.startSpin = QSpinBox()
        self.endSpin = QSpinBox()

        self.frameSpin = QDoubleSpinBox()
        self.widthLSpin = QDoubleSpinBox()
        self.widthRSpin = QDoubleSpinBox()

        self.outputLine = QLineEdit('RoadMesh')
        processBtn = QPushButton('Process')

        gridLay.addWidget(self.leftBut, 0, 0)
        gridLay.addWidget(self.rigthBut, 0, 1)

        gridLay.addWidget(startLab, 1, 0)
        gridLay.addWidget(endLab, 1, 1)

        gridLay.addWidget(self.startSpin, 2, 0)
        gridLay.addWidget(self.endSpin, 2, 1)

        gridLay.addWidget(widthLLab, 3, 0)
        gridLay.addWidget(widthRLab, 3, 1)

        gridLay.addWidget(self.widthLSpin, 4, 0)
        gridLay.addWidget(self.widthRSpin, 4, 1)

        gridLay.addWidget(self.widthLSpin, 5, 0)
        gridLay.addWidget(self.widthRSpin, 5, 1)

        gridLay.addWidget(frameLab, 6, 0)
        gridLay.addWidget(self.frameSpin, 6, 1)

        gridLay.addWidget(outpuLab, 7, 0)
        gridLay.addWidget(self.outputLine, 7, 1)


        mainLayout.addLayout(gridLay)
        self.setCentralWidget(central)
        mainLayout.addWidget(processBtn)


        self.frameSpin.setValue(1)
        self.frameSpin.setSingleStep(.1)
        self.leftBut.clicked.connect(self.addWheel)
        self.rigthBut.clicked.connect(self.addWheel)
        processBtn.clicked.connect(self.process)

        map(lambda x: x.setValue(.2), (self.widthLSpin, self.widthRSpin))
        map(lambda x: x.setMaximum(99999), (self.startSpin, self.endSpin))
        map(lambda x: x.setSingleStep(.1), (self.widthLSpin, self.widthRSpin))

        self.endSpin.setValue(cmds.playbackOptions(max=True, q=True))
        self.startSpin.setValue(cmds.playbackOptions(min=True, q=True))

        self.show()
        self.setMaximumSize(300, 200)
        self.setWindowTitle('RoadGenerator')

    def process(self):

        for entity in [self.leftBut, self.rigthBut]:
            if not cmds.objExists(entity.text()):
                raise Exception('please select valid mesh')

        obj = Gen(self.leftBut.text(), self.rigthBut.text())

        obj.build(self.startSpin.value(),
                  self.endSpin.value(),
                  self.frameSpin.value(),
                  self.widthLSpin.value(),
                  self.widthRSpin.value(),
                  self.outputLine.text()
                  )

    def addWheel(self):

        mesh = cmds.ls(sl=True, o=True, type='transform') or []

        if not mesh:
            self.sender().setText("Pick a Mesh")
            return

        self.sender().setText(mesh[0])


