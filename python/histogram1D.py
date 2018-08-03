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

Class to plot basic 1D histograms

This does not include an interface to load/access data.
Here we just plot the 1D data we're given.
"""
from math import fabs
from copy import deepcopy

from plotter import Plotter,PlotterData
import tools

import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.ticker import FormatStrFormatter
import numpy as np




class Histogram1D(Plotter):
    """One dimensional histogram with HEP plotter formatting and structure"""
    def __init__(self):       
        Plotter.__init__(self,1)
        # extra options
        self.CMSlabel = 'top left'
        self.legend   = {"ncol":-1,"draw_frame":False}
        self.ratio    = PlotterRatio()

        return



    def execute(self):
        """
        Make the plot!
        return the Figure object to the user (they can edit it if they please)
        """
        draw_ratio = False
        if len(self.ratio.ratios2plot)>0:
            fig = plt.figure()
            gs  = gridspec.GridSpec(2,1,height_ratios=[3,1],hspace=0.0)
            self.ax1 = fig.add_subplot(gs[0])
            self.ax2 = fig.add_subplot(gs[1],sharex=self.ax1)
            plt.setp(self.ax1.get_xticklabels(),visible=False)

            draw_ratio = True
        else:
            fig,self.ax1 = plt.subplots()

        # separate data into errorbars and histograms
        bars2plot  = [self.data2plot[e] for e in self.data2plot if self.data2plot[e].isErrorbar]
        hists2plot = [self.data2plot[e] for e in self.data2plot if self.data2plot[e].isHistogram]


        ##  Errorbars (should be in foreground:  start with zorder 150)
        for n,bar2plot in enumerate(bars2plot):
            bar2plot.kwargs["zorder"] = 150+n

            # if global value for 'normed' is True, override object setting
            # need to remake content using histogram (no 'density' kwarg in plt.errorbar())
            if self.normed or bar2plot.normed:
                bar2plot.normed = True

                h_data  = bar2plot.data
                og_data = h_data.content.copy()
                data,be = np.histogram(h_data.center,bins=h_data.bins,
                                       weights=og_data,density=True)
                error = h_data.error * (data/og_data)  # scale error bars
                bar2plot.data.content = data
                bar2plot.data.error   = error

            tmp_barplot  = self.plotErrorbar(bar2plot)
            bars2plot[n] = tmp_barplot            # update data


        ##  Histograms (should be in background: start with zorder 100)
        bottom = None                             # 'bottom' for stacking histograms
        for n,hist2plot in enumerate(hists2plot):
            hist2plot.kwargs["zorder"] = 100+n
            hist2plot.kwargs["bottom"] = bottom if self.stacked else None

            # if global value for 'normed' is True, override object setting
            if self.normed or hist2plot.normed:
                hist2plot.normed = True
                hist2plot.kwargs["density"] = True

            tmp_hist2plot = self.plotHistogram(hist2plot,uncertainty=hist2plot.uncertainty)
            hists2plot[n] = tmp_hist2plot         # update data

            if n==0: bottom  = tmp_hist2plot.plotData.copy() # modify 'bottom' for stacked plots
            else:    bottom += tmp_hist2plot.plotData.copy()

        ## now that the plots have been made, update the data2plot dictionary
        for i in hists2plot: self.data2plot[i.name] = i
        for i in bars2plot:  self.data2plot[i.name] = i

        ## ratio plot
        xaxis = None
        if draw_ratio:
            self.plotRatio()              # make the ratio plot
            xaxis = self.ax2              # draw ratio plot xaxis instead of self.ax1

        ## Axis ticks/labels
        self.set_xaxis(xaxis)
        self.set_yaxis()

        ## CMS label
        if self.CMSlabel is not None:
            self.text_labels()

        ## Legend
        self.drawLegend()

        return fig


    def plotErrorbar(self,bar2plot,axis=None,**kwargs):
        """Draw errorbar plot(s)"""
        if axis is None: axis = self.ax1
        bar2plot.kwargs.update(kwargs)

        h_data = bar2plot.data
        data   = h_data.content
        error  = h_data.error
        bins   = h_data.bins
        bin_center = h_data.center

        p,c,b = axis.errorbar(bin_center,data,yerr=error,fmt=bar2plot.fmt,
                              label=bar2plot.label,
                              ecolor=bar2plot.ecolor,
                              mec=bar2plot.markeredgecolor,
                              mfc=bar2plot.markerfacecolor,
                              markersize=bar2plot.markersize,
                              elinewidth=bar2plot.elinewidth,
                              **bar2plot.kwargs)
        bar2plot.plotData = data

        return bar2plot



    def plotHistogram(self,histogram,axis=None,uncertainty={},**kwargs):
        """Plot histograms"""
        if axis is None: axis = self.ax1
        histogram.kwargs.update(kwargs)

        h_data  = histogram.data
        data    = h_data.content
        error   = h_data.error
        binning = h_data.bins
        bin_center = h_data.center
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
        histogram.plotData = data

        # only use this for histograms because errorbar has 'yerr' option
        # uncertainty might be a bool and just use the options from hist to plot it
        if uncertainty:
            try:
                self.plotUncertainty(histogram,axis,**uncertainty)
            except TypeError:
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
        self.ratio.initialize()       # set parameters for ratio plots
        value = self.ratio.value      # type of plot (ratio/significance)

        for d in self.ratio.ratios2plot:
            numerator   = self.data2plot[d['numerator']]
            denominator = self.data2plot[d['denominator']]

            num_data = numerator.plotData
            den_data = denominator.plotData

            # create new object for plotting ratio (clone numerator properties)
            ratio_data = deepcopy(numerator)

            # using the kwargs option in Ratio.Add(), the user can modify properties
            ratio_kwargs = d['kwargs']
            self.setParameters(ratio_data,**ratio_kwargs)
            uncertainty  = d.get("uncertainty",{})


            # calculate the ratio
            if value=="ratio":
                ratio_data.data.content = (num_data / den_data).copy()
                ratio_data.data.error   = (numerator.data.error / den_data).copy()
            else:
                # significance = s/sqrt(b) for now
                ratio_data.data.content = (num_data / np.sqrt(den_data)).copy()
                ratio_data.data.error   = None

            # make the ratio plot
            inf_ind = np.where( np.isinf(ratio_data.data.content) )  # remove infinities 

            if ratio_data.draw_type=='errorbar':
                ratio_data.data.content[inf_ind] = np.nan
                ratio_data.kwargs["xerr"] = ratio_kwargs.get('xerr',numerator.data.width)
                ratio_data.kwargs["zorder"] = ratio_data.kwargs.get("zorder",150)

                self.plotErrorbar(ratio_data,axis=self.ax2)
            else:
                # remove NaN/inf values from hist
                content = ratio_data.data.content
                max_con = max( [i for i in content if not (np.isnan(i) or np.isinf(i))] )
                nan_ind = np.where( np.isnan(content) )
                ratio_data.data.content[nan_ind] = 0.
                ratio_data.data.content[inf_ind] = 10.*max_con

                if len(inf_ind)>0 and value=='significance':
                    print " WARNING : The significance calculation yielded infinite values"
                    print "         : These will skew the histogram visualization - "
                    print "         : consider changing to an 'errorbar' plot. "

                # set some options unless user specifies them in 'kwargs'
                ratio_data.kwargs["zorder"]  = ratio_data.kwargs.get("zorder",100)
                ratio_data.kwargs['density'] = ratio_kwargs.get('density',False)

                self.plotHistogram(ratio_data,axis=self.ax2,uncertainty=uncertainty)

        ## Add extra line for ratio plot
        if value=='ratio':
            self.ax2.axhline(y=1,ls='--',c='k',zorder=11,lw=1)  # line to 'guide the eye'

        ## Modify tick marks for y-axis
        axis_ticks = self.ratio.yticks if value=='ratio' else self.ax2.get_yticks()[::2]
        self.ax2.set_yticks(axis_ticks)
        self.ax2.set_ylim(  self.ratio.ylim)
        self.ax2.set_ylabel(self.ratio.ylabel,ha='center',va='bottom')

        # Modify tick labels
        formatter = FormatStrFormatter('%g')
        self.ax2.set_yticklabels(np.array([formatter(i) for i in axis_ticks]))

        return



    def plotUncertainty(self,hist,axis,**kwargs):
        """
        Plot uncertainties for 'step' and 'stepfilled' data 
        (errorbar already has this functionality).

        @param hist     PlotterData() object to plot
        @param axis     Axis for drawing the plot
        @param kwargs   Any extra plotting arguments passed here -- these will override
                        parameters in hist and hist.kwargs
                        https://matplotlib.org/api/_as_gen/matplotlib.pyplot.fill_between.html
        """
        hist.kwargs.update(kwargs)

        error   = hist.data.error.copy()
        nominal = hist.plotData.copy()
        binning = hist.data.bins.copy()

        resid_unc = {'up':nominal+error, 'dn':nominal-error}
        if kwargs.get('normalize'):
            resid_unc['up'] /= nominal
            resid_unc['dn'] /= nominal

        # remove kwargs unsupported by fill_between
        remove = ['density','normalize','bottom']
        for rem in remove:
            try:    hist.kwargs.pop(rem)
            except: continue

        # Draw uncertainty as rectangles for each bin
        keys = ['up','dn']
        resid_unc = dict( (k,list(resid_unc[k].repeat(2))) for k in keys )  # convert to lists
        fill_between_bins = [binning[0]]+list(binning[1:-1].repeat(2))+[binning[-1]]

        axis.fill_between(fill_between_bins,resid_unc['dn'],resid_unc['up'],
                          **hist.kwargs)

        return



    def drawLegend(self,axis=None,legend_args=None):
        """Draw the legend"""
        if axis is None: axis = self.ax1
        if legend_args is None: legend_args = self.legend

        # get items in the legend (can re-order them here)
        handles, labels = axis.get_legend_handles_labels()
        if 'extra_handles' in self.legend.keys():
            handles += self.legend['extra_handles']
            labels  += self.legend['extra_labels']
            self.legend.pop('extra_handles')
            self.legend.pop('extra_labels')

        # Check for extra kwargs the user may have added to override defaults
        kwargs = dict( (k,legend_args[k]) for k in legend_args if (k!="ncol" and k!='draw_frame'))

        if legend_args['ncol']<0: legend_args['ncol'] = 1 if len(handles)<4 else 2

        leg = axis.legend(handles,labels,ncol=legend_args["ncol"],**kwargs)
        leg.draw_frame(legend_args['draw_frame'])

        return




class PlotterRatio(object):
    """Simple class to contain information for ratio plot"""
    def __init__(self):
        self.ratios2plot  = []   # list of dictionaries containing information for ratio
        self.listOfRatios = []   # list of tuples (numerator,denominator) to monitor which ratios to plot
        self.value  = 'ratio'    # kind of ratio plot (ratio or significance at the moment)
        self.ylim   = None
        self.yticks = None
        self.ylabel = ''

    def initialize(self):
        """Set some default options if not set by the user"""
        if self.value not in ['ratio','significance']:
            print " WARNING : You have chosen an unsupported method for ratio plot:"
            print "         : > {0}".format(self.value)
            print "         : Setting to 'ratio'."
            self.value = 'ratio'

        if not self.ylabel:
            self.ylabel = 'Ratio' if self.value=='ratio' else r'S/$\sqrt{\text{B}}$'

        if self.value=='ratio':
            if self.ylim is None:   self.ylim   = (0.5,1.5)
            if self.yticks is None: self.yticks = np.array([0.6,1.0,1.4])

        return

    def Add(self,numerator='',denominator='',**kwargs):
        """
        Add a ratio plot to this figure.
        @param numerator        name to identify data for numerator
        @param denominator      name to identify data for denominator
        @param kwargs           arguments for matplotlib options
                                *including drawing an uncertainty band*
                   -- hist:     https://matplotlib.org/api/_as_gen/matplotlib.pyplot.hist.html
                   -- errorbar: https://matplotlib.org/api/_as_gen/matplotlib.pyplot.errorbar.html
        """
        ratio  = (numerator,denominator)
        params = {"numerator":numerator,"denominator":denominator}
        if kwargs.get("uncertainty"):
            params['uncertainty'] = kwargs['uncertainty']
            kwargs.pop('uncertainty')
        params['kwargs'] = kwargs

        if ratio in self.listOfRatios:
            return

        self.listOfRatios.append(ratio)
        self.ratios2plot.append(params)

        return


## THE END
