"""
Created:        17 October   2018
Last Updated:   17 October   2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
-----

Simple functions to help accessing data with ROOT
"""
import ROOT



def hist2list(histo,name,normed,reBin,results):
    """Convert ROOT histogram for internal use."""
    bin_centers  = []
    bin_contents = []
    bin_errors   = []
    bin_widths   = []
    bin_edges    = []

    if not histo.GetSumw2N():
        histo.Sumw2()

    if normed:
        integral = histo.Integral()
        histo.Scale(1./integral);

    try:
        histo.Rebin(reBin)
    except TypeError:
        newname = histo.GetName()+"_"+name
        histo.Rebin(len(reBin)-1,newname,reBin)
        histo = ROOT.gROOT.FindObject( newname )

    bin_edges = [histo.GetXaxis().GetBinLowEdge(1)]

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



def hist2list2D(histo,name,reBin,normed,results):
    """Convert ROOT histogram for internal use."""
    bin_centers  = {'x':[],'y':[]}
    bin_contents = []
    bin_errors   = []
    bin_widths   = {'x':[],'y':[]}
    bin_edges    = {'x':[],'y':[]}

    if not histo.GetSumw2N():
        histo.Sumw2()

    if normed:
        integral = histo.Integral()
        histo.Scale(1./integral)

    ## -- Rebin
    if reBin is not None:
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

    bin_edges = {'x':[histo.GetXaxis().GetBinLowEdge(1)],\
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

    return results


## THE END ##