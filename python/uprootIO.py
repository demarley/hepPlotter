"""
Created:        17 October   2018
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple functions to help accessing data with uproot / numpy
"""
from hist import Hist
from baseIO import BaseIO


class UprootIO(BaseIO):
    def __init__(self):
        BaseIO.__init__(self)

    def convert(data):
        """Convert ROOT/Numpy data into uniform format"""
        self._isHistogram  = ('TH1' in data._classname) or ('TH2' in data._classname)
        self._isEfficiency = False
        # TEfficiency currently unsupported in uproot '3.2.5' and uproot-methods '0.2.5'
        # - throws NotImplementedError (/.../uproot/rootio.py", line 645)

        # convert data for internal use (uniform I/O)
        h_data = Hist()
        if isHistogram:
            if self.dimensions==1:
                h_data = self.hist2data(data,reBin=self.rebin,normed=hist.normed)
            else:
                h_data = self.hist2data2D(data,reBin=self.rebin,normed=hist.normed)
        else:
            # others, e.g., numpy data (may or may not need to be put into a histogram)
            if self.dimensions==1:
                h_data = self.array2data(data,weights=weights,normed=hist.normed,binning=self.binning)
            else:
                h_data = self.array2data2D(data,weights=weights,normed=hist.normed,binning=self.binning)

        return h_data


    def array2data(data,weights=None,normed=False,binning=1,reBin=None):
        """
        Convert array of data to internal format
        - Designed for arrays of raw, un-binned data.
        - If you pass values here from an existing histogram ('weights' is not None
          and the 'data' param is just bin centers), it is possible to re-bin
          this histogram using the 'reBin' keyword
        """
        data,bins = np.histogram(data,bins=binning,weights=weights,normed=normed)

        errors = np.sqrt(data)
        if weights is not None:
            # numpy digitize to get sumw2

        results = Hist()
        results.content = data
        results.error   = errors
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

        errors = np.sqrt(data)
        if weights is not None:
            # scipy.stats to get sumw2

        results = Hist()
        results.content = data.flatten()   # data is a ndarray (nxbins,nybins)
        results.error   = errors

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



    def hist2data(histo,reBin=None,normed=False):
        """Convert ROOT histogram for internal use."""
        bin_contents,bin_edges = histo.numpy()

        results.content = bin_contents
        results.bins    = bin_edges
        results.center  = midpoints(bin_edges)
        results.width   = bin_edges[1:] - bin_edges[:-1]

        if len(histo.variances)>0:
            results.error = histo.variances
        else:
            results.error = np.sqrt( bin_contents )

        if reBin is not None:
            results.Rebin(reBin)

        if normed:
            # normalize after re-binning
            integral = np.sum(results.content)
            results.content = np.divide(results.content,integral,dtype=np.float32)
            results.error   = np.divide(results.error,  integral,dtype=np.float32)

        return results



    def hist2data2D(histo,reBin=None,normed=False):
        """Convert ROOT histogram for internal use."""
        bin_contents,(xbin_edges,ybin_edges) = histo.numpy()

        if len(histo.allvariances)>0:
            bin_errors = histo.allvariances[1:-1,1:-1]  # variances() doesn't produce correct values in 2D right now
        else:
            bin_errors = np.sqrt(bin_contents)

        results = Hist()
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


## THE END ##