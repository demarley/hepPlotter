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
import importlib
from collections import OrderedDict

import numpy as np
import matplotlib.style
import matplotlib as mpl

thisfile  = os.path.dirname(os.path.realpath(__file__))
stylefile = thisfile.replace('python','data')+'/cms.mplstyle'
mpl.style.use(stylefile)

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter,LogFormatterSciNotation

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
        self.data   = None         # should be Hist() object from hist.py
        self.normed = False
        self.weight = None
        self.draw_type   = 'step'  # 'step','stepfilled','errorbar' (others?)
        self.plotData    = None    # get the data from the plot to use later
        self.uncertainty = {}      # kwargs for drawing uncertainty of this object
        self.isHistogram = False   # plt.hist()
        self.isErrobar   = False   # plt.errorbar()
        self.isLinePlot  = False   # basic plt.plot() -- not supported yet
        self.isTH1  = False        # ROOT Histogram
        self.isTEff = False        # ROOT TEfficiency
        self.kwargs = {}           # extra kwargs for plotting



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
        self.rebin      = None        # rebin root histograms
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

        self.data_io = None
        self.backend = 'ROOT' if (os.environ.get('ROOTSYS') is not None)
        self.format_minor_ticklabels = False
        self.text_coords = {'top left': {'x':[0.03]*3,        'y':[0.96,0.89,0.82]},\
                            'top right':{'x':[0.97]*3,        'y':[0.96,0.89,0.82]},\
                            'outer':    {'x':[0.02,0.99,0.99],'y':[1.0,1.0,0.9]}}

        return



    def initialize(self):
        """Initialize the plot and set basic parameters"""
        self.ax1    = None
        self.ax2    = None
        self.kwargs = {}

        self.data2plot = OrderedDict()

        if self.format!='pdf': 
            print " WARNING : Chosen format '{0}' may conflict with backend".format(self.format)

        if not self.axis_scale:
            self.axis_scale = {'y':1.4,'x':-1}
            if self.dimensions==2: self.axis_scale['y'] = 1.0

        if self.backend == 'ROOT':
            self.data_io = importlib.import_module('io_root')
        else:
            self.data_io = importlib.import_module('io_uproot')

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
        hist = PlotterData(name)

        self.setParameters(hist,**kwargs)     # set parameters based on kwargs

        io        = self.data_io()
        hist.data = io.convert(data)

        if io.isTH1() and not kwargs.get("isTH1",False):     hist.isTH1  = True
        elif io.isTEff() and not kwargs.get("isTEff",False): hist.isTEff = True

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
        elif self.axis_scale.get('x',-1)>=0:
            xlims = axis.get_xlim()
            xlims = (xlims[0],xlims[1]*self.axis_scale['x'])
            axis.set_xlim(xlims)

        axis.set_xlabel(self.x_label,ha='right',va='top',position=(1,0))

        # Modify tick labels after axis has been adjusted
        axis_ticks = {'major':axis.get_xticks(),
                      'minor':axis.get_xticks(minor=True)}

        tick_labels = self.set_ticklabels(axis_ticks,axis="x")
        axis.set_xticklabels(tick_labels.get('minor',[]), minor=True )
        axis.set_xticklabels(tick_labels['major'])

        return



    def set_yaxis(self):
        """Modify the y-axis"""
        if self.logplot["y"]: self.ax1.set_yscale('log')

        if self.ylim is not None:
            self.ax1.set_ylim(self.ylim)
        elif self.ylim is None and self.dimensions==1:
            # auto-scale upper part of axis to accommodate legend/text
            ylims = self.ax1.get_ylim()
            ylims = (ylims[0],ylims[1]*self.axis_scale['y'])
            self.ax1.set_ylim(ylims)

        self.ax1.set_ylabel(self.y_label,ha='right',va='bottom',position=(0,1))

        # Modify tick labels after axis has been adjusted
        axis_ticks = {'major':self.ax1.get_yticks(),
                      'minor':self.ax1.get_yticks(minor=True)}

        tick_labels = self.set_ticklabels(axis_ticks,axis="y")
        self.ax1.set_yticklabels(tick_labels.get('minor',[]), minor=True )
        self.ax1.set_yticklabels(tick_labels['major'] )

        return


    def set_ticklabels(self,axis_ticks,axis="y"):
        """Set tick labels (major and minor) for x/y-axes"""
        formatter  = FormatStrFormatter('%g')
        tlabels  = {'major':None}
        if self.logplot[axis]:
            tlabels['major'] = [r"10$^{\text{%s}}$"%(int(np.log10(i))) if i>0 else '' for i in axis_ticks['major']]
            if axis=="y": tlabels['major'] = ["",""]+tlabels['major'][2:]

            if self.format_minor_ticklabels:
                mtlabels = []
                for m,mtl in enumerate(axis_ticks['minor']):
                    mtl_sci = format(mtl,'.0e').split("e")
                    mtl_exp = int(mtl_sci[1])
                    mtlabels.append( mtl_sci[0]+r'$\times$10$^\text{%d}$'%mtl_exp )
                tlabels['minor'] = mtlabels
        else:
            tlabels['major'] = [formatter(i) for i in axis_ticks['major']]
            if axis=="y": tlabels['major'] = [""]+tlabels['major'][1:]

        return tlabels


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
        cms_stamp = labels.CMSStamp(self.CMSlabelStatus)

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



    def savefig(self,**kwargs):
        """Save the figure. Use kwargs to modify arguments from style file"""
        plt.savefig(self.saveAs+'.'+self.format,**kwargs)
        plt.close()

        return


## THE END
