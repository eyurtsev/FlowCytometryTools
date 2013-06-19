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
from numpy import nan, unravel_index

def get_meta_FCS(x, fields):
    '''
    TODO: change to extract data from other notes fields (not just 'text')
    '''
    return [x.notes.text[field] for field in fields]

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
    if obj is None:
        return obj
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
        '''
        Read the datafile specified in Sample.datafile and 
        return the resulting object.
        Does NOT assign the data to self.data
        '''
        kwargs.setdefault('transform', None)
        data = loadFCS(self.datafile, **kwargs)
        return data
    
    def set_data(self, data=None, datafile=None, readdata_kwargs={}):
        '''
        Assign a value to Sample.data. 
        Data is not returned
        '''
        if data is not None:
            self.data = data
        else:
            if datafile is not None:
                self.datafile = datafile
            self.data = self.read_data(**readdata_kwargs)     
    
    def clear_data(self):
        self.data = None
    
    def get_metadata(self, fields):
        if self.data is None:
            raise Exception, 'Data must be read before extracting metadata.'
        fields = to_list(fields)
        return get_meta_FCS(self.data, fields)
    
    def apply(self, func, applyto='FCS', noneval=nan, nout=1, keepdata=False):
        '''
        Apply func either to self or to associated FCS data.
        If data is not already parsed, try and read it.
        
        Parameters
        ----------
        func : callable 
            Each func value is a callable that accepts a Sample 
            object or an FCS object.
        applyto : 'FCS' | 'SAMPLE'
            'FCS'    : apply to associated FCS data
            'SAMPLE' : apply to sample object itself. 
        noneval : obj
            Value returned if applyto is 'FCS' but no data is available.
        nout : int
            number of outputs from func.
        '''         
        applyto = applyto.upper()
        if applyto == 'FCS':
            if self.data is not None:
                data = self.data
            elif self.datafile is None:
                if nout==1:
                    return noneval
                else:
                    return [noneval]*nout
            else:
                data = self.read_data()
                if keepdata:
                    self.data = data
            return func(data)
        elif applyto == 'SAMPLE':
            return func(self)
        else:
            raise ValueError, 'Encountered unsupported value "%s" for applyto paramter.' %applyto       
        
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
        
        datafiles : str| iterable of str | None
            Datafiles to parse.
            If None is given, parse self.datafiles 
        '''
        self.ID = ID
        self.shape = shape
        self.extracted = {}
        if row_labels is None:
            row_labels = self._default_labels('rows')
        if col_labels is None:
            col_labels = self._default_labels('cols')
        self.row_labels = row_labels
        self.col_labels = col_labels
        
        self.wells_d = {}
        self._make_wells(row_labels, col_labels)
        self.set_datafiles(datafiles, datadir, pattern, recursive)
        self.assign_datafiles_to_wells() 

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
                well = Sample(ID)
                wells[clabel][rlabel] = well
                self.wells_d[well.ID] = well
        self.wells = wells 
    
    def _datafile_wellID_parser(self, datafile, parser):
        if hasattr(parser, '__call__'):
            return parser(datafile)
        if parser == 'name':
            return datafile.split('_')[-1].split('.')[0]
        elif parser == 'number':
            number = int(datafile.split('.')[-2])
            i,j = unravel_index(number, self.shape)
            return self.wells.values[i,j].ID
        elif parser == 'read':
            data = loadFCS(datafile, transform=None)
            return data.notes.text['src']
        else:
            raise ValueError,  'Encountered unsupported value "%s" for parser paramter.' %parser 
    
    def assign_datafiles_to_wells(self, assignments=None, parser='name'):
        '''
        assignments : dict
            keys    = well ids
            values = data file names (str)
        parser : 'name' | 'number' | callable 
        '''
        if assignments is None: #guess assignments
            assignments = {}
            for datafile in self.datafiles:
                ID = self._datafile_wellID_parser(datafile, parser)
                assignments[ID] = datafile
            
        wells = self.get_wells(assignments.keys())
        for well_id, datafile in assignments.iteritems():
            wells[well_id].datafile = datafile
                          
    def set_datafiles(self, datafiles=None, datadir=None, 
                      pattern='*.fcs', recursive=True):
        '''
        datafiles : str| iterable of str | None
            Datafiles to parse.
            If None is given, parse self.datafiles 
        ''' 
        if datafiles is not None:
            datafiles = to_list(datafiles)
        else:
            datafiles = get_files(datadir, pattern, recursive)        
        self.datafiles = datafiles
    
    @property
    def well_IDS(self):
        return [well.ID for well in self.wells.values.flatten()]
    
    def get_wells(self, well_ids):
        '''
        Return a dictionary of the wells that correspond
        to the requested ids.
        '''
        return dict( ((ID,self.wells_d[ID]) for ID in well_ids) )
    
    def clear_well_data(self, well_ids=None):
        if well_ids is None:
            well_ids = self.well_IDS
        for well in self.get_wells(well_ids).itervalues():
            well.clear_data()
        
    def apply(self, func, outputs, applyto='FCS', noneval=nan,
              well_ids=None, keepdata=False):
        '''
        
        Parameters
        ----------
        func : dict 
            Each func value is a callable that accepts a Sample 
            object and returns a single number/string. 
        outputs : str | str iterable
            Names of outputs of func
        applyto : 'FCS' | 'SAMPLE'
        well_ids : str| iterable of str | None
            IDs of well to apply function to.
            If None is given
        ''' 
        if well_ids is None:
            well_ids = self.well_IDS
        else:
            well_ids = to_list(well_ids)
        
        outputs = to_list(outputs)
        nout    = len(outputs)
        
        def applied_func(well):
            if well.ID not in well_ids:
                if nout==1:
                    return noneval
                else:
                    return [noneval]*nout
            return well.apply(func, applyto, noneval, nout, keepdata)
               
        result = self.wells.applymap(applied_func)  
        
        if nout==1:
            out = {outputs[0]:result}
        else:
            out = {}
            for i,output in enumerate(outputs):
                out[output] = result.applymap(lambda x: x[i])
        self.extracted.update(out)
            
    def get_well_metadata(self, fields, noneval=nan, well_ids=None):
        fields = to_list(fields)
        func = lambda x: get_meta_FCS(x, fields)
        self.apply(func, fields, 'fcs', noneval, well_ids)
        
if __name__ == '__main__':
    datadir = '../tests/data/'
#     print get_files(datadir)
    plate = Plate('test', datadir=datadir, shape=(4,5))
#     print plate
#     print plate.wells 
#     print plate.well_IDS
    
#     plate.apply(lambda x:x.ID, 'ID', applyto='sample', well_ids=['A1','B1'])
    plate.apply(lambda x:x.datafile, 'file', applyto='sample')
#     plate.apply(lambda x:x.shape[0], 'counts')
#     plate.get_well_metadata(['date', 'etim'])
    print plate.extracted['file'].values
    
#     plate.wells['1']['A'].get_meta()
#     
#     well_ids = ['A2' , 'B3']
#     print plate.get_wells(well_ids)
#     
#     plate.clear_well_data()  
#     plate.clear_well_data(well_ids)             
            
        