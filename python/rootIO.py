"""
Created:        17 October   2018
Last Updated:   19 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple functions to help accessing data with c++ ROOT
"""
from hist import Hist
from baseIO import BaseIO


class UprootIO(BaseIO):
    def __init__(self):
        BaseIO.__init__(self)

    def convert(data):
        """Convert ROOT data into uniform format for framework"""
        self._isHistogram  = isinstance(data,ROOT.TH1)
        self._isEfficiency = isinstance(data,ROOT.TEfficiency)

        # convert data for internal use (uniform I/O)
        h_data = Hist()
        if isHistogram:
            if not kwargs.get("isTH1"): hist.isTH1 = True   # plot TH1/TH2
            if self.dimensions==1:
                h_data = tools.hist2list(data,reBin=self.rebin,normed=hist.normed)
            else:
                h_data = tools.hist2list2D(data,reBin=self.rebin,normed=hist.normed)
        elif isEfficiency:
            if not kwargs.get("isTEff"): hist.isTEff = True # plot TEfficiency
            h_data = tools.TEfficiency2list(data)

        return h_data


    def hist2data(histo,normed=False,reBin=None):
        """Convert ROOT histogram for internal use."""
        results = Hist()
            if not histo.GetSumw2N():
                histo.Sumw2()

            if reBin is not None:
                # Use ROOT functionality to re-bin histogram
                try:
                    histo.Rebin(reBin)
                except TypeError:
                    newname = histo.GetName()+"_"+name
                    histo.Rebin(len(reBin)-1,newname,reBin)
                    histo = ROOT.gROOT.FindObject( newname )

            if normed:
                integral = histo.Integral()
                histo.Scale(1./integral)

            bin_centers  = []
            bin_contents = []
            bin_errors   = []
            bin_widths   = []
            bin_edges    = [histo.GetXaxis().GetBinLowEdge(1)]

            for i in xrange(1,histo.GetNbinsX()+1):
                bin_edges.append(histo.GetXaxis().GetBinUpEdge(i))
                bin_centers.append(histo.GetBinCenter(i))
                bin_contents.append(histo.GetBinContent(i))
                bin_errors.append(histo.GetBinError(i))
                bin_widths.append(histo.GetXaxis().GetBinWidth(i)*0.5)

            results.content = np.array(bin_contents)
            results.error   = np.array(bin_errors)
            results.bins    = np.array(bin_edges)
            results.center  = bin_centers
            results.width   = bin_widths

        return results

    return results



    def hist2data2D(histo,reBin,normed,results):
    """Convert ROOT histogram for internal use."""
        results = Hist()

        if _ROOT_available:
            if not histo.GetSumw2N():
                histo.Sumw2()

            if reBin is not None:
                # Use ROOT functionality to re-bin histogram
                try:
                    histo.Rebin2D(reBin,reBin)
                except TypeError:
                    newname   = histo.GetName()+"_"+name
                    old_histo = histo.Clone()             # special rebinning, redefine histo
                    try:
                        new_x = reBin['x']
                        new_y = reBin['y']
                    except KeyError:
                        print " WARNING : Need to pass new bins for re-binning as a dictionary"
                        print "         : Not applying re-binning, please check your setup."
                        new_x = old_histo.GetXaxis().GetArray() # not sure if this works
                        new_y = old_histo.GetYaxis().GetArray()
                    histo = ROOT.TH2F(old_histo.GetName()+newname,old_histo.GetTitle()+newname,len(new_x)-1,new_x,len(new_y)-1,new_y)
                    xaxis = old_histo.GetXaxis()
                    yaxis = old_histo.GetYaxis()
                    for i in xrange(1,xaxis.GetNbins()):
                        for j in xrange(1,yaxis.GetNbins()):
                            histo.Fill(xaxis.GetBinCenter(i),yaxis.GetBinCenter(j),old_histo.GetBinContent(i,j) )

            if normed:
                integral = histo.Integral()
                histo.Scale(1./integral)

            bin_centers  = {'x':[],'y':[]}
            bin_contents = []
            bin_errors   = []
            bin_widths   = {'x':[],'y':[]}
            bin_edges    = {'x':[histo.GetXaxis().GetBinLowEdge(1)],\
                            'y':[histo.GetYaxis().GetBinLowEdge(1)]}
            bin_edges['x']+=[histo.GetXaxis().GetBinUpEdge(i) for i in xrange(1,histo.GetNbinsX()+1)]
            bin_edges['y']+=[histo.GetYaxis().GetBinUpEdge(j) for j in xrange(1,histo.GetNbinsY()+1)]

            for i in xrange(1,histo.GetNbinsX()+1):
                for j in xrange(1,histo.GetNbinsY()+1):
                    bin_contents.append(histo.GetBinContent(i,j))
                    bin_errors.append(histo.GetBinError(i,j))
                    bin_centers['x'].append(histo.GetXaxis().GetBinCenter(i))
                    bin_centers['y'].append(histo.GetYaxis().GetBinCenter(j))
                    bin_widths['x'].append(histo.GetXaxis().GetBinWidth(i)*0.5)
                    bin_widths['y'].append(histo.GetYaxis().GetBinWidth(i)*0.5)

            results.content = np.array(bin_contents)
            results.error   = np.array(bin_errors)

            results.xbins   = np.array(bin_edges['x'])
            results.ybins   = np.array(bin_edges['y'])
            results.xcenter = bin_centers['x']
            results.ycenter = bin_centers['y']
            results.xwidth  = bin_widths['x']
            results.ywidth  = bin_widths['y']

            results.bins    = {'x':results.xbins, 'y':results.ybins}
            results.center  = bin_centers
            results.width   = bin_widths
        else:


    return results


    def TEfficiency2data(histo):
        """Convert TEfficiency to internal format. No support for re-binning TEfficiencies."""
        h_histo  = histo.GetPassedHistogram()

        bin_contents  = []
        bin_errors_up = []
        bin_errors_dn = []
        bin_centers   = []
        bin_widths    = []
        bin_edges     = [h_histo.GetXaxis().GetBinLowEdge(1)]

        for i in xrange(1,h_histo.GetNbinsX()+1):
            bin_contents.append(histo.GetEfficiency(i))
            bin_errors_up.append(histo.GetEfficiencyErrorUp(i))
            bin_errors_dn.append(histo.GetEfficiencyErrorLow(i))
            bin_centers.append(h_histo.GetXaxis().GetBinCenter(i))
            bin_edges.append(h_histo.GetXaxis().GetBinUpEdge(i))
            bin_widths.append(h_histo.GetXaxis().GetBinWidth(1)/2.)

        results = Hist()
        results.content = np.array(bin_contents)
        results.error   = [bin_errors_dn,bin_errors_up]
        results.bins    = np.array(bin_edges)
        results.center  = bin_centers
        results.width   = bin_widths

        return results



    def TEfficiency2data2D(histo):
        """Convert 2D TEfficiency to internal format. No support for re-binning TEfficiencies."""
        h_histo  = histo.GetPassedHistogram()

        bin_centers   = {'x':[],'y':[]}
        bin_contents  = []
        bin_error_ups = [] # eff uncertainty up
        bin_error_dns = [] # eff uncertainty down
        bin_widths    = {'x':[],'y':[]}

        binns = {'x':[h_histo.GetXaxis().GetBinLowEdge(1)],\
                 'y':[h_histo.GetYaxis().GetBinLowEdge(1)]}
        bin_edges['x']+=[h_histo.GetXaxis().GetBinUpEdge(i) for i in xrange(1,h_histo.GetNbinsX()+1)]
        bin_edges['y']+=[h_histo.GetYaxis().GetBinUpEdge(j) for j in xrange(1,h_histo.GetNbinsY()+1)]

        for i in xrange(1,h_histo.GetNbinsX()+1):
            for j in xrange(1,h_histo.GetNbinsY()+1):
                bin_center['x'].append(h_histo.GetXaxis().GetBinCenter(i))
                bin_center['y'].append(h_histo.GetYaxis().GetBinCenter(j))

                this_bin = histo.GetGlobalBin(i,j)
                bin_contents.append(histo.GetEfficiency(this_bin))
                bin_error_ups.append(histo.GetEfficiencyErrorUp(this_bin))
                bin_error_dns.append(histo.GetEfficiencyErrorLow(this_bin))
                bin_widths['x'].append(h_histo.GetXaxis().GetBinWidth(1)/2.)
                bin_widths['y'].append(h_histo.GetYaxis().GetBinWidth(1)/2.)

        results = Hist()
        results.content = np.array(bin_contents)
        results.error   = [np.array(bin_error_dns),np.array(bin_error_ups)]
        results.bins    = {'x':np.array(bin_edges['x']),'y':np.array(bin_edges['y'])}
        results.center  = bin_centers
        results.width   = bin_widths

        return results

## THE END ##