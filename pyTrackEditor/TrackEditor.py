import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from ast import literal_eval as make_tuple
from .utils import get_testdata, tree_to_segments

from . import MaskEditor
import h5py
import copy
import pandas as pd
import numpy as np
from skimage import measure

def _label_to_tuple(l):
    return 
def _tuple_to_label(t):
    return 

class TrackEditor(MaskEditor.MaskEditor):
    def __init__(self,roiSize=250,default_dir=None):
        self.show_all_masks=False
        self.total_tree=None
        self.drawn_segments=pd.DataFrame()
        self.waiting=[]
        self.segment=None
        self.final_states=None
        self.state="visualize"
        self.default_dir=default_dir
        super().__init__()
        self.draw.drawEnabled=False
        self.roiSize=roiSize
        
    def initControls(self,layout):
        super()._initControls(layout)
        self.modifybutton=QtGui.QPushButton("Modify Track (M)",self)
        layout.addRow(self.modifybutton)
        self.modifybutton.clicked.connect(self.modifyStart)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence("M"), self)
        shortcut.activated.connect(self.modifyStart)
        shortcut.setEnabled(True)
        
        self.terminatebutton=QtGui.QPushButton("Terminate Track (T)",self)
        layout.addRow(self.terminatebutton)
        self.terminatebutton.clicked.connect(self.terminate)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence("T"), self)
        shortcut.activated.connect(self.terminate)
        shortcut.setEnabled(True)
        
        self.finalizebutton=QtGui.QPushButton("Finalize (F)",self)
        layout.addRow(self.finalizebutton)
        self.finalizebutton.clicked.connect(self.finalize)
        shortcut = QtGui.QShortcut(QtGui.QKeySequence("F"), self)
        shortcut.activated.connect(self.finalize)
        shortcut.setEnabled(True)
        
        self.currentlabel=QtGui.QLabel("",self)
        layout.addRow(self.currentlabel)
    
    def initMenu(self):
        saveAction=QtGui.QAction("&Save Tracking Data",self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.setStatusTip("Save tracking data to HDF5")
        saveAction.triggered.connect(self.saveTracking)
        menubar=self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)
        
    def modifyStart(self):
        if self.t_index>max(self.segment.index)+1:
            print("modification not possible")
            return
        self.state="modify"
        self._t_slider.setEnabled(False)
        self.candidates=set()
        self.draw.drawEnabled=True
        
    def modifyEnd(self):
        t=self.t_index
        if "frame" in self.drawn_segments.columns:
            drawn=self.drawn_segments[(self.drawn_segments["frame"]==t)&
                                  (self.drawn_segments["label"].isin(list(self.candidates)))]
        else:
            drawn=[]
        if len(drawn)==0:
            if len(self.candidates)==1:
                cand=list(self.candidates)[0]
                self.segment=self.segment[self.segment.index<t]
                k=str((t,cand))            
                if k in self.total_tree:
                    segment,self.final_states=self.get_segment_df_and_final(k)
                    self.segment=self.segment.append(segment)
                else:
                    self.segment.loc[t]={"label":cand}
                    self.final_states="terminated"
            if len(self.candidates)==2:
                self.segment=self.segment[self.segment.index<t]
                self.final_states=[(t,cand) for cand in self.candidates]
            elif len(self.candidates)>2:
                print("selected number must be less than 3")
        else:
            print("cell already tracked")
        self.state="visualize"
        self._t_slider.setEnabled(True)
        self.draw.drawEnabled=False
        self.update_image()
        self.update_mask()
        
    def terminate(self):
        t=self.t_index
        if self.t_index>max(self.segment.index):
            print("termination not possible")
            return
        text, ok = QtGui.QInputDialog.getText(self, 'terminate segment', 'enter terminate annotation:')
        if ok:
            self.segment=self.segment[self.segment.index<=t]
            self.final_states=text
    
    def finalize(self):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        df=self.segment.copy()
        df=df.reset_index()
        row=df.sort_values("frame").iloc[0]
        df["track_id"]=str((row["frame"],row["label"]))
        df["final_states"]=[copy.copy(self.final_states)]*len(df)
        self.drawn_segments=self.drawn_segments.append(df,ignore_index=True)
        if isinstance(self.final_states,list):
            self.waiting.extend([str(k) for k in self.final_states])
        self.initiate_tracking()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
    
    def keyPressEvent(self,event):
        if self.state=="visualize":
            super().keyPressEvent(event)
        elif self.state=="modify":
            if (event.modifiers() != QtCore.Qt.ControlModifier and
                event.modifiers() != QtCore.Qt.ShiftModifier and
                event.modifiers() != QtCore.Qt.AltModifier): 
                if event.key() == QtCore.Qt.EnterKeyDefault or \
                   event.key() == QtCore.Qt.Key_Return:
                    self.modifyEnd()
        else:
            raise RuntimeError("wrong state")
        
        if event.modifiers() == QtCore.Qt.ShiftModifier:
            if event.key() == QtCore.Qt.Key_Right:
                shift=min(self.roi[0][1]+10,self._imgarray.shape[1])-self.roi[0][1]
                self.roi[0][0]+=shift
                self.roi[0][1]+=shift
                super().update_image()
                self.update_mask()
            if event.key() == QtCore.Qt.Key_Left:
                shift=self.roi[0][0]-max(self.roi[0][0]-10,0)
                self.roi[0][0]-=shift
                self.roi[0][1]-=shift
                super().update_image()
                self.update_mask()
            if event.key() == QtCore.Qt.Key_Up:
                shift=self.roi[1][0]-max(self.roi[1][0]-10,0)
                self.roi[1][0]-=shift
                self.roi[1][1]-=shift
                super().update_image()
                self.update_mask()
            if event.key() == QtCore.Qt.Key_Down:
                shift=min(self.roi[1][1]+10,self._imgarray.shape[2])-self.roi[1][1]
                self.roi[1][0]+=shift
                self.roi[1][1]+=shift
                super().update_image()
                self.update_mask()
        
    def plotClicked(self,event):
        if self.state=="visualize":
            super().plotClicked(event)
        elif self.state=="modify":
            if event.button()==QtCore.Qt.LeftButton \
                and event.modifiers() != QtCore.Qt.ControlModifier:
                ind=super().getClickedLabel(event.pos())
                if ind>0:
                    if ind in self.candidates:
                        self.candidates.remove(ind)
                    else:
                        self.candidates.add(ind)
                    self.update_mask()
                    print(self.candidates)
            else:
                super().plotClicked(event)
            
    def update_mask(self):
        in_index=None
        if not self.maskarray is None:
            if not self.show_all_masks:
                visible=self.get_visible_index(self.t_index)
                in_index=np.isin(np.arange(self._mask_max),visible)
                def modify_lut(lut):
                    lut[np.logical_not(in_index),3]=0
                    if "frame" in self.drawn_segments.columns:
                        tracked=self.drawn_segments[self.drawn_segments["frame"]==self.t_index]["label"].values
                        lut[tracked,:3]=128
                        lut[tracked,3]=200
                    if self.state=="modify":
                        lut[list(self.candidates),3]=128
                        lut[list(self.candidates),:3]=255
                    return lut
            else:
                def modify_lut(lut):
                    return lut
            super().update_mask(modify_lut=modify_lut)
        
    def set_lineage_tree(self,total_tree):
        self.total_tree=total_tree

    def initiate_tracking(self,node_id=None):
        if not node_id is None:
            self.set_root_node(node_id)
        else:
            if len(self.waiting)>0:
                node_id=self.waiting.pop(0)
                self.set_root_node(node_id)
            else:
                first_cells=self.total_tree.children(self.total_tree.root)
                already_drawn=self.drawn_segments["track_id"] \
                                if "track_id" in self.drawn_segments.columns else []
                first_cells=[n.identifier for n in first_cells 
                             if make_tuple(n.identifier)[0]==0 and 
                             not n.identifier in already_drawn]
                node_id=np.random.choice(first_cells)
                self.set_root_node(node_id)
    
    def get_segment_df_and_final(self,node_id):
        if node_id in self.total_tree:
            st=tree_to_segments(self.total_tree,self.total_tree[node_id])
        else:
            st=[[node_id],None]
        segment=pd.DataFrame({
            "frame":[make_tuple(s)[0] for s in st[0]],
            "label":[make_tuple(s)[1] for s in st[0]]})
        segment=segment.set_index("frame")
        assert len(segment)==len(st[0])
        if not st[1] is None:
            final_states=[(make_tuple(c[0][0])[0],
                           make_tuple(c[0][0])[1]) for c in st[1]]
        else:
            final_states="terminated"
        return segment,final_states

    def set_root_node(self,node_id):
        self.currentlabel.setText(node_id+\
                                  "\n totally checked"+\
                                  str(len(self.drawn_segments[self.drawn_segments["frame"]==0]) 
                                      if "frame" in self.drawn_segments.columns else 0))
        
        self.segment,self.final_states=self.get_segment_df_and_final(node_id)
        t=make_tuple(node_id)[0]
        ind=make_tuple(node_id)[1]
        self.t_index=t
        self._t_slider.setValue(t)
        ind_mask=self.maskarray[self.t_index]==ind
        if np.any(ind_mask):
            M=measure.moments(ind_mask)
            pos=(int(M[1,0]/M[0,0]), int(M[0,1]/M[0,0]))
            self.setViewRoi([[max(0,pos[0]-self.roiSize),
                              min(self._imgarray.shape[1],pos[0]+self.roiSize)],
                             [max(0,pos[1]-self.roiSize),
                              min(self._imgarray.shape[2],pos[1]+self.roiSize)]])

        self.update_image()
        self.update_mask()
        
    def get_visible_index(self,t):
        if not self.segment is None:
            cell_indices=[]
            if t in self.segment.index:
                cell_indices.append(self.segment.loc[t,"label"])
            return cell_indices+[c[1] for c in self.final_states if c[0]==t]
        else:
            return None

    def maskDeleteEnabled(self):
        return self.state=="modify"
    
    def saveTracking(self,file_name=None,attrs={}):
        print("save tracking...",file_name)
        if not file_name:
            file_name,_=pg.FileDialog.getSaveFileName(self, 'save HDF5 path', self.default_dir, 
                                            initialFilter='*.hdf5')
        print("save tracking...",file_name)
        if file_name:
            assert not any(self.drawn_segments.duplicated(["frame","label"]))
            with h5py.File(file_name,"a") as f:
                if "mask_array" in f: del f["mask_array"]
                f["mask_array"]=self.maskarray
                for k,v in attrs.items():
                    f.attrs[k]=v
                if "waiting" in f: del f["waiting"]
                f["waiting"]=np.array(self.waiting,dtype=h5py.special_dtype(vlen=str))
            self.drawn_segments.to_hdf(file_name,"drawn_segments")
        print("save finished")

    def loadTracking(self,file_name):
        with h5py.File(file_name,"r") as f:
            self.maskarray=np.array(f["mask_array"])
            self.waiting=list(np.array(f["waiting"]))
        self.drawn_segments=pd.read_hdf(file_name,"drawn_segments")
        children_set=list(set(sum([f for f in self.drawn_segments["final_states"] 
                  if isinstance(f,list)],[])))
        waiting=[str(c) for c in children_set if not any((self.drawn_segments["frame"]==c[0])
                                                   &(self.drawn_segments["label"]==c[1]))]
        self.waiting=self.waiting+waiting
        assert not any(self.drawn_segments.duplicated(["frame","label"]))