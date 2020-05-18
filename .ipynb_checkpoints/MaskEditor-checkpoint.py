import os
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
from . import pgwidgets as pgw
from matplotlib import pyplot as plt
from .utils import make_random_colormap,get_testdata
from skimage import draw,io,segmentation



class MaskEditor(QtGui.QMainWindow):
    def __init__(self, image=None):
        super(MaskEditor, self).__init__()

        self.cp_path = os.path.dirname(os.path.realpath(__file__))
        self.mask_max=100000
        self.colormap,self.mask_lut=make_random_colormap(plt.cm.gist_ncar,self.mask_max,128)
        self.t_index=0
        self.mask_alpha=100
        self.imgarray=None
        self.maskarray=None
        self.maskarray_boundary=None

        self.img=None
        self.maskimg=None
        self.mask_boundary=None
        self.draw=None
        self.vb=None
        self.tslider=None
        
        self.initUI()
        self.update_image()
        self.update_mask()
        self.win.show()
        self.show()

    def initUI(self):
        self.setGeometry(50, 50, 1200, 1000)
        self.setWindowTitle("maskEdit")
        self.cwidget = QtGui.QWidget(self)
        self.setCentralWidget(self.cwidget)
        self.l0 = QtGui.QHBoxLayout()
        self.cwidget.setLayout(self.l0)

        self.lleft = QtGui.QFormLayout()
        self.lright = QtGui.QVBoxLayout()
        self.l0.addLayout(self.lleft,stretch=0)
        self.l0.addLayout(self.lright,stretch=1)

        self.initControls(self.lleft)
        self.initImageItems(self.lright)

        self.tslider=QtGui.QSlider(QtCore.Qt.Horizontal,self)
        self.lright.addWidget(self.tslider)
        self.tslider.valueChanged.connect(self.change_t)

        self.initMenu()

    def initControls(self,layout):
        self.alphaslider=QtGui.QSlider(QtCore.Qt.Horizontal,self)
        layout.addRow(QtGui.QLabel("mask alpha"),self.alphaslider)
        self.alphaslider.valueChanged.connect(self.change_alpha)
        self.alphaslider.setValue(self.mask_alpha)
        
        self.maskcheckbox=QtGui.QCheckBox()
        layout.addRow(QtGui.QLabel("display mask"),self.maskcheckbox)
        self.maskcheckbox.stateChanged.connect(self.switch_mask)
        self.maskcheckbox.setChecked(True)
        
        self.boundarycheckbox=QtGui.QCheckBox()
        layout.addRow(QtGui.QLabel("display boundary"),self.boundarycheckbox)
        self.boundarycheckbox.stateChanged.connect(self.switch_boundary)
        self.boundarycheckbox.setChecked(True)

    def initImageItems(self,layout):
        self.win = pg.GraphicsLayoutWidget()
        layout.addWidget(self.win,1)
        self.win.scene().sigMouseClicked.connect(self.plotClicked)

        self.vb=pgw.ModifiedViewBox(parent=self,lockAspect=True,
                                    invertY=True,enableMenu=False,
                                    enableMouse=True,border=[100, 100, 100])
        self.win.addItem(self.vb)
        # Item for displaying image data
        self.img = pg.ImageItem(viewbox=self.vb)
        self.img.setZValue(100)
        self.vb.addItem(self.img)
        self.maskimg = pg.ImageItem(viewbox=self.vb)
        self.maskimg.setZValue(101)
        self.vb.addItem(self.maskimg)
        self.mask_boundary = pg.ImageItem(viewbox=self.vb)
        self.mask_boundary.setZValue(102)
        self.vb.addItem(self.mask_boundary)
        self.draw = pgw.ClickDrawableImageItem(viewbox=self.vb,
                            end_draw_callback=self.draw_completed)
        self.draw.setZValue(103)
        self.vb.addItem(self.draw)

        # Contrast/color control
        self.hist = pg.HistogramLUTItem()
        self.win.addItem(self.hist)
        self.hist.vb.setMouseEnabled(y=False)
        self.hist.setImageItem(self.img)

    def initMenu(self):
        openImageAction=QtGui.QAction("&Open Image",self)
        openImageAction.setShortcut("Ctrl+O")
        openImageAction.setStatusTip("Open image (T x X x Y tiff)")
        openImageAction.triggered.connect(self.openImage)

        openMaskAction=QtGui.QAction("&Open Mask",self)
        openMaskAction.setShortcut("Ctrl+Shift+O")
        openMaskAction.setStatusTip("Open mask (T x X x Y tiff)")
        openMaskAction.triggered.connect(self.openMask)

        saveMaskAction=QtGui.QAction("&Save Mask",self)
        saveMaskAction.setShortcut("Ctrl+S")
        saveMaskAction.setStatusTip("Save mask to TIFF")
        saveMaskAction.triggered.connect(self.saveMask)

        menubar=self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openImageAction)
        fileMenu.addAction(openMaskAction)
        fileMenu.addAction(saveMaskAction)

    def openImage(self):
        fname = pg.FileDialog.getOpenFileName(self, 'Open image TIFF','',"Tiff Image file (*.tiff)")
        if fname[0]!="":
            imgs=io.imread(fname[0])
            try:
                self.set_images(imgs)
                self.img_fname=fname[0]
            except Exception as e:
                raise e 
            self.update_image()
            self.clear_masks()
            self.update_mask()

    def openMask(self):
        fname = pg.FileDialog.getOpenFileName(self, 'Open mask TIFF','',"Tiff Mask file (*.tiff)")
        if fname[0]!="":
            masks=io.imread(fname[0])
            try:
                self.set_masks(masks)
                self.mask_fname=fname[0]
            except Exception as e:
                raise e
            self.update_mask()

    def saveMask(self):
        if hasattr(self,"img_fname") and not self.maskarray is None:
            maskname=os.path.splitext(self.img_fname)[0]+"_masks.tif"
            io.imsave(maskname,self.maskarray)

    def maskDeleteEnabled(self):
        return True
    
    def change_t(self,event):
        self.t_index=self.tslider.value()
        self.draw.endDraw()
        self.update_image()
        self.update_mask()

    def change_alpha(self,event):
        self.mask_alpha=self.alphaslider.value()
        self.update_mask()

    def switch_mask(self):
        if hasattr(self,"vb") and not self.maskimg is None:
            if self.maskcheckbox.isChecked():
                self.vb.addItem(self.maskimg)
            else:
                self.vb.removeItem(self.maskimg)

    def switch_boundary(self):
        print("boundary toggle")
        if hasattr(self,"vb") and not self.mask_boundary is None:
            if self.boundarycheckbox.isChecked():
                print("boundary toggle")
                self.vb.addItem(self.mask_boundary)
            else:
                self.vb.removeItem(self.mask_boundary)

    def getClickedLabel(self,pos):
        try: 
            pos=self.vb.mapSceneToView(pos)
        except AttributeError:
            return
        ix=np.round(pos.x()).astype(np.int)
        iy=np.round(pos.y()).astype(np.int)
        ix,iy=self.convertPos(ix,iy)
        print(ix,iy)
        if 0 <= ix and ix < self.maskarray.shape[1] \
           and 0 <= iy and iy < self.maskarray.shape[2] :
            return self.maskarray[self.t_index,ix,iy]
        else:
            return None
    
    def plotClicked(self,event):
        if event.button()==QtCore.Qt.LeftButton:
            if (self.maskcheckbox.isChecked()\
                or self.boundarycheckbox.isChecked()):
                try: 
                    ind=self.getClickedLabel(event.pos())
                except AttributeError:
                    return
                if not ind is None and ind>0:
                    if self.maskDeleteEnabled() \
                        and event.modifiers() == QtCore.Qt.ControlModifier:
                        self.maskarray[self.t_index,self.maskarray[self.t_index,:,:]==ind]=0
                        #self.update_mask_boundary(self.t_index)
                        self.update_mask()
                    else:
                        print(ind)
    
    def draw_completed(self,poss):
        poss=np.array(poss)
        polyr,polyc=draw.polygon(poss[:,0],poss[:,1],shape=self.maskarray.shape[1:])
        existing_inds=np.unique(self.maskarray[self.t_index])
        existing_inds=existing_inds[existing_inds!=0]
        new_ind=next(i for i,e in enumerate(sorted(existing_inds)+[None],1) if i!=e)
        print(existing_inds,new_ind)
        temporary_mask=np.zeros_like(self.maskarray[self.t_index],dtype=np.bool)
        temporary_mask[self.roi[0][0]:self.roi[0][1],
                       self.roi[1][0]:self.roi[1][1]][polyr,polyc]=True
        self.maskarray[self.t_index][np.logical_and(temporary_mask,self.maskarray[self.t_index]==0)]=new_ind
        #self.update_mask_boundary(self.t_index)
        self.update_mask()

    def setViewRoi(self,roi=None):
        if roi is None:
            if not self.imgarray is None:
                self.roi=[[0,self.imgarray.shape[1]],
                          [0,self.imgarray.shape[2]]]
        else:
            self.roi=roi
        print(self.roi)

    def convertPos(self,ix,iy):
        return ix+self.roi[0][0],iy+self.roi[1][0]
        
    def set_images(self,imgs):
        if imgs.ndim==2:
            self.imgarray=imgs[np.nexaxis,:,:]
        if imgs.ndim==3:
            self.imgarray=imgs
        else:
            raise NotImplementedError("currently supported image dimension is 2 or 3")
        self.t_index_max=imgs.shape[0]-1
        self.tslider.setTickInterval(1)
        self.tslider.setMinimum(0)
        self.tslider.setMaximum(self.t_index_max)
        self.setViewRoi()

    def set_masks(self,masks):
        if masks.ndim==2:
            self.maskarray=masks[np.nexaxis,:,:]
        if masks.ndim==3:
            self.maskarray=masks
        assert not self.imgarray is None
        assert all(np.array(self.imgarray.shape)==np.array(masks.shape))
        self.maskarray=masks
        #self.update_mask_boundary()

#    def update_mask_boundary(self,t_index=None):
#        if self.maskarray_boundary is None:
#            self.maskarray_boundary=np.zeros_like(self.maskarray,dtype=np.bool)
#        if t_index is None:
#            self.maskarray_boundary=np.array([segmentation.find_boundaries(self.maskarray[ti],mode="inner")\
#                                          for ti in range(self.t_index_max+1)])
#        else:
#            self.maskarray_boundary[t_index]=segmentation.find_boundaries(self.maskarray[t_index],mode="inner")

    def clear_masks(self):
        if not self.imgarray is None:
            self.maskarray=np.zeros_like(self.imgarray,dtype=np.uint16)
            self.maskarray_boundary=np.zeros_like(self.maskarray,dtype=np.bool)

    def update_image(self,adjust_hist=False):
        if not self.imgarray is None:
            subarray=self.imgarray[self.t_index,
                                   self.roi[0][0]:self.roi[0][1],
                                   self.roi[1][0]:self.roi[1][1]]
            self.img.setImage(subarray,
                              autoLevels=False)
            if adjust_hist:
                self.hist.setLevels(subarray.min(), subarray.max())
    
    def get_mask_lut_applied(self,lut):
        return lut[self.maskarray[self.t_index,
                                  self.roi[0][0]:self.roi[0][1],
                                  self.roi[1][0]:self.roi[1][1]],:]
                
    def update_mask(self,modify_lut=lambda lut:None):
        if not self.maskarray is None:
            self.mask_lut[1:,3]=self.mask_alpha
            lut=self.mask_lut.copy()
            lut=modify_lut(lut)
            #XXX Not the optimal but levels are force set in pyqtgraph makeARGB ... 
            #according to the source code,
            self.maskimg.setImage(self.get_mask_lut_applied(lut),autoDownsample=False)
            
            self.mask_boundary.setImage(segmentation.find_boundaries(
                self.maskarray[self.t_index,
                               self.roi[0][0]:self.roi[0][1],
                               self.roi[1][0]:self.roi[1][1]]),mode="inner")
            self.mask_boundary.setLookupTable([[0,0,0,0],[255,255,255,255]])
            self.mask_boundary.setLevels((0,1))
            self.draw.clear(self.maskarray[self.t_index,
                                           self.roi[0][0]:self.roi[0][1],
                                           self.roi[1][0]:self.roi[1][1]].shape)
    
    def keyPressEvent(self,event):
        if (event.modifiers() != QtCore.Qt.ControlModifier and
            event.modifiers() != QtCore.Qt.ShiftModifier and
                event.modifiers() != QtCore.Qt.AltModifier) and not self.draw.drawing:
            if event.key() == QtCore.Qt.Key_Left:
                if self.t_index>0:
                    self.t_index=self.t_index-1 
                    self.tslider.setValue(self.t_index) 
                    self.update_image() 
                    self.update_mask()
            elif event.key() == QtCore.Qt.Key_Right:
                if self.t_index<self.t_index_max:
                    self.t_index=self.t_index+1
                    self.tslider.setValue(self.t_index)
                    self.update_image()
                    self.update_mask()