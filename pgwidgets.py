from PyQt5 import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import functions as fn
from pyqtgraph import Point
import numpy as np

class ModifiedViewBox(pg.ViewBox):
    def __init__(self, parent=None, border=None, lockAspect=False, 
                 enableMouse=True, invertY=False, enableMenu=True, name=None, invertX=False):
        super().__init__(None, border, lockAspect, enableMouse, invertY, enableMenu, name, invertX)
        self.parent=parent


class ClickDrawableImageItem(pg.ImageItem):
    def __init__(self,image=None,
                 kernel=np.ones((3,3),dtype=np.bool),
                 color=[0,0,128,128],
                 close_threshold=3,
                 length_threshold=6,
                 end_draw_callback=None,
                 **kwargs):
        super().__init__(image,**kwargs)
        self.setDrawKernel(kernel=kernel,mode="set")
        self.setLookupTable([[0,0,0,0],color])
        self.close_threshold=close_threshold
        self.length_threshold=length_threshold
        self.end_draw_callback=end_draw_callback
        self.drawing=False
    
    def clear(self,shape):
        self.setImage(np.zeros(shape,dtype=np.bool))
        self.setLevels([0,1])

    def hoverEvent(self, event):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        event.acceptClicks(QtCore.Qt.RightButton)
        #XXX using mouseMoveEvent may be better, but I couldn't figure out how to call setMouseTracking...
        if self.drawing:
            self.poss.append([event.pos().x(),event.pos().y()])
            point_num=int(np.max(np.abs([self.poss[-2][i]-self.poss[-1][i] for i in range(2)])))+1
            for pos2 in np.linspace(self.poss[-2],self.poss[-1],point_num):
                self.drawAt(QtCore.QPoint(*pos2))
            if self.is_at_start_point(event.pos()):
                self.endDraw()
    
    def is_at_start_point(self,pos):
        poss=np.array(self.poss)
        dist=np.sqrt((poss[0,0]-pos.x())**2+(poss[0,1]-pos.y())**2)
        length=np.sum(np.sqrt((poss[1:,0]-poss[:-1,0])**2+(poss[1:,1]-poss[:-1,1])**2))
        return dist<self.close_threshold and length>self.length_threshold

    def mouseClickEvent(self, event):
        print("mouseclick")
        if event.button() & QtCore.Qt.RightButton:
            if self.drawing:
                self.endDraw()
            else:
                self.drawing=True
                self.poss=[]
                self.poss.append([event.pos().x(),event.pos().y()])
    
    def endDraw(self):
        self.drawing=False
        if not self.end_draw_callback is None:
            self.end_draw_callback(self.poss)