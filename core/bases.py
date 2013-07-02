'''
Created on Jun 18, 2013

@author: jonathanfriedman

Base objects for sample and plate objects.
'''
from pandas import DataFrame as DF
from numpy import nan, unravel_index
from pylab import sca
from GoreUtilities.util import get_files, save, load, to_list


class BaseObject(object):
    '''
    Object providing common utility methods.
    Used for inheritance. 
    '''

    def __repr__(self): return repr(self.ID)
    
    def save(self, path):
        save(self, path)
    
    @classmethod
    def load(cls, path):
        return load(path)


class BaseSample(BaseObject):
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

    def read_data(self, **kwargs):
        '''
        This function should be overwritten for each 
        specific data type.
        '''
        pass
    
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

    def get_data(self, **kwargs):
        '''
        quick fix for working with data.
        TODO
        To Jonathan: can you add a property or else a function that will correctly
        return the data that I should be working with?
        probably add a call to this method from within apply function
        '''
        if self.data is not None:
            return self.data
        elif self.datafile is not None:
            return self.read_data(**kwargs)
        else:
            return None
    
    
    def clear_data(self):
        self.data = None
    
    def ID_from_data(self):
        '''
        Get sample ID from loaded data.
        
        This function should be overwritten for each 
        specific data type.
        '''
        pass
    
    def get_metadata(self, fields):
        '''
        This function should be overwritten for each 
        specific data type.
        '''
        pass

    def apply(self, func, applyto='data', noneval=nan, nout=1, keepdata=False):
        '''
        Apply func either to self or to associated FCS data.
        If data is not already parsed, try and read it.
        
        Parameters
        ----------
        func : callable 
            Each func value is a callable that accepts a Sample 
            object or an FCS object.
        applyto : 'data' | 'sample'
            'data'    : apply to associated data
            'sample' : apply to sample object itself. 
        noneval : obj
            Value returned if applyto is 'data' but no data is available.
        nout : int
            number of outputs from func.
        '''         
        applyto = applyto.lower()
        if applyto == 'data':
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
        elif applyto == 'sample':
            return func(self)
        else:
            raise ValueError, 'Encountered unsupported value "%s" for applyto paramter.' %applyto       

BaseWell = BaseSample
        
class BasePlate(BaseObject):
    '''
    A class for holding plate data.
    '''
    _sample_class = BaseSample
    
    def __init__(self, ID,
                 shape=(8,12), row_labels=None, col_labels=None, 
                 datafiles=None, datadir=None, 
                 pattern='*', recursive=False):
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
                well = self._sample_class(ID)
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
            sample = self._sample_class(datafile)
            return sample.ID_from_data()
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
                      pattern='*', recursive=True):
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
        
    def apply(self, func, outputs, applyto='data', noneval=nan,
              well_ids=None, keepdata=False):
        '''
        
        Parameters
        ----------
        func : dict 
            Each func value is a callable that accepts a Sample 
            object and returns a single number/string. 
        outputs : str | str iterable
            Names of outputs of func
        applyto : 'data' | 'sample'
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
            result = well.apply(func, applyto, noneval, nout, keepdata)
            if result is not None:
                return result
            else:
                if nout==1:
                    return noneval
                else:
                    return [noneval]*nout

               
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
        func = lambda x: x.get_metadata(fields)
        self.apply(func, fields, 'sample', noneval, well_ids)


    def grid_plot(self, func, applyto='data', well_ids=None, row_labels=None, col_labels=None,
                xaxislim=None, yaxislim=None,
                row_label_xoffset=-0.1, col_label_yoffset=-0.3,
                hide_tick_labels=True, hide_tick_lines=True,
                hspace=0, wspace=0, row_labels_kwargs={}, col_labels_kwargs={}):
        '''
        Creates subplots for each well in the plate. Uses func to plot on each axis.
        Follow with a call to matplotlibs show() in order to see the plot.

        TODO: Finish documentation, document plot function also in utilities.graph
        fix col_label, row_label offsets to use figure coordinates

        @author: Eugene Yurtsev

        Parameters
        ----------
        func : dict
            Each func is a callable that accepts a Sample
            object (with an optional axis reference) and plots on the current axis.
            return values from func are ignored
            NOTE: if using applyto='sample', the function
            when querying for data should make sure that the data
            actually exists
        applyto : 'sample' | 'data'
        well_ids : None
        col_labels : str
            labels for the columns if None default labels are used
        row_labels : str
            labels for the rows if None default labels are used
        xaxislim : 2-tuple
            min and max x value for each subplot
            if None, the limits are automatically determined for each subplot

        Returns
        -------
        gHandleList: list
            gHandleList[0] -> reference to main axis
            gHandleList[1] -> a list of lists
                example: gHandleList[1][0][2] returns the subplot in row 0 and column 2

        Examples
        ---------
            def y(well, ax):
                data = well.get_data()
                if data is None:
                    return None
                graph.plotFCM(data, 'Y2-A')
            def z(data, ax):
                plot(data[0:100, 1], data[0:100, 2])
            plate.plot(y, applyto='sample');
            plate.plot(z, applyto='data');

        '''
        # Acquire call arguments to be passed to create plate layout
        callArgs = locals().copy() # This statement must remain first. The copy is just defensive.
        [callArgs.pop(varname) for varname in  ['self', 'func', 'applyto', 'well_ids']] # pop args
        callArgs['rowNum'] = self.shape[0]
        callArgs['colNum'] = self.shape[1]

        if row_labels == None: callArgs['row_labels'] = self.row_labels
        if col_labels == None: callArgs['col_labels'] = self.col_labels

        # TODO: decide on naming convention
        try:
            from GoreUtilities import graph
        except:
            from GoreUtilities import graph

        gHandleList = graph.create_grid_layout(**callArgs)

        well_ids = to_list(well_ids)

        for row, row_label in enumerate(self.row_labels):
            for col, col_label in enumerate(self.col_labels):
                if well_ids and self.wells[col_label][row_label].ID not in well_ids:
                    break

                ax = gHandleList[1][row][col]
                sca(ax) # sets the current axis

                if applyto == 'sample':
                    func(self.wells[col_label][row_label], ax) # reminder: pandas row/col order is reversed
                elif applyto == 'data':
                    data = self.wells[col_label][row_label].get_data()
                    if data is not None:
                        if func.func_code.co_argcount == 1:
                            func(data)
                        else:
                            func(data, ax)
                else:
                    raise ValueError, 'Encountered unsupported value {} for applyto paramter.'.format(applyto)

        sca(gHandleList[0]) # sets to the main axis -- more intuitive
        return gHandleList

if __name__ == '__main__':
    pass
