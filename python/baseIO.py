"""
Created:        19 October   2018
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple class for interfacing with different input data types
"""

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


## THE END ##