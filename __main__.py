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

class MainW(QtGui.QMainWindow):
    def __init__(self, image=None):
        super(MainW, self).__init__()

        # Interpret image data as row-major
        pg.setConfigOptions(imageAxisOrder="row-major")
        self.setGeometry(50, 50, 1200, 1000)
        self.setWindowTitle("pyGUITrack")
        self.cp_path = os.path.dirname(os.path.realpath(__file__))

        self.cwidget = QtGui.QWidget(self)
        self.l0 = QtGui.QGridLayout()
        self.cwidget.setLayout(self.l0)
        self.setCentralWidget(self.cwidget)

        self.win = pg.GraphicsLayoutWidget()
        self.l0.addWidget(self.win, 0,3)

        self.vb=pgw.ModifiedViewBox(parent=self,lockAspect=True,enableMouse=True,border=[100, 100, 100])
        self.win.addItem(self.vb)
        # Item for displaying image data
        self.img = pg.ImageItem(viewbox=self.vb)
        self.vb.addItem(self.img)
        self.layer = pg.ImageItem(viewbox=self.vb)
        self.vb.addItem(self.layer)

        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.hist.setImageItem(self.img)
        self.win.addItem(self.hist)
        self.hist.vb.setMouseEnabled(y=False) # makes user interaction a little easier

        #set image to view
        data=np.random.randint(100,size=(1000,500),dtype=np.int8)
        data[300:500,200:250]=100
        self.img.setImage(data)
        self.hist.setLevels(data.min(), data.max())

        mask=np.zeros(data.shape)
        mask[20:50,100:200]=4
        mask[90:100,100:200]=7
        unique_indices=np.unique(mask)
        mask2=np.zeros_like(mask,dtype=np.int16)
        for j,i in enumerate(unique_indices):
            if i!=0: mask2[mask==i]=j

        self.colormap=(plt.get_cmap('gist_ncar')(np.linspace(0.0,.9,1000)) * 255).astype(np.uint8)
        self.colormap_random=np.concatenate([[[255,255,255,0]],self.colormap])
        self.colormap_random[1:,-1]=128
        self.layer.setImage(mask2,lut=self.colormap_random)

        self.win.show()
        self.show()


    def make_viewbox(self):
        self.p0 = guiparts.ViewBoxNoRightDrag(
            parent=self,
            lockAspect=True,
            name="plot1",
            border=[100, 100, 100],
            invertY=True
        )
        self.brush_size=3
        self.win.addItem(self.p0, 0, 0)
        self.p0.setMenuEnabled(False)
        self.p0.setMouseEnabled(x=True, y=True)
        self.img = pg.ImageItem(viewbox=self.p0, parent=self)
        self.layer = guiparts.ImageDraw(viewbox=self.p0, parent=self)
        self.layer.setLevels([0,255])
        self.scale = pg.ImageItem(viewbox=self.p0, parent=self)
        self.scale.setLevels([0,255])
        self.p0.scene().contextMenuItem = self.p0
        #self.p0.setMouseEnabled(x=False,y=False)
        self.Ly,self.Lx = 512,512
        self.p0.addItem(self.img)
        self.p0.addItem(self.layer)
        self.p0.addItem(self.scale)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window=MainW()
    sys.exit(app.exec_())