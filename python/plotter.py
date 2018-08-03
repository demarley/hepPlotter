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
thisfile = '{0}/cms.mplstyle'.format(os.path.dirname(os.path.abspath(__file__)))
mpl.style.use(thisfile.replace('python','data'))

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter

import tools
import labels



class PlotterData(object):
    """Class for containing data objects to plot"""
    def __init__(self,name=''):
        """The following are nominal attributes of the class with common parameters"""
        self.name  = name
        self.color = 'k' 
        self.fmt   = 'o'
        self.linecolor = 'k'
        self.edgecolor = 'k'
        self.linestyle = '-'
        self.linewidth = 2
        self.ecolor = 'k'
        self.elinewidth = 1.5
        self.markeredgecolor = 'k'
        self.markerfacecolor = 'k'
        self.markersize = 6
        self.label  = ''
        self.data   = None        # Data() object (tools.py)
        self.normed = False
        self.weight = None
        self.draw_type   = 'step' # 'step','stepfilled','errorbar' (others?)
        self.plotData    = None   # get the data from the plot to use later
        self.uncertainty = {}     # kwargs for drawing uncertainty of this object
        self.isHistogram = False  # plt.hist()
        self.isErrobar   = False  # plt.errorbar()
        self.isLinePlot  = False  # basic plt.plot() -- not supported yet
        self.isTH1  = False       # ROOT Histogram
        self.isTEff = False       # ROOT TEfficiency
        self.kwargs = {}          # extra kwargs for plotting



class Plotter(object):
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
        self.stacked    = False       # stack plots (1D only)
        self.normed     = False       # globally set histograms to be normalized
        self.binning    = 20          # integer for number of bins, or list for non-uniform bins
        self.rebin      = 1           # rebin root histograms
        self.label_size = 20          # text labels on plot
        self.underflow  = False       # plot the underflow
        self.overflow   = False       # plot the overflow
        self.xlim       = None        # tuple for (xmin,xmax)
        self.ylim       = None        # tuple for (ymin,ymax)
        self.axis_scale = {}          # scale axes (mainly the y-axis to accommodate legend/labels
        self.x_label = 'x'
        self.y_label = 'y'
        self.extra_text  = labels.PlotText()
        self.lumi     = '35.9'
        self.plotLUMI = False
        self.CMSlabel = None                 # 'top left', 'top right' & 'outer' for 2D
        self.CMSlabelStatus = 'Internal'     # ('Simulation')+'Internal' || 'Preliminary'
        self.format = 'pdf'                  # file format for saving image
        self.saveAs = "result"               # save figure with name
        self.logplot = {"y":False,"x":False,"data":False}  # plot axes or data (2D) on log scale

        self.text_coords = {'top left': {'x':[0.03]*3,        'y':[0.96,0.89,0.82]},\
                            'top right':{'x':[0.97]*3,        'y':[0.96,0.89,0.82]},\
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

        if not self.axis_scale:
            self.axis_scale = {'y':1.4,'x':1.0}
            if self.dimensions==2: self.axis_scale['y'] = 1.0

        return



    def setParameters(self,hist,**kwargs):
        """
        Set parameters passed by the user to the plot.
        For matplotlib arguments with multiple keywords, cross-check them here
        """
        mult_keywords = {"lc":"linecolor",
                         "ls":"linestyle",
                         "lw":"linewidth",
                         "ec":"edgecolor",
                         "ms":"markersize",
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

        hist.kwargs      = kwargs                           # set user-defined arguments

        # relevant for 1-dimension plots
        hist.isHistogram = (hist.draw_type in ['step','stepfilled'])
        hist.isErrorbar  = (hist.draw_type == 'errorbar')

        return


    def Add(self,data,name='',weights=None,**kwargs):
        """
        Add histogram data for this figure.
        @param data             data for plot (python array or ROOT TH1)
        @param name             name to identify histogram object
        @param weights          weights for making histogram data
        @param kwargs           arguments for matplotlib options
                   -- hist:     https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist.html
                   -- hist2d:   https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist2d.html
                   -- errorbar: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.errorbar.html
                   -- lineplot: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html
        """
        hist = PlotterData()
        hist.name = name

        self.setParameters(hist,**kwargs)

        # convert data for internal use (uniform I/O)
        if isinstance(data,ROOT.TH1):
            if not kwargs.get("isTH1"): hist.isTH1 = True   # plot TH1/TH2
            if self.dimensions==1:
                h_data = tools.hist2list(data,name=name,reBin=self.rebin,normed=hist.normed)
            else:
                h_data = tools.hist2list2D(data,name=name,reBin=self.rebin,normed=hist.normed)
        elif isinstance(data,ROOT.TEfficiency):
            if not kwargs.get("isTEff"): hist.isTEff = True # plot TEfficiency
            h_data = tools.TEfficiency2list(data)
        else:
            # others, e.g., numpy data (may or may not need to be put into a histogram)
            if self.dimensions==1:
                h_data = tools.data2list(data,weights=weights,normed=hist.normed,binning=self.binning)
            else:
                h_data = tools.data2list2D(data,weights=weights,normed=hist.normed,binning=self.binning)
        ## FUTURE:
        ## Add support for data that doesn't need to be put into a histogram (line data)

        hist.data = h_data
        self.data2plot[name] = hist   # store in this in a dictionary

        return



    def execute(self):
        """Execute the plot.  Done in inherited class"""
        pass



    def set_xaxis(self,axis=None):
        """Modify the x-axis"""
        if axis is None: axis=self.ax1

        if self.logplot["x"]: axis.set_xscale('log')

        if self.xlim is not None:
            axis.set_xlim(self.xlim)

        axis.set_xlabel(self.x_label,ha='right',va='top',position=(1,0))

        # Modify tick labels
        formatter  = FormatStrFormatter('%g')
        axis_ticks = axis.get_xticks()

        if self.logplot["x"]:
            tick_labels = [r"10$^{\text{%s}}$"%(int(np.log10(i))) if i>0 else '' for i in axis_ticks]
        else:
            tick_labels = [formatter(i) for i in axis_ticks]

        axis.set_xticklabels(tick_labels)

        return



    def set_yaxis(self):
        """Modify the y-axis"""
        if self.logplot["y"]: self.ax1.set_yscale('log')

        if self.ylim is not None:
            self.ax1.set_ylim(self.ylim)
        else:
            ymax_scale = self.axis_scale['y']
            self.ax1.set_ylim(0.,ymax_scale*self.ax1.get_ylim()[1])  # scale axis to accommodate legend/text

        self.ax1.set_ylabel(self.y_label,ha='right',va='bottom',position=(0,1))

        # Modify tick labels
        formatter  = FormatStrFormatter('%g')
        axis_ticks = self.ax1.get_yticks()

        if self.logplot["y"]:
            tick_labels = [r"10$^{\text{%s}}$"%(int(np.log10(i))) if i>0 else '' for i in axis_ticks]
            tick_labels = ["",""]+tick_labels[2:]
        else:
            tick_labels = [formatter(i) for i in axis_ticks]
            tick_labels = [""]+tick_labels[1:]

        self.ax1.set_yticklabels( tick_labels )

        return



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
        cms_stamp    = labels.CMSStamp(self.CMSlabelStatus)

        cms_stamp.coords = [text['x'][0], text['y'][0]]
        if self.CMSlabel=='top right':
            cms_stamp.ha = 'right'
        if self.dimensions==2 or self.CMSlabel=='outer':
            cms_stamp.va = 'bottom'   # change alignment for 2d labels

        energy_stamp = labels.EnergyStamp()
        energy_stamp.coords = [0.99,1.0]
        energy_stamp.ha = 'right'
        energy_stamp.va = 'bottom'

        # only need this if self.plotLUMI is True and you aren't writing the energy
        lumi_stamp = labels.LumiStamp(self.lumi)
        lumi_stamp.coords = [0.99,1.0]  # drawn with energy
        lumi_stamp.ha = 'right'
        lumi_stamp.va = 'bottom'


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
        plt.savefig(self.saveAs+'.'+self.format)
        plt.close()

        return


## THE END
