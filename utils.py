import numpy as np
def make_random_colormap(cmap,number,alpha):
    colormap=np.array(cmap(np.linspace(0.0,.9,1000)) * 255).astype(np.uint8)
    colormap_random=colormap.copy()
    np.random.shuffle(colormap_random)
    colormap_random=np.concatenate([[[255,255,255,0]],colormap_random])
    colormap_random[1:,-1]=alpha
    return colormap,colormap_random