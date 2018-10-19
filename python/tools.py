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


_scipy_available  = False  # for re-binning 2D histograms
_ROOT_available   = False

try:
    import io_root
    _ROOT_available = True
except ImportError:
    import uproot
    _ROOT_available = False

try:
    import scipy.stats
    _scipy_available = True
except ImportError:
    _scipy_available = False
    print ' WARNING : Scipy not available, may cause issues with re-binning 2D histograms.'


def widths(data):
    """Return the widths of bins given the bin edges"""
    return 0.5*(data[1:]-data[:-1])


def midpoints(data):
    """Return the midpoints of bins given the bin edges"""
    return 0.5*(data[:-1]+data[1:])


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

    def Rebin(self):
        if isinstance(reBin, (int,long)):
            # merge bins together by some integer factor 'reBin'
            if reBin<=0 or self.bin_contents.size%reBin:
                print " WARNING : Cannot re-bin with {0}".format(reBin)
                print "         : Not re-binning the histogram"
                return
            else:
                reBin = np.array( [self.bins[i] for i in range(0,self.bins.size,reBin)] )
        elif not all((i in self.bins) for i in reBin):
            print " WARNING : Cannot re-bin with {0}".format(reBin)
            print "         : Not re-binning the histogram"
            return
        else:
            print " WARNING : Cannot re-bin with {0}".format(reBin)
            print "         : Not re-binning the histogram"
            return

        # re-bin the histogram (by making a new histogram)
        # with variable binning -- edges must still line up!
        bin_contents,bin_edges = np.histogram(bin_centers,bins=reBin,weights=bin_contents,normed=normed)
        nbin_edges = len(bin_edges)
        if len(histo.variances):
            # re-bin bin errors
            bin_index   = np.digitize(bin_centers, bin_edges)  # find where original values migrated in new binning
            bin_weights = np.asarray([bin_errors[np.where(bin_index==idx)[0]] for idx in range(1,nbin_edges)])
            bin_weights_sqr = np.square(bin_weights)
            bin_weights_sum = [ np.sum(i) for i in bin_weights_sqr ] # in case the array has variable length elements
            bin_errors      = np.sqrt( bin_weights_sum )
        else:
            bin_errors  = bin_contents.copy()

        self.content = bin_contents
        self.error   = bin_errors
        self.bins    = bin_edges
        self.center  = midpoints(bin_edges)
        self.width   = widths(bin_edges)

        return

    def Rebin2D(self,reBin):
        """Re-bin 2D histogram"""
        xrebin = xbin_edges.copy()         # default to original binning
        yrebin = ybin_edges.copy()         # default to original binning

        xbins  = self.bins['x']
        ybins  = self.bins['y']
        nbinsx = len(xbins)-1
        nbinsy = len(ybins)-1
        if isinstance(reBin, (int,long)):
            # new bins should be merged bin edges
            if reBin<=0 or nbinsx%reBin or nbinsy%reBin:
                print " WARNING : Cannot re-bin with {0}".format(reBin)
                print "         : Not re-binning the histogram"
                return
            else:
                xrebin = np.array([xbins[i] for i in range(0,nbinsx+1,reBin)] )
                yrebin = np.array([ybins[i] for i in range(0,nbinsy+1,reBin)] )
        else:
            # new bins should be new array bin edges
            # - edges must still match previous binning, e.g.,
            #   can't re-bin [0,1,4,6] into [0,3,6]
            try: 
                xrebin = reBin['x']
                yrebin = reBin['y']
            except TypeError:
                xrebin = reBin[0]
                yrebin = reBin[1]

            if (not all((i in xbins) for i in xrebin)) or (not all((i in ybins) for i in yrebin)):
                print " WARNING : Cannot re-bin 2D histogram using {0}".format(reBin)
                print "         : Not re-binning histogram"
                return

        # - generate dummy values of the bin centers and pass data as weights
        ymbins = midpoints(xbins)
        xmbins = midpoints(ybins)
        xbins  = xmbins.repeat(len(ymbins))
        ybins  = np.tile(ymbins, (1,len(xmbins)))[0]

        rb_hist2d = np.histogram2d(xbins,ybins,bins=[xrebin,yrebin],normed=normed,\
                                   weights=bin_contents.flatten())
        bin_contents,xbin_edges,ybin_edges = rb_hist2d

        nxbins = len(self.bins['x'])-1
        nybins = len(self.bins['y'])-1
        xbins_unravel = nxbins+2
        ybins_unravel = nybins+2
        if _scipy_available:
            # rebin the histogram to see where the old bins get merged into new bins
            s,bx,by,bin_index = scipy.stats.binned_statistic_2d(xbins,ybins,xbins,bins=[xrebin,yrebin])
            # convert scipy bin_index to bin_index of given array (scipy includes over/underflow)
            unrv_bc = np.unravel_index(bin_index,[xbins_unravel,ybins_unravel])
            bin_idx = np.array(unrv_bc).T-1      # convert unrv_bc from tuple to 2D array

            # combine weights in quadrature into array
            fbin_errors = bin_errors.flatten()
            bin_weights = np.zeros(nxbins*nybins).reshape(nxbins,nybins) # same shape as hist
            for ix in range(nxbins):
                for iy in range(nybins):
                    matches = [ib==[ix,iy] for ib in bin_idx.tolist()]
                    bin_weights[ix][iy] = np.sqrt( np.sum( np.square(fbin_errors[matches])))
            bin_errors = bin_weights.copy()
        else:
            bin_errors = np.sqrt(bin_contents)

        self.content = bin_contents
        self.error   = bin_errors
        self.bins    = bin_edges
        self.center  = midpoints(bin_edges)
        self.width   = widths(bin_edges)

        return


def array2data(data,weights=None,normed=False,binning=1,reBin=None):
    """
    Convert array of data to internal format
    - Designed for arrays of raw, un-binned data.
    - If you pass values here from an existing histogram ('weights' is not None
      and the 'data' param is just bin centers), it is possible to re-bin
      this histogram using the 'reBin' keyword
    """
    data,bins = np.histogram(data,bins=binning,weights=weights,normed=normed)

    results = Data()
    results.content = data
    results.error   = np.sqrt(data)
    results.bins    = bins
    results.center  = midpoints(bins)
    results.width   = widths(bins)

    if reBin is not None:
        results.Rebin(reBin)

    return results


def array2data2D(data,weights=None,normed=False,binning=1,reBin=None):
    """
    Convert array of data to internal format
    - Designed for arrays of raw, un-binned data.
    - If you pass values here from an existing histogram ('weights' is not None
      and the 'data' param is just bin centers), it is possible to re-bin
      this histogram using the 'reBin' keyword
    """
    try:
        x = data['x']
        y = data['y']
    except TypeError:
        x = data[0]
        y = data[1]

    data,bins_x,bins_y = np.histogram2d(x,y,bins=binning,normed=normed,weights=weights)

    results = Data()
    results.content = data.flatten()   # data is a ndarray (nxbins,nybins)
    results.error   = np.sqrt(data)    # no way to do sumw2 with numpy

    results.bins    = {'x':bins_x,'y':bins_y}
    results.center  = {'x':midpoints(bins_x),'y':midpoints(bins_y)}
    results.width   = {'x':widths(bins_x),   'y':widths(bins_y)}

    if reBin is not None:
        results.Rebin2D(reBin)

    results.xbins   = results.bins['x']
    results.ybins   = results.bins['y']
    results.xcenter = results.center['x']
    results.ycenter = results.center['y']
    results.xwidth  = results.width['x']
    results.ywidth  = results.width['y']

    return results


def hist2data(histo,normed=False,reBin=None):
    """Convert ROOT histogram for internal use."""
    results = Data()

    if _ROOT_available:
        results = io_root.hist2list(histo,normed,reBin,results)
    else:
        bin_contents,bin_edges = histo.numpy()

        results.content = bin_contents
        results.error   = histo.variances if len(histo.variances)>0 else bin_contents
        results.bins    = bin_edges
        results.center  = midpoints(bin_edges)
        results.width   = bin_edges[1:] - bin_edges[:-1]

        if reBin is not None:
            results.Rebin2D(reBin)

        if normed:
            bin_contents = np.divide(bin_contents,np.sum(bin_contents),dtype=np.float32)

    return results



def hist2data2D(histo,reBin=None,normed=False):
    """Convert ROOT histogram for internal use."""
    results = Data()

    if _ROOT_available:
        results = io_root.hist2list2D(histo,reBin,normed,results)
    else:
        bin_contents,(xbin_edges,ybin_edges) = histo.numpy()
        bin_errors = histo.allvariances[1:-1,1:-1] if len(histo.allvariances)>0 else bin_contents

        results.content = bin_contents.flatten()
        results.error   = bin_errors.flatten()
        results.bins    = {'x':xbin_edges,'y':ybin_edges}
        results.center  = {'x':midpoints(xbin_edges),'y':midpoints(ybin_edges)}
        results.width   = {'x':xbin_edges[1:]-xbin_edges[:-1],'y':ybin_edges[1:]-ybin_edges[:-1]}

        if reBin is not None:
            results.Rebin2D(reBin)

        if normed:
            # normalize after re-binning
            integral = np.sum(results.content)
            results.content = np.divide(results.content,integral,dtype=np.float32)
            results.error   = np.divide(results.error,  integral,dtype=np.float32)

        # Set extra attributes (placeholders for the moment)
        results.xbins   = results.bins['x']
        results.ybins   = results.bins['y']
        results.xcenter = results.center['x']
        results.ycenter = results.center['y']
        results.xwidth  = results.width['x']
        results.ywidth  = results.width['y']

    return results



def TEfficiency2data(histo):
    """Convert TEfficiency to internal format. No support for re-binning TEfficiencies."""
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



def TEfficiency2data2D(histo):
    """Convert 2D TEfficiency to internal format. No support for re-binning TEfficiencies."""
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