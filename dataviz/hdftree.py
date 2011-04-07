# hdftree.py --- 
# 
# Filename: hdftree.py
# Description: 
# Author: Subhasis Ray
# Maintainer: 
# Copyright (C) 2010 Subhasis Ray, all rights reserved.
# Created: Fri Mar  4 17:54:30 2011 (+0530)
# Version: 
# Last-Updated: Thu Apr  7 18:06:48 2011 (+0530)
#           By: Subhasis Ray
#     Update #: 185
# URL: 
# Keywords: 
# Compatibility: 
# 
# 

# Commentary: 
# 
# 
# 
# 

# Change log:
# 
# 
# 

# Code:

import sys
import os
import re
import h5py
from PyQt4 import Qt, QtCore, QtGui

class H5TreeWidgetItem(QtGui.QTreeWidgetItem):
    def __init__(self, parent, h5node):
        QtGui.QTreeWidgetItem.__init__(self, parent)
        self.h5node = h5node
        if isinstance(h5node, h5py.File):
            self.setText(0, QtCore.QString(h5node.filename))
        else:
            self.setText(0, QtCore.QString(h5node))

    # def childCount(self):
    #     ret = 0
    #     if isinstance(self.h5node, h5py.Group):
    #         ret = len(self.h5node)
    #     print self.text(0), type(self.h5node), 'childCount =', ret
    #     return ret

    # def hasChildren(self, index):
    #     ret = (len(self.h5node) > 0)
    #     print ret
    #     return ret
    
    # def index(self):
    #     print 'here'
    #     QtCore.qDebug('Here')

    def path(self):        
        path = str(self.data(0, Qt.Qt.DisplayRole).toString())
        parent = self.parent()
        root = self.treeWidget().invisibleRootItem()
        while parent is not None:
            path = str(parent.data(0, Qt.Qt.DisplayRole).toString()) + "/" + path
            parent = parent.parent()
        return str(path)

class H5TreeWidget(QtGui.QTreeWidget):
    def __init__(self, *args):
        QtGui.QTreeWidget.__init__(self, *args)
        self.fhandles = {}
        
    def addH5Handle(self, filename):
        if not filename.startswith('/'):
            filename = os.path.abspath(filename)
        if not filename in self.fhandles.keys():
            file_handle = h5py.File(filename, 'r')
            self.fhandles[filename] = file_handle
            item = H5TreeWidgetItem(self, file_handle)
            self.addTopLevelItem(item)
            item.setText(0, QtCore.QString(filename))
            self.addTree(item, file_handle)
            
    def addTree(self, currentItem, node):
        if isinstance(node, h5py.Group) or isinstance(node, h5py.File):
            for child in node:
                # print '## ', child, type(child)
                item = H5TreeWidgetItem(currentItem, child)
                self.addTree(item, node[child])

    def getData(self, path):
        path = str(path)
        filename = None
        h5f = None
        for key, value in self.fhandles.items():
            if path.startswith(key):
                filename = key
                path = path[len(filename):] # 1 for '/'
                h5f = value
                break
        if filename is None:
            raise Exception('No open file for path: %s', path)
        node = h5f[path]
        if isinstance(node, h5py.Dataset):
            return node

    # I have a little problem here - how do we find nodes by regular
    # expression for arbitrary file structure?
    #
    # This is not trivial to solve and will need writing a dfa in
    # python. Looks like an overkill.
    
    def getDataByRe(self, pattern):
        """Select data items based on pattern.

        Currently this will do just a regular expression match. It
        checks through all the currently selected files.

        """
        regex = re.compile(pattern)
        ret = {}
        for item in self.selectedItems():
            current = item
            parent = current.parent()
            while parent != self.invisibleRootItem():
                current = parent
            filename = str(current.text())
            filehandle = self.fhandles(filename)
            # It's 5 PM and I feel too lazy to implement a regex
            # matcher. So using old policy of letting the user(me) do
            # the work.
            path = current.path()[len(filename)+1:]
            current_node = filehandle[path]
            paths = []
            current_node.visit(paths.append)
            for path in paths:
                if regex.match(path):
                    ret[filename+path] = current_node[path]
        return ret
                
            
            


    def __del__(self):
        for filename, fhandle in self.fhandles.items():
            fhandle.close()
            
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.qApp = app
    # mainwin = DataVizGui()
    mainwin = QtGui.QMainWindow()
    tree = H5TreeWidget(mainwin)    
    tree.addH5Handle('../py/data/data_20110215_112900_1335.h5')
    mainwin.setCentralWidget(tree)
    mainwin.show()
    app.exec_()
                


# 
# hdftree.py ends here
