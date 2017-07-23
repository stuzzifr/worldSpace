from maya.OpenMaya import *
from maya.OpenMayaUI import *

import maya.cmds as cmds
import math
import pdb

db = pdb.set_trace


def biggestAngle(A, B, C):
    """Description
    A: anchor as MPoint
    B: other MPoint
    C: other MPoint
    """
    v1 = B - A
    v2 = C - A
    Aangle = v1.angle(v2)

    v1 = C - B
    v2 = A - B
    Bangle = v1.angle(v2)

    v1 = B - C
    v2 = A - C
    Cangle = v1.angle(v2)

    angles = [Aangle, Bangle, Cangle]
    return angles.sort(reverse=True)


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

    def getLeftVtx(self, preFace):
        """ Description
        preface as int()
        """

        faces = self.reorderFaces(self.facesAround, preFace)

        lastFace = Face(faces[-1])

        # get connected edges
        # for each poly check if edges in this poly
        # then minus capital

        if lastFace.nature == 'quad':
            return faces[-1]

        if self.index in lastFace.vtx and lastFace.nature == 'tri':
            return faces[-2]

        if lastFace.nature == 'tri' and self.index not in lastFace.vtx:
            return faces[-2]

        # -- then do the same for vtx (ccw check)

        return -1

    def reorderFaces(self, facesArray, preface):

        ind = facesArray.index(preface)

        nw = facesArray[ind:]
        nw += facesArray[0:ind]

        return nw[1:]


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
            self.setTo(num)

    @property
    def nature(self):

        nature = ''

        num = len(self.vtx)

        if num == 3:
            return 'tri'

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

    def setTo(self, num):

        util = MScriptUtil()
        prev = util.asIntPtr()

        self.fn.setIndex(num, prev)
        self.index = num

    def corner(self):

        index = self.vtx.index(self.anchor)
        p1, p2, p3 = self.vtx[index-1: index+1]

        P1 = Point(p1)
        P2 = Point(p2)
        P3 = Point(p3)

        biggestAngle(P2.pos, P1.pos, P3.pos)

    def getLeftVtxTEMP(self):
        # -- vertice of the left, poly creation is anti CW

        leftVtx = -1
        anchorP = Point(self.anchor)

        if self.fn.nature == 'cinq':
            for i in range(1, 3):
                anchorP.setTo(self.vtx[self.anchor - i])

                if len(anchorP.numEdges) == 4:
                    leftVtx = anchorP.index()
                    break

        if self.fn.nature == 'quad':
            for i in range(1, 2):
                anchorP.setTo(self.vtx[self.anchor - i])

                if len(anchorP.numEdges) == 4:
                    leftVtx = anchorP.index()
                    break
        return leftVtx


class Mesh(object):

    def __init__(self):

        self._dag = MDagPath()
        self._obj = MObject()

        self._preVert = -1
        self._preFace = -1
        self._way = 0

        if not self.iterG.count() == 2:
            raise Exception("not correspondance")

        it = self.iterG

        first = True
        while not it.isDone():

            if first:
                self._startVert = Point(it.index())
                first = False
            else:
                self._endVert = Point(it.index())

            it.next()

    @classmethod
    def dag(cls):

        obj = MObject()
        dag = MDagPath()
        sel = MSelectionList()

        MGlobal.getActiveSelectionList(sel)
        sel.getDagPath(0, dag, obj)

        return dag

    @property
    def iterG(self):

        sel = MSelectionList()

        MGlobal.getActiveSelectionList(sel)
        sel.getDagPath(0, self._dag, self._obj)

        return MItMeshVertex(self._dag, self._obj)

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

    @property
    def preVert(self):
        return self._preVert

    @property
    def preFace(self):
        return self._preFace

    @preVert.setter
    def preVert(self, value):
        self._preVert = value

    @preFace.setter
    def preFace(self, value):
        self._preFace = value


class Rerout(object):

    def __init__(self):

        self.mesh = Mesh()
        self.mesh.way = 1  # -- need to determine the direction
        self.mesh.preFace = 14  # -- need to determine which face

        self.analyse()

    def analyse(self):

        print 'mesh.startVert ', self.mesh.startVert.index
        print 'mesh.endVert ', self.mesh.endVert.index

        vert = self.mesh.startVert

        for i in range(3):  # -- search distance

            print '/n****loop', i

            leftVert = vert.getLeftVtx(self.mesh.preFace)

            # face.anchor = vert

            outString = ' v.{} -- face:{} -- leftFace:{}'

            print outString.format(vert.index,
                                   vert.facesAround,
                                   leftVert
                                   )

            # vert = foundVert
            # self.mesh.preVert = vert
            # self.mesh.preFace = face

# Anchor angle (consecutive edges on quad poly)
# Anchor angle (if tris, consetcutive if biggest angle degree)
# Anchor angle (if tris, next + 1 if not biggest angle degree)


# Get first vert
# Get faces around (faceA)
# PreVert = -1
# PreFace = -1

# For each face
    # check how much polys connected to the vert ??
    # if face is preFace or preVert in face.vertAround
        # continue

    # check nature of this face and get consecutive

    # set preVert
    # set prevface
    # set vert
