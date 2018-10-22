<img src="data/logo.png" width="500">


Interface for plotting HEP data with matplotlib

Built with:

Software | Version
-------- | -------
[matplotlib](https://matplotlib.org/) | 2.2.2
[numpy](http://www.numpy.org/)        | 1.14.5
[ROOT](https://root.cern.ch/)         | 6.14/04
[uproot](https://github.com/scikit-hep/uproot) | 3.2.5


# Getting Started


### CMSSW Environment

To use in a CMSSW environment, the `hepPlotter` code will need to be nested inside a directory under `$CMSSW_BASE/src/`.  
For this setup, it is assumed that other analysis code lives in the directory `$CMSSW_BASE/src/Analysis/`:

```
## setup CMSSW
cmsrel CMSSW_9_4_4
cd CMSSW_9_4_4/src/
cmsenv
git cms-init --upstream-only

mkdir Analysis
git clone https://github.com/demarley/hepPlotter.git Analysis/
```

### Custom Environment

Outside of a CMSSW environment, 
you will need to modify your python path appropriately (as shown in the examples).
Thus, you can clone this repository (`git clone https://github.com/demarley/hepPlotter.git`)
into any directory you wish.

# Examples

See the [examples](examples/) directory for jupyter notebooks that detail how to use the framework.

Notebook | ABOUT
-------- | -----
simple_1D_arrays.ipynb | Plots showing arrays turned into 1-dimensional histograms (created with `numpy`)
simple_1D_root.ipynb   | Plots of ROOT histograms and efficiencies (accessed with `ROOT`)
simple_1D_uproot.ipynb | Plots showing 1-dimensional histograms (accessed with `uproot`)
simple_2D_root.ipynb   | Plots showing 2-dimensional histograms (accessed with `ROOT`)
simple_2D_uproot.ipynb | Plots showing 2-dimensional histograms (accessed with `uproot`)
simple_datamc.ipynb    | Plots showing Data/MC comparisons (accessed with `ROOT`)

## Backend

The framework now supports using `c++ ROOT` or `uproot` as backends.
This means that, for a given ROOT file with histograms, you can choose a backend
of either `ROOT` or `uproot` to open & manipulate your histograms.
This is particularly useful in virtual environments (and other python-focused settings)
where `c++ ROOT` isn't available.  
To set your backend, simply set the option `backend = 'uproot'` or `backend = 'ROOT'`
when making your histograms (see the notebooks in `examples/` for more information.

**If no backend is declared, hepPlotter will first try to set the backend to `c++ ROOT`. 
If that is unavailable, hepPlotter will try to use `uproot` as the backend.**  
You can see how the `backend` is defined 
[here](https://github.com/demarley/hepPlotter/blob/master/python/plotter.py#L136-L162).

_If you are using raw data or binned data (stored in arrays), use the `uproot` backend._

## Notes

### Data/MC in 2 Dimensions

Most commonly, data/mc plots are just for 1-dimensional distributions.
It is possible to plot 2-dimensional data/mc plots, but this is not natively supported in hepPlotter.  
Instead, as a user you can pass a 2-dimensional histogram that represents the data/mc ratio to hepPlotter.

Here is an example snippet of code:
```
# 2-dimensional Data/MC plot
# Setup the plot with the usual declarations for 2-dimensional histograms
hist = Histogram2D()

hist.backend = 'ROOT'
hist.x_label = "x-label"
hist.y_label = "y-label"
hist.saveAs  = "hist2d_datamc_example"
hist.CMSlabel = 'outer'
hist.CMSlabelStatus = "Simulation Internal"
hist.logplot['data'] = False

# Set properties unique to 2D histogram
hist.colormap = 'bwr'               # blue-white-red
hist.colorbar['title'] = "Data/MC"  # text label for colorbar

hist.initialize()   # sets the parameters of the plot

# Add data to the plot - just an example (not stored in example.root)
total_mc_hist = file.Get("totalMC2D")  # access 2D MC data (may need to add multiple histograms)
data_hist     = file.Get("data2D")     # access 2D data
data_hist.Divide(total_mc_hist)        # get the ratio
hist.Add(datamc,name="datamc")

p = hist.execute() # make the plot (p represents the matplotlib 'figure' object)
hist.savefig()     # save the figure (with name "hist.saveAs+hist.format") and close it
```

### Systematic Uncertainties

There is no native support to calculate systematic uncertainties for the user in hepPlotter.
Instead, users are encouraged to modify the bin error to represent the total systematic uncertainty.

Future updates will allow the user to plot a statistical uncertainty, systematic uncertainty, and stat+syst uncertainty (in addition to individual curves for specific sources of uncertainty).  
The code will be an expanded version of 
[this](https://github.com/demarley/hepPlotter/blob/master/python/datamc.py#L175) 
function using code from 
[here](https://github.com/cms-ttbarAC/CyMiniAna/blob/master/python/hepPlotter/hepPlotterDataMC.py#L356).


# Questions or Comments

Contact the author, submit an issue, or submit a PR.
