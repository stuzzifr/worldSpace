from maya.OpenMaya import *
from maya.OpenMayaUI import *

import maya.cmds as cmds
import math
import pdb

db = pdb.set_trace


class Point(object):

    def __init__(self, num):


        self._fn = MItMeshVertex(Mesh.dag())

        if num:
            self.setTo(num)

        self._edgesAround = MIntArray()
        self._facesAround = MIntArray()

    @property
    def fn(self):
        return self._fn

    @property
    def pos(self):
        return self.fn.position(MSpace.kWorld)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def edgesAround(self):
        self.fn.getConnectedEdges(self._edgesAround)
        return [self._edgesAround[i] for i in range(self._edgesAround.length())]

    @property
    def facesAround(self):
        self.fn.getConnectedFaces(self._facesAround)
        return [self._facesAround[i] for i in range(self._facesAround.length())]

    @property
    def numEdges(self):
        util = MScriptUtil()
        num = util.asIntPtr()

        self.fn.numConnectedEdges(num)

        return num

    def setTo(self, num):

        util = MScriptUtil()
        prev = util.asIntPtr()

        self.fn.setIndex(num, prev)
        self.index = num

    def getOppositeVtx(self, edgeNum):

        util = MScriptUtil()
        VtxPtr = util.asIntPtr()

        self.fn.getOppositeVertex(VtxPtr, edgeNum)

        return util.getInt(VtxPtr)


class Edge(object):
    def __init__(self, num=None):

        self._fn = MItMeshEdge(Mesh.dag())
        self._index = None

        if num:
            self.setTo(num)


    @property
    def fn(self):
        return self._fn

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def aroundFaces(self):
        connFaces = MIntArray()
        self.fn.getConnectedFaces(connFaces)

        return [connFaces[i] for i in range(connFaces.length())]

    @property
    def aroundEdges(self):
        connEges = MIntArray()
        self.fn.getConnectedEdges(connEges)

        return [connEges[i] for i in range(connEges.length())]


    @property
    def pair(self):

        first = self.fn.index(0)
        second = self.fn.index(1)

        return (first, second)

    def setTo(self, num):

        util = MScriptUtil()
        prev = util.asIntPtr()

        self.fn.setIndex(num, prev)
        self.index = num


class Face(object):

    def __init__(self, num):

        self._fn = MItMeshPolygon(Mesh.dag())
        self._anchor = int()
        self._index = None

        if num:
            self.fn.setTo(num)


    @property
    def nature(self):

        nature = ''
        num = self.fn.numConnectedEdges()

        if num == 3:
            return 'tris'

        if num == 4:
            return 'quad'

        if num == 5:
            return 'cinq'

        return 'invalid'

    @property
    def fn(self):
        return self._fn

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
    def vtx(self):

        around = MIntArray()
        self.fn.getVertices(around)

        return [around[i] for i in range(around.length())]

    @property
    def edges(self):

        around = MIntArray()
        self.fn.getEdges(around)

        return [around[i] for i in range(around.length())]

    @property
    def having(self, vertNum, edgeNum):
        pass

    @property
    def twin(self):
        pass


    def setTo(self, num):

        util = MScriptUtil()
        prev = util.asIntPtr()

        self.fn.setIndex(num, prev)
        self.index = num

    @property
    def leftVtx(self):

        # -- vertice of the left, poly creation is anti CW

        leftVtx = -1
        checkP = Point(self.anchor)

        if self.fn.nature == 'cinq':
            for i in range(1, 3):
                checkP.setTo(self.around[self.anchor - i])

                if len(checkP.numEdges) == 4:
                    leftVtx = checkP.index()
                    break

        if self.fn.nature == 'quad':
            for i in range(1, 2):
                checkP.setTo(self.around[self.anchor - i])

                if len(checkP.numEdges) == 4:
                    leftVtx = checkP.index()
                    break

        return leftVtx


class Mesh(object):

    def __init__(self):


        self._startVert = None
        self._endVert = None
        self._itVert = None
        self._way = 0

        if not self.iterV.count() == 2:
            raise Exception("not correspondance")

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


class Rerout(object):

    def __init__(self):

        self.mesh = Mesh()
        self.mesh.way = 1 # -- need to determine the direction
        # self.analyse()

    def analyse(self):

        vert = self.mesh.startVert
        # face = -- will need to find the good face

        for f in vert.facesAround:

            print '/n****face', f

            face = Face(f)
            face.anchor = vert



            oppositeNum = vert.getOppositeVtx(vert.edgesAround[self.mesh.way])
            opp = Point(oppositeNum)

            outString = ' v.{} -- faces:{} -- v.{} -- face:{}'

            print outString.format(vert.index,
                                   vert.facesAround,
                                   opp.index,
                                   opp.facesAround
                                   )

            # face = reinit face

# Anchor angle (consecutive edges on quad poly)
# Anchor angle (if tris, consetcutive if biggest angle degree)
# Anchor angle (if tris, next + 1 if not biggest angle degree)


# Get first vert
# Get faces around (faceA)

# For each face
    # check how much polys connected to the vert
    # check nature of this face and get consecutive
    # reset vert

