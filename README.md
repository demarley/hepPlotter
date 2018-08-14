<img src="data/logo.png" width="500">


Interface for plotting HEP data with matplotlib

Built with:
- [matplotlib](https://matplotlib.org/) 2.2.2
- [numpy](http://www.numpy.org/) 1.14.5
- [ROOT](https://root.cern.ch/) 6.10/02
- [uproot](https://github.com/scikit-hep/uproot) 2.9.0 (NB: not currently implemented)


# Getting Started

To use in a CMSSW environment, the `hepPlotter` code will need to be nested inside a directory under `$CMSSW_BASE/src/`.  
For this setup, it is assumed that other analysis code lives in the directory `$CMSSW_BASE/src/Analysis/`.
```
## setup CMSSW
cmsrel CMSSW_9_4_4
cd CMSSW_9_4_4/src/
cmsenv
git cms-init

mkdir Analysis
git clone https://github.com/demarley/hepPlotter.git Analysis/
```

Outside of a CMSSW environment, you will need to modify your python path appropriately (as shown in the examples).

# Examples

See the [examples](examples/) directory for jupyter notebooks that detail how to use the framework.

# Questions or Comments

Contact the author, submit an issue, or submit a PR.
