from utility.FloatTensor import *

def palette(name,device='cuda:0'):
    color = {'fire' : FloatTensor([[0.533333,0.000000,0.082353],
                                   [0.929412,0.109804,0.141176],
                                   [1.000000,0.498039,0.152941],
                                   [1.000000,0.788235,0.054902],
                                   [1.000000,0.949020,0.000000],
                                   [0.937255,0.894118,0.690196],
                                   [1.000000,1.000000,1.000000]],device=device),
             'black' : FloatTensor([[0,0,0],[1,1,1]],device=device),
             'red'   : FloatTensor([[1,0,0],[1,1,1]],device=device),
             'sign'  : FloatTensor([[0.019608,0.443137,0.690196],
                                    [0.572549,0.772549,0.870588],
                                    [0.968627,0.968627,0.968627],
                                    [0.956863,0.647059,0.509804],
                                    [0.792157,0.000000,0.125490]],device=device),
             'cinolib' : FloatTensor([[0.992157,0.407843,0.462745],
                                      [0.992157,0.529412,0.337255],
                                      [0.996078,0.898039,0.615686],
                                      [0.776471,0.874510,0.713725],
                                      [0.301961,0.756863,0.776471],
                                      [0.713725,0.784314,0.901961],
                                      [0.486275,0.619608,0.984314],
                                      [0.988235,0.349020,0.580392]],device=device),
            }
    return color[name]
