import numpy as np
def make_random_colormap(cmap,number,alpha):
    colormap=(cmap(np.linspace(0.0,.9,1000)) * 255).astype(np.uint8)
    colormap_random=np.concatenate([[[255,255,255,0]],colormap])
    colormap_random[1:,-1]=alpha
    return colormap,colormap_random