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
Here we just plot the 1D data we're given.
"""
from math import fabs
from copy import deepcopy

from hepPlotter import HepPlotter,HepPlotterData

from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
import numpy as np



class HepPlotterHist1D(HepPlotter):
    def __init__(self):       
        HepPlotter.__init__(self,"histogram",1)
        # extra options
        self.CMSlabel = 'top left'

        return


    def execute(self):
        """
        Execute the plot.  Pass arguments concerning the data in the following way:

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
            fig,self.ax1 = plt.subplots(figsize=(10,6))


        ## -- Loop over data to plot
        ##    Errorbars should be in foreground:  start with zorder 150
        ##    Histograms should be in background: start with zorder 100
        y_lim_value = None    # weird protection against the axis autoscaling to values smaller than previously drawn histograms
                              # I can't find the source, and no one else seems to have this problem :/
        max_value   = 0.0
        bottomEdge  = None    # for stacking plots (use this instead of the 'stack' argument
                              # so that all plots can be made in one for-loop)
        for n,data2plot in enumerate(self.data2plot):

kwargs = non-plotting options

            data       = data2plot.data
            error      = data2plot.error
            bin_center = data2plot.center
            bin_width  = data2plot.width
            binning    = data2plot.bins

            kwargs["zorder"] = 150+n

            # Make the errorbar plot
            if hasattr(data2plot,"normed") and data2plot.normed:
                # if the errorbar plot needs to be normalized, you need to make the histogram first
                data, bin_edges = np.histogram(bin_center,bins=binning,weights=data,normed=True)

            p,c,b = self.ax1.plot(bin_center,data,yerr=error,**kwargs)
        ## End loop over data


        if self.ratio_plot:
            self.drawRatio()
            x_axis = self.ax2
        else:
            x_axis = self.ax1

        # y-axis
        if self.ylim is not None:
            self.ax1.set_ylim(self.ylim)
        else:
            if self.ymaxScale is None:
                self.ymaxScale = self.yMaxScaleValues["histogram"]
            self.ax1.set_ylim(0.,self.ymaxScale*y_lim_value)

        self.ax1.set_yticks(self.ax1.get_yticks()[1:])
        self.ax1.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        self.setYAxis(self.ax1)

        # x-axis
        self.ax1.xaxis.set_major_formatter(FormatStrFormatter('%.1f'))
        if self.xlim is not None:
            plt.xlim(self.xlim)
        self.setXAxis(x_axis)

        # axis ticks
        self.setAxisTickMarks()
        plt.tick_params(which='minor', length=4) # ticks

        # CMS label
        if self.CMSlabel is not None:
            self.text_labels()

        # Legend
        self.drawLegend()

        return fig


    def drawLegend(self):
        """Draw the legend"""
        handles, labels = self.ax1.get_legend_handles_labels() # for re-ordering, if needed
        leg = self.ax1.legend(handles,labels,numpoints=1,
                              fontsize=self.legend["fontsize"], #self.label_size-2,
                              ncol=self.legend["n_columns"],
                              columnspacing=self.legend["spacing"], #0.3
                              loc=self.legend["location"])
        leg.draw_frame(False)

        return



    def drawRatio(self):
        """Ratio plot in frame under main plot
           Can handle plotting multiple ratios with one quantity
           (e.g., up/down systs with nominal or compare two distributions)
        """
        drawn_ratios = []
        for i in self.names:

            if self.ratio_partner[i] is None: continue  # no ratio plot for this one, skip

            partners = self.ratio_partner[i]                  # partner(s) for plotting ratio
            single_partner = isinstance(partners,basestring)  # check if there is one or many partners

            if not single_partner:
                for p,partner in partners:
                    if (i,p) in drawn_ratios: continue    # only plot ratios once
                    drawn_ratios.append( (i,p) )

                    self.plotRatio()
###
                histName = num_hists_names[nh]

                if self.ratio_type=="ratio":
                    residual     = deepcopy( num_hist / den_hist )
                    residual_err = deepcopy( self.data2plot[histName]['error'] / den_hist )
                elif self.ratio_type == "significance":
                    residual     = deepcopy( num_hist / np.sqrt(den_hist) )
                    residual_err = [0 for _ in residual] # don't know how to estimate this
                else:
                    print " WARNING :: Un-specified method for ratio plot "
                    print "            Setting ratio equal to 1.0"
                    residual     = np.ones( len(num_hist) )
                    residual_err = [0 for _ in residual]

                # Obtain data points for drawing the ratio
                bin_center = self.data2plot[histName]['center']
                bin_width  = self.data2plot[histName]['width']

                if histName in self.errorbarplot:
                    if self.linestyles[histName]=='solid':
                        self.linestyles[histName] = 'o'
                    lcolor = self.linecolors[histName]
                    self.ax2.errorbar(bin_center,residual,xerr=bin_width,yerr=residual_err,
                                  capsize=0,fmt=self.linestyles[histName],
                                  mec=lcolor,mfc=lcolor,color=lcolor,zorder=100)
                else:
                    residual = np.array( [fabs(rr) if (not np.isnan(rr) and not np.isinf(rr)) else 0.0 for rr in residual] )
                    self.ax2.hist(bin_center,bins=self.binning,weights=residual,
                                  edgecolor=self.linecolors[histName],lw=2,
                                  color=self.colors[histName],ls=self.linestyles[histName],
                                  histtype='step',zorder=100)
###
            else:
                self.plotRatio()

self.histograms[partners]
den_hist = np.array( self.histograms[i] )

            # Draw the ratio!
            for nh,num_hist in enumerate(num_hists):


            ## Simulation Uncertainties
            if self.drawStatUncertainty:
                self.plotUncertainty(self.ax2,pltname=i,normalize=True)

        if self.ratio_type=='ratio':
            self.ax2.axhline(y=1,ls='--',c='k',zorder=1)  # line to 'guide the eye'

        ## Set the axis properties of the ratio y-axis
        self.ax2.set_ylim(ymin=self.ratio_ylims['ymin'][self.ratio_type],
                          ymax=self.ratio_ylims['ymax'][self.ratio_type])
        self.ratio_yticks['significance']=self.ax2.get_yticks()[::2]

        self.ax2.yaxis.set_major_formatter(FormatStrFormatter('%g'))
        self.ax2.xaxis.set_major_formatter(FormatStrFormatter('%g'))

        self.ax2.set_yticks(self.ax2.get_yticks()[::2])
        self.ax2.set_ylabel(self.y_label_ratio,fontsize=self.label_size,ha='center',va='bottom')
        self.ax2.set_yticklabels(self.ax2.get_yticks(),fontProperties,fontsize=self.label_size)

        return



    def plotUncertainty(self,axis,pltname='',normalize=False):
        """
        Plot uncertainties

        @param axis
        @param name        Name of sample to plot (access data from global dictionaries)
        @param normalize   draw on ratio plot (divide by total prediction)
        """
        if self.yerrors[pltname] is None:
            return

        error   = self.uncertainties[pltname]
        nominal = self.histograms[pltname]

        # Draw errorbars that are rectangles for each bin
        if self.yerrors[pltname]=='rectangle':
            if normalize:
                resid_unc = {'up': list(((nominal+error)/nominal).repeat(2)),
                             'dn': list(((nominal-error)/nominal).repeat(2))}
            else:
                resid_unc = {'up': list((nominal+error).repeat(2)),
                             'dn': list((nominal-error).repeat(2))}

            fill_between_bins = self.binning   ## for plotting hatch uncertainty
            fill_between_bins = [self.binning[0]]+list(fill_between_bins[1:-1].repeat(2))+[self.binning[-1]]

            axis.fill_between(fill_between_bins,resid_unc['dn'],resid_unc['up'],
                              zorder=10,color=self.colors[pltname],**self.kwargs[pltname])
        # Draw vertical line for errors
        elif self.yerrors[pltname]=='line':
            if normalize:
                resid_unc = {'up': list(((nominal+error)/nominal)),
                             'dn': list(((nominal-error)/nominal))}
            else:
                resid_unc = {'up': list((nominal+error)),
                             'dn': list((nominal-error))}

            error      = [resid_unc['dn'],resid_unc['up']]
            data       = [1. for _ in nominal] if normalize else nominal
            bin_center = 0.5*(self.binning[:-1]+self.binning[1:])
            p,c,b = self.ax1.errorbar(bin_center,data,yerr=error,
                                     fmt=self.linestyles[pltname],color=self.colors[pltname],
                                     zorder=100,**self.kwargs[pltname])

        return


## THE END