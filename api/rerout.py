from maya.OpenMaya import *

from maya.OpenMayaUI import *
import maya.cmds as cmds
import pdb
import math

db = pdb.set_trace


class Point(object):

    def __init__(self, num):

        self._iterV = MItMeshVertex()

        self._edgesAround = MIntArray()
        self._facesAround = MIntArray()

        util = MScriptUtil()
        prev = util.asIntPtr()
        self.iterV.setIndex(num, prev)

        self.index = num
        self._pos = iterV.position(MSpace.kWorld)

    @property
    def pos(self):
        return self._pos

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def edgesAround(self):
        iterV.getConnectedEdges(self._edgesAround)
        return self._edgesAround

    @property
    def facesAround(self):
        iterV.getConnectedFaces(self._facesAround)
        return self._facesAround

    @property
    def numEdges(self):
        util = MScriptUtil()
        num = util.asIntPtr()

        self._iterV.numConnectedEdges(num)

        return num

    def setTo(self, num):

        util = MScriptUtil()
        prev = util.asIntPtr()

        self._iterV.setIndex(num, prev)
        self.index = self._iterV.index()

    def getOppositeVtx(self, edgeNum):

        util = MScriptUtil()
        VtxPtr = util.asIntPtr()

        self._iterV.getOppositeVertex(VtxPtr, edgeNum)

        return util.getInt(VtxPtr)


class Mesh(object):

    def __init__(self):

        self._startVert = None
        self._endVert = None
        self._itVert = None
        self._way = 0

        if not self.iterV.count() == 2:
            raise Exception("no correspondance")

        for i in range(2):

            if i == 0:
                self._startVert = Point(i)

            if i == 1:
                self._endVert = Point(i)

    @classmethod
    def dag(cls):

        obj = MObject()
        dag = MDagPath()
        sel = MSelectionList()

        MGlobal.getActiveSelectionList(sel)
        sel.getDagPath(0, dag, obj)

        return dag

    @property
    def iterV(self):

        sel = MSelectionList()
        obj = MObject()

        return MItMeshVertex(Mesh.dag(), obj)

    @property
    def startVert(self):
        return self._startVert

    @property
    def endVert(self):
        return self._endVert

    @property
    def fn(self):
        return MFnMesh(Mesh.dag())

    @property
    def way(self):
        return self._way

    @way.setter
    def way(self, value):
        self._way = value


class Face(object):

    def __init__(self):

        self._iterF = MItMeshPolygon(Mesh.dag())
        self._anchor = int()
        self._index = int()

    @property
    def nature(self):

        nature = ''
        num = self._iterF.numConnectedEdges()

        if num == 3:
            return 'tris'

        if num == 4:
            return 'quad'

        if num == 5:
            return 'cinq'

        return 'invalid'

    @property
    def anchor(self):
        return self._anchor

    @anchor.setter
    def anchor(self, num):
        self._anchor = num

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def around(self):

        around = MIntArray()
        self._iterF.getVertices(around)

        return [around[i] for i in range(around.length())]

    @property
    def leftVtx(self):

        # -- vertice of the left, poly creation is anti CW

        leftVtx = int()
        checkP = Point(self.anchor)

        if self._iterF.nature == 'cinq':
            for i in range(1, 3):
                checkP.setTo(self.around[self.anchor - i])

                if len(checkP.numEdges) == 4:
                    leftVtx = checkP.index()
                    break

        if self._iterF.nature == 'quad':
            for i in range(1, 2):
                checkP.setTo(self.around[self.anchor - i])

                if len(checkP.numEdges) == 4:
                    leftVtx = checkP.index()
                    break

        return leftVtx


class Rerout(object):

    def __init__(self):

        self.mesh = Mesh()
        self.mesh.way = 1
        self.analyse()

    def analyse(self):

        vert = self.mesh.startVert
        for i in self.mesh.startVert.edgesAround:

            print '/n****loop', i

            for e in range(0, 4):

                opposite = vert.getOppositeVtx(vert.edgesAround[self.mesh.way])
                outString = ' v.{} -- edges:{} -- faces:{} -- way{}'

                print outString.format(vert.index,
                                       vert.edgesAround,
                                       vert.facesAround,
                                       opposite
                                       )

                vert.setTo(opposite)
