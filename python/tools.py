"""
Created:         1 September 2016
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University
-----

Simple functions to help with plotting & accessing data
"""
import numpy as np


def midpoints(data):
    """Return the midpoint of bins given the bin edges"""
    return 0.5*(data[:-1]+data[1:])

def widths(data):
    """Return half the width of bins given the bin edges"""
    return 0.5*(data[1:]-data[:-1])

def dummy_bins2D(x_bins,y_bins):
    """Convert two lists of values, e.g., bin midpoints, into array of values"""
    xbins  = x_bins.repeat(len(y_bins))
    ybins  = np.tile(y_bins, (1,len(x_bins)))[0]
    return xbins,ybins

def extract(str_value, start_='{', stop_='}'):
    """Extract a string between two symbols, e.g., parentheses."""
    extraction = str_value[str_value.index(start_)+1:str_value.index(stop_)]
    return extraction


def getDataStructure(h_data):
    """
    Find the data structure determining the appropriate color scheme.
    Only call if the self.colormap attribute is None.

    @param h_data    The histogram data
    @param colorMap  Current choice for colormap
    """
    max_value = max(h_data)
    min_value = min(h_data)

    ## linear (same sign)
    if max_value*min_value >= 0:
        if max_value>0:
            colormap = "Reds"    # positive values
        else:
            colormap = "Blues"   # negative values
    ## diverging
    else:
        colormap = "bwr"         # blue2red map

    return colormap



def betterColors():
    """
    Better colors for plotting.
    In matplotlib 2.0, these are available by default: 
    > https://matplotlib.org/users/dflt_style_changes.html#colors-color-cycles-and-color-maps
    """
    old_colors = [
         (31, 119, 180),  #blue
         (214, 39, 40),   #red
         (44, 160, 44),   #green
         (255, 127, 14),  #orange
         (148, 103, 189), #purple
         (227, 119, 194), #pink
         (127, 127, 127), #teal
         (188, 189, 34),  #gray
         (23, 190, 207),  #green-gold
         (140, 86, 75),   #brown
         # lighter versions
         (174, 199, 232), #blue
         (255, 152, 150), #red
         (152, 223, 138), #green
         (255, 187, 120), #orange
         (197, 176, 213), #purple
         (247, 182, 210), #pink
         (158, 218, 229), #teal
         (199, 199, 199), #gray
         (219, 219, 141), #green-gold
         (196, 156, 148), #brown
    ]
    lc = []
    for jj in old_colors:
        new_color = [i/255. for i in jj]
        lc.append(new_color)

    ls  = ['solid' for _ in lc]
    ls += ['dashed' for _ in lc]

    return {'linecolors':lc,'linestyles':ls}


## THE END