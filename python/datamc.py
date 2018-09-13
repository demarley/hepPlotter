"""
Created:         2 August    2018
Last Updated:    2 August    2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University
-----
Plot comparisons between data and mc (prediction).
"""
from math import fabs
from copy import deepcopy

from histogram1D import Histogram1D
from plotter import PlotterData
import tools

import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np






class DataMC(Histogram1D):
    """One dimensional histogram with HEP plotter formatting and structure"""
    def __init__(self):
        Histogram1D.__init__(self)
        self.stack_signal = False
        self.normed       = False
        self.blind_data   = None    # blind data (just on/off for now -- expand!)
                                    # Overrides any data/asimov you pass to hepPlotter
        self.asimov       = False   # Draw 'asimov' data (total background)
                                    # Overrides any data you pass to hepPlotter

        self.ratio.value  = "ratio"
        self.ratio.ylabel = "Data/MC"
        self.datamc_denominator = 'total_bckg' # 'total_bckg_signal'

        self.uncertainty_colors = {'stat':'#66b266','syst':'#99cc99','statsyst':'#cce5cc'}
        self.uncertainty_band   = ['stat']  
        # list of uncertainty bands (ratio plot) to
        # individually draw:  ['stat', 'syst', 'statsyst']

        self.datamc_uncertainty = {}

        return


    def execute(self):
        """
        Make the plot!
        return the Figure object to the user (they can edit it if they please)
        """
        fig = plt.figure()
        gs  = gridspec.GridSpec(2,1,height_ratios=[3,1],hspace=0.0)
        self.ax1 = fig.add_subplot(gs[0])
        self.ax2 = fig.add_subplot(gs[1],sharex=self.ax1)
        plt.setp(self.ax1.get_xticklabels(),visible=False)


        # organize data for plotting
        data2plot   = None # data points (only support one source of data in data/mc plot)
        bckg2plot   = []   # backgrounds
        signal2plot = []   # signal distribution

        for e in self.data2plot:
            d2p = self.data2plot[e]
            sample_type = d2p.draw_type

            if sample_type=='data':         data2plot = d2p
            elif sample_type=='background': bckg2plot.append(d2p)
            elif sample_type=='signal':     signal2plot.append(d2p)


        ##  Data points
        if data2plot is not None:
            if self.asimov:
                data2plot = self.make_asimov(bckg2plot)

            if self.blind_data is not None:
                data2plot = self.make_blind(data2plot)

            data2plot.draw_type = 'errorbar'
            data2plot.kwargs["zorder"] = 125
            tmp_data  = self.plotErrorbar(data2plot)
            data2plot = tmp_data
        elif data2plot is None:
            data2plot = PlotterData('data')
            data2plot.data         = tools.Data()
            data2plot.data.content = np.array( [np.nan for _ in bckg2plot[0].data.content] )

            if self.asimov:
                # Use the total bckg to plot 'asimov' data
                data2plot = self.make_asimov(bckg2plot)
                data2plot.draw_type = 'errorbar'
                data2plot.kwargs["zorder"] = 125
                tmp_data  = self.plotErrorbar(data2plot)
                data2plot = tmp_data
        self.data2plot[data2plot.name] = data2plot  # update the dictionary

        ##  Background samples
        bottom   = None                             # 'bottom' for stacking histograms
        bckg_unc = None
        for n,hist2plot in enumerate(bckg2plot):
            hist2plot.draw_type = 'stepfilled'
            hist2plot.kwargs["zorder"] = 100+n
            hist2plot.kwargs["bottom"] = bottom     # stack the background contributions

            tmp_hist2plot = self.plotHistogram(hist2plot,uncertainty=hist2plot.uncertainty)
            bckg2plot[n]  = tmp_hist2plot           # update data

            try:
                bottom += hist2plot.plotData.copy() # modify bottom
            except:
                bottom  = hist2plot.plotData.copy()

            if bckg_unc is None:
                bckg_unc  = np.square(hist2plot.data.error.copy())
            else:
                bckg_unc += np.square(hist2plot.data.error.copy())

        # store the total background prediction and uncertainty
        prediction = deepcopy(bckg2plot[0])       # copy attributes from bckg2plot
        prediction.plotData     = bottom.copy()   # copy data from sum of all bckgs
        prediction.data.content = bottom.copy()
        prediction.data.error   = np.sqrt( bckg_unc )
        self.data2plot['total_bckg'] = prediction

        for i in bckg2plot: self.data2plot[i.name] = i  # update the dictionary


        ##  Signal distributions (designed for BSM, but could support a SM signal)
        for n,hist2plot in enumerate(signal2plot):
            hist2plot.draw_type = 'stepfilled' if self.stack_signal else 'step'
            hist2plot.kwargs["zorder"] = 150+n
            hist2plot.kwargs["bottom"] = bottom if self.stack_signal else None

            tmp_hist2plot  = self.plotHistogram(hist2plot,uncertainty=self.uncertainty)
            signal2plot[n] = tmp_hist2plot         # update data

            try:
                bottom += hist2plot.plotData.copy()      # stack signal on top of background
            except:
                bottom  = hist2plot.plotData.copy()
        for i in signal2plot: self.data2plot[i.name] = i # update the dictionary


        ## ratio plot [data/mc (mc=total background)]
        self.ratio.Add(numerator=data2plot.name,denominator=self.datamc_denominator)

        #  ratio plot uncertainty band (uncertainty on the prediction)
        #  there are no data points to draw, we just want the uncertainty (centered on 1.)
        self.drawPredictionUncertainty()

        self.plotRatio()


        ## Axis ticks/labels
        self.set_xaxis(self.ax2)
        self.set_yaxis()

        ## CMS label
        self.text_labels()

        ## Legend
        self.drawLegend()

        return fig



    def drawPredictionUncertainty(self,axis=None):
        """
        Draw the uncertainty on the prediction.
        By default assume this is done on the smaller ratio plot (author's style).
        """
        hist = deepcopy(self.data2plot['total_bckg'])

        uncertainty_band = {'alpha':1,'zorder':10}

        if axis is None:
            axis = self.ax2
            uncertainty_band['normalize'] = True

        # include user options in uncertainty band drawing properties
        uncertainty_band.update(self.datamc_uncertainty)

        # loop over possible uncertainty bands
        # e.g., may want to plot 'stat' and 'statsyst' at the same time
        for band in self.uncertainty_band:
            fc = uncertainty_band.get('facecolor',self.uncertainty_colors[band])
            uncertainty_band['facecolor'] = fc

            self.plotUncertainty(hist,axis,**uncertainty_band)

        return


    def make_asimov(self,backgrounds):
        """Calculate asimov (pseudo-data) from backgrounds"""
        pseudo      = sum( [x.data.content for x in backgrounds] )
        asimov_data = PlotterData('data')
        asimov_data.data = deepcopy(backgrounds[0].data)  # copy attributes of background
        asimov_data.data.content = pseudo
        asimov_data.data.error   = np.array( [np.sqrt(i) for i in pseudo] )
        return asimov_data


    def make_blind(self,data):
        """
        Blind the data distribution in the plots.
        
        - Simple boolean ON/OFF    : mode = 'bool'
        - Value cut                : mode = 'value';        value = x>cut
        - Signficance cut          : mode = 'significance'; value = <significance>
        - % contribution in a bin  : mode = 'yield';        value = <percent_yield>
        """
        if self.blind_data=='bool':
            # mask all data points
            data.data.content = np.array( [np.nan for _ in data.data.content] )

        return data


## THE END
