"""
Created:        17 October   2018
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple functions to help accessing data with uproot / numpy
"""
import numpy as np
import tools
from hist import Hist
from baseIO import BaseIO


class UprootIO(BaseIO):
    def __init__(self,**kwargs):
        BaseIO.__init__(self,**kwargs)

    def convert(self,data):
        """Convert ROOT/Numpy data into uniform format"""
        try:
            classname = data._classname
        except AttributeError:
            classname = str(type(data))
        self._isHistogram  = ('TH1' in classname) or ('TH2' in classname)
        self._isEfficiency = False
        # TEfficiency currently unsupported in uproot '3.2.5' and uproot-methods '0.2.5'
        # - throws NotImplementedError (/.../uproot/rootio.py", line 645)

        h_data = Hist()
        if self._isHistogram:
            if self.dimensions==1:
                h_data = self.hist2data(data,reBin=self.rebin,normed=self.normed)
            else:
                h_data = self.hist2data2D(data,reBin=self.rebin,normed=self.normed)
        else:
            # others, e.g., numpy data (may or may not need to be put into a histogram)
            if self.dimensions==1:
                h_data = self.array2data(data,weights=self.weights,normed=self.normed,\
                                         binning=self.binning,reBin=self.rebin)
            else:
                h_data = self.array2data2D(data,weights=self.weights,normed=self.normed,\
                                           binning=self.binning,reBin=self.rebin)

        return h_data


    def array2data(self,data,weights=None,normed=False,binning=1,reBin=None):
        """
        Convert array of data to internal format
        - Designed for arrays of raw, un-binned data.
        - If you pass values here from an existing histogram ('weights' is not None
          and the 'data' param is just bin centers), it is possible to re-bin
          this histogram using the 'reBin' keyword
        """
        data,bins = np.histogram(data,bins=binning,weights=weights,normed=normed)

        results = Hist()
        results.content = data
        results.bins    = bins
        results.center  = tools.midpoints(bins)
        results.width   = tools.widths(bins)

        results.error   = np.sqrt(data)
        if weights is not None:
            # numpy digitize to get sumw2
            results.error = results.sumw2_1D(xdata=data,values=weights)

        if reBin is not None:
            results.Rebin(reBin)
            if normed: results.normalize()  # normalize after re-binning

        return results


    def array2data2D(self,data,weights=None,normed=False,binning=1,reBin=None):
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

        results = Hist()
        results.content = data.flatten()   # data is a ndarray (nxbins,nybins)
        results.bins    = {'x':bins_x,'y':bins_y}
        results.center  = {'x':tools.midpoints(bins_x),'y':tools.midpoints(bins_y)}
        results.width   = {'x':tools.widths(bins_x),   'y':tools.widths(bins_y)}

        results.error   = np.sqrt(data)
        if weights is not None:
            # scipy.stats to get sumw2
            xdata,ydata   = tools.dummy_bins2D(tools.midpoints(x),tools.midpoints(y))
            results.error = results.sumw2_2D(xdata=xdata,ydata=ydata,values=weights)

        if reBin is not None:
            results.Rebin2D(reBin)
            if normed: results.normalize() # normalize after re-binning

        results.xbins   = results.bins['x']
        results.ybins   = results.bins['y']
        results.xcenter = results.center['x']
        results.ycenter = results.center['y']
        results.xwidth  = results.width['x']
        results.ywidth  = results.width['y']

        return results



    def hist2data(self,histo,reBin=None,normed=False):
        """Convert ROOT histogram for internal use."""
        bin_contents,bin_edges = histo.numpy()

        results = Hist()
        results.content = bin_contents
        results.bins    = bin_edges
        results.center  = tools.midpoints(bin_edges)
        results.width   = tools.widths(bin_edges)

        if len(histo.variances)>0:
            results.error = histo.variances
        else:
            results.error = np.sqrt( bin_contents )

        if reBin is not None:
            results.Rebin(reBin)
        if normed: results.normalize()

        return results



    def hist2data2D(self,histo,reBin=None,normed=False):
        """Convert ROOT histogram for internal use."""
        bin_contents,(xbin_edges,ybin_edges) = histo.numpy()
        bin_contents = bin_contents.T

        if len(histo.allvariances)>0:
            bin_errors = histo.allvariances[1:-1,1:-1]  # variances() doesn't produce correct values in 2D right now
        else:
            bin_errors = np.sqrt(bin_contents)

        xbin_centers,ybin_centers = tools.dummy_bins2D(tools.midpoints(xbin_edges),tools.midpoints(ybin_edges))
        xbin_widths,ybin_widths   = tools.dummy_bins2D(tools.widths(xbin_edges),tools.widths(ybin_edges))

        results = Hist()
        results.content = bin_contents.flatten()
        results.error   = bin_errors.flatten()
        results.bins    = {'x':xbin_edges,  'y':ybin_edges}
        results.center  = {'x':xbin_centers,'y':ybin_centers}
        results.width   = {'x':xbin_widths, 'y':ybin_widths}

        if reBin is not None:
            results.Rebin2D(reBin)
        if normed: results.normalize()

        # Set extra attributes (placeholders for the moment)
        results.xbins   = results.bins['x']
        results.ybins   = results.bins['y']
        results.xcenter = results.center['x']
        results.ycenter = results.center['y']
        results.xwidth  = results.width['x']
        results.ywidth  = results.width['y']

        return results


## THE END ##