"""
Created:         6 April     2016
Last Updated:   11 July      2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University

Bennett Magy
bmagy@umichSPAMNOT.edu
University of Michigan, Ann Arbor, MI 48109
-----

Class to make a simple instance each time we want some basic plots!

This does not include an interface to load/access data.
Here we just plot the 2D data we're given.
"""
from hepPlotter import HepPlotter,HepPlotterData

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

import hepPlotterTools as hpt



class HepPlotter2D(HepPlotter):
    """Two dimensional histogram with HepPlotter formatting and structure"""
    def __init__(self):
        HepPlotter.__init__(self,"histogram",1)
        # extra options
        self.CMSlabel = 'outer'
        self.bin_errors = {}
        self.bin_yields = {}          # parameters for text of bin yields

        return



    def initialize(self):
        """Initialize the plot and set basic parameters"""
        HepPlotter.initialize(self)

        ## 2D plot -- set some specific options
        if self.colormap is None: 
            self.setColormap()

        # set default parameters for bin yields/errors text
        def_params = {"color":"k","ha":"center","va":"center"}
        for k in def_params:
            if not self.bin_yields.get(k): self.bin_yields[k] = def_params[k]
            if not self.bin_errors.get(k): self.bin_errors[k] = def_params[k]

        return



    def execute(self):
        """
        Make the plot using `pyplot.hist2d()`.
        return the Figure object to the user (they can edit it if they please)
        """
        fig,self.ax1 = plt.subplots()

        name         = self.data2plot.keys()[0]
        data2plot    = self.data2plot[name]     # only one histogram is supported in 2D plots

        h_data       = data2plot.data
        h_error      = data2plot.error
        x_bin_center = data2plot.center['x']
        y_bin_center = data2plot.center['y']
        binns_x      = data2plot.bins['x']
        binns_y      = data2plot.bins['y']

        # Make the plot
        norm2d = LogNorm() if self.logplot['data'] else None

        plt.hist2d(x_bin_center,y_bin_center,bins=[binns_x,binns_y],
                   weights=h_data,cmap=self.colormap,norm=norm2d,**data2plot.kwargs)

        # Plot bin values/errors, if requested
        if self.bin_yields: self.plotBinYields(h_data, x_bin_center,y_bin_center)
        if self.bin_errors: self.plotBinErrors(h_error,x_bin_center,y_bin_center)

        # Configure the colorbar
        self.drawColorbar()

        # Configure the labels
        if self.CMSlabel is not None:
            self.text_labels()

        return fig



    def drawColorbar(self):
        """
        Draw the vertically-oriented colorbar.

        * Not many customizable options here because the colorbar is a 'plt' object
        * and the options are applied to attributes.  
        * User needs to modify or extend this function.
        """
        cbar = plt.colorbar()

        if self.colorbar:
            try:
                cbar.ax.set_ylabel(self.colorbar["title"])
            except KeyError:
                print "WARNING : Key 'title' not specified for colorbar"

            # Modify tick labels
            cbar_fsize = int(mpl.rcParams['axes.labelsize']*0.75)
            cbar.ax.set_yticklabels(cbar.ax.get_yticklabels(),fontsize=cbar_fsize)

            # Modify tick sizes
            for tick in ['major','minor']:
                try:
                    length = self.colorbar["ytick.{0}.size".format(tick)]
                except KeyError:
                    length = 0
                cbar.ax.yaxis.set_tick_params(which=tick,length=length)

        return



    def plotBinYields(self,h_data=[],x_bin_center=[],y_bin_center=[],bin_data=None):
        """Print bin values inside the plots for each bin."""
        if bin_data is None: bin_data = self.bin_yields

        if isinstance(bin_data["color"],basestring):
            color = bin_data["color"]
            bin_data["color"] = [color for _ in x_bin_center]

        for i,e in enumerate(h_data):
            self.ax1.text(x_bin_center[i],y_bin_center[i],
                          "{0:.1f}".format(e),
                          ha=bin_data["ha"],va=bin_data["va"],
                          color=bin_data["color"][i])

        return



    def plotBinErrors(self,h_data=[],x_bin_center=[],y_bin_center=[]):
        """Print bin errors inside the plots for each bin."""
        self.plotBinYields(h_data,x_bin_center,y_bin_center,bin_data=self.bin_errors)
        return



    def setColormap(self,h):
        """Colormap setup for 2D plots"""
        linear_cmap_choice  = np.random.choice(["Reds","Blues","Greens"])
        default_cmap_choice = np.random.choice(["viridis","magma","inferno","plasma"])

        colormaps = {'diverge':"bwr",
                     'linear': linear_cmap_choice,
                     'default':default_cmap_choice}
        try:
            self.colormap = getattr( plt.cm,colormaps[self.colormap] )   # use a pre-defined choice
        except:
            try:
                self.colormap = getattr(plt.cm,self.colormap)            # access map from matplotlib choices
            except AttributeError:
                print " WARNING : Unsupported colormap '{0}'".format(self.colormap)
                print "           Choosing the colormap based on data structure "

                datastructure = hpt.getDataStructure( h.data.data )
                self.colormap = getattr( plt.cm,datastructure )

        return

## THE END