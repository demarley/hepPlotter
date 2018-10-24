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
            # no support for TEfficiencies in uproot right now
            h_data = self.convert_array(data)


        return h_data


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