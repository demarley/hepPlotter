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


m_scipy_available  = False  # for re-binning 2D histograms
m_ROOT_available   = False
m_uproot_available = False

try:
    import scipy.stats
    m_scipy_available = True
except ImportError:
    m_scipy_available = False
    print ' WARNING : Scipy not available, may cause issues with re-binning 2D histograms.'

try:
    import ROOT
    m_ROOT_available = True
except ImportError:
    m_ROOT_available = False
    try:
        import uproot as up
        m_uproot_available = True
    except ImportError:
        m_uproot_available = False
        print " WARNING : Neither 'uproot' nor 'CERN ROOT' available."
        print "         : Will not be able to load ROOT histograms."

if m_ROOT_available and m_uproot_available:
    print " INFO : Both 'CERN ROOT' and 'uproot' available. Defaulting to 'uproot'."
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
    """
    Convert ROOT histogram to (dictionary of) lists.
    For re-binning, try to mirror CERN ROOT functionality with numpy histograms.
    """
    bin_centers  = []
    bin_contents = []
    bin_errors   = []
    bin_widths   = []
    bin_edges    = []

    if m_uproot_available:
        bin_contents,bin_edges = histo.numpy()
        if normed:
            bin_contents = np.divide(bin_contents,np.sum(bin_contents),dtype=np.float32)

        bin_errors  = histo.variances if len(histo.variances) else bin_contents
        bin_centers = midpoints(bin_edges)

        if reBin is not None:
            if isinstance(reBin, (int,long)):
                # merge bins together by some integer factor 'reBin'
                if reBin<=0 or bin_contents.size%reBin:
                    print " WARNING : Cannot re-bin with {0}".format(reBin)
                    print "         : Not re-binning the histogram"
                    reBin = bin_edges.copy()
                else:
                    reBin = np.array( [bin_edges[i] for i in range(0,bin_edges.size,reBin)] )
            elif not all((i in bin_edges) for i in reBin):
                print " WARNING : Cannot re-bin with {0}".format(reBin)
                print "         : Not re-binning the histogram"
                reBin = bin_edges.copy()

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

        # set the bin centers and widths
        bin_centers = midpoints(bin_edges)
        bin_widths  = bin_edges[1:] - bin_edges[:-1]
    elif m_ROOT_available:
		if not histo.GetSumw2N():
			histo.Sumw2()

		if normed:
			integral = histo.Integral()
			histo.Scale(1./integral);

		try:
			histo.Rebin(reBin)
		except TypeError:
			newname = histo.GetName()+"_"+name
			histo.Rebin(len(reBin)-1,newname,reBin)
			histo = ROOT.gROOT.FindObject( newname )

		bin_edges = [histo.GetXaxis().GetBinLowEdge(1)]

		for i in xrange(1,histo.GetNbinsX()+1):
			bin_edges.append(histo.GetXaxis().GetBinUpEdge(i))
			bin_centers.append(histo.GetBinCenter(i))
			bin_contents.append(histo.GetBinContent(i))
			bin_errors.append(histo.GetBinError(i))
			bin_widths.append(histo.GetXaxis().GetBinWidth(i)*0.5)

    results = Data()
    results.content = np.array(bin_contents)
    results.error   = np.array(bin_errors)
    results.bins    = np.array(bin_edges)
    results.center  = bin_centers
    results.width   = bin_widths

    return results



def hist2list2D(histo,name='',reBin=None,normed=False):
    """
    Convert ROOT histogram to list for 2D plots.
    For re-binning, try to mirror CERN ROOT functionality with numpy histograms.
    """
    bin_centers  = {'x':[],'y':[]}
    bin_contents = []
    bin_errors   = []
    bin_widths   = {'x':[],'y':[]}
    bin_edges    = {'x':[],'y':[]}

    if m_uproot_available:
        if normed:
            histo = np.divide(histo,np.sum(histo),dtype=np.float32)

        bin_contents,(xbin_edges,ybin_edges) = histo.numpy()
        bin_errors = histo.allvariances[1:-1,1:-1] if len(histo.allvariances) else bin_contents

        if reBin is not None:
            # re-bin the histogram (by making a new histogram)
            xrebin = xbin_edges.copy() # default to original binning
            yrebin = ybin_edges.copy() # default to original binning
            if isinstance(reBin, (int,long)):
                # new bins should be merged bin edges
                if reBin<=0 or bin_contents[0].size%reBin or bin_contents[1].size%reBin:
                    print " WARNING : Cannot re-bin with {0}".format(reBin)
                    print "         : Not re-binning the histogram"
                else:
                    xrebin = np.array([xbin_edges[i] for i in range(0,xbin_edges.size,reBin)] )
                    yrebin = np.array([ybin_edges[i] for i in range(0,ybin_edges.size,reBin)] )
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

                if (not all((i in xbin_edges) for i in xrebin)) or (not all((i in ybin_edges) for i in yrebin)):
                    print " WARNING : Cannot re-bin 2D histogram using {0}".format(reBin)
                    print "         : Not re-binning histogram"
                    xrebin = xbin_edges.copy() # default to original binning
                    yrebin = ybin_edges.copy() # default to original binning

            # - generate dummy values of the bin centers and pass data as weights
            ymbins = midpoints(xbin_edges)
            xmbins = midpoints(ybin_edges)
            xbins  = xmbins.repeat(len(ymbins))
            ybins  = np.tile(ymbins, (1,len(xmbins)))[0]

            rb_hist2d = np.histogram2d(xbins,ybins,bins=[xrebin,yrebin],normed=normed,\
                                       weights=bin_contents.flatten())
            bin_contents,xbin_edges,ybin_edges = rb_hist2d

            nxbins = len(xbin_edges)-1
            nybins = len(ybin_edges)-1
            xbins_unravel = nxbins+2
            ybins_unravel = nybins+2
            if len(histo.variances) and m_scipy_available:
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
                        #bin_weights_sqr     = np.square(fbin_errors[matches])
                        #bin_weights_sum     = [ np.sum(i) for i in bin_weights_sqr ] # in case the array has variable length elements
#                         print bin_weights_sqr
#                         print bin_weights_sum
#                         bin_weights[ix][iy] = np.sqrt( bin_weights_sum )
                        bin_weights[ix][iy] = np.sqrt( np.sum( np.square(fbin_errors[matches])))
                bin_errors = bin_weights.copy()
            else:
                bin_errors = bin_contents.copy()

        bin_contents = bin_contents.flatten()
        bin_errors   = bin_errors.flatten()
        bin_edges    = {'x':xbin_edges,'y':ybin_edges}
        bin_centers  = {'x':midpoints(xbin_edges),'y':midpoints(ybin_edges)}
        bin_widths   = {'x':xbin_edges[1:]-xbin_edges[:-1],'y':ybin_edges[1:]-ybin_edges[:-1]}
    elif m_ROOT_available:
        if not histo.GetSumw2N():
            histo.Sumw2()

        if normed:
            integral = histo.Integral()
            histo.Scale(1./integral)

        ## -- Rebin
        if reBin is not None:
            try:
                histo.Rebin2D(reBin,reBin)
            except TypeError:
                newname   = histo.GetName()+"_"+name
                old_histo = histo.Clone()             # special rebinning, redefine histo
                try:
                    new_x = reBin['x']
                    new_y = reBin['y']
                except KeyError:
                    print " WARNING : Need to pass new bins for re-binning as a dictionary"
                    print "         : Not applying re-binning, please check your setup."
                    new_x = old_histo.GetXaxis().GetArray() # not sure if this works
                    new_y = old_histo.GetYaxis().GetArray()
                histo = ROOT.TH2F(old_histo.GetName()+newname,old_histo.GetTitle()+newname,len(new_x)-1,new_x,len(new_y)-1,new_y)
                xaxis = old_histo.GetXaxis()
                yaxis = old_histo.GetYaxis()
                for i in xrange(1,xaxis.GetNbins()):
                    for j in xrange(1,yaxis.GetNbins()):
                        histo.Fill(xaxis.GetBinCenter(i),yaxis.GetBinCenter(j),old_histo.GetBinContent(i,j) )

        bin_edges = {'x':[histo.GetXaxis().GetBinLowEdge(1)],\
                     'y':[histo.GetYaxis().GetBinLowEdge(1)]}
        bin_edges['x']+=[histo.GetXaxis().GetBinUpEdge(i) for i in xrange(1,histo.GetNbinsX()+1)]
        bin_edges['y']+=[histo.GetYaxis().GetBinUpEdge(j) for j in xrange(1,histo.GetNbinsY()+1)]

        for i in xrange(1,histo.GetNbinsX()+1):
            for j in xrange(1,histo.GetNbinsY()+1):
                bin_contents.append(histo.GetBinContent(i,j))
                bin_errors.append(histo.GetBinError(i,j))
                bin_centers['x'].append(histo.GetXaxis().GetBinCenter(i))
                bin_centers['y'].append(histo.GetYaxis().GetBinCenter(j))
                bin_widths['x'].append(histo.GetXaxis().GetBinWidth(i)*0.5)
                bin_widths['y'].append(histo.GetYaxis().GetBinWidth(i)*0.5)

    results = Data()
    results.content = np.array(bin_contents)
    results.error   = np.array(bin_errors)

    results.xbins   = np.array(bin_edges['x'])
    results.ybins   = np.array(bin_edges['y'])
    results.xcenter = bin_centers['x']
    results.ycenter = bin_centers['y']
    results.xwidth  = bin_widths['x']
    results.ywidth  = bin_widths['y']

    results.bins    = {'x':results.xbins, 'y':results.ybins}
    results.center  = bin_centers
    results.width   = bin_widths

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