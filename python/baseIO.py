"""
Created:        19 October   2018
Last Updated:   23 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Base class for interfacing with different input data types
"""
import tools
import numpy as np
from hist import Hist


class BaseIO(object):
    def __init__(self,**kwargs):
        """Store data for plotting (collection of arrays) in a class"""
        self.dimensions = kwargs.get("dimensions",1)
        self.rebin      = kwargs.get("rebin",False)
        self.normed     = kwargs.get("normed",False)
        self.binning    = kwargs.get("binning",1)
        self.weights    = kwargs.get("weights")

        self._isHistogram  = False
        self._isEfficiency = False

    def isTH1(self):
        return self._isHistogram
    def isTEff(self):
        return self._isEfficiency

    def convert(self,data):
        """Convert data into internal format"""
        pass


    def convert_array(self,data):
        """Convert data from an array format into internal format"""
        h_data = None
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

## THE END ##