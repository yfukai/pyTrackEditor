"""
Demonstrates common image analysis tools.

Many of the features demonstrated here are already provided by the ImageView
widget, but here we present a lower-level approach that provides finer control
over the user interface.
"""
from pyqtgraph.Qt import QtGui
if not __package__ is None:
    from .utils import get_testdata
    from .MaskEditor import MaskEditor
else:
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
    from pyTrackEditor.utils import get_testdata
    from pyTrackEditor.MaskEditor import MaskEditor

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
