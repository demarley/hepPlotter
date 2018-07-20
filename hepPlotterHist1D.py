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
import tools

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
import numpy as np


class HepPlotterHist1D(HepPlotter):
    """One dimensional histogram with HepPlotter formatting and structure"""
    def __init__(self):       
        HepPlotter.__init__(self,1)
        # extra options
        self.CMSlabel = 'top left'
        self.legend   = {"ncol":-1,"draw_frame":False}

        self.ratio_plot    = ""
        self.y_label_ratio = "Ratio"
        self.ratio_ylims   = {'ratio':(0.5,1.5),'significance':(0.0,None)}
        self.ratio_yticks  = np.array([0.6,1.0,1.4])

        return


    def execute(self):
        """
        Make the plot!
        return the Figure object to the user (they can edit it if they please)
        """
        if self.ratio_plot:
            fig = plt.figure()
            gs  = gridspec.GridSpec(2,1,height_ratios=[3,1],hspace=0.0)
            self.ax1 = fig.add_subplot(gs[0])
            self.ax2 = fig.add_subplot(gs[1],sharex=self.ax1)
            plt.setp(self.ax1.get_xticklabels(),visible=False)

            self.ylim_ratio = self.ratio_ylims[self.ratio_plot]
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

        ## ratio plot (common to many plots)
        xaxis = None
        if self.ratio_plot:
            self.plotRatio()
            xaxis = self.ax2

        ## CMS label
        if self.CMSlabel is not None:
            self.text_labels()

        ## Legend
        self.drawLegend()

        ## Axis labels
        self.set_xaxis(xaxis)
        self.set_yaxis()

        return fig


    def plotErrorbars(self,bar2plot,axis=None,**kwargs):
        """Draw errorbar plot(s)"""
        if axis is None: axis = self.ax1

        h_data = bar2plot.data
        data   = h_data.content
        error  = h_data.error
        bins   = h_data.bins
        bin_center = h_data.center

        # if global value for 'normed' is True, set all histograms to 'normed'=True
        # unless a kwarg is passed to override this (e.g., the ratio plot isn't normalized)
        if self.normed and not ('normed' in kwargs):
            bar2plot.normed = True

        # if the errorbar plot needs to be normalized, 
        # you need to make a histogram from the data, then plot the errorbar
        if hasattr(bar2plot,"normed") and bar2plot.normed:
            original_data  = data.copy()
            data,bin_edges = np.histogram(bin_center,bins=bins,weights=data,density=True)
            error = error * (data/original_data)  # scale error bars appropriately

        # Modify axis scale
        # set log scale if global parameter is set, unless kwarg overrides it
        if not ('logplot' in kwargs):
            if self.logplot["y"]: axis.set_yscale('log')
        if self.logplot["x"]: axis.set_xscale('log')

        p,c,b = axis.errorbar(bin_center,data,yerr=error,fmt=bar2plot.fmt,
                              label=bar2plot.label,
                              ecolor=bar2plot.ecolor,
                              mec=bar2plot.markeredgecolor,
                              mfc=bar2plot.markerfacecolor,
                              markersize=bar2plot.markersize,
                              **bar2plot.kwargs)
        bar2plot.plotData = data

        return bar2plot


    def plotHistograms(self,histogram,axis=None,uncertainty=False,**kwargs):
        """Plot histograms"""
        if axis is None: axis = self.ax1

        h_data  = histogram.data
        data    = h_data.content
        error   = h_data.error
        binning = h_data.bins
        bin_center = h_data.center

        # if global value for 'normed' is True, set all histograms to 'normed'=True
        # unless a kwarg is passed to override this
        if self.normed and not ('normed' in kwargs):
            histogram.kwargs["density"] = True

        this_label = histogram.label
        if histogram.draw_type=='step':
            # Changing legend for step histograms -> a line instead of a rectangle
            this_label = None
            _ = axis.plot([],[],
                          color=histogram.edgecolor,lw=histogram.linewidth,
                          ls=histogram.linestyle,label=histogram.label)

        # Make the histogram
        data,b,p = axis.hist(bin_center,bins=binning,weights=data,
                             label=this_label,
                             lw=histogram.linewidth,histtype=histogram.draw_type,
                             ls=histogram.linestyle,
                             color=histogram.color,
                             edgecolor=histogram.edgecolor,
                             **histogram.kwargs)

        # Modify axis scale
        # set log scale if global parameter is set, unless kwarg overrides it
        if not ('logplot' in kwargs):
            if self.logplot["y"]: axis.set_yscale('log')
        if self.logplot["x"]: axis.set_xscale('log')

        histogram.plotData = data

        # only use this for histograms because errorbar has 'yerr' option
        if self.drawStatUncertainty and uncertainty:
            self.plotUncertainty(histogram,axis)

        return histogram



    def plotRatio(self):
        """
        Ratio plot in frame under main plot
           e.g., up/down systs with nominal or compare two distributions

           'ratios' stored as [ (partner,True/False),... ]
           where
               partner      The other histogram with which to plot the ratio
               True/False   True=numerator; False=denominator
        """
        drawn_ratios = []
        for d in self.data2plot:
            data2plot = self.data2plot[d]
            partners  = data2plot.ratios            # partner(s) for ratio

            if not partners: continue      # no ratio plot, skip

            for p,partner in enumerate(partners):
                names = (data2plot.name,partner[0]) if partner[1] else (partner[0],data2plot.name)
                if names in drawn_ratios: continue
                drawn_ratios.append(names)

                p_data = self.data2plot[partner[0]]  # load data of ratio 'partner'

                if partner[1]:
                    numerator   = data2plot
                    denominator = p_data
                else:
                    numerator   = p_data
                    denominator = data2plot

                num_data = numerator.data.content
                den_data = denominator.data.content

                # put information into new instance -- copy original information
                ratio_data = HepPlotterData()
                for key in dir(numerator):
                    if key=='data': continue
                    original = getattr(numerator,key)
                    try:
                        setattr( ratio_data, key, original )
                    except AttributeError:
                        continue
                ratio_data.kwargs['density'] = False

                # calculate the ratio depending on the user setting ('ratio' or 'significance')
                if self.ratio_plot=="ratio":
                    ratio_data.data.content = (num_data / den_data).copy()
                    ratio_data.data.error   = (numerator.data.error / den_data).copy()
                elif self.ratio_plot=="significance":
                    # s/sqrt(b) for now
                    ratio_data.data.content = (num_data / np.sqrt(den_data)).copy()
                    ratio_data.data.error   = None
                else:
                    print " WARNING :: Un-specified method for ratio plot '{0}' ",format(self.ratio_plot)
                    print "            Setting ratio equal to 1.0 with no uncertainties    "
                    ratio_data.data.content = np.ones( len(num_data) )
                    ratio_data.data.error   = [0 for _ in residual]

                # make the ratio plot
                if numerator.isErrorbar:
                    inf_ind = np.where( np.isinf(ratio_data.data.content) )
                    ratio_data.data.content[inf_ind] = np.nan
                    ratio_data.kwargs["xerr"] = numerator.data.width

                    self.plotErrorbars(ratio_data,axis=self.ax2,normed=False,logplot=False)
                else:
                    # remove NaN/inf values from hist
                    content = ratio_data.data.content
                    max_con = max( [i for i in content if not (np.isnan(i) or np.isinf(i))] )
                    nan_ind = np.where( np.isnan(content) ) 
                    inf_ind = np.where( np.isinf(content) )
                    ratio_data.data.content[nan_ind] = 0.
                    ratio_data.data.content[inf_ind] = 0.
                    ratio_data.data.content[inf_ind] = 10.*max_con  # random large value

                    self.plotHistograms(ratio_data,axis=self.ax2,uncertainty=True,
                                        normed=False,logplot=False)

            ## Ratio Uncertainties
            if self.drawStatUncertainty:
                self.plotUncertainty(data2plot,self.ax2,normalize=True)

        ## Add extra line for ratio plot
        if self.ratio_plot=='ratio':
            self.ax2.axhline(y=1,ls='--',c='k',zorder=1,lw=1)  # line to 'guide the eye'

        ## Modify tick marks for y-axis
        axis_ticks = self.ratio_yticks if self.ratio_plot=='ratio' else self.ax2.get_yticks()[::2]
        self.ax2.set_yticks(axis_ticks)
        self.ax2.set_ylim(  self.ratio_ylims[self.ratio_plot])
        self.ax2.set_ylabel(self.y_label_ratio,ha='center',va='bottom')

        # Modify tick labels
        formatter = FormatStrFormatter('%g')
        self.ax2.set_yticklabels(np.array([formatter(i) for i in axis_ticks]))

        return



    def plotUncertainty(self,hist,axis,normalize=False):
        """
        Plot uncertainties

        @param axis
        @param name        Name of sample to plot (access data from global dictionaries)
        @param normalize   draw on ratio plot (divide by total prediction)
        """
        error   = hist.data.error
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



    def drawLegend(self,axis=None):
        """Draw the legend"""
        if axis is None: axis = self.ax1

        # get items in the legend (can re-order them here)
        handles, labels = axis.get_legend_handles_labels()

        # Check for extra kwargs the user may have added to override defaults
        kwargs = dict( (k,self.legend[k]) for k in self.legend if (k!="ncol" and k!='draw_frame'))

        if self.legend['ncol']<0: self.legend['ncol'] = 1 if len(handles)<4 else 2

        leg = axis.legend(handles,labels,ncol=self.legend["ncol"],**kwargs)
        leg.draw_frame(self.legend['draw_frame'])

        return


## THE END