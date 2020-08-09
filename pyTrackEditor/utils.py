import numpy as np
import treelib

def make_random_colormap(cmap,number,alpha):
    colormap=np.array(cmap(np.linspace(0.0,.9,number-1)) * 255).astype(np.uint8)
    colormap_random=colormap.copy()
    np.random.shuffle(colormap_random)
    colormap_random=np.concatenate([[[255,255,255,0]],colormap_random])
    colormap_random[1:,-1]=alpha
    return colormap,colormap_random

def get_testdata(size=(10,1000,500)):
    data = np.random.randint(100, size=size, dtype=np.int8)
    data[300:500, 200:250] = 100

    mask = np.zeros(data.shape)
    mask[0,300:600, 100:200] = 4
    mask[0,700:900, 300:900] = 7
    mask[1:,100:600, 100:200] = 4
    mask[1:,200:900, 300:900] = 7
    unique_indices = np.unique(mask)
    mask2 = np.zeros_like(mask, dtype=np.int16)
    for j, i in enumerate(unique_indices):
        if i != 0: mask2[mask == i] = j
    return data,mask2

def tree_to_segments(tree,node):
    segment=[node.identifier]
    while True:
        children=tree.children(node.identifier)
        if len(children)==0:
            return segment,None
        elif len(children)==1:
            node=children[0]
            segment.append(node.identifier)
        else:
            return segment, [tree_to_segments(tree,c) for c in children]
        
def create_nodes(tree,segments,parent):
    for s in segments:
        k=s[0][0]
        tree.create_node(k,k,parent=parent)
        if not s[1] is None:
            create_nodes(tree,s[1],k)
            
def tree_to_segment_tree(tree,node):
    segments=tree_to_segments(tree,node)
    segment_tree=treelib.Tree()
    create_nodes(segment_tree,[segments],None)
    return segment_tree
    