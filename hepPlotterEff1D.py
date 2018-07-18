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
Here we just plot the 1D data we're given.
"""
from math import fabs
from copy import deepcopy

from hepPlotterHist1D import HepPlotterHist1D

import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np



class HepPlotterEff1D(HepPlotterHist1D):
    """One dimensional histogram with HepPlotter formatting and structure"""
    def __init__(self):       
        HepPlotterHist1D.__init__(self)
        # extra options
        self.CMSlabel = 'top left'

        return


    def execute(self):
        """
        Make the plot!
        return the Figure object to the user (they can edit it if they please)
        """
        self.ratio_ylims  = {}
        self.ratio_yticks = {}

        if self.ratio_plot:
            fig = plt.figure()
            gs  = matplotlib.gridspec.GridSpec(2,1,height_ratios=[3,1],hspace=0.0)
            self.ax1 = fig.add_subplot(gs[0])
            self.ax2 = fig.add_subplot(gs[1],sharex=self.ax1)
            plt.setp(self.ax1.get_xticklabels(),visible=False)

            self.ratio_ylims = {'ymin':{'ratio':0.5,'significance':0.0},
                                'ymax':{'ratio':1.5,'significance':None}}
            self.ratio_yticks = {'ratio':np.asarray([0.6,1.0,1.4]),
                                 'significance':self.ax2.get_yticks()[::2]}
        else:
            fig,self.ax1 = plt.subplots(figsize=self.figsize)


        # draw horizontal lines to guide the eye
        self.ax1.axhline(y=0.25,color='lightgray',ls='--',lw=1,zorder=0)
        self.ax1.axhline(y=0.50,color='lightgray',ls='--',lw=1,zorder=0)
        self.ax1.axhline(y=0.75,color='lightgray',ls='--',lw=1,zorder=0)
        self.ax1.axhline(y=1.00,color='lightgray',ls='--',lw=1,zorder=0)

        # organize data for plotting
        bars2plot  = []   # efficiency data to draw as 'errorbars' (recommended)
        hists2plot = []   # efficiency data to draw as 'step'/'stepfilled' (not recommended)
        phys2plot  = []   # underlying physics distribution to plot as 'step'

        for e in self.data2plot:
            data2plot = self.data2plot[e]

            if data2plot.isTH1:
                phys2plot.append(data2plot)       # TH1 represents physics distribution
                continue

            if data2plot.isErrorbar:    bars2plot.append(data2plot)
            elif data2plot.isHistogram: hists2plot.append(data2plot)


        ##  Errorbars (should be in foreground:  start with zorder 150)
        for n,bar2plot in enumerate(bars2plot):
            bar2plot.kwargs["zorder"] = 150+n

            tmp_barplot  = self.plotErrorbars(bar2plot)
            bars2plot[n] = tmp_barplot

        ##  Histograms (should be in background: start with zorder 100)
        bottom = None                             # 'bottom' for stacking histograms
        for n,hist2plot in enumerate(hists2plot):
            hist2plot.kwargs["zorder"] = 100+n
            hist2plot.kwargs["bottom"] = bottom if self.stacked else None

            tmp_hist2plot = self.plotHistograms(hist2plot,uncertainty=self.drawUncertaintyMain)
            hists2plot[n] = tmp_hist2plot

            if n==0: bottom  = hist2plot.plotData # modify 'bottom' for stacked plots
            else:    bottom += hist2plot.plotData

        ##  Physics distributions
        if phys2plot:
            phys2plot = self.drawPhysics(phys2plot)


        ## now that the plots have been made, update the data2plot dictionary
        for i in hists2plot: self.data2plot[i.name] = i
        for i in bars2plot:  self.data2plot[i.name] = i
        for i in phys2plot:  self.data2plot[i.name] = i

        ## ratio plot
        if self.ratio_plot:
            self.drawRatio()   # possibly to show scale factor (data/mc)

        ## y-axis
        if self.ylim is not None:
            self.ax1.set_ylim(self.ylim)
        else:
            if self.ymaxScale is None:
                self.ymaxScale = self.yMaxScaleValues["efficiency"]
            self.ax1.set_ylim(0., self.ymaxScale * self.ax1.get_ylim()[1])

        self.ax1.set_yticks(self.ax1.get_yticks()[1:])
        self.setYAxis(self.ax1)

        ## x-axis
        if self.xlim is not None:
            plt.xlim(self.xlim)
        x_axis = self.ax2 if self.ratio_plot else self.ax1
        self.setXAxis(x_axis)

        ## axis ticks
        self.setAxisTickMarks()
        plt.tick_params(which='minor', length=4) # ticks

        ## CMS label
        if self.CMSlabel is not None:
            self.text_labels()

        ## Legend
        self.drawLegend()

        return fig



    def drawPhysics(self,data2plot,axis=None):
        """Along with the efficiency curve, draw the physics distribution on twin axis"""
        self.yTwinMinorLocator = AutoMinorLocator()

        if axis is None: axis = self.ax1
        axis_twin = axis.twinx()

        ## Draw the histogram
        for n,data in enumerate(data2plot):

            bottom = None                        # 'bottom' for stacking histograms
            if data.isErrorbar:
                data.kwargs["zorder"] = 70+n     # draw behind efficiency curves
                tmp_dataplot = self.plotErrorbars(data,axis=axis_twin)
            elif data.isHistogram:
                data.kwargs["zorder"] = 50+n
                data.kwargs["bottom"] = bottom if self.stacked else None
                tmp_dataplot = self.plotHistograms(data,axis=axis_twin)

            data2plot[n] = tmp_barplot
            if n==0: bottom  = data.plotData      # modify 'bottom' for stacked plots
            else:    bottom += data.plotData      # this also records the height of plotted data

        axis_twin.yaxis.set_tick_params(which='major', length=8)
        axis_twin.set_ylabel("",fontsize=0,ha='right',va='top')
        axis_twin.set_ylim(ymin=0.0,ymax=self.ymaxScale*max(bottom))

        # modify axis_twin ticks & hide tick labels
        twin_ticks = axis_twin.get_yticks()
        axis_twin.set_yticks( np.linspace( twin_ticks[0],twin_ticks[-1],len(axis.get_yticks())) )
        axis_twin.set_yticklabels([])
        axis.set_zorder(axis_twin.get_zorder()+1) # put ax in front of axis_twin
        axis.patch.set_visible(False)             # hide the 'canvas'
        
        return data2plot


## THE END