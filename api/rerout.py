from maya.OpenMaya import *
from maya.OpenMayaUI import *

import maya.cmds as cmds
import math
import pdb

db = pdb.set_trace


def reorder(array, ind):

    ind = array.index(ind)

    sortArray = array[ind:]
    sortArray += array[0:ind]

    return sortArray[1:]

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

    @property
    def capital(self):
        """how many tris around the vert
        8 is normal : only quad or split quads
        the 7th is the good one
        """

        capital = 0

        for face in self.facesAround:

            f = Face(face)

            if f.nature == 'tri':
                capital += 1

            if f.nature == 'quad':
                capital += 2

            if f.nature == 'cinq':
                capital += 3

        return capital


    def getLeftFace(self, preFace):
        """ Description
        preface as int()
        """

        faces = reorder(self.facesAround, preFace)

        lastFace = Face(faces[-1])

        if lastFace.nature == 'quad' and self.capital == 8:
            print 'first'
            return faces[-1]

        elif lastFace.nature == 'quad' and self.capital == 7:
            print 'second'
            return faces[-1]

        elif lastFace.nature == 'tri' and self.capital == 7:
            print 'third'
            return faces[-1]

        elif lastFace.nature == 'tri' and self.capital == 8:
            print 'fourth'
            return faces[-2]

        else:
            raise Exception('''cannot find this scenario
                index: %s
                nature: %s
                capital: %s''' % (self.index, lastFace.nature, self.capital))





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

    def getLeftVtx(self, anchor):
        # -- vertice of the left, poly creation is anti CW

        sortedVtx = reorder(self.vtx, anchor)
        return sortedVtx[-1]


    def getTurkish(self):

        facesAround = MIntArray()
        self.fn.getConnectedFaces(facesAround)

        for f in xrange(facesAround):
            face = Face(f)

            if face.

            aroundSet = set(facesAround)
            currentSet = set(self.vtx)

            res = aroundSet.difference(currentSet)

            if res == 1:
                return f



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
        self.mesh.preFace = 44  # -- need to determine which face

        self.analyse()

    def analyse(self):

        vert = self.mesh.startVert
        poses = MPointArray()


        # need to add turkish face when capital 7
        for i in range(6):  # -- search distance

            leftFace = vert.getLeftFace(self.mesh.preFace)

            f = Face(leftFace)
            leftVtx = f.getLeftVtx(vert.index)

            outString = 'v.{} -- leftFace:{}, -- leftVtx:{}\n'
            print outString.format(vert.index,
                                   leftFace,
                                   leftVtx,
                                   )

            self.mesh.preFace = leftFace
            vert = Point(leftVtx)

        # cmds.createNode('transform', n='loc')
        # cmds.parent(sph[0], 'loc')
