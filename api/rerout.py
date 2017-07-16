from maya.OpenMaya import *
from maya.OpenMayaUI import *
import maya.cmds as cmds
import pdb
import math

db = pdb.set_trace


class Point(object):

    def __init__(self, iterV):

        self._edgesAround = MIntArray()
        self._facesAround = MIntArray()

        iterV.getConnectedFaces(self._facesAround)
        iterV.getConnectedEdges(self._edgesAround)

        self._index = iterV.index()
        self._pos = iterV.position(MSpace.kWorld)

    @property
    def pos(self):
        return self._pos

    @property
    def index(self):
        return self._index

    @property
    def edgesAround(self):
        return self._edgesAround

    @property
    def facesAround(self):
        return self._facesAround


class Mesh(object):

    def __init__(self):

        self._dag = MDagPath()
        self._obj = MObject()

        self._startVert = None
        self._endVert = None
        self._itVert = None

        if not self.iterV.count() == 2:
            raise Exception("not correspondance")

        for i in range(2):

            util = MScriptUtil()
            prev = util.asIntPtr()

            self.iterV.setIndex(i, prev)

            if i == 0:
                self._startVert = Point(self.iterV)

            if i == 1:
                self._endVert = Point(self.iterV)

    @property
    def dag(self):

        sel = MSelectionList()

        MGlobal.getActiveSelectionList(sel)
        sel.getDagPath(0, self._dag, self._obj)

        return self._dag

    @property
    def iterV(self):

        sel = MSelectionList()

        MGlobal.getActiveSelectionList(sel)
        return MItMeshVertex(self.dag, self._obj)

    @property
    def obj(self):
        return self._obj

    @property
    def startVert(self):
        return self._startVert

    @property
    def endVert(self):
        return self._endVert

    @property
    def fn(self):
        return MFnMesh(self._dag)


class Face(object):

    def __init__(self):
        pass


class Rerout(object):

    def __init__(self):

        self.mesh = Mesh()
        self.analyse()

    def analyse(self):

        first = True
        vert = None  # -- Point()

        for i in self.mesh.startVert.edgesAround:

            # vert = next one
            if first:
                vert = self.mesh.startVert



            # first = False
            print ' v.{} -- edges:{} -- faces:{}'.format(vert.index,
                                                         vert.edgesAround,
                                                         vert.facesAround
                                                         )

# setPosition()

# reload(realignStraigth)
# import realignStraigth as r
# r.show()
