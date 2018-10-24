"""
Created:        19 October   2018
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple class for storing data internally to HEP Plotter as histogram-like object
"""
import numpy as np
import tools

_scipy_available = False  # for re-binning 2D histograms

try:
    import scipy.stats
    _scipy_available = True
except ImportError:
    _scipy_available = False




class Hist(object):
    """Internal histogram-like object for storing & manipulating data"""
    def __init__(self):
        """Store data for plotting in a class"""
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

    def normalize(self):
        integral = np.sum(self.content)
        self.content = np.divide(self.content,integral,dtype=np.float32)
        self.error   = np.divide(self.error,  integral,dtype=np.float32)
        return

    def sumw2_1D(self,xdata,values=None,binning=None):
        """Calculate the sum of weights squared using numpy.digitize"""
        if values is None:  values  = self.error
        if binning is None: binning = self.bins

        # find the new bin location of original values
        bin_index   = np.digitize(xdata,binning)

        # find in which bin the values now exist
        bin_weights = np.asarray([values[np.where(bin_index==idx)[0]] for idx in range(1,len(binning))])
        bin_weights_sqr = np.square(bin_weights)
        bin_weights_sum = [ np.sum(i) for i in bin_weights_sqr ] # in case the array has variable length elements

        return np.sqrt( bin_weights_sum )


    def sumw2_2D(self,xdata,ydata,values=None,binning=None):
        """Calculate the sum of weights squared for 2D array using scipy.stats"""
        if values is None:  values  = self.error
        if binning is None: binning = [self.bins['x'],self.bins['y']]

        # find the new bin location of original values
        s,bx,by,bin_index = scipy.stats.binned_statistic_2d(xdata,ydata,xdata,bins=binning)

        # convert scipy bin_index to bin_index of given array (scipy includes over/underflow)
        nxbins = len(binning[0])-1
        nybins = len(binning[1])-1
        xbins_unravel = nxbins+2
        ybins_unravel = nybins+2
        unrv_bc = np.unravel_index(bin_index,[xbins_unravel,ybins_unravel])
        bin_idx = np.array(unrv_bc).T-1      # convert unrv_bc from tuple to 2D array

        # combine weights in quadrature into array
        fvalues     = values.flatten()
        bin_weights = np.zeros(nxbins*nybins).reshape(nxbins,nybins) # same shape as hist
        for ix in range(nxbins):
            for iy in range(nybins):
                matches = [ib==[ix,iy] for ib in bin_idx.tolist()]
                bin_weights[ix][iy] = np.sqrt( np.sum( np.square(fvalues[matches])))

        return bin_weights


    def Rebin(self,reBin):
        if isinstance(reBin, (int,long)):
            # merge bins together by some integer factor 'reBin'
            if reBin<=0 or self.content.size%reBin:
                print " WARNING : Cannot re-bin with {0}".format(reBin)
                print "         : Not re-binning the histogram"
                return
            else:
                reBin = np.array( [self.bins[i] for i in range(0,self.bins.size,reBin)] )
        elif not all((i in self.bins) for i in reBin):
            print " WARNING : Cannot re-bin with {0}".format(reBin)
            print "         : Not re-binning the histogram"
            return

        # re-bin the histogram (by making a new histogram)
        bin_contents,bin_edges = np.histogram(self.center,bins=reBin,weights=self.content)

        self.content = bin_contents
        self.bins    = bin_edges
        self.center  = tools.midpoints(bin_edges)
        self.width   = tools.widths(bin_edges)
        self.error   = self.sumw2_1D(xdata=self.center)  # use data for re-binning, not bin content

        return


    def Rebin2D(self,reBin):
        """Re-bin 2D histogram"""
        xbins  = self.bins['x']
        ybins  = self.bins['y']
        nbinsx = len(xbins)-1
        nbinsy = len(ybins)-1

        xrebin = xbins.copy()         # default to original binning
        yrebin = ybins.copy()         # default to original binning

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
            # new bins should be new array bin edges that must match previous binning:
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
        xbins,ybins = tools.dummy_bins2D(tools.midpoints(xbins),tools.midpoints(ybins))
        rb_hist2d   = np.histogram2d(xbins,ybins,bins=[xrebin,yrebin],weights=self.content.tolist())
        bin_contents,xbin_edges,ybin_edges = rb_hist2d

        self.content = bin_contents.flatten()
        self.bins    = {'x':xbin_edges,'y':ybin_edges}

        xbin_center,ybin_center = tools.dummy_bins2D(tools.midpoints(xbin_edges),tools.midpoints(ybin_edges))
        xbin_width,ybin_width   = tools.dummy_bins2D(tools.widths(xbin_edges),tools.widths(ybin_edges))
        self.center  = {'x':xbin_center,'y':ybin_center}
        self.width   = {'x':xbin_width, 'y':ybin_width}

        if _scipy_available:
            self.error = self.sumw2_2D(xdata=xbins,ydata=ybins)
        else:
            self.error = np.sqrt(bin_contents.flatten())

        return


## THE END ##