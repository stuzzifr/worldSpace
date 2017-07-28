from maya.OpenMaya import *
from maya.OpenMayaUI import *

import maya.cmds as cmds
import math
import pdb

db = pdb.set_trace


def reorderFaces(array, ind):

    ind = array.index(ind)

    sortArray = array[ind:]
    sortArray += array[0:ind]

    return sortArray[1:]

def reorderVertices(array, ind):

    array.reverse()

    ind = array.index(ind)

    print array, ind
    sortArray = array[ind:]
    sortArray += array[0:ind]

    return sortArray



class Point(object):

    def __init__(self, num):

        self._fn = MItMeshVertex(Mesh.dag())

        if num:
            self.setTo(num)

        self._edgesAround = MIntArray()
        self._facesAround = MIntArray()
        self._captial = -1
        self._config = -1

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

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def getCommute(self, face):
        # 2 common points but is not the anchor

        for i in face.facesAround:

            face = Face(i)
            if not self.index in face.vtx and face.nature == 'tri':
                face.isYang = True

            if self.index in face.vtx and face.nature == 'tri':
                face.isYang = False

            return face


    def getNextFace(self, mesh):

        # need to get the left index

        array = dict()

        lastFace = mesh.preFace
        faces = reorderFaces(self.facesAround, lastFace)

        i = 0
        while i < len(faces):

            face = Face(faces[i])
            # print '{} _ {}'.format(face.index, face.nature)

            if face.nature == 'quad':

                vtx = reorderVertices(face.vtx, self.index)
                poses = MPointArray()

                for v in vtx:
                    point = Point(v)
                    poses.append(point.pos)

                array.setdefault(faces[i], poses)


            if face.nature == 'tri':

                preFace = Face(lastFace)

                # preFaceSet = set(preFace.vtx)
                # thisFaceSet = set(face.vtx)

                # diff = thisFaceSet.difference(preFaceSet)

                poses = MPointArray()

                # -- ying and yang, share 2 common points but not the anchor
                # if len(diff) == 1 and not list(diff)[0] == self.index:


                faceYang = self.getCommute(face)

                vtxYing = reorderVertices(face.vtx, self.index)
                db()
                vtxYang = reorderVertices(faceYang.vtx, vtxYing[1])
                print 'aaaaa'

                vtx = vtxYing[0:2]
                vtx += vtxYang[1:3]

                for v in vtx:
                    point = Point(v)
                    poses.append(point.pos)

                if faceYang.isYang:
                    lastFace = faces[i]
                    array.setdefault(face.index, poses)

                if not faceYang.isYang:
                    lastFace = faces[i+1]
                    i+=2
                    array.setdefault(face.index, poses)

                    continue



                # # -- ying and ying
                # if len(diff) == 1 and self.index in :
                #     print 'iNT IT '
                #     faceYang = Face(faces[i]+1)

                #     vtxYing = reorderVertices(face.vtx, self.index)
                #     vtxYang = reorderVertices(faceYang.vtx, vtxYing[1])

                #     vtx = vtxYing[0:2]
                #     vtx += vtxYang[1:3]

                #     for v in vtx:
                #         point = Point(v)
                #         poses.append(point.pos)

                #     lastFace = faces[i]
                #     array.setdefault(faces[i], poses)
                #     i+= 2

                #     continue

            i+=1

        return array



    def getLeftFace(self, mesh):
        """ Description
        preface as int()
        """

        faces = reorderFaces(self.facesAround, mesh.preFace)
        lastFace = Face(faces[-1])
        outFace = -1


        if lastFace.nature == 'quad' and self.capital == 8:
            self.config = 'first'
            outFace = faces[-1]

        elif lastFace.nature == 'quad' and self.capital == 7:
            self.config = 'second'
            outFace = faces[-1]

        elif lastFace.nature == 'tri' and self.capital == 7:
            self.config = 'third'

            if mesh.turkish == 'third':
                outFace = faces[-2]
            else:
                outFace = faces[-1]

        elif lastFace.nature == 'tri' and self.capital == 8:
            self.config = 'fourth'
            other = Face(faces[-2])

            if other.nature == 'tri':
                outFace = faces[-3]

            if other.nature == 'quad':
                outFace = faces[-2]

        elif lastFace.nature == 'tri' and self.capital == 6:
            outFace = faces[-1]
            self.config = 'fifth'

        else:
            raise Exception('''cannot find this scenario
                index: %s
                nature: %s
                capital: %s''' % (self.index, lastFace.nature, self.capital))

        return outFace



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
    def isYang(self):
        return self._isYang

    @isYang.setter
    def isYang(self, value):
        self._isYang = value

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
    def facesAround(self):
        around = MIntArray()
        self.fn.getConnectedFaces(around)

        return [around[i] for i in range(around.length())]

    def setTo(self, num):

        util = MScriptUtil()
        prev = util.asIntPtr()

        self.fn.setIndex(num, prev)
        self.index = num


    def getLeftVtx(self, anchor):
        # -- vertice of the left, poly creation is anti CW

        sortedVtx = reorderFaces(self.vtx, anchor)
        return sortedVtx[-1]


class Mesh(object):

    def __init__(self):

        self._dag = MDagPath()
        self._obj = MObject()

        self._preVert = -1
        self._preFace = -1
        self._turkish = -1
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

    @property
    def turkish(self):
        return self._turkish

    @turkish.setter
    def turkish(self, value):
        self._turkish = value


class Rerout(object):

    def __init__(self):

        self.mesh = Mesh()
        self.mesh.way = 1  # -- need to determine the direction
        self.mesh.preFace = 22  # -- need to determine which face

        # self.analyse()
        self.analyse2()

    def analyse2(self):

        vert = self.mesh.startVert
        poses = MPointArray()

        toto = vert.getNextFace(self.mesh)


        mainGrp = cmds.createNode('transform', n='polys')
        for key, item in toto.items():
            grp = cmds.createNode('transform', n='poly_%d' % key)

            for i in xrange(item.length()):

                sph = cmds.sphere(n="face_%d_" % key,
                                  r=0.01,
                                  p=[item[i].x, item[i].y, item[i].z])

                cmds.parent(sph[0], grp)
            cmds.parent(grp, mainGrp)

        cmds.select(mainGrp, add=False)


    # def analyse(self):

    #     vert = self.mesh.startVert
    #     poses = MPointArray()

    #     for i in range(4):  # -- search distance

    #         leftFace = vert.getLeftFace(self.mesh)

    #         f = Face(leftFace)
    #         leftVtx = f.getLeftVtx(vert.index)

    #         self.mesh.turkish = vert.capital

    #         outString = 'v.{} -- leftFace:{}, -- leftVtx:{}\t -- cap:{} -- config:{}'
    #         print outString.format(vert.index,
    #                                leftFace,
    #                                leftVtx,
    #                                vert.capital,
    #                                vert.config
    #                                )

    #         self.mesh.preFace = leftFace
    #         vert = Point(leftVtx)
    #         poses.append(MPoint(vert.pos.x, vert.pos.y, vert.pos.z))




    #     cmds.createNode('transform', n='loc')
    #     for i in xrange(poses.length()):
    #         sph = cmds.sphere(p=(poses[i].x, poses[i].y, poses[i].z), n='sphe%d' % i, r=.02)
    #         cmds.parent(sph[0], 'loc')

    #     cmds.select('loc')
