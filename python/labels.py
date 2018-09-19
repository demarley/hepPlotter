"""
Created:        --
Last Updated:   16 February  2018

Dan Marley
daniel.edison.marley@cernSPAMNOT.ch
Texas A&M University
-----

File for containing information about plotting.
"""
from array import array
from collections import OrderedDict



## -- Classes for handling text on plots
class Text(object):
    """Class to hold extra text object"""
    def __init__(self):
        self.text     = ''         # Actual text to show on plot
        self.coords   = [0.,0.]    # coordinates on plot to draw to the text
        self.fontsize = 16
        self.color    = 'k'
        self.ha = 'left'           # horizontal alignment
        self.va = 'top'            # vertical alignment
        self.transform = None      # 'None' so the user can change it -- it will be set below
        return

    def __str__(self):
        """print text object with attributes"""
        for i in ['text','coords','fontsize','color','ha','va','transform']:
            print "%-*s: %s" % (10,i,self.__dict__[i])
        return


class PlotText(object):
    """Class to draw new text on the plots"""
    def __init__(self):
        self.texts  = []

    def Add(self,plt_text,**txt_kwargs):
        """
        Add new text to the plot
        @param plt_text    text to draw
        @param txt_kwargs  key-word arguments:
                             'coords','fontsize','color','ha','va','transform'
        """
        pltTextObject = Text()
        pltTextObject.text = plt_text

        # set parameters of the text object if they are passed to the 'Add()' function
        # - use defaults if no argument is passed - this ensures any unsupported 
        # arguments don't harm anything in the text object

        for param in dir(pltTextObject):
            if param.startswith("__"): continue
            try:
                setattr( pltTextObject,param,txt_kwargs[param] )
            except KeyError: # use the defaults
                continue

        self.texts.append(pltTextObject)

        return

    def Print(self):
        """Print out the text arguments"""
        for text in self.texts:
            print text
    def getText(self):
        """Return the list of Text objects"""
        return self.texts

class EnergyStamp(Text):
    """Class for writing center of mass energy on plot"""
    def __init__(self):
        Text.__init__(self)
        self.text = r"(13 TeV)"

class LumiStamp(Text):
    """Class for writing luminosity on plot"""
    def __init__(self,lumi="36.1"):
        Text.__init__(self)
        self.text = r"%s fb$^{\text{-1}}$"%(lumi)

class CMSStamp(Text):
    """Class for writing official CMS name & plot type (Simulation, Internal, etc.) on plot"""
    def __init__(self,label_status="Internal"):
        Text.__init__(self)
        self.text = r"\textbf{CMS} {\Large \textit{%s}}"%(label_status)    # CMS style



if __name__ == '__main__':
    print "Do not execute this file, only import it."


## The End. ##

