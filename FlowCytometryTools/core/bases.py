"""Base objects for measurement and plate objects."""
import inspect
import os

import decorator
import pylab as pl
import six
from numpy import nan, unravel_index
from pandas import DataFrame as DF

from FlowCytometryTools.core import graph
from FlowCytometryTools.core.common_doc import doc_replacer
from FlowCytometryTools.core.utils import get_tag_value, get_files, save, load, to_list


@doc_replacer
def _assign_IDS_to_datafiles(datafiles, parser, measurement_class=None, **kwargs):
    """
    Assign measurement IDS to datafiles using specified parser.

    Parameters
    ----------
    datafiles : iterable of str
        Path to datafiles. An ID will be assigned to each.
        Note that this function does not check for uniqueness of IDs!
    {_bases_filename_parser}
    measurement_class: object
        Used to create a temporary object when reading the ID from the datafile.
        The measurement class needs to have an `ID_from_data` method.
        Only used when parser='read'.
    kwargs: dict
        Additional parameters to be passed to parser is it is a callable, or 'read'.
        If parser is 'read', kwargs are passed to the measurement class's `ID_from_data` method.

    Returns
    -------
    Dict of ID:datafile
    """
    if isinstance(parser, collections.Mapping):
        fparse = lambda x: parser[x]
    elif hasattr(parser, '__call__'):
        fparse = lambda x: parser(x, **kwargs)
    elif parser == 'name':
        kwargs.setdefault('pre', 'Well_')
        kwargs.setdefault('post', ['_', '\.', '$'])
        kwargs.setdefault('tagtype', str)
        fparse = lambda x: get_tag_value(os.path.basename(x), **kwargs)
    elif parser == 'number':
        fparse = lambda x: int(x.split('.')[-2])
    elif parser == 'read':
        fparse = lambda x: measurement_class(ID='temporary', datafile=x).ID_from_data(**kwargs)
    else:
        raise ValueError('Encountered unsupported value "%s" for parser parameter.' % parser)
    d = dict((fparse(dfile), dfile) for dfile in datafiles)
    return d


def int2letters(x, alphabet):
    """
    Return the alphabet representation of a non-negative integer x.
    For example, with alphabet=['a','b']
    0 -> 'a'
    1 -> 'b'
    2 -> 'aa'
    3 -> 'ab'
    4 -> 'ba'

    Modified from:
    http://stackoverflow.com/questions/2267362/convert-integer-to-a-string-in-a-given-numeric-base-in-python
    """
    base = len(alphabet)
    if x < 0:
        raise ValueError('Only non-negative numbers are supported. Encountered %s' % x)
    letters = []
    quotient = x
    while quotient >= 0:
        quotient, remainder = divmod(quotient, base)
        quotient -= 1
        letters.append(alphabet[remainder])
    letters.reverse()
    return ''.join(letters)


_now = 'apply_now'


@decorator.decorator
def queueable(fun, *args, **kwargs):
    params = inspect.getcallargs(fun, *args, **kwargs)
    if not _now in params:
        raise ValueError('"%s" must be a parameter of queued function "%s"' % (_now, fun.__name__))
    f_name = fun.__name__
    kw_name = inspect.getargspec(fun).keywords
    kws = params.pop(kw_name, {})
    params.update(kws)
    if params[_now]:
        out = fun(*args, **kwargs)
        out.queue = []
        out.history.append((f_name, params))
        return out
    else:
        new = params['self'].copy()
        del params['self']
        params[_now] = True

        new.queue.append((f_name, params))
        return new


class BaseObject(object):
    """
    Object providing common utility methods.
    Used for inheritance.
    """

    def __repr__(self):
        return '<{0} {1}>'.format(type(self).__name__, repr(self.ID))

    def save(self, path):
        """ Saves object to a pickled file. """
        save(self, path)

    @classmethod
    def load(cls, path):
        """ Loads object from a pickled file. """
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
    """
    A class for holding data from a single measurement, i.e.
    a single well or a single tube.
    """

    def __init__(self, ID,
                 datafile=None, readdata=False, readdata_kwargs={},
                 metafile=None, readmeta=True, readmeta_kwargs={}):
        self.ID = ID
        self.datafile = datafile
        self.metafile = metafile
        self._data = None
        self._meta = None
        self.readdata_kwargs = readdata_kwargs
        self.readmeta_kwargs = readmeta_kwargs
        if readdata: self.set_data()
        if readmeta: self.set_meta()
        self.position = {}
        self.history = []
        self.queue = []

    def _set_position(self, orderedcollection_id, pos):
        self.position[orderedcollection_id] = pos

    @property
    def shape(self):
        if self.data is None:
            return None
        else:
            return self.data.shape

    def apply_queued(self):
        new = self.copy()
        new.queue = []
        for a in self.queue:
            name, params = a
            new = getattr(new, name)(**params)
        return new

    #     # An example for how to write a queueable function
    #     @queueable
    #     def fake_action(self, a, b='!', apply_now=False, **kws):
    #         '''
    #         Detailed doc.
    #         '''
    #         new = self.copy()
    #         data = self.get_data()
    #         if data is None: data = ''
    #         c = kws.get('c',' ')
    #         new_data = data + (a + b +' (%s). '%c)
    #         new.set_data(data=new_data)
    #         new.data = new_data
    #         return new

    # ----------------------
    # Methods of exposing underlying data
    # ----------------------
    def __contains__(self, key):
        return self.data.__contains__(key)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    # ----------------------
    # Methods getting/setting data
    # ----------------------
    def read_data(self, **kwargs):
        """
        This function should be overwritten for each
        specific data type.
        """
        pass

    def read_meta(self, **kwargs):
        """
        This function should be overwritten for each
        specific data type.
        """
        pass

    def set_data(self, data=None, **kwargs):
        """
        Read data into memory, applying all actions in queue.
        Additionally, update queue and history.
        """
        if data is None:
            data = self.get_data(**kwargs)
        setattr(self, '_data', data)
        self.history += self.queue
        self.queue = []

    def set_meta(self, meta=None, **kwargs):
        """
        Assign values to self.meta.
        Meta is not returned
        """
        if meta is None:
            meta = self.get_meta(**kwargs)
        setattr(self, '_meta', meta)

    def _get_attr_from_file(self, name, **kwargs):
        """
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
        """
        current_value = getattr(self, '_' + name)
        if current_value is not None:
            value = current_value
        else:
            parser_kwargs = getattr(self, 'read%s_kwargs' % name, {})
            value = getattr(self, 'read_%s' % name)(**parser_kwargs)
        return value

    def get_data(self, **kwargs):
        """
        Get the measurement data.
        If data is not set, read from 'self.datafile' using 'self.read_data'.
        """
        if self.queue:
            new = self.apply_queued()
            return new.get_data()
        else:
            return self._get_attr_from_file('data', **kwargs)

    def get_meta(self, **kwargs):
        """
        Get the measurement metadata.
        If not metadata is not set, read from 'self.metafile' using 'self.read_meta'.
        """
        return self._get_attr_from_file('meta', **kwargs)

    data = property(get_data, set_data, doc='Data may be stored in memory or on disk')
    meta = property(get_meta, set_meta, doc='Metadata associated with measurement.')

    # ----------------------
    def get_meta_fields(self, fields, **kwargs):
        """
        Get specific fields of associated metadata.

        This function should be overwritten for each
        specific data type.
        """
        pass

    def ID_from_data(self):
        """
        Get measurement ID from loaded data.

        This function should be overwritten for each
        specific data type.
        """
        pass

    def apply(self, func, applyto='measurement', noneval=nan, setdata=False):
        """
        Apply func either to self or to associated data.
        If data is not already parsed, try and read it.

        Parameters
        ----------
        func : callable
            The function either accepts a measurement object or an FCS object.
            Does some calculation and returns the result.
        applyto : ['data' | 'measurement']
            * 'data' : apply to associated data
            * 'measurement' : apply to measurement object itself.
        noneval : obj
            Value to return if `applyto` is 'data', but no data is available.
        setdata : bool
            Used only if data is not already set.
            If true parsed data will be assigned to self.data
            Otherwise data will be discarded at end of apply.
        """
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
        elif applyto == 'measurement':
            return func(self)
        else:
            raise ValueError('Encountered unsupported value "%s" for applyto parameter.' % applyto)


Well = Measurement

import collections


class MeasurementCollection(collections.MutableMapping, BaseObject):
    """
    A collection of measurements
    """
    _measurement_class = Measurement  # to be replaced when inheriting

    def __init__(self, ID, measurements):
        """
        A dictionary-like container for holding multiple Measurements.

        Note that the collection keys are not necessarily identical to the Measurements IDs.
        Additionally, like a dict, measurement keys must be unique.

        Parameters
        ----------
        ID : hashable
            Collection ID
        measurements : mappable | iterable
            values are measurements of appropriate type (type is explicitly check for).
        """
        self.ID = ID
        self.data = {}
        if isinstance(measurements, collections.Mapping):
            self.update(measurements)
        else:
            for m in measurements:
                self[m.ID] = m

    @classmethod
    @doc_replacer
    def from_files(cls, ID, datafiles, parser, readdata_kwargs={}, readmeta_kwargs={}, **ID_kwargs):
        """
        Create a Collection of measurements from a set of data files.

        Parameters
        ----------
        {_bases_ID}
        {_bases_data_files}
        {_bases_filename_parser}
        {_bases_ID_kwargs}
        """
        d = _assign_IDS_to_datafiles(datafiles, parser, cls._measurement_class, **ID_kwargs)
        measurements = []
        for sID, dfile in d.items():
            try:
                measurements.append(cls._measurement_class(sID, datafile=dfile,
                                                           readdata_kwargs=readdata_kwargs,
                                                           readmeta_kwargs=readmeta_kwargs))
            except:
                msg = 'Error occurred while trying to parse file: %s' % dfile
                raise IOError(msg)
        return cls(ID, measurements)

    @classmethod
    @doc_replacer
    def from_dir(cls, ID, datadir, parser, pattern='*.fcs', recursive=False,
                 readdata_kwargs={}, readmeta_kwargs={}, **ID_kwargs):
        """
        Create a Collection of measurements from data files contained in a directory.

        Parameters
        ----------
        ID : hashable
            Collection ID
        datadir : str
            Path of directory containing the data files.
        pattern : str
            Only files matching the pattern will be used to create measurements.
        recursive : bool
            Recursively look for files matching pattern in subdirectories.
        {_bases_filename_parser}
        {_bases_ID_kwargs}
        """
        datafiles = get_files(datadir, pattern, recursive)
        return cls.from_files(ID, datafiles, parser,
                              readdata_kwargs=readdata_kwargs, readmeta_kwargs=readmeta_kwargs,
                              **ID_kwargs)

    # ----------------------
    # MutableMapping methods
    # ----------------------
    def __str__(self):
        return 'ID:\n%s\n\nData:\n%s' % (self.ID, repr(self.data))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if not isinstance(value, self._measurement_class):
            msg = ('Collection of type %s can only contain object of type %s.\n' % (
                type(self), type(self._measurement_class)) +
                   'Encountered type %s.' % type(value))
            raise TypeError(msg)
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    # ----------------------
    # User methods
    # ----------------------
    def apply(self, func, ids=None, applyto='measurement', noneval=nan,
              setdata=False, output_format='dict', ID=None,
              **kwargs):
        """
        Apply func to each of the specified measurements.

        Parameters
        ----------
        func : callable
            Accepts a Measurement object or a DataFrame.
        ids : hashable| iterable of hashables | None
            Keys of measurements to which func will be applied.
            If None is given apply to all measurements.
        applyto :  'measurement' | 'data'
            * 'measurement' : apply to measurements objects themselves.
            * 'data'        : apply to measurement associated data
        noneval : obj
            Value returned if applyto is 'data' but no data is available.
        setdata : bool
            Whether to set the data in the Measurement object.
            Used only if data is not already set.
        output_format : ['dict' | 'collection']
            * collection : keeps result as collection
            WARNING: For collection, func should return a copy of the measurement instance rather
            than the original measurement instance.
        Returns
        -------
        Dictionary keyed by measurement keys containing the corresponding output of func
        or returns a collection (if output_format='collection').
        """
        if ids is None:
            ids = self.keys()
        else:
            ids = to_list(ids)
        result = dict((i, self[i].apply(func, applyto, noneval, setdata)) for i in ids)

        if output_format == 'collection':
            can_keep_as_collection = all(
                [isinstance(r, self._measurement_class) for r in result.values()])
            if not can_keep_as_collection:
                raise TypeError(
                    'Cannot turn output into a collection. The provided func must return results of type {}'.format(
                        self._measurement_class))

            new_collection = self.copy()
            # Locate IDs to remove
            ids_to_remove = [x for x in self.keys() if x not in ids]
            # Remove data for these IDs
            for ids in ids_to_remove:
                new_collection.pop(ids)
            # Update keys with new values
            for k, v in new_collection.items():
                new_collection[k] = result[k]
            if ID is not None:
                new_collection.ID = ID
            return new_collection
        else:
            # Return a dictionary
            return result

    def set_data(self, ids=None):
        """
        Set the data for all specified measurements (all if None given).
        """
        fun = lambda x: x.set_data()
        self.apply(fun, ids=ids, applyto='measurement')

    def _clear_measurement_attr(self, attr, ids=None):
        fun = lambda x: setattr(x, attr, None)
        self.apply(fun, ids=ids, applyto='measurement')

    def clear_measurement_data(self, ids=None):
        """
        Clear the data in all specified measurements (all if None given).
        """
        self._clear_measurement_attr('data', ids=None)

    def clear_measurement_meta(self, ids=None):
        """
        Clear the metadata in all specified measurements (all if None given).
        """
        self._clear_measurement_attr('meta', ids=None)

    def get_measurement_metadata(self, fields, ids=None, noneval=nan,
                                 output_format='DataFrame'):
        """
        Get the metadata fields of specified measurements (all if None given).

        Parameters
        ----------
        fields : str | iterable of str
            Names of metadata fields to be returned.
        ids : hashable| iterable of hashables | None
            Keys of measurements for which metadata will be returned.
            If None is given return metadata of all measurements.
        noneval : obj
            Value returned if applyto is 'data' but no data is available.
        output_format :  'DataFrame' | 'dict'
            'DataFrame' : return DataFrame,
            'dict'      : return dictionary.

        Returns
        -------
        Measurement metadata in specified output_format.
        """
        fields = to_list(fields)
        func = lambda x: x.get_meta_fields(fields)
        meta_d = self.apply(func, ids=ids, applyto='measurement',
                            noneval=noneval, output_format='dict')
        if output_format == 'dict':
            return meta_d
        elif output_format == 'DataFrame':
            from pandas import DataFrame as DF
            meta_df = DF(meta_d, index=fields)
            return meta_df
        else:
            msg = ("The output_format must be either 'dict' or 'DataFrame'. " +
                   "Encountered unsupported value %s." % repr(output_format))
            raise Exception(msg)

    # ----------------------
    # Filtering methods
    # ----------------------
    def filter(self, criteria, applyto='measurement', ID=None):
        """
        Filter measurements according to given criteria.
        Retain only Measurements for which criteria returns True.

        TODO: add support for multiple criteria

        Parameters
        ----------
        criteria : callable
            Returns bool.
        applyto : 'measurement' | 'keys' | 'data' | mapping
             'measurement' : criteria is applied to Measurement objects
             'keys'         : criteria is applied to the keys.
             'data'         : criteria is applied to the Measurement objects' data.
             mapping        : for each key criteria is applied to mapping value with same key.
        ID : str
            ID of the filtered collection.
            If None is given, append '.filterd' to the current sample ID.

        Returns
        -------
        Filtered Collection.
        """
        fil = criteria
        new = self.copy()
        if isinstance(applyto, collections.Mapping):
            remove = (k for k, v in self.items() if not fil(applyto[k]))
        elif applyto == 'measurement':
            remove = (k for k, v in self.items() if not fil(v))
        elif applyto == 'keys':
            remove = (k for k, v in self.items() if not fil(k))
        elif applyto == 'data':
            remove = (k for k, v in self.items() if not fil(v.get_data()))
        else:
            raise ValueError('Unsupported value "%s" for applyto parameter.' % applyto)
        for r in remove:
            del new[r]
        if ID is None:
            ID = self.ID
        new.ID = ID
        return new

    def filter_by_key(self, keys, ID=None):
        """
        Keep only Measurements with given keys.
        """
        keys = to_list(keys)
        fil = lambda x: x in keys
        if ID is None:
            ID = self.ID
        return self.filter(fil, applyto='keys', ID=ID)

    def filter_by_attr(self, attr, criteria, ID=None):
        applyto = {k: getattr(v, attr) for k, v in self.items()}
        if ID is None:
            ID = self.ID
        return self.filter(criteria, applyto=applyto, ID=ID)

    def filter_by_IDs(self, ids, ID=None):
        """
        Keep only Measurements with given IDs.
        """
        fil = lambda x: x in ids
        return self.filter_by_attr('ID', fil, ID)

    def filter_by_meta(self, criteria, ID=None):
        raise NotImplementedError

    def filter_by_rows(self, rows, ID=None):
        """
        Keep only Measurements in corresponding rows.
        """
        rows = to_list(rows)
        fil = lambda x: x in rows
        applyto = {k: self._positions[k][0] for k in self.keys()}
        if ID is None:
            ID = self.ID
        return self.filter(fil, applyto=applyto, ID=ID)

    def filter_by_cols(self, cols, ID=None):
        """
        Keep only Measurements in corresponding columns.
        """
        rows = to_list(cols)
        fil = lambda x: x in rows
        applyto = {k: self._positions[k][1] for k in self.keys()}
        if ID is None:
            ID = self.ID + '.filtered_by_cols'
        return self.filter(fil, applyto=applyto, ID=ID)


class OrderedCollection(MeasurementCollection):
    """
    Collection of Measurements that have an order, e.g. a 96-well Plate.

    TODO:
        - add reshape?
    """

    @doc_replacer
    def __init__(self, ID, measurements, position_mapper, shape=(8, 12),
                 positions=None, row_labels=None, col_labels=None):
        """
        A dictionary-like container for holding multiple Measurements in a 2D array.

        Note that the collection keys are not necessarily identical to the Measurements IDs.
        Additionally, like a dict, measurement keys must be unique.

        Parameters
        ----------
        ID : hashable
            Collection ID
        measurements : mappable | iterable
            values are measurements of appropriate type (type is explicitly checked for).
        {_bases_position_mapper}
        shape : 2-tuple
            Shape of the 2D array of measurements (rows, cols).
        positions : dict | None
            Mapping of measurement_key:(row,col)
            If None is given set positions as specified by the position_mapper arg.
        row_labels : iterable of str
            If None is given, rows will be labeled 'A','B','C', ...
        col_labels : iterable of str
            If None is given, columns will be labeled 1,2,3, ...
        """
        ## init the collection
        super(OrderedCollection, self).__init__(ID, measurements)
        ## set shape-related attributes
        if row_labels is None:
            row_labels = self._default_labels('rows', shape)
        if col_labels is None:
            col_labels = self._default_labels('cols', shape)
        self.row_labels = row_labels
        self.col_labels = col_labels
        ##set positions
        self._positions = {}
        self.set_positions(positions, position_mapper=position_mapper)
        ## check that all positions have been set
        for k in self.keys():
            if k not in self._positions:
                msg = ('All measurement position must be set,' +
                       ' but no position was set for measurement %s' % k)
                raise Exception(msg)

    def __str__(self):
        layout = self.layout
        print_layout = layout.applymap(lambda x: x.ID if hasattr(x, 'ID') else '')
        return 'ID:\n%s\n\nData:\n%s' % (self.ID, print_layout)

    @classmethod
    @doc_replacer
    def from_files(cls, ID, datafiles, parser='name',
                   position_mapper=None,
                   readdata_kwargs={}, readmeta_kwargs={}, ID_kwargs={}, **kwargs):
        """
        Create an OrderedCollection of measurements from a set of data files.

        Parameters
        ----------
        {_bases_ID}
        {_bases_data_files}
        {_bases_filename_parser}
        {_bases_position_mapper}
        {_bases_ID_kwargs}
        kwargs : dict
            Additional key word arguments to be passed to constructor.
        """
        if position_mapper is None:
            if isinstance(parser, six.string_types):
                position_mapper = parser
            else:
                msg = "When using a custom parser, you must specify the position_mapper keyword."
                raise ValueError(msg)
        d = _assign_IDS_to_datafiles(datafiles, parser, cls._measurement_class, **ID_kwargs)
        measurements = []
        for sID, dfile in d.items():
            try:
                measurements.append(cls._measurement_class(sID, datafile=dfile,
                                                           readdata_kwargs=readdata_kwargs,
                                                           readmeta_kwargs=readmeta_kwargs))
            except:
                msg = 'Error occured while trying to parse file: %s' % dfile
                raise IOError(msg)
        return cls(ID, measurements, position_mapper, **kwargs)

    @classmethod
    @doc_replacer
    def from_dir(cls, ID, path,
                 parser='name',
                 position_mapper=None, pattern='*.fcs', recursive=False,
                 readdata_kwargs={}, readmeta_kwargs={}, ID_kwargs={}, **kwargs):
        """
        Create a Collection of measurements from data files contained in a directory.

        Parameters
        ----------
        {_bases_ID}
        datadir : str
            Path of directory containing the data files.
        pattern : str
            Only files matching the pattern will be used to create measurements.
        recursive : bool
            Recursively look for files matching pattern in subdirectories.
        {_bases_filename_parser}
        {_bases_position_mapper}
        {_bases_ID_kwargs}
        kwargs : dict
            Additional key word arguments to be passed to constructor.
        """
        datafiles = get_files(path, pattern, recursive)
        return cls.from_files(ID, datafiles, parser=parser, position_mapper=position_mapper,
                              readdata_kwargs=readdata_kwargs, readmeta_kwargs=readmeta_kwargs,
                              ID_kwargs=ID_kwargs, **kwargs)

    def set_labels(self, labels, axis='rows'):
        """
        Set the row/col labels.
        Note that this method doesn't check that enough labels were set for all the assigned positions.
        """
        if axis.lower() in ('rows', 'row', 'r', 0):
            assigned_pos = set(v[0] for v in self._positions.itervalues())
            not_assigned = set(labels) - assigned_pos
            if len(not_assigned) > 0:
                msg = 'New labels must contain all assigned positions'
                raise ValueError(msg)
            self.row_labels = labels
        elif axis.lower() in ('cols', 'col', 'c', 1):
            self.col_labels = labels
        else:
            raise TypeError('Unsupported axis value %s' % axis)

    def _default_labels(self, axis, shape):
        import string
        if axis == 'rows':
            return [int2letters(i, string.ascii_uppercase) for i in range(shape[0])]
        else:
            return range(1, 1 + shape[1])

    def _is_valid_position(self, position):
        """
        check if given position is valid for this collection
        """
        row, col = position
        valid_r = row in self.row_labels
        valid_c = col in self.col_labels
        return valid_r and valid_c

    @doc_replacer
    def _get_ID2position_mapper(self, position_mapper):
        """
        Defines a position parser that is used
        to map between sample IDs and positions.

        Parameters
        --------------
        {_bases_position_mapper}

        TODO: Fix the name to work with more than 26 letters
        of the alphabet.
        """

        def num_parser(x, order):
            i, j = unravel_index(int(x - 1), self.shape, order=order)
            return (self.row_labels[i], self.col_labels[j])

        if hasattr(position_mapper, '__call__'):
            mapper = position_mapper
        elif isinstance(position_mapper, collections.Mapping):
            mapper = lambda x: position_mapper[x]
        elif position_mapper == 'name':
            mapper = lambda x: (x[0], int(x[1:]))
        elif position_mapper in ('row_first_enumerator', 'number'):
            mapper = lambda x: num_parser(x, 'F')
        elif position_mapper == 'col_first_enumerator':
            mapper = lambda x: num_parser(x, 'C')
        else:
            msg = '"{}" is not a known key_to_position_parser.'.format(position_mapper)
            raise ValueError(msg)
        return mapper

    def set_positions(self, positions=None, position_mapper='name', ids=None):
        """
        checks for position validity & collisions,
        but not that all measurements are assigned.

        Parameters
        -----------
        positions : is dict-like of measurement_key:(row,col)
        parser :
            callable - gets key and returns position
            mapping  - key:pos
            'name'   - parses things like 'A1', 'G12'
            'number' - converts number to positions, going over rows first.
        ids :
            parser will be applied to specified ids only.
            If None is given, parser will be applied to all measurements.

        TODO: output a more informative message for position collisions
        """
        if positions is None:
            if ids is None:
                ids = self.keys()
            else:
                ids = to_list(ids)
            mapper = self._get_ID2position_mapper(position_mapper)
            positions = dict((ID, mapper(ID)) for ID in ids)
        else:
            pass
        # check that resulting assignment is unique (one measurement per position)
        temp = self._positions.copy()
        temp.update(positions)
        if not len(temp.values()) == len(set(temp.values())):
            msg = 'A position can only be occupied by a single measurement'
            raise Exception(msg)

        for k, pos in positions.items():
            if not self._is_valid_position(pos):
                msg = 'Position {} is not supported for this collection'.format(pos)
                raise ValueError(msg)
            self._positions[k] = pos
            self[k]._set_position(self.ID, pos)

    def get_positions(self, copy=True):
        """
        Get a dictionary of measurement positions.
        """
        if copy:
            return self._positions.copy()
        else:
            return self._positions

    def _dict2DF(self, d, noneval, dropna=False):
        df = DF(noneval, index=self.row_labels, columns=self.col_labels, dtype=object)
        for k, res in d.items():
            i, j = self._positions[k]
            df[j][i] = res
        try:
            df = df.astype(float)
        except:
            pass
        if dropna:
            return df.dropna(axis=0, how='all').dropna(axis=1, how='all')
        else:
            return df

    def dropna(self):
        """
        Remove rows and cols that have no assigned measurements.
        Return new instance.
        """
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

    def apply(self, func, ids=None, applyto='measurement',
              output_format='DataFrame', noneval=nan,
              setdata=False, dropna=False, ID=None):
        """
        Apply func to each of the specified measurements.

        Parameters
        ----------
        func : callable
            Accepts a Measurement object or a DataFrame.
        ids : hashable| iterable of hashables | None
            Keys of measurements to which func will be applied.
            If None is given apply to all measurements.
        applyto :  'measurement' | 'data'
            'measurement' : apply to measurements objects themselves.
            'data'        : apply to measurement associated data
        output_format: ['DataFrame' | 'dict' | 'collection']
        noneval : obj
            Value returned if applyto is 'data' but no data is available.
        setdata : bool
            Whether to set the data in the Measurement object.
            Used only if data is not already set.
        dropna : bool
            whether to remove rows/cols that contain no measurements.
        ID : [None | str | numeric]
            ID is used as the new ID for the collection.
            If None, then the old ID is retained.
            Note: Only applicable when output is a collection.

        Returns
        -------
        DataFrame/Dictionary/Collection containing the output of func for each Measurement.
        """
        _output = 'collection' if output_format == 'collection' else 'dict'
        result = super(OrderedCollection, self).apply(func, ids, applyto,
                                                      noneval, setdata,
                                                      output_format=_output)

        # Note: result should be of type dict or collection for the code
        # below to work
        if output_format == 'dict':
            return result
        elif output_format == 'DataFrame':
            return self._dict2DF(result, noneval, dropna)
        elif output_format == 'collection':
            return result
        else:
            msg = ("output_format must be either 'dict' or 'DataFrame'. " +
                   "Encountered unsupported value %s." % repr(output_format))
            raise Exception(msg)

    @doc_replacer
    def grid_plot(self, func, applyto='measurement', ids=None,
                  row_labels=None, col_labels=None,
                  xlim='auto', ylim='auto',
                  xlabel=None, ylabel=None,
                  colorbar=True,
                  row_label_xoffset=None, col_label_yoffset=None,
                  hide_tick_labels=True, hide_tick_lines=True,
                  hspace=0, wspace=0,
                  row_labels_kwargs={}, col_labels_kwargs={}):
        """
        Creates subplots for each well in the plate. Uses func to plot on each axis.
        Follow with a call to matplotlibs show() in order to see the plot.

        Parameters
        ----------
        func : callable
            func is a callable that accepts a measurement
            object (with an optional axis reference) and plots on the current axis.
            Return values from func are ignored.
            .. note: if using applyto='measurement', the function
            when querying for data should make sure that the data
            actually exists
        applyto : 'measurement' | 'data'
        {_graph_grid_layout}
        {bases_OrderedCollection_grid_plot_pars}

        Returns
        -------
        {_graph_grid_layout_returns}

        Examples
        ---------
        >>> def y(well, ax):
        >>>     data = well.get_data()
        >>>     if data is None:
        >>>         return None
        >>>     graph.plotFCM(data, 'Y2-A')
        >>> def z(data, ax):
        >>>     plot(data[0:100, 1], data[0:100, 2])
        >>> plate.plot(y, applyto='measurement');
        >>> plate.plot(z, applyto='data');
        """
        # Acquire call arguments to be passed to create plate layout
        callArgs = locals().copy()  # This statement must remain first. The copy is just defensive.
        [callArgs.pop(varname) for varname in
         ['self', 'func', 'applyto', 'ids', 'colorbar', 'xlim', 'ylim']]  # pop args

        callArgs['rowNum'] = self.shape[0]
        callArgs['colNum'] = self.shape[1]

        subplots_adjust_args = {}
        subplots_adjust_args.setdefault('right', 0.85)
        subplots_adjust_args.setdefault('top', 0.85)
        pl.subplots_adjust(**subplots_adjust_args)

        # Uses plate default row/col labels if user does not override them by specifying row/col
        # labels
        if row_labels == None: callArgs['row_labels'] = self.row_labels
        if col_labels == None: callArgs['col_labels'] = self.col_labels

        ax_main, ax_subplots = graph.create_grid_layout(**callArgs)
        subplots_ax = DF(ax_subplots, index=self.row_labels, columns=self.col_labels)

        if ids is None:
            ids = self.keys()
        ids = to_list(ids)

        for ID in ids:
            measurement = self[ID]
            if not hasattr(measurement, 'data'):
                continue

            row, col = self._positions[ID]
            ax = subplots_ax[col][row]
            pl.sca(ax)  # sets the current axis

            if applyto == 'measurement':
                func(measurement, ax)  # reminder: pandas row/col order is reversed
            elif applyto == 'data':
                data = measurement.get_data()
                if data is not None:
                    if func.func_code.co_argcount == 1:
                        func(data)
                    else:
                        func(data, ax)
            else:
                raise ValueError('Encountered unsupported value {} for applyto parameter.'.format(
                    applyto))

        # Autoscaling axes
        graph.scale_subplots(ax_subplots, xlim=xlim, ylim=ylim)

        #####
        # Placing ticks on the top left subplot
        ax_label = ax_subplots[0, -1]
        pl.sca(ax_label)

        if xlabel:
            xlim = ax_label.get_xlim()
            pl.xticks([xlim[0], xlim[1]], rotation=90)

        if ylabel:
            ylim = ax_label.get_ylim()
            pl.yticks([ylim[0], ylim[1]], rotation=0)

        pl.sca(ax_main)  # sets to the main axis -- more intuitive

        return ax_main, ax_subplots
