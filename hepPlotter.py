"""
Created:         6 April     2016
Last Updated:   13 July      2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University

Bennett Magy
bmagy@umichSPAMNOT.edu
University of Michigan, Ann Arbor, MI 48109
-----

Class to make a simple instance each time we want some basic plots!

This does not include an interface to load/access data.
Here we just plot the data we're given.

Base class for turning histograms or efficiency curves into plots
"""
import os
import sys
import ROOT
from collections import OrderedDict

import numpy as np
import matplotlib.style
import matplotlib as mpl
mpl.style.use('{0}/cms.mplstyle'.format(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.colors import LogNorm
from matplotlib.ticker import AutoMinorLocator,FormatStrFormatter

import hepPlotterTools as hpt
import hepPlotterLabels as hpl



class HepPlotterData(object):
    """Class for containing data objects to plot"""
    def __init__(self):
        """The following are nominal attributes of the class with common parameters"""
        self.name  = ''
        self.color = 'k' 
        self.fmt   = 'o'
        self.linecolor = 'k'
        self.edgecolor = 'k'
        self.linestyle = '-'
        self.linewidth = 2
        self.markeredgecolor = 'k'
        self.markerfacecolor = 'k'
        self.label  = ''
        self.data   = None
        self.normed = False
        self.weight = None
        self.draw_type   = 'step' # 'step','stepfilled','errorbar' (others?)
        self.uncertainty = None
        self.plotData    = None   # get the data from the plot to use later
        self.isHistogram = False  # plt.hist()
        self.isErrobar   = False  # plt.errorbar()
        self.isLinePlot  = False  # basic plt.plot() -- not supported yet
        self.isTH1  = False       # ROOT Histogram
        self.isTEff = False       # ROOT TEfficiency
        self.ratios = []          # which other data to plot with as a ratio
                                  # stored as (partner,True/False) where
                                  #   'partner'  = other data
                                  #   True/False = Numerator/Denominator
        self.kwargs = {}          # extra kwargs for plotting



class HepPlotter(object):
    def __init__(self,dimensions):
        """
        @param typeOfPlot    Set the kind of plot: histogram or efficiency
        """
        if not isinstance(dimensions,(int,long)):
            print " You have specified a dimension of non-integer type."
            print " This is not supported. "
            print " For the hepPlotter class, choose either 1 or 2 dimenions."
            sys.exit(1)

        # customizable options
        self.dimensions = dimensions  # number of dimensions in histogram
        self.ratio_plot = ""          # "ratio","significance": plot a ratio of things
        self.stacked    = False       # stack plots (1D only)
        self.normed     = False       # globally set histograms to be normalized
        self.binning    = 20          # integer for number of bins, or list for non-uniform bins
        self.rebin      = 1           # rebin root histograms
        self.label_size = 20          # text labels on plot
        self.underflow  = False       # plot the underflow
        self.overflow   = False       # plot the overflow
        self.colormap   = None        # 2D plot colormap
        self.colorbar   = {}          # parameters for colorbar on 2D plot
        self.xlim       = None        # tuple for (xmin,xmax)
        self.ylim       = None        # tuple for (ymin,ymax)
        self.axis_scale = {}          # scale axes (mainly the y-axis to accommodate legend/labels
        self.x_label = 'x'
        self.y_label = 'y'
        self.y_label_ratio = self.ratio_plot
        self.extra_text  = hpl.PlotText()
        self.lumi     = '14.7'
        self.plotLUMI = False
        self.CMSlabel = None                 # 'top left', 'top right' & 'outer' for 2D
        self.CMSlabelStatus = 'Internal'     # ('Simulation')+'Internal' || 'Preliminary'
        self.format = 'pdf'                  # file format for saving image
        self.saveAs = "plot{0}D_{1}".format(self.dimensions,self.CMSlabelStatus) # save figure with name
        self.drawStatUncertainty = False
        self.drawUncertaintyMain = False  # draw uncertainties in the top frame
        self.legend  = {"ncol":2}
        self.logplot = {"y":False,"x":False,"data":False}  # plot axes or data (2D) on log scale

        self.text_coords = {'top left': {'x':[0.03]*3,        'y':[0.97,0.90,0.83]},\
                            'top right':{'x':[0.97]*3,        'y':[0.97,0.90,0.83]},\
                            'outer':    {'x':[0.02,0.99,0.99],'y':[1.0,1.0,0.9]}}

        return



    def initialize(self):
        """Initialize the plot and set basic parameters"""
        self.ax1    = None
        self.ax2    = None
        self.kwargs = {}

        self.data2plot = OrderedDict()    # {'name',HepPlotterData()}

        if self.format!='pdf': 
            print " WARNING : Chosen format '{0}' may conflict with backend".format(self.format)

        # draw minor ticks in the 'right' places
        self.x1minorLocator = AutoMinorLocator()
        self.y1minorLocator = AutoMinorLocator()
        self.x2minorLocator = AutoMinorLocator()
        self.y2minorLocator = AutoMinorLocator()
        self.yTwinMinorLocator = AutoMinorLocator()   # twin axis for efficiency plots

        return



    def setDefaults(self,hist,**kwargs):
        """
        Set parameters passed by the user to the plot.
        For matplotlib arguments with multiple keywords, cross-check them here
        """
        mult_keywords = {"lc":"linecolor",
                         "ls":"linestyle",
                         "lw":"linewidth",
                         "ec":"edgecolor",
                         "mec":"markeredgecolor",
                         "mfc":"markerfacecolor"}
        kwargs_keys = kwargs.keys()
        mult_keys   = mult_keywords.keys()

        for k in kwargs_keys:
            if hasattr( hist, k ):
                setattr( hist, k, kwargs[k] )               # overwrite default
                _ = kwargs.pop(k)                           # remove from kwargs

            # check args with multiple keywords
            if k in mult_keys:
                setattr( hist,mult_keywords[k],kwargs[k] )  # overwrite default
                _ = kwargs.pop(k)                           # remove from kwargs

        hist.kwargs = kwargs                                # set user-defined arguments

        return


    def Add(self,data,name='',weights=None,ratios=None,**kwargs):
        """
        Add histogram data for this figure.
        @param data             data for plot (python array or ROOT TH1)
        @param name             name to identify histogram object
        @param weights          weights for making histogram data
        @param ratios           plot in ratios: {"partner":True/False} for numerator/denominator
        @param kwargs           arguments for matplotlib options
                   -- hist:     https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist.html
                   -- hist2d:   https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist2d.html
                   -- errorbar: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.errorbar.html
                   -- lineplot: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html
        """
        hist = HepPlotterData()
        hist.name = name

        self.setParameters(hist,kwargs)

        # convert data for internal use (uniform I/O)
        if isinstance(data,ROOT.TH1):
            if not kwargs.get("isTH1"): hist.isTH1 = True   # plot TH1/TH2
            if self.dimensions==1:
                h_data = hpt.hist2list(data,name=name,reBin=self.rebin,normed=hist.normed)
            else:
                h_data = hpt.hist2list2D(data,name=name,reBin=self.rebin,normed=hist.normed)
        elif isinstance(data,ROOT.TEfficiency):
            if not kwargs.get("isTEff"): hist.isTEff = True # plot TEfficiency
            h_data = hpt.TEfficiency2list(data)
        else:
            # others, e.g., numpy data that needs to be put into a histogram
            if self.dimensions==1:
                h_data = hpt.data2list(data,weights=weights,normed=hist.normed,binning=self.binning)
            else:
                h_data = hpt.data2list2D(data,weights=weights,normed=hist.normed,binning=self.binning)
        ## FUTURE:
        ## Add support for data that doesn't need to be put into a histogram (line data)

        hist.isHistogram = (hist.draw_type in ['step','stepfilled'])
        hist.isErrorbar  = (hist.draw_type == 'errorbar')
        hist.ratios = ratios
        hist.data   = h_data

        # store in this list to use throughout the class
        self.data2plot[name] = hist

        return



    def execute(self):
        """Execute the plot.  Done in inherited class"""
        pass



    def text_labels(self,axis=None):
        """Labels for CMS plots"""
        if self.dimensions==2 and self.CMSlabel!='outer':
            print " WARNING :: You have chosen a label position "
            print "            not considered for 2D plots. "
            print "            Please consider changing the "
            print "            parameter 'CMSlabel' to 'outer'."

        if axis is None: axis = self.ax1
        text = self.text_coords[self.CMSlabel]

        ## CMS, Energy, and LUMI labels
        cms_stamp    = hpl.CMSStamp(self.CMSlabelStatus)
        lumi_stamp   = hpl.LumiStamp(self.lumi)
        energy_stamp = hpl.EnergyStamp()

        cms_stamp.coords    = [text['x'][0], text['y'][0]]
        lumi_stamp.coords   = [text['x'][1], text['y'][1]]  # always drawn with the energy
        energy_stamp.coords = [text['x'][1], text['y'][1]]

        # modify defaults
        if self.CMSlabel == 'top right':
            cms_stamp.ha = 'right'
        if self.dimensions==2:
            cms_stamp.va    = 'bottom'   # change alignment for 2d labels
            lumi_stamp.ha   = 'right'
            energy_stamp.ha = 'right'


        axis.text(cms_stamp.coords[0],cms_stamp.coords[1],cms_stamp.text,fontsize=cms_stamp.fontsize,
                      ha=cms_stamp.ha,va=cms_stamp.va,transform=axis.transAxes)

        energy_lumi_text = energy_stamp.text+", "+lumi_stamp.text if self.plotLUMI else energy_stamp.text
        axis.text(energy_stamp.coords[0],energy_stamp.coords[1],energy_lumi_text,
                      fontsize=energy_stamp.fontsize,ha=energy_stamp.ha,va=energy_stamp.va,
                      color=energy_stamp.color,transform=axis.transAxes)


        ## Extra text -- other text labels the user wants to add
        for txtItem in self.extra_text.texts:
            if txtItem.transform is None: txtItem.transform = axis.transAxes
            axis.text( txtItem.coords[0],txtItem.coords[1],txtItem.text,
                           fontsize=txtItem.fontsize,ha=txtItem.ha,va=txtItem.va,
                           color=txtItem.color,transform=txtItem.transform  )

        return



    def savefig(self):
        """Save the figure"""
        plt.savefig(self.saveAs+'.'+self.format,
                    format=self.format,dpi=300,bbox_inches='tight')
        plt.close()

        return


## THE END
