"""
Created:        17 October   2018
Last Updated:   17 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple functions to help accessing data with uproot
"""
import uproot
import numpy as np

m_scipy_available  = False  # for re-binning 2D histograms

try:
    import scipy.stats
    m_scipy_available = True
except ImportError:
    m_scipy_available = False
    print ' WARNING : Scipy not available, may cause issues with re-binning 2D histograms.'



def hist2list(histo,name,normed,reBin,results):
    """
    Convert ROOT histogram for internal use.
    For re-binning, try to mirror CERN ROOT functionality with numpy histograms.
    """
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
    results.content = np.array(bin_contents)
    results.error   = np.array(bin_errors)
    results.bins    = np.array(bin_edges)
    results.center  = bin_centers
    results.width   = bin_widths

    return results




def hist2list2D(histo,name,reBin,normed,results):
    """
    Convert ROOT histogram for internal use.
    For re-binning, try to mirror CERN ROOT functionality with numpy histograms.
    """
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
                    bin_weights[ix][iy] = np.sqrt( np.sum( np.square(fbin_errors[matches])))
            bin_errors = bin_weights.copy()
        else:
            bin_errors = bin_contents.copy()

    bin_contents = bin_contents.flatten()
    bin_errors   = bin_errors.flatten()
    bin_edges    = {'x':xbin_edges,'y':ybin_edges}
    bin_centers  = {'x':midpoints(xbin_edges),'y':midpoints(ybin_edges)}
    bin_widths   = {'x':xbin_edges[1:]-xbin_edges[:-1],'y':ybin_edges[1:]-ybin_edges[:-1]}

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


## THE END ##