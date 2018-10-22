<img src="data/logo.png" width="500">


Interface for plotting HEP data with matplotlib

Built with:
- [matplotlib](https://matplotlib.org/) 2.2.2
- [numpy](http://www.numpy.org/) 1.14.5
- [ROOT](https://root.cern.ch/) 6.14/04
- [uproot](https://github.com/scikit-hep/uproot) 3.2.5


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
0-simple_1D.ipynb | Plots of ROOT histograms and efficiencies (accessed with `ROOT`)
1-datamc.ipynb    | Plots showing Data/MC comparisons (accessed with `ROOT`)
2-simple_2D.ipynb | Plots showing 2-dimensional histograms (accessed with `ROOT`)
3-simple_1D_uproot.ipynb | Plots showing 1-dimensional histograms (accessed with `uproot`)
4-simple_1D_arrays.ipynb | Plots showing arrays turned into 1-dimensional histograms (created with `numpy`)

## Backend

The framework now supports using C++ ROOT or uproot as backends.
This means that, for a given ROOT file with histograms, you can choose a backend
or either 'ROOT' or 'uproot' to load your histograms.
This is particularly useful in virtual environments (and other python-focused settings)
where C++ ROOT isn't available.  
To set your backend, simply set the option `backend = 'uproot'` or `backend = 'ROOT'`
when making your histograms (see the notebooks in `examples/` for more information.

# Questions or Comments

Contact the author, submit an issue, or submit a PR.
