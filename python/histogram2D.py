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

Class to plot basic 2D histograms.

This does not include an interface to load/access data.
Here we just plot the 2D data we're given.
"""
from plotter import Plotter,PlotterData

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

import tools



class Histogram2D(Plotter):
    """Plotting two dimensional data with HEP plotter formatting and structure"""
    def __init__(self):
        Plotter.__init__(self,2)
        # extra options
        self.CMSlabel = 'outer'
        self.colormap = None
        self.colorbar = {}          # parameters for colorbar on 2D plot

        # write bin yields/errors on the plot
        self.write_bin_errors = False
        self.write_bin_yields = False

        self.bin_text = {"color":"k","ha":"center","va":"center"}

        return



    def execute(self):
        """
        Make the plot using `pyplot.hist2d()`.
        return the Figure object to the user (they can edit it if they please)
        """
        fig,self.ax1 = plt.subplots()

        name      = self.data2plot.keys()[0]
        data2plot = self.data2plot[name]     # only one histogram is supported in 2D plots

        h_data = data2plot.data
        data   = h_data.content
        error  = h_data.error
        bins_x = h_data.bins['x']
        bins_y = h_data.bins['y']
        x_bin_center = h_data.center['x']
        y_bin_center = h_data.center['y']

        # Make the plot
        self.setColormap(data)
        data2plot.kwargs['cmap']   = self.colormap
        data2plot.kwargs['norm']   = LogNorm() if self.logplot['data'] else None
        data2plot.kwargs['normed'] = self.normed or data2plot.normed

        h_,x_,y_,i_ = plt.hist2d(x_bin_center,y_bin_center,bins=[bins_x,bins_y],
                      weights=data,**data2plot.kwargs)

        # Plot bin values/errors, if requested
        if self.write_bin_yields: self.writeYields(data, x_bin_center,y_bin_center)
        if self.write_bin_errors: self.writeErrors(error,x_bin_center,y_bin_center)

        # Configure the colorbar
        self.drawColorbar()

        ## Axis ticks/labels
        self.set_xaxis()
        self.set_yaxis()

        ## CMS label
        if self.CMSlabel is not None:
            self.text_labels()

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

        try:
            cbar.ax.set_ylabel(self.colorbar["title"])
        except KeyError:
            print " WARNING : Key 'title' not specified for colorbar."
            print "         : Leaving colorbar title blank. "

        # Modify tick labels
        axis_ticklabels = cbar.ax.get_yticklabels()

        if self.logplot['data']:
            for i,atl in enumerate(axis_ticklabels):
                atl = atl.get_text()
                if not atl.startswith("$10^{"): continue
                exponent = tools.extract(atl)
                axis_ticklabels[i] = r"10$^{\text{%s}}$"%exponent
        else:
            axis_ticklabels = [i.get_text().strip("$") for i in axis_ticklabels]


        cbar_fsize = int(mpl.rcParams['axes.labelsize']*0.75)
        cbar.ax.set_yticklabels(np.array(axis_ticklabels),
                                fontsize=cbar_fsize)

        # Modify tick sizes
        for tick in ['major','minor']:
            length = self.colorbar.get("ytick.{0}.size".format(tick),0)
            cbar.ax.yaxis.set_tick_params(which=tick,length=length)

        return



    def writeYields(self,h_data=[],x_bin_center=[],y_bin_center=[],bin_data=None):
        """Print bin values inside the plots for each bin."""
        if bin_data is None: bin_data = self.bin_text

        if isinstance(bin_data["color"],basestring):
            color = bin_data["color"]
            bin_data["color"] = [color for _ in x_bin_center]

        for i,e in enumerate(h_data):
            self.ax1.text(x_bin_center[i],y_bin_center[i],
                          "{0:.1f}".format(e),
                          ha=bin_data["ha"],va=bin_data["va"],
                          color=bin_data["color"][i])

        return



    def writeErrors(self,h_data=[],x_bin_center=[],y_bin_center=[]):
        """Print bin errors inside the plots for each bin."""
        self.writeYields(h_data,x_bin_center,y_bin_center)
        return



    def setColormap(self,data):
        """Colormap setup for 2D plots"""
        linear_cmap_choice  = np.random.choice(["Reds","Blues","Greens"])
        default_cmap_choice = np.random.choice(["viridis","magma","inferno","plasma"])

        colormaps = {'diverge':"bwr",
                     'linear': linear_cmap_choice,
                     'default':default_cmap_choice}
        try:
            self.colormap = getattr( plt.cm,colormaps[self.colormap] )   # use a hepPlotter option
        except:
            try:
                self.colormap = getattr(plt.cm,self.colormap)            # access map from matplotlib
            except:
                print " WARNING : Unsupported colormap '{0}'".format(self.colormap)
                print "           Choosing the colormap based on data structure "

                datastructure = tools.getDataStructure( data )
                self.colormap = getattr( plt.cm,datastructure )

        return

## THE END
