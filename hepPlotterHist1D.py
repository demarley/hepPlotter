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

from hepPlotter import HepPlotter,HepPlotterData

import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np



class HepPlotterHist1D(HepPlotter):
    """One dimensional histogram with HepPlotter formatting and structure"""
    def __init__(self):       
        HepPlotter.__init__(self,1)
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
            fig,self.ax1 = plt.subplots()


        ##  Errorbars (should be in foreground:  start with zorder 150)
        bars2plot = [self.data2plot[e] for e in self.data2plot if self.data2plot[e].isErrorbar]

        for n,bar2plot in enumerate(bars2plot):
            bar2plot.kwargs["zorder"] = 150+n
            
            tmp_barplot  = self.plotErrorbars(bar2plot)
            bars2plot[n] = tmp_barplot

        ##  Histograms (should be in background: start with zorder 100)
        hists2plot = [self.data2plot[e] for e in self.data2plot if self.data2plot[e].isHistogram]

        bottom = None                             # 'bottom' for stacking histograms
        for n,hist2plot in enumerate(hists2plot):
            hist2plot.kwargs["zorder"] = 100+n
            hist2plot.kwargs["bottom"] = bottom if self.stacked else None

            tmp_hist2plot = self.plotHistograms(hist2plot,uncertainty=self.drawUncertaintyMain)
            hists2plot[n] = tmp_hist2plot

            if n==0: bottom  = hist2plot.plotData # modify 'bottom' for stacked plots
            else:    bottom += hist2plot.plotData

        ## now that the plots have been made, update the data2plot dictionary
        for i in hists2plot: self.data2plot[i.name] = i
        for i in bars2plot:  self.data2plot[i.name] = i


        ## ratio plot
        if self.ratio_plot:
            self.drawRatio()

        ## y-axis
        if self.ylim is not None:
            self.ax1.set_ylim(self.ylim)
        else:
            if self.ymaxScale is None:
                self.ymaxScale = self.yMaxScaleValues["histogram"]
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


    def plotErrorbars(self,errorbar,axis=None):
        """Draw errorbar plot(s)"""
        if axis is None: axis = self.ax1

        data       = data2plot.data
        error      = data2plot.error
        bin_center = data2plot.center

        if hasattr(bar2plot,"normed") and bar2plot.normed:
            # if the errorbar plot needs to be normalized, 
            # you need to make a histogram from the data, then plot the errorbar
            data, bin_edges = np.histogram(bin_center,bins=data2plot.bins,weights=data,normed=True)

        p,c,b = axis.errorbar(bin_center,data,yerr=error,fmt=bar2plot.fmt,
                              color=bar2plot.color,label=bar2plot.label,
                              zorder=zorder,**bar2plot.kwargs)
        bar2plot.plotData = data

        return errorbar


    def plotHistograms(self,histogram,axis=None,uncertainty=False):
        """Plot histograms"""
        if axis is None: axis = self.ax1

        data       = data2plot.data
        error      = data2plot.error
        bin_center = data2plot.center

        if not histogram.kwargs.get("zorder"):
            histogram.kwargs["zorder"] = 100+n

        this_label = data2plot.label
        if histogram.draw_type=='step':
            # Changing legend for step histograms -> a line instead of a rectangle
            this_label = None
            _ = axis.plot([],[],
                          color=data2plot.linecolor,lw=data2plot.linewidth,
                          ls=data2plot.linestyle,label=data2plot.label)

        # Make the histogram
        data,b,p = axis.hist(bin_center,bins=binning,weights=data,
                             label=this_label,stacked=self.stacked,
                             lw=histogram.linewidth,histtype=data2plot.draw_type,
                             ls=histogram.linestyle,
                             color=histogram.color,
                             edgecolor=histogram.edgecolor,
                             **kwargs)

        if self.logplot["y"]: axis.set_yscale('log')
        if self.logplot["x"]: axis.set_xscale('log')

        data2plot.plotData = data

        # only use this for histograms because errorbar has 'yerr' option
        if self.drawStatUncertainty and uncertainty:
            self.plotUncertainty(data2plot,axis)

        return data2plot


    def drawLegend(self,axis=None):
        """Draw the legend"""
        if axis is None: axis = self.ax1

        # Check for extra kwargs the user may have added to override defaults
        kwargs = dict( (k,self.legend[k]) for k in self.legend if k!="ncol" )

        handles, labels = axis.get_legend_handles_labels() # for re-ordering, if needed
        leg = axis.legend(handles,labels,ncol=self.legend["ncol"],**kwargs)
        leg.draw_frame(False)

        return



    def drawRatio(self):
        """
        Ratio plot in frame under main plot
           e.g., up/down systs with nominal or compare two distributions

           'ratios' stored as [ (partner,True/False),... ]
           where
               partner      The other histogram with which to plot the ratio
               True/False   True=numerator; False=denominator
        """
        drawn_ratios = []
        for data2plot in self.data2plot:
            if not data2plot.ratios: continue      # no ratio plot, skip

            partners = data2plot.ratios            # partner(s) for ratio
            single_partner = len(partners)==1

            names    = None
            num_data = None
            den_data = None

            if not single_partner:
                for p,partner in enumerate(partners):
                    #self.plotRatio(num_data,den_data)
                    names = self.plotRatio(data2plot,partner)
                    if names: drawn_ratios.append( names )
            else:
                names = self.plotRatio(data2plot,partners)
                if names: drawn_ratios.append( names )


            ## Ratio Uncertainties
            if self.drawStatUncertainty:
                self.plotUncertainty(data2plot,self.ax2,normalize=True)

        if self.ratio_type=='ratio':
            self.ax2.axhline(y=1,ls='--',c='k',zorder=1)  # line to 'guide the eye'

        ## Set the axis properties of the ratio y-axis
        self.ax2.set_ylim(ymin=self.ratio_ylims['ymin'][self.ratio_type],
                          ymax=self.ratio_ylims['ymax'][self.ratio_type])
        self.ratio_yticks['significance']=self.ax2.get_yticks()[::2]

        self.ax2.set_yticks(self.ratio_yticks[self.ratio_type])
        self.ax2.set_ylabel(self.y_label_ratio,ha='center',va='bottom')

        return



    def plotRatio(self,data2plot,partner):
        """Make the ratio plot"""
        names  = False
        p_name = partner[0]
        p_data = self.data2plot[p_name]
        isNumerator = partner[1]

        if isNumerator:
            names       = (data2plot.name,p_name)
            numerator   = data2plot
            denominator = p_data
        else:
            names    = (p_name,data2plot.name)
            numerator = p_data
            denominator = data2plot

        if names in drawn_ratios:
            return False

        bin_center = numerator.center
        bin_width  = numerator.width

        # put information into new instance -- copy original information
        ratio_data = hpt.Data()
        for key in dir(num_data):
            original = getattr(numerator,key)
            setattr( ratio_data, key, original )


        num_data = numerator.data
        den_data = denominator.data

        if self.ratio_type=="ratio":
            ratio_data.data  = (num_data / den_data).copy
            ratio_data.error = (numerator.error / den_data).copy
        elif self.ratio_type == "significance":
            # s/sqrt(b)
            ratio_data.data  = (num_data / np.sqrt(den_data)).copy
            ratio_data.error = None                # don't know how to estimate this
        else:
            print " WARNING :: Un-specified method for ratio plot '{0}' ",format(self.ratio_type)
            print "            Setting ratio equal to 1.0 with no uncertainties    "
            ratio_data.data  = np.ones( len(num_data) )
            ratio_data.error = [0 for _ in residual]


        if numerator.isErrorbar:
            ratio_data.kwargs["xerr"] = numerator.width
            self.plotErrorbars(ratio_data,axis=self.ax2)
        else:
            # remove NaN/inf values from hist
            nan_inf_ind = np.where( np.isnan(ratio_data.data) or np.isinf(ratio_data.data) )
            ratio_data.data[nan_inf_ind] = 0.

            self.plotHistograms(ratio_data,axis=self.ax2,uncertainty=True)

        return names



    def plotUncertainty(self,hist,axis,normalize=False):
        """
        Plot uncertainties

        @param axis
        @param name        Name of sample to plot (access data from global dictionaries)
        @param normalize   draw on ratio plot (divide by total prediction)
        """
        error   = hist.error
        nominal = hist.plotData

        # Draw vertical line for errors
        keys = ['up','dn']
        if normalize:
            resid_unc = {'up':(nominal+error)/nominal,
                         'dn':(nominal-error)/nominal}
        else:
            resid_unc = {'up':nominal+error,
                         'dn':nominal-error}

        if hist.isErrorbar:
            # Draw uncertainty as errorbars
            resid_unc = dict( (k,list(resid_unc[k])) for k in keys )  # convert to lists

            error      = [resid_unc['dn'],resid_unc['up']]
            data       = [1. for _ in nominal] if normalize else nominal
            bin_center = 0.5*(self.binning[:-1]+self.binning[1:])

            axis.errorbar(bin_center,data,yerr=error,
                          fmt=hist.fmt,color=hist.color,
                          zorder=100,**hist.kwargs)
        else:
            # Draw uncertainty as rectangles for each bin
            resid_unc = dict( (k,list(resid_unc[k].repeat(2))) for k in keys )  # convert to lists

            fill_between_bins = [self.binning[0]]+list(self.binning[1:-1].repeat(2))+[self.binning[-1]]

            axis.fill_between(fill_between_bins,resid_unc['dn'],resid_unc['up'],
                              zorder=10,color=hist.color,**hist.kwargs)

        return


## THE END
