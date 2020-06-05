"""
Demonstrates common image analysis tools.

Many of the features demonstrated here are already provided by the ImageView
widget, but here we present a lower-level approach that provides finer control
over the user interface.
"""
from pyqtgraph.Qt import QtGui
from .utils import get_testdata

from MaskEditor import MaskEditor

class PyTrackGUI(MaskEditor):
    def __init__(self):
        super(PyTrackGUI, self).__init__()

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window=MaskEditor()
    data,mask2=get_testdata()
    window.set_images(data)
    window.set_masks(mask2)
    window.update_image()
    window.update_mask()
    sys.exit(app.exec_())
