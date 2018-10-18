"""
Created:         1 September 2016
Last Updated:   17 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University
-----

Simple functions to help with plotting & accessing data
"""
import numpy as np

m_ROOT_available   = False
try:
    import ROOT
    m_ROOT_available = True
except ImportError:
    m_ROOT_available = False



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



##########################################################################################
# Extract data from histograms / TEfficiencies / arrays & organize into custom object
def midpoints(data):
    """Return the midpoint of bins given the bin edges"""
    return 0.5*(data[:-1]+data[1:])


class Data(object):
    def __init__(self):
        """Store data for plotting (collection of arrays) in a class"""
        self.content = None
        self.error   = None
        self.bins    = None
        self.center  = None
        self.width   = None
        self.xbins   = None
        self.ybins   = None
        self.xcenter = None
        self.ycenter = None
        self.xwidth  = None
        self.ywidth  = None


def data2list(data,weights=None,normed=False,binning=1):
    """Convert array of data into dictionary of information matching 'hist2list' """
    data,bins = np.histogram(data,bins=binning,weights=weights,normed=normed)

    results = Data()
    results.content = data
    results.error   = np.sqrt(data)
    results.bins    = bins
    results.center  = 0.5*(bins[:-1]+bins[1:])
    results.width   = 0.5*(bins[:-1]-bins[1:])

    return results


def data2list2D(data,weights=None,normed=False,binning=1):
    """Convert array of data into dictionary of information matching 'hist2list' """
    try:
        x = data['x']
        y = data['y']
    except TypeError:
        x = data[0]
        y = data[1]

    data,bins_x,bins_y = np.histogram2d(x,y,bins=binning,normed=normed,weights=weights)

    # create dummy binning
    mbins_x = midpoints(bins_x)  # get midpoints of bins given the bin edges
    mbins_y = midpoints(bins_y)
    xbins = mbins_x.repeat(len(mbins_y))
    ybins = np.tile(mbins_y, (1,len(mbins_x)) )[0]

    results = Data()
    results.content = data.flatten()   # data is a ndarray (nxbins,nybins)
    results.error   = np.sqrt(data)

    results.xbins   = np.array(bins_x)
    results.ybins   = np.array(bins_y)
    results.xcenter = xbins
    results.ycenter = ybins
    results.xwidth  = 0.5*(bins_x[:-1]-bins_x[1:])
    results.ywidth  = 0.5*(bins_y[:-1]-bins_y[1:])

    results.bins    = {'x':results.xbins,'y':results.ybins}
    results.center  = {'x':xbins,'y':ybins}
    results.width   = {'x':results.xwidth,
                       'y':results.ywidth}

    return results


def hist2list(histo,name='',normed=False,reBin=None):
    """Convert ROOT histogram for internal use."""
    results = Data()

    if m_ROOT_available:
        results = io_root.hist2list(histo,name,normed,reBin,results)
    else:
        results = io_uproot.hist2list(histo,name,normed,reBin,results)

    return results



def hist2list2D(histo,name='',reBin=None,normed=False):
    """Convert ROOT histogram for internal use."""
    results = Data()

    if m_ROOT_available:
        results = io_root.hist2list2D(histo,name,reBin,normed,results)
    else:
        results = io_uproot.hist2list2D(histo,name,reBin,normed,results)

    return results



def TEfficiency2list(histo):
    """Convert TEfficiency to lists.  Return dictionary of lists"""
    h_histo  = histo.GetPassedHistogram()

    bin_contents  = []
    bin_errors_up = []
    bin_errors_dn = []
    bin_centers   = []
    bin_widths    = []
    bin_edges     = [h_histo.GetXaxis().GetBinLowEdge(1)]

    for i in xrange(1,h_histo.GetNbinsX()+1):
        bin_contents.append(histo.GetEfficiency(i))
        bin_errors_up.append(histo.GetEfficiencyErrorUp(i))
        bin_errors_dn.append(histo.GetEfficiencyErrorLow(i))
        bin_centers.append(h_histo.GetXaxis().GetBinCenter(i))
        bin_edges.append(h_histo.GetXaxis().GetBinUpEdge(i))
        bin_widths.append(h_histo.GetXaxis().GetBinWidth(1)/2.)

    results = Data()
    results.content = np.array(bin_contents)
    results.error   = [bin_errors_dn,bin_errors_up]
    results.bins    = np.array(bin_edges)
    results.center  = bin_centers
    results.width   = bin_widths

    return results



def TEfficiency2list2D(histo):
    """Convert 2D TEfficiency to lists"""
    h_histo  = histo.GetPassedHistogram()

    bin_centers   = {'x':[],'y':[]}
    bin_contents  = []
    bin_error_ups = [] # eff uncertainty up
    bin_error_dns = [] # eff uncertainty down
    bin_widths    = {'x':[],'y':[]}

    binns = {'x':[h_histo.GetXaxis().GetBinLowEdge(1)],\
             'y':[h_histo.GetYaxis().GetBinLowEdge(1)]}
    bin_edges['x']+=[h_histo.GetXaxis().GetBinUpEdge(i) for i in xrange(1,h_histo.GetNbinsX()+1)]
    bin_edges['y']+=[h_histo.GetYaxis().GetBinUpEdge(j) for j in xrange(1,h_histo.GetNbinsY()+1)]

    for i in xrange(1,h_histo.GetNbinsX()+1):
        for j in xrange(1,h_histo.GetNbinsY()+1):
            bin_center['x'].append(h_histo.GetXaxis().GetBinCenter(i))
            bin_center['y'].append(h_histo.GetYaxis().GetBinCenter(j))

            this_bin = histo.GetGlobalBin(i,j)
            bin_contents.append(histo.GetEfficiency(this_bin))
            bin_error_ups.append(histo.GetEfficiencyErrorUp(this_bin))
            bin_error_dns.append(histo.GetEfficiencyErrorLow(this_bin))
            bin_widths['x'].append(h_histo.GetXaxis().GetBinWidth(1)/2.)
            bin_widths['y'].append(h_histo.GetYaxis().GetBinWidth(1)/2.)

    results = Data()
    results.content = np.array(bin_contents)
    results.error   = [np.array(bin_error_dns),np.array(bin_error_ups)]
    results.bins    = {'x':np.array(bin_edges['x']),'y':np.array(bin_edges['y'])}
    results.center  = bin_centers
    results.width   = bin_widths

    return results



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