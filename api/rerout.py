from maya.OpenMaya import *



class Rer(object):

    _firstP = MI
    _secondP
    def __init__(self):

        self.

    @property
    def firstP(self):
        return self._firstP

    def



        obj = MObject()
        dag = MDagPath()

        sel = MSelectionList()
        sel.add('rerout1')
        sel.getDagPath(0, dag, obj)

        fnComp = MFnSingleIndexedComponent()
        fnComp.create(MFn.kMeshVertComponent)
        for ind in [21,62]:
            fnComp.addElement(ind)

        iter = MItGeometry(dag, obj)
        while not iter.isDone():
            print iter.index()
            iter.next()


            /swiss/project/VOLVO_43X_3703/shots/brosarp_010/maya/cache/alembic