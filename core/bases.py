'''
Created on Jun 18, 2013

@author: jonathanfriedman

Base objects for sample and plate objects.

TODO:
- make plate a subclass of collection
- consider converting init methods to accepting data, and adding
factory methods for construction from files.
- consider always reading in data in samples, perhaps storing on disk
using shelve|PyTables|pandas HDFStore
'''
from pandas import DataFrame as DF
from numpy import nan, unravel_index
import pylab as pl
from GoreUtilities.util import get_files, save, load, to_list
from GoreUtilities import graph

def _assign_IDS_to_datafiles(datafiles, parser, sample_class=None):
    '''
    Assign sample IDS to datafiles using specified parser.
    Return a dict of ID:datafile
    '''
    if isinstance(parser, collections.Mapping):
        fparse = lambda x: parser[x]
    elif hasattr(parser, '__call__'):
        fparse = parser
    elif parser == 'name':
        fparse = lambda x: x.split('_')[-1].split('.')[0]
    elif parser == 'number':
        fparse = lambda x: int(x.split('.')[-2])
    elif parser == 'read':
        fparse = lambda x: sample_class(ID='temporary', datafile=x).ID_from_data()
    else:
        raise ValueError,  'Encountered unsupported value "%s" for parser paramter.' %parser 
    d = dict( (fparse(dfile), dfile) for dfile in datafiles )
    return d

def _parse_criteria(criteria):
    if hasattr(criteria, '__call__'):
        return criteria

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

    @property
    def _constructor(self):
        return self.__class__
    
    def copy(self, deep=True):
        """
        Make a copy of this object

        Parameters
        ----------
        deep : boolean, default True
            Make a deep copy, i.e. also copy data

        Returns
        -------
        copy : type of caller
        """
        from copy import copy, deepcopy
        if deep:
            return deepcopy(self)
        else:
            return copy(self)

class Measurement(BaseObject):
    '''
    A class for holding data from a single sample, i.e.
    a single well or a single tube.
    '''
    
    def __init__(self, ID,  
                 datafile=None, readdata=False, readdata_kwargs={},
                 metafile=None, readmeta=True,  readmeta_kwargs={}):
        self.ID = ID
        self.datafile = datafile
        self.metafile = metafile
        if readdata:
            self.set_data(datafile=datafile, **readdata_kwargs)
        else:
            self.data = None
        if readmeta:
            self.set_meta(metafile=metafile, **readmeta_kwargs)
        else:
            self.meta = None
        self.position = {}

    def _set_position(self, orderedcollection_id, pos):
        self.position[orderedcollection_id] = pos

    @property
    def shape(self):
        if self.data is None:
            return None
        else:
            return self.data.shape

    # ----------------------
    # Methods of exposing underlying data
    # ----------------------
    def __contains__(self, key):
        return self.data.__contains__(key)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    # ----------------------
    def read_data(self, **kwargs):
        '''
        This function should be overwritten for each 
        specific data type. 
        '''
        pass
    
    def read_meta(self, **kwargs):
        '''
        This function should be overwritten for each 
        specific data type. 
        '''
        pass

    def _set_attr_from_file(self, name, value=None, path=None, **kwargs):
        '''
        Assign values to attribute of self.
        Attribute values can be passed by user or read from file.
        If read from file: 
            i) the method used to read the file is 'self.read_[attr name]'
            (e.g. for an attribute named 'meta' 'self.read_meta' 
            will be used).
            ii) the file path will also be set to an attribute
            named: '[attr name]file'. (e.g. for an attribute named 
            'meta' a 'metafile' attribute will be created).
        '''
        if value is not None:
            setattr(self, name, value)
        else:
            if path is not None:
                setattr(self, name+'file', path)
            value = getattr(self, 'read_%s' %name)(**kwargs)
        setattr(self, name, value)

    def set_data(self, data=None, datafile=None, **kwargs):
        '''
        Assign values to self.data and self.meta. 
        Data is not returned
        '''
        self._set_attr_from_file('data', data, datafile, **kwargs)

    def set_meta(self, meta=None, metafile=None, **kwargs):
        '''
        Assign values to self.data and self.meta. 
        Data is not returned
        '''
        self._set_attr_from_file('meta', meta, metafile, **kwargs)

    def _get_attr_from_file(self, name, **kwargs):
        '''
        return values of attribute of self.
        Attribute values can the ones assigned already, or the read for 
        the corresponding file.
        If read from file: 
            i) the method used to read the file is 'self.read_[attr name]'
            (e.g. for an attribute named 'meta' 'self.read_meta' 
            will be used).
            ii) the file path will be the one specified in an attribute
            named: '[attr name]file'. (e.g. for an attribute named 
            'meta' a 'metafile' attribute will be created).
        '''
        current_value = getattr(self, name)
        current_path  = getattr(self, name+'file')
        if current_value is not None:
            value = current_value
        elif current_path is not None:
            value = getattr(self, 'read_%s' %name)(**kwargs)
        else:
            value = None
        return value

    def get_data(self, **kwargs):
        '''
        Get the sample data.
        If data is not set, read from 'self.datafile' using 'self.read_data'.
        '''
        return self._get_attr_from_file('data', **kwargs)

    def get_meta(self, **kwargs):
        '''
        Get the sample metadata.
        If not metadata is not set, read from 'self.metafile' using 'self.read_meta'.
        '''
        return self._get_attr_from_file('meta', **kwargs)

    def get_meta_fields(self, fields, **kwargs):
        '''
        Get specific fields of associated metadata.
        
        This function should be overwritten for each 
        specific data type.
        '''
        pass

    def ID_from_data(self):
        '''
        Get sample ID from loaded data.
        
        This function should be overwritten for each 
        specific data type.
        '''
        pass

    def apply(self, func, applyto='sample', noneval=nan, setdata=False):
        '''
        Apply func either to self or to associated data.
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
        setdata : bool
            Used only if data is not already set.
            If true parsed data will be assigned to self.data
            Otherwise data will be discarded at end of apply.
        '''
        applyto = applyto.lower()
        if applyto == 'data':
            if self.data is not None:
                data = self.data
            elif self.datafile is None:
                return noneval
            else:
                data = self.read_data()
                if setdata:
                    self.data = data
            return func(data)
        elif applyto == 'sample':
            return func(self)
        else:
            raise ValueError, 'Encountered unsupported value "%s" for applyto paramter.' %applyto       

Well = Measurement

import collections
class MeasurementCollection(collections.MutableMapping, BaseObject):
    '''
    A collection of samples
    '''
    _sample_class = Measurement #to be replaced when inheriting

    def __init__(self, ID, samples):
        '''
        Constructor
        
        samples : mappable | iterable
            values are samples of appropriate type.
        '''
        self.ID = ID
        self.data = {}
        if isinstance(samples, collections.Mapping):
            self.update(samples)
        else:
            for s in samples:
                self[s.ID] = s 

    @classmethod
    def from_files(cls, ID, datafiles, parser='name'):
        '''
        TODO: allow different sample IDs and collection keys
        '''
        d = _assign_IDS_to_datafiles(datafiles, parser, cls._sample_class)
        samples = []
        for sID, dfile in d.iteritems():
                samples.append(cls._sample_class(sID, datafile=dfile))
        return cls(ID, samples)

    @classmethod
    def from_dir(cls, ID, path, pattern='*.fcs', recursive=False,
                  parser='name'):
        datafiles = get_files(path, pattern, recursive)
        return cls.from_files(ID, datafiles, parser)

    # ----------------------
    # MutableMapping methods
    # ----------------------
    def __repr__(self):
        return 'ID:\n%s\n\nData:\n%s' %(self.ID, repr(self.data))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if not isinstance(value, self._sample_class):
            msg = ('Collection of type %s can only contain object of type %s.\n' %(type(self), type(self._sample_class)) +
                   'Encountered type %s.' %type(value))
            raise TypeError, msg
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    # ----------------------
    # Init support methods
    # ----------------------
    def set_datafiles(self, datafiles=None, datadir=None, 
                      pattern='*.fcs', recursive=True):
        '''
        datafiles : str| iterable of str | None
            Datafiles to parse.
        ''' 
        if datafiles is not None:
            datafiles = to_list(datafiles)
        else:
            datafiles = get_files(datadir, pattern, recursive)        
        self.datafiles = datafiles

    def _assign_IDS_to_datafiles(self, parser):
        '''
        Assign sample IDS to self.datafiles using specified parser.
        Return a dict of ID:datafile
        '''
        if isinstance(parser, collections.Mapping):
            fparse = lambda x: parser[x]
        elif hasattr(parser, '__call__'):
            fparse = parser
        elif parser == 'name':
            fparse = lambda x: x.split('_')[-1].split('.')[0]
        elif parser == 'number':
            fparse = lambda x: int(x.split('.')[-2])
        elif parser == 'read':
            fparse = lambda x: self._sample_class(ID='temporary', datafile=x).ID_from_data()
        else:
            raise ValueError,  'Encountered unsupported value "%s" for parser paramter.' %parser 
        d = dict( (fparse(dfile), dfile) for dfile in self.datafiles )
        return d

    def _create_samples_from_datafile(self, parser):
        d = self._assign_IDS_to_datafiles(parser)
        for ID, dfile in d.iteritems():
                self[ID] = self._sample_class(ID, datafile=dfile)

    # ----------------------
    # User methods
    # ----------------------
    def apply(self, func, ids=None, applyto='sample', 
              noneval=nan, setdata=False):
        '''
        Apply func to each of the specified samples.
        
        Parameters
        ----------
        func : dict 
            Each func value is a callable that accepts a Sample 
            object and returns a single number/string. 
        ids : hashable| iterable of hashables | None
            IDs of well to apply function to.
            If None is given
        applyto : 'data' | 'sample'
            'data'   : apply to samples associated data
            'sample' : apply to sample objects themselves.
        noneval : obj
            Value returned if applyto is 'data' but no data is available.
        setdata : bool
            Used only if data is not already set.
            If true parsed data will be assigned to self.data
            Otherwise data will be discarded at end of apply.
        ''' 
        if ids is None:
            ids = self.keys()
        else:
            ids = to_list(ids)
        result = dict( (i, self[i].apply(func, applyto, noneval, setdata)) for i in ids )
        return result

    def _clear_sample_attr(self, attr, ids=None):
        fun = lambda x: setattr(x, attr, None)
        self.apply(fun, ids=ids, applyto='sample')

    def clear_sample_data(self, ids=None):
        self._clear_sample_attr('data', ids=None)

    def clear_sample_meta(self, ids=None):
        self._clear_sample_attr('meta', ids=None)

    def get_sample_metadata(self, fields, ids=None, noneval=nan,
                            output_format='DataFrame'):
        '''
        '''
        fields = to_list(fields)
        func = lambda x: x.get_meta_fields(fields)
        meta_d = self.apply(func, ids=ids, applyto='sample', 
                          noneval=noneval)
        if output_format is 'dict':
            return meta_d
        elif output_format is 'DataFrame':
            from pandas import DataFrame as DF
            meta_df = DF(meta_d, index=fields)
            return meta_df
        else:
            msg = ("The output_format must be either 'dict' or 'DataFrame'. " +
                   "Encounterd unsupported value %s." %repr(output_format))
            raise Exception(msg)

    # ----------------------
    # Filtering methods
    # ----------------------
    def filter(self, criteria, applyto='samples', ID=None):
        '''
        Filter samples according to given criteria
        
        TODO: add support for multiple criteria
        '''
        fil = _parse_criteria(criteria)
        new = self.copy()
        if isinstance(applyto, collections.Mapping):
            remove = (k for k,v in self.iteritems() if not fil(applyto[k]))
        elif applyto=='samples':
            remove = (k for k,v in self.iteritems() if not fil(v))
        elif applyto=='keys':
            remove = (k for k,v in self.iteritems() if not fil(k))
        elif applyto=='data':
            remove = (k for k,v in self.iteritems() if not fil(v.get_data()))
        else:
            raise ValueError, 'Unsupported value "%s" for applyto parameter.' %applyto
        for r in remove:
            del new[r]
        if ID is None:
            ID = self.ID + '.filtered'
        new.ID = ID
        return new

    def filter_by_key(self, keys, ID=None):
        keys = to_list(keys)
        fil = lambda x: x in keys
        if ID is None:
            ID = self.ID + '.filtered_by_key'            
        return self.filter(fil, applyto='keys', ID=ID) 

    def filter_by_attr(self, attr, criteria, ID=None):
        applyto = {k:getattr(v,attr) for k,v in self.iteritems()}
        if ID is None:
            ID = self.ID + '.filtered_by_%s' %attr
        return self.filter(criteria, applyto=applyto, ID=ID)

    def filter_by_IDs(self, ids, ID=None):
        fil = lambda x: x in ids
        return self.filter_by_attr('ID', fil, ID)

    def filter_by_meta(self, criteria, ID=None):
        raise NotImplementedError

    def filter_by_rows(self, rows, ID=None):
        rows = to_list(rows)
        fil = lambda x: x in rows
        applyto = {k:self._positions[k][0] for k in self.iterkeys()}
        if ID is None:
            ID = self.ID + '.filtered_by_rows'        
        return self.filter(fil, applyto=applyto, ID=ID)

    def filter_by_cols(self, cols, ID=None):
        rows = to_list(cols)
        fil = lambda x: x in rows
        applyto = {k:self._positions[k][1] for k in self.iterkeys()}
        if ID is None:
            ID = self.ID + '.filtered_by_cols'        
        return self.filter(fil, applyto=applyto, ID=ID)

class OrderedCollection(MeasurementCollection):
    '''
    - add dropna to self?
    - add reshape? 
    - add factory methods (from_files, for_path)
    - get entire rows/cols 
    - output format (of some filter/apply): list, dict, 
    OC of original size, OC of new size
    + OC should check for position collisions.
    ''' 
    def __init__(self, ID, samples, shape=(8,12),
                 positions=None, position_parser='name',
                 row_labels=None, col_labels=None):
        ## init the collection
        super(OrderedCollection, self).__init__(ID, samples)
        ## set shape-related attributes
        if row_labels is None:
            row_labels = self._default_labels('rows', shape)
        if col_labels is None:
            col_labels = self._default_labels('cols', shape)
        self.row_labels = row_labels
        self.col_labels = col_labels
        ##set positions
        self._positions = {}
        self.set_positions(positions, parser=position_parser)
        ## check that all positions have been set
        for k in self.iterkeys():
            if k not in self._positions:
                msg = ('All sample position must be set,' +
                       ' but no position was set for sample %s' %k)
                raise Exception, msg

    def __repr__(self):
        layout=self.layout
        print_layout = layout.fillna('')
        return 'ID:\n%s\n\nData:\n%s' %(self.ID, repr(print_layout))

    @classmethod
    def from_files(cls, ID, datafiles, file_parser='name', **kwargs):
        '''
        TODO: allow different sample IDs and collection keys
        '''
        d = _assign_IDS_to_datafiles(datafiles, file_parser, cls._sample_class)
        samples = []
        for sID, dfile in d.iteritems():
                samples.append(cls._sample_class(sID, datafile=dfile))
        return cls(ID, samples, **kwargs)

    @classmethod
    def from_dir(cls, ID, path, pattern='*.fcs', recursive=False,
                  file_parser='name', **kwargs):
        datafiles = get_files(path, pattern, recursive)
        return cls.from_files(ID, datafiles, file_parser='name', **kwargs)

#     def set_labels(self, labels, axis='rows'):
#         '''
#         Set the row/col labels.
#         Note that this method doesn't check that enough labels were set for all the assigned positions.
#         '''
#         if axis.lower() in ('rows', 'row', 'r', 0):
#             assigned_pos = set(v[0] for v in self._positions.itervalues())
#             not_assigned = set(labels) - assigned_pos
#             if len(not_assigned)>0:
#                 msg = 'New labels must contain all assigned positions'
#                 raise ValueError, msg
#             self.row_labels = labels
#         elif axis.lower() in ('cols', 'col', 'c', 1):
#             self.col_labels = labels
#         else:
#             raise TypeError, 'Unsupported axis value %s' %axis


    def _default_labels(self, axis, shape):
        import string
        if axis == 'rows':
            return [string.uppercase[i] for i in range(shape[0])]
        else:
            return  range(1, 1+shape[1])

    def _is_valid_position(self, position):
        '''
        check if given position is valid for this collection
        '''
        row, col = position
        valid_r = row in self.row_labels
        valid_c = col in self.col_labels
        return valid_r and valid_c

    def _get_ID2position_parser(self, parser):
        '''
        '''
        if hasattr(parser, '__call__'):
            pass
        elif isinstance(parser, collections.Mapping):
            parser = lambda x: parser[x]
        elif parser == 'name':
            parser = lambda x: (x[0], int(x[1:]))
        elif parser == 'number':
            def num_parser(x):
                i,j = unravel_index(int(x), self.shape)
                return (self.row_labels[i], self.col_labels[j])
            parser = num_parser
        else:
            raise ValueError,  'Encountered unsupported value "%s" for parser paramter.' %parser 
        return parser

    def set_positions(self, positions=None, parser='name', ids=None):
        '''
        checks for position validity & collisions, 
        but not that all samples are assigned.
        
        pos is dict-like of sample_key:(row,col)
        parser :
            callable - gets key and returns position
            mapping  - key:pos
            'name'   - parses things like 'A1', 'G12'
            'number' - converts number to positions, going over rows first.
        ids :
            parser will be applied to specified ids only. 
            If None is given, parser will be applied to all samples.
        TODO: output a more informative message for position collisions
        '''
        if positions is None:
            if ids is None:
                ids = self.keys()
            else:
                ids = to_list(ids)
            parser = self._get_ID2position_parser(parser)
            positions = dict( (ID, parser(ID)) for ID in ids )
        else:
            pass
        # check that resulting assignment is unique (one sample per position)
        temp = self._positions.copy()
        temp.update(positions)
        if not len(temp.values())==len(set(temp.values())):
            msg = 'A position can only be occupied by a single sample'
            raise Exception, msg

        for k, pos in positions.iteritems():
            if not self._is_valid_position(pos):
                msg = 'Position {} is not supported for this collection'.format(pos)
                raise ValueError, msg
            self._positions[k] = pos
            self[k]._set_position(self.ID, pos)

    def get_positions(self, copy=True):
        '''
        Get a dictionary of sample positions.
        '''
        if copy:
            return self._positions.copy()
        else:
            return self._positions

    def _dict2DF(self, d, noneval, dropna=False):
        df = DF(noneval, index=self.row_labels, columns=self.col_labels, dtype=object)
        for k, res in d.iteritems():
            i,j = self._positions[k]
            df[j][i] = res
        if dropna:
            return df.dropna(axis=0, how='all').dropna(axis=1, how='all')
        else:
            return df

    def dropna(self):
        '''
        Remove rows and cols that have no assigned samples.
        Return new instance.
        '''
        new = self.copy()
        tmp = self._dict2DF(self, nan, True)
        new.row_labels = list(tmp.index)
        new.col_labels = list(tmp.columns)
        return new
        
    @property
    def layout(self):
        return self._dict2DF(self, nan)

    @property
    def shape(self):
        return (len(self.row_labels), len(self.col_labels))

    def apply(self, func, ids=None, applyto='sample', 
              output_format='DataFrame', noneval=nan, 
              setdata=False, dropna=False):
        '''
        Apply func to each of the specified samples.
        
        Parameters
        ----------
        func : dict 
            Each func value is a callable that accepts a Sample 
            object and returns a single number/string. 
        ids : hashable| iterable of hashables | None
            IDs of well to apply function to.
            If None is given
        output_format : 'DataFrame' | 'dict'
        applyto : 'data' | 'sample'
            'data'   : apply to samples associated data
            'sample' : apply to sample objects themselves.
        noneval : obj
            Value returned if applyto is 'data' but no data is available.
        setdata : bool
            Used only if data is not already set.
            If true parsed data will be assigned to self.data
            Otherwise data will be discarded at end of apply.
        dropna : bool
            whether to remove rows/cols that contain no samples.
        ''' 
        result = super(OrderedCollection, self).apply(func, ids, applyto, 
                                                       noneval, setdata)
        if output_format is 'dict':
            return result
        elif output_format is 'DataFrame':
            return self._dict2DF(result, noneval, dropna)
        else:
            msg = ("The output_format must be either 'dict' or 'DataFrame'. " +
                   "Encounterd unsupported value %s." %repr(output_format))
            raise Exception(msg)

    def grid_plot(self, func, applyto='sample', ids=None, row_labels=None, col_labels=None,
                xlim=None, ylim=None,
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
        ids : None
        col_labels : str
            labels for the columns if None default labels are used
        row_labels : str
            labels for the rows if None default labels are used
        xlim : 2-tuple
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
        [callArgs.pop(varname) for varname in  ['self', 'func', 'applyto', 'ids']] # pop args
        callArgs['rowNum'] = self.shape[0]
        callArgs['colNum'] = self.shape[1]

        if row_labels == None: callArgs['row_labels'] = self.row_labels
        if col_labels == None: callArgs['col_labels'] = self.col_labels

        # TODO: decide on naming convention

        gHandleList = graph.create_grid_layout(**callArgs)
        subplots_ax = DF(gHandleList[1], index=self.row_labels, columns=self.col_labels)

        if ids is None:
            ids = self.keys()
        ids = to_list(ids)

        for ID in ids:
            sample = self[ID]
            if not hasattr(sample, 'data'):
                continue

            row, col = self._positions[ID]
            ax = subplots_ax[col][row]
            pl.sca(ax) # sets the current axis

            if applyto == 'sample':
                func(sample, ax) # reminder: pandas row/col order is reversed
            elif applyto == 'data':
                data = sample.get_data()
                if data is not None:
                    if func.func_code.co_argcount == 1:
                        func(data)
                    else:
                        func(data, ax)
            else:
                raise ValueError, 'Encountered unsupported value {} for applyto paramter.'.format(applyto)

        # Takes care of scaling the view properly
        if not xlim and not ylim:
            axis = 'both'
        elif not xlim:
            axis = 'x'
        elif not ylim:
            axis = 'y'

        pl.autoscale(True, axis)

        pl.sca(gHandleList[0]) # sets to the main axis -- more intuitive
        return gHandleList

if __name__ == '__main__':
    pass
