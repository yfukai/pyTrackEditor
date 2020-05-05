"""
Demonstrates common image analysis tools.

Many of the features demonstrated here are already provided by the ImageView
widget, but here we present a lower-level approach that provides finer control
over the user interface.
"""

import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pgwidgets as pgw
from matplotlib import pyplot as plt
from utils import make_random_colormap
class MainW(QtGui.QMainWindow):
    def __init__(self, image=None):
        super(MainW, self).__init__()

        # Interpret image data as row-major
        #pg.setConfigOptions(imageAxisOrder="row-major")
        self.setGeometry(50, 50, 1200, 1000)
        self.setWindowTitle("pyGUITrack")
        self.cp_path = os.path.dirname(os.path.realpath(__file__))

        self.colormap,self.colormap_random=make_random_colormap(plt.cm.gist_ncar,1000,128)

        self.cwidget = QtGui.QWidget(self)
        self.l0 = QtGui.QGridLayout()
        self.cwidget.setLayout(self.l0)
        self.setCentralWidget(self.cwidget)

        self.win = pg.GraphicsLayoutWidget()
        self.win.setMouseTracking(True)
        self.l0.addWidget(self.win, 0,3)

        self.vb=pgw.ModifiedViewBox(parent=self,lockAspect=True,invertY=True,enableMenu=False,enableMouse=True,border=[100, 100, 100])
        self.win.addItem(self.vb)
        # Item for displaying image data
        self.img = pg.ImageItem(viewbox=self.vb)
        self.vb.addItem(self.img)
        self.mask = pg.ImageItem(viewbox=self.vb)
        self.vb.addItem(self.mask)
        self.draw = pgw.ClickDrawableImageItem(viewbox=self.vb,
                            end_draw_callback=lambda poss : print("poss:",poss))
#        self.draw.setLookupTable(np.array([[0,0,0,0],[255,0,0,255]]))
        self.vb.addItem(self.draw)

        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.win.addItem(self.hist)
        self.hist.vb.setMouseEnabled(y=False) # makes user interaction a little easier
        self.hist.setImageItem(self.img)

#        self.win.scene().sigMouseClicked.connect(lambda : print("ccckucj"))
        self.mask.setLookupTable(self.colormap_random)
        self.update_image()
        self.update_mask()
        self.win.show()
        self.show()

    def set_images(self,imgs):
        assert imgs.ndim==3
        self.imgarray=imgs
    def set_masks(self,masks):
        assert masks.ndim==3
        self.maskarray=masks

    def update_image(self,i=0,adjust_hist=True):
        if hasattr(self,"imgarray"):
            self.img.setImage(self.imgarray[i])
            if adjust_hist:
                self.hist.setLevels(self.imgarray.min(), self.imgarray.max())
    def update_mask(self,i=0):
        if hasattr(self,"maskarray"):
            self.mask.setImage(self.maskarray[i])
            self.draw.clear(self.maskarray[i].shape)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    data = np.random.randint(100, size=(10,1000, 500), dtype=np.int8)
    data[300:500, 200:250] = 100

    mask = np.zeros(data.shape)
    mask[0,300:600, 100:200] = 4
    mask[0,700:900, 300:900] = 7
    unique_indices = np.unique(mask)
    mask2 = np.zeros_like(mask, dtype=np.int16)
    for j, i in enumerate(unique_indices):
        if i != 0: mask2[mask == i] = j
    app = QtGui.QApplication(sys.argv)
    window=MainW()
    window.set_images(data)
    window.set_masks(mask2)
    window.update_image()
    window.update_mask()
    sys.exit(app.exec_())
