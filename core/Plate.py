'''
Created on Jun 14, 2013

@author: jonathanfriedman
'''
try:
    import cPickle as pickle
except ImportError:
    import pickle

from fcm import loadFCS
from pandas import DataFrame as DF


def get_files(dirname=None, pattern='*.fcs', recursive=True):
    '''
    Get all file names within a given directory those names match a
    given pattern.  
    
    Parameters
    ----------
    dirname : str | None 
        Directory containing the datafiles.
        If None is given, open a dialog box. 
    pattern : str
        Return only files whose names match the specified pattern.
    recursive : bool
        True : Search recursively within all sub-directories.
        False : Search only in given directory.
        
    Returns
    -------
    matches: list
       List of file names (including full path). 
    '''
    import os, fnmatch, glob
    
    # get dirname from user if not given
    if dirname is None:
        import Tkinter, tkFileDialog
        root = Tkinter.Tk()
        dirname = tkFileDialog.askdirectory(parent=root,initialdir=os.curdir,title='Please select a directory')
        root.destroy()
    
    # find all files in dirname that match pattern
    if recursive: # search subdirs
        matches = []
        for root, dirnames, filenames in os.walk(dirname):
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(root, filename))        
    else:
        matches = glob.glob(dirname + pattern)
    return matches

def save(obj, path):
    """
    Pickle (serialize) object to input file path

    Parameters
    ----------
    obj : any object
    path : string
        File path
    """
    f = open(path, 'wb')
    try:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    finally:
        f.close()

def load(path):
    """
    Load pickled object from the specified file path.

    Parameters
    ----------
    path : string
        File path

    Returns
    -------
    unpickled : type of object stored in file
    """
    f = open(path, 'rb')
    try:
        return pickle.load(f)
    finally:
        f.close()

def to_list(obj):
    '''
    Convert an object to a list if it is not already 
    a non-string iterable.
    '''
    if isinstance(obj, basestring):
        l = [obj]
    elif not hasattr(obj, '__iter__'):
        l = list(obj)
    else:
        l = obj
    return l

class Sample(object):
    '''
    A class for holding data from a single sample, i.e.
    a single well or a single tube.
    '''
    
    def __init__(self, ID, datafile=None, 
                 readdata=False, readdata_kwargs={}):
        self.ID = ID
        self.datafile = datafile
        if readdata:
            self.data = self.read_data(**readdata_kwargs)
        else:
            self.data = None
    
    def __repr__(self): return repr(self.ID)
    
    def save(self, path):
        save(self, path)
    
    @classmethod
    def load(cls, path):
        return load(path)
    
    def read_data(self, **kwargs):
        kwargs.setdefault('transform', None)
        data = loadFCS(self.datafile, transform=None)
        self.data = data
    
    def clear_data(self):
        self.data = None
    
    def get_metadata(self, fields):
        if self.data is None:
            raise Exception, 'Data must be read before extracting metadata.'
        all_meta = self.data.notes
        return dict( (field, all_meta[field]) for field in fields )
        
        
        
class Plate(object):
    '''
    A class for holding plate data.
    '''

    def __init__(self, ID, 
                 shape=(8,12), row_labels=None, col_labels=None, 
                 datafiles=None, datadir=None, 
                 pattern='*.fcs', recursive=True):
        '''
        Constructor
        '''
        self.ID = ID
        self.shape = shape
        if row_labels is None:
            row_labels = self._default_labels('rows')
        if col_labels is None:
            col_labels = self._default_labels('cols')
        self.row_labels = row_labels
        self.col_labels = col_labels
        self._make_wells(row_labels, col_labels)
        self.set_datafiles(datafiles, datadir, pattern, recursive) 

    def __repr__(self): return repr(self.ID)
    
    def save(self, path):
        save(self, path)
    
    @classmethod
    def load(cls, path):
        return load(path)
    
    def _default_labels(self, axis):
        import string
        if axis == 'rows':
            return [string.uppercase[i] for i in range(self.shape[0])]
        else:
            return  range(1, 1+self.shape[1])
           
    def _make_wells(self, row_labels, col_labels):
        wells = DF(index=row_labels, columns=col_labels, dtype=object)
        for rlabel in row_labels:
            for clabel in col_labels:
                ID = '%s%s' %(rlabel, clabel)
                wells[clabel][rlabel] = Sample(ID)
        self.wells = wells 
                    
    def set_datafiles(self, datafiles=None, datadir=None, 
                      pattern='*.fcs', recursive=True):
        if datadir is not None:
            datafiles = get_files(datadir, pattern, recursive)        
        if datafiles is not None:
            if isinstance(datafiles, basestring):
                datafiles = [datafiles]
        self.datafiles = datafiles
    
    @property
    def well_IDS(self):
        return self.wells.values.flatten().tolist()
    
    def get_wells(self, well_ids):
        '''
        Return a dictionary off the wells that corresponding 
        to the requested ids.
        '''
        inds = self.wells.applymap(lambda x:x.ID in well_ids)
        return dict( (ID,well) for ID,well in zip(well_ids, self.wells[inds]) )
    
    
    def clear_well_data(self, well_ids=None):
        if well_ids is None:
            well_ids = self.well_IDS
        for well in self.get_wells(well_ids).itervalues():
            well.clear_data()
    
    def analyze_well(self, well_id, analyzers):
        # parse fcs file using fcm
        well = self.get_well(well_id)
        data = well.read_data()
        # extract desired values
        vals = [analyzer(data) for analyzer in analyzers]
        return vals
        
    def analyze_files(self, analyzers, datafiles=None):
        '''
        
        Parameters
        ----------
        analyzers : dict 
            Each analyzer value is a callable that accepts a Sample 
            object and returns a single number/string. 
        datafiles : str| iterable of str | None
            Datafiles to parse.
            If None is given, parse self.datafiles 
        ''' 
        if datafiles is None: 
            datafiles = self.datafiles
        elif isinstance(datafiles, basestring):
            datafiles = [datafiles]
        
        
if __name__ == '__main__':
    plate = Plate('test', shape=(2,3))
    print plate
    print plate.wells 
    print plate.well_IDS
    
    plate.wells['1']['A'].get_meta()
    
    well_ids = ['A2' , 'B3']
    print plate.get_wells(well_ids)
    
    plate.clear_well_data()  
    plate.clear_well_data(well_ids)             
            
        