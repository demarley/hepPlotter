"""
Created:         1 September 2016
Last Updated:   16 February  2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University
-----

Simple functions to help with basic plots.
"""
import ROOT
import numpy as np


def betterColors():
    """
    Better colors for plotting.
    In matplotlib 2.0, these are available by default: 
    > https://matplotlib.org/users/dflt_style_changes.html#colors-color-cycles-and-color-maps
    """
    old_colors = [
         (31, 119, 180),  #blue
         (214, 39, 40),   #red
         (44, 160, 44),   #green
         (255, 127, 14),  #orange
         (148, 103, 189), #purple
         (227, 119, 194), #pink
         (127, 127, 127), #teal
         (188, 189, 34),  #gray
         (23, 190, 207),  #green-gold
         (140, 86, 75),   #brown
         # lighter versions
         (174, 199, 232), #blue
         (255, 152, 150), #red
         (152, 223, 138), #green
         (255, 187, 120), #orange
         (197, 176, 213), #purple
         (247, 182, 210), #pink
         (158, 218, 229), #teal
         (199, 199, 199), #gray
         (219, 219, 141), #green-gold
         (196, 156, 148), #brown
    ]
    lc = []
    for jj in old_colors:
        new_color = [i/255. for i in jj]
        lc.append(new_color)

    ls  = ['solid' for _ in lc]
    ls += ['dashed' for _ in lc]

    return {'linecolors':lc,'linestyles':ls}


def extract(str_value, start_='{', stop_='}'):
    """Extract a string between two symbols, e.g., parentheses."""
    extraction = str_value[str_value.index(start_)+1:str_value.index(stop_)]

    return extraction


def getName(filename):
    """Given a root file full of histograms, return the sample name
    example name: TTS_M500_XXX.root
    can be customized by users depending on their files
    best (future) solution: metadata in root file with "name" option
    """
    name = filename.split(".root")[0].split("/")[-1]

    return name


def getSampleType(name):
    """Given a sample name return the sample type"""
    backgrounds = open("share/sampleNamesShort.txt").readlines()
    backgrounds = [i.rstrip("\n") for i in backgrounds]
    signal = ['TTS','BBS','TTD','BBD','XX','YY','zprime']
    data = ['data']

    sampletype = ''
    if name=='data':
        sampletype = 'data'
    elif any(name.startswith(i) for i in signal):
        sampletype = 'signal'
    elif name in backgrounds:
        sampletype = 'background'
    else:
        sampletype = ''

    return sampletype


def getDataStructure(h_data):
    """
    Find the data structure determining the appropriate color scheme.
    Only call if the self.colormap attribute is None.

    @param h_data    The histogram data
    @param colorMap  Current choice for colormap
    """
    max_value = max(h_data)
    min_value = min(h_data)

    ## linear (same sign)
    if max_value*min_value > 0:
        if max_value>0:
            colormap = "Reds"    # positive values
        else:
            colormap = "Blues"   # negative values
    ## diverging
    else:
        colormap = "bwr"         # blue2red map

    return colormap


def hist1d(nbins,bin_low,bin_high):
    """
    Set the binning for each histogram.
    @param nbins	  Number of bins in histogram
    @param bin_low    Lower bin edge
    @param bin_high   Upper bin edge
    """
    binsize = float(bin_high-bin_low)/nbins
    arr     = [i*binsize+bin_low for i in xrange(nbins+1)]
    return arr




class Data(object):
    def __init__(self):
        """Store data for plotting (collection of arrays) in a class"""
        self.data   = None
        self.error  = None
        self.bins   = None
        self.center = None
        self.width  = None


def data2list(data,weights=None,normed=False,binning=1):
    """Convert array of data into dictionary of information matching 'hist2list' """
    data,bins = np.histogram(data,bins=binning,weights=weights,normed=normed)

    results = Data()
    results.data   = data
    results.error  = np.sqrt(data)
    results.bins   = bins
    results.center = 0.5*(bins[:-1]+bins[1:])
    results.width  = 0.5*(bins[:-1]-bins[1:])

    return results


def data2list2D(data,weights=None,normed=False,binning=1):
    """Convert array of data into dictionary of information matching 'hist2list' """
    try:
        x = data['x']
        y = data['y']
    except TypeError:
        x = data[0]
        y = data[1]
    data,bins_x,bins_y = np.histogram2d(x, y, bins=binning,normed=normed,weights=weights)

    binnsx = []
    binnsy = []
    for x in 0.5*(bins_x[:-1]+bins_x[1:]):
        for y in 0.5*(bins_y[:-1]+bins_y[1:]):
            binnsx.append(x)
            binnsy.append(y)

    results = Data()
    results.data   = data
    results.error  = np.sqrt(data)
    results.bins   = {'x':bins_x,'y':bins_y}
    results.center = {'x':binnsx,'y':binnsy}
    results.width  = {'x':0.5*(bins_x[:-1]-bins_x[1:]),
                      'y':0.5*(bins_y[:-1]-bins_y[1:])}

    return results


def hist2list(histo,name='',normed=False,reBin=1):
    """Convert ROOT histogram to (dictionary of) lists"""
    if not histo.GetSumw2N():
        histo.Sumw2()

    if normed:
        histo.Scale(1./histo.Integral());

    try:
        histo.Rebin(reBin)
    except TypeError:
        newname = histo.GetName()+"_"+name
        histo.Rebin(len(reBin)-1,newname,reBin)
        histo = ROOT.gROOT.FindObject( newname )

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
        bin_widths.append(histo.GetXaxis().GetBinWidth(i)/2.)

    results = Data()
    results.data   = np.array(bin_contents)
    results.error  = np.array(bin_errors)
    results.bins   = bin_edges
    results.center = bin_centers
    results.width  = bin_widths

    return results



def hist2list2D(histo,name='',reBin=None,normed=False):
    """Convert ROOT histogram to list for 2D plots."""
    if not histo.GetSumw2N():
        histo.Sumw2()

    if normed:
        histo.Scale(1./histo.Integral())

    ## -- Rebin
    if reBin is not None:
        try:
            histo.Rebin2D(reBin,reBin)
        except TypeError:
            newname = histo.GetName()+"_"+name

            old_histo = histo.Clone()     # special rebinning, redefine histo
            new_x     = reBin['x']
            new_y     = reBin['y']
            histo     = ROOT.TH2F(old_histo.GetName()+newname,old_histo.GetTitle()+newname,len(new_x)-1,new_x,len(new_y)-1,new_y)
            xaxis = old_histo.GetXaxis()
            yaxis = old_histo.GetYaxis()
            for i in xrange(1,xaxis.GetNbins()):
                for j in xrange(1,yaxis.GetNbins()):
                    histo.Fill(xaxis.GetBinCenter(i),yaxis.GetBinCenter(j),old_histo.GetBinContent(i,j) )

    bin_centers  = {'x':[],'y':[]}
    bin_contents = []
    bin_errors   = []
    bin_widths   = {'x':[],'y':[]}
    bin_edges = {'x':[histo.GetXaxis().GetBinLowEdge(1)],\
                 'y':[histo.GetYaxis().GetBinLowEdge(1)]}

    bin_edges['x']+=[histo.GetXaxis().GetBinUpEdge(i) for i in xrange(1,histo.GetNbinsX()+1)]
    bin_edges['y']+=[histo.GetYaxis().GetBinUpEdge(j) for j in xrange(1,histo.GetNbinsY()+1)]

    for i in xrange(1,histo.GetNbinsX()+1):
        for j in xrange(1,histo.GetNbinsY()+1):
            bin_centers['x'].append(histo.GetXaxis().GetBinCenter(i))
            bin_centers['y'].append(histo.GetYaxis().GetBinCenter(j))

            bin_contents.append(histo.GetBinContent(i,j))
            bin_errors.append(histo.GetBinError(i,j))

            bin_widths['x'].append(histo.GetXaxis().GetBinWidth(i)/2.)
            bin_widths['y'].append(histo.GetYaxis().GetBinWidth(i)/2.)

    results = Data()
    results.data   = np.array(bin_contents)
    results.error  = np.array(bin_errors)
    results.bins   = bin_edges
    results.center = bin_centers
    results.width  = bin_widths

    return results



def TEfficiency2list(histo):
    """Convert TEfficiency to lists.  Return dictionary of lists"""
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

    results = Data()
    results.data   = np.array(bin_contents)
    results.error  = [bin_errors_dn,bin_errors_up]
    results.bins   = bin_edges
    results.center = h_eff_mp
    results.width  = bin_widths

    return results



def TEfficiency2list2D(histo):
    """Convert 2D TEfficiency to lists"""
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

    results = Data()
    results.data   = np.array(bin_contents)
    results.error  = [np.array(bin_error_dns),np.array(bin_error_ups)]
    results.bins   = bin_edges
    results.center = bin_centers
    results.width  = bin_widths

    return results


## THE END