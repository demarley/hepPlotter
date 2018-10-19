"""
Created:        19 October   2018
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple class for storing data internally to HEP Plotter as histogram-like object
"""
import numpy as np


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

    def midpoints(self,data):
        """Return the midpoint of bins given the bin edges"""
        return 0.5*(data[:-1]+data[1:])

    def widths(self,data):
        """Return half the width of bins given the bin edges"""
        return 0.5*(data[1:]-data[:-1])

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

        # re-bin the histogram (by making a new histogram)
        bin_contents,bin_edges = np.histogram(bin_centers,bins=reBin,weights=bin_contents,normed=normed)
        nbin_edges = len(bin_edges)

        # re-bin errors
        bin_index   = np.digitize(bin_centers, bin_edges)  # find where original values migrated in new binning
        bin_weights = np.asarray([bin_errors[np.where(bin_index==idx)[0]] for idx in range(1,nbin_edges)])
        bin_weights_sqr = np.square(bin_weights)
        bin_weights_sum = [ np.sum(i) for i in bin_weights_sqr ] # in case the array has variable length elements
        bin_errors      = np.sqrt( bin_weights_sum )

        self.content = bin_contents
        self.error   = bin_errors
        self.bins    = bin_edges
        self.center  = self.midpoints(bin_edges)
        self.width   = self.widths(bin_edges)

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
        ymbins = self.midpoints(xbins)
        xmbins = self.midpoints(ybins)
        xbins  = xmbins.repeat(len(ymbins))
        ybins  = np.tile(ymbins, (1,len(xmbins)))[0]

        rb_hist2d = np.histogram2d(xbins,ybins,bins=[xrebin,yrebin],normed=normed,\
                                   weights=bin_contents.flatten())
        bin_contents,xbin_edges,ybin_edges = rb_hist2d

        xbins_unravel = nbinsx+2
        ybins_unravel = nbinsy+2
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
        self.center  = self.midpoints(bin_edges)
        self.width   = self.widths(bin_edges)

        return


## THE END ##