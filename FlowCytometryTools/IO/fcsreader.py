#!/usr/bin/env python
# A script to read FCS 3.0 formatted file (and potentially FCS 2.0 and 3.1)
# Eugene Yurtsev 07/20/2013
# (I do not promise this works)
# Distributed under the MIT License
# TODO: Throw an error if there is logarithmic amplification (or else implement support for it)

# Useful documentation for dtypes in numpy

# Bytes swap may be faster?
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.ndarray.byteswap.html?highlight=byteswap#numpy.ndarray.byteswap
# http://docs.scipy.org/doc/numpy/user/basics.types.html
# http://docs.scipy.org/doc/numpy/reference/arrays.dtypes.html


import sys, warnings, re, string
import numpy

try:
    import pandas
    pandas_found = True
except ImportError:
    print('You do not have pandas installed, so the parse_fcs function can only be used together with numpy.')
    pandas_found = False
except Exception as e:
    print('Your pandas is improperly configured. It raised the following error {0}'.format(e))
    pandas_found = False

def raise_parser_feature_not_implemented(message):
    print """ Some of the parser features have not yet been implemented.
              If you would like to see this feature implemented, please send a sample FCS file
              to the developers.
              The following problem was encountered with your FCS file:
              {0} """.format(message)
    raise NotImplementedError(message)

class FCS_Parser(object):
    """
    A Parser for .fcs files.
    Should work for FCS 3.0
    May work for other FCS formats (2.0, 3.1)

    self.annotation: a dictionary holding the parsed content of the TEXT segment
                     In addition, a key called __header__ has been added to this dictionary
                     It specifies the information parsed from the FCS file HEADER segment.
                     (This won't be necessary for most users.)

    self.data holds the parsed DATA segment
    self.analysis holds the ANALYSIS segment as read from the file.

    self.channel_names holds the chosen names of the channels
    self.channel_names_alternate holds the alternate names of the channels
    """
    def __init__(self, path, read_data=True, channel_naming='$PnS'):
        """
        Parameters
        ----------
        path : str
            Path of .fcs file
        read_data : bool
            If True, reads the data immediately.
            Otherwise, use read_data method to read in the data from the fcs file.
        channel_naming: '$PnS' | '$PnN'
            Determines which meta data field is used for naming the channels.

            The default should be $PnS (even though it is not guaranteed to be unique)

            $PnN stands for the short name (guaranteed to be unique). Will look like 'FL1-H'
            $PnS stands for the actual name (not guaranteed to be unique). Will look like 'FSC-H' (Forward scatter)

            The chosen field will be used to population self.channels.

            If the chosen field does not exist in the fcs file. The program attempts to use the alternative field by default.

            Note: These names are not flipped in the implementation.
            It looks like they were swapped for some reason in the official FCS specification.
        """
        self._data = None
        self._channel_naming = channel_naming

        if channel_naming not in ('$PnN', '$PnS'):
            raise ValueError("channel_naming must be either '$PnN' or '$PnS")

        self.annotation = {}
        self.path = path

        with open(path,'rb') as f:
            self.read_header(f)
            self.read_text(f)
            if read_data:
                self.read_data(f)

    def read_header(self, file_handle):
        """
        Reads the header of the FCS file.
        The header specifies where the annotation, data and analysis are located inside the binary file.
        """
        header = {}
        header['FCS format'] = file_handle.read(6)

        #if header['FCS format'] != 'FCS3.0':
            #warnings.warn("""This parser was designed with the FCS 3.0 format in mind. It may or may not work for other FCS formats.""")

        file_handle.read(4) # 4 space characters after the FCS format

        for field in ['text start', 'text end', 'data start', 'data end', 'analysis start', 'analysis end']:
            header[field] = int(file_handle.read(8))

        if header['data start'] == 0 or header['data end'] == 0:
            raise_parser_feature_not_implemented("""The locations of data start and end are located in the TEXT section of the data. However,
            this parser cannot handle this case yet. Please send the sample fcs file to the developer. """)

        if header['analysis start'] != 0:
            warnings.warn('There appears to be some information in the ANALYSIS segment of file {0}. However, might be unable to read it correctly.'.format(self.path))

        self.annotation['__header__'] = header

    def read_text(self, file_handle):
        """
        Reads the TEXT segment of the FCS file.
        This is the meta data associated with the FCS file.
        Converting all meta keywords to lower case.
        """
        header = self.annotation['__header__'] # For convenience

        #####
        # Read in the TEXT segment of the FCS file
        # There are some differences in how the 
        file_handle.seek(header['text start'], 0)
        raw_text = file_handle.read(header['text end'] - header['text start'] + 1)

        #####
        # Parse the TEXT segment of the FCS file into a python dictionary
        delimiter = raw_text[0]

        if raw_text[-1] != delimiter:
            raw_text = raw_text.strip()
            if raw_text[-1] != delimiter:
                print 'The first two characters were: '
                print repr(raw_text[:2])
                print 'The last two characters were: '
                print repr(raw_text[-2:])
                raise_parser_feature_not_implemented('Parser expects the same delimiter character in beginning and end of TEXT segment')

        raw_text_segments = raw_text[1:-1].split(delimiter) # Using 1:-1 to remove first and last characters which should be reserved for delimiter
        keys, values = raw_text_segments[0::2], raw_text_segments[1::2]
        text = {key : value for key, value in zip(keys, values)} # Build dictionary

        ####
        # Extract channel names and convert some of the channel properties and other fields into numeric data types (from string)
        # Note: do not use regular expressions for manipulations here. Regular expressions are too heavy in terms of computation time.
        pars = int(text['$PAR'])
        if '$P0B' in keys: # Checking whether channel number count starts from 0 or from 1
            self.channel_numbers = range(0, pars) # Channel number count starts from 0
        else:
            self.channel_numbers = range(1, pars + 1) # Channel numbers start from 1

        ## Extract parameter names
        try:
            names_n = tuple([text['$P{0}N'.format(i)] for i in self.channel_numbers])
        except KeyError:
            names_n = []

        try:
            names_s = tuple([text['$P{0}S'.format(i)] for i in self.channel_numbers])
        except KeyError:
            names_s = []

        if self._channel_naming == '$PnS':
            self.channel_names, self.channel_names_alternate = names_s, names_n
        else:
            self.channel_names, self.channel_names_alternate = names_n, names_s

        if len(self.channel_names) == 0:
            self.channel_names = self.channel_names_alternate

        # Convert some of the fields into integer values
        keys_encoding_bits  = ['$P{0}B'.format(i) for i in self.channel_numbers]
        keys_encoding_range = ['$P{0}R'.format(i) for i in self.channel_numbers]
        add_keys_to_convert_to_int = ['$NEXTDATA', '$PAR', '$TOT']

        keys_to_convert_to_int = keys_encoding_bits + add_keys_to_convert_to_int

        for key in keys_to_convert_to_int:
            value = text[key]
            text[key] = int(value)

        text['_channel_names_'] = self.channel_names

        self.annotation.update(text)

        ### Keep for debugging
        #key_list = self.header['text'].keys()
        #for key in sorted(text.keys()):
            #print key, text[key]
        #raise Exception('here')

    def read_analysis(self, file_handle):
        """
        Reads the ANALYSIS segment of the FCS file and stores it in self.analysis
        Warning: This has never been tested with an actual fcs file that contains an analysis segment.
        """
        start = self.annotation['__header__']['analysis start']
        end = self.annotation['__header__']['analysis end']
        if start != 0 and end != 0:
            file_handle.seek(self.start, 0)
            self._analysis = file_handle.read(self.end - self.start)
        else:
            self._analysis = ''

    def _check_assumptions(self):
        """
        Checks the FCS file to make sure that some of the assumptions made by the parser are met.
        """
        text = self.annotation
        keys = text.keys()

        if '$NEXTDATA' in text and text['$NEXTDATA'] != 0:
            raise_parser_feature_not_implemented('Not implemented $NEXTDATA is not 0')

        if '$MODE' not in text or text['$MODE'] != 'L':
            raise_parser_feature_not_implemented('Mode not implemented')

        if '$P0B' in keys:
            raise_parser_feature_not_implemented('Not expecting a parameter starting at 0')

        if text['$BYTEORD'] not in ["1,2,3,4", "4,3,2,1", "1,2", "2,1"]:
            raise_parser_feature_not_implemented('$BYTEORD {} not implemented'.format(text['$BYTEORD']))

        # TODO: check logarithmic amplification

    def read_data(self, file_handle):
        """ Reads the DATA segment of the FCS file. """
        self._check_assumptions()
        header, text = self.annotation['__header__'], self.annotation # For convenience
        num_events = text['$TOT'] # Number of events recorded
        num_pars   = text['$PAR'] # Number of parameters recorded

        if text['$BYTEORD'].strip() == '1,2,3,4' or text['$BYTEORD'].strip() == '1,2':
            endian = '<'
        elif text['$BYTEORD'].strip() == '4,3,2,1' or text['$BYTEORD'].strip() == '2,1':
            endian = '>'

        #conversion_dict = {'F' : 'f4', 'D' : 'f8', 'I' : 'u'} # matching FCS naming convention with numpy naming convention f4 - 4 byte (32 bit) single precision float
        conversion_dict = {'F' : 'f', 'D' : 'f', 'I' : 'u'} # matching FCS naming convention with numpy naming convention f4 - 4 byte (32 bit) single precision float

        if text['$DATATYPE'] not in conversion_dict.keys():
            raise_parser_feature_not_implemented('$DATATYPE = {0} is not yet supported.'.format(text['$DATATYPE']))

        #dtype = '{endian}{numerical_type}'.format(endian=endian, numerical_type=conversion_dict[text['$DATATYPE']])

        # Calculations to figure out data types of each of parameters
        bytes_per_par_list   = [text['$P{0}B'.format(i)] / 8  for i in self.channel_numbers] # $PnB specifies the number of bits reserved for a measurement of parameter n
        par_numeric_type_list   = ['{endian}{type}{size}'.format(endian=endian, type=conversion_dict[text['$DATATYPE']], size=bytes_per_par) for bytes_per_par in bytes_per_par_list]
        bytes_per_event = sum(bytes_per_par_list)
        total_bytes = bytes_per_event * num_events

        # Parser for list mode. Here, the order is a list of tuples. where each tuples stores event related information
        file_handle.seek(header['data start'], 0) # Go to the part of the file where data starts

        # Read in the data
        if len(set(par_numeric_type_list)) > 1:
            data = numpy.fromfile(file_handle, dtype=','.join(par_numeric_type_list), count=num_events)
            raise_parser_feature_not_implemented('The different channels were saved using mixed numeric formats')
        else:
            dtype = par_numeric_type_list[0]
            data = numpy.fromfile(file_handle, dtype=dtype, count=num_events * num_pars)
            data = data.reshape((num_events, num_pars))

        self._data = data

    @property
    def data(self):
        """ Holds the parsed DATA segment of the FCS file. """
        if self._data is None:
            with open(self.path, 'rb') as f:
                self.read_data()
        return self._data

    @property
    def analysis(self):
        """ Holds the parsed ANALYSIS segment of the FCS file. """
        if self._analysis == '':
            with open(self.path, 'rb') as f:
                self.read_analysis()
        return self._analysis

    def reformat_meta(self):
        """ Collects the meta data information in a more user friendly format.
        Function looks throught the meta data, collecting the channel related information into a dataframe and moving it into the _channels_ key
        """
        meta = self.annotation
        channel_properties = []

        for key, value in meta.items():
            if key[:3] == '$P1':
                if key[3] not in string.digits:
                    channel_properties.append(key[3:])

        # Capture all the channel information in a list of lists -- used to create a data frame
        channel_matrix = [[meta.get('$P{0}{1}'.format(ch, p)) for p in channel_properties] for ch in self.channel_numbers]

        # Remove this information from the dictionary
        for ch in self.channel_numbers:
            for p in channel_properties:
                key = '$P{0}{1}'.format(ch, p)
                if key in meta:
                    meta.pop(key)

        num_channels = meta['$PAR']
        column_names = ['$Pn{0}'.format(p) for p in channel_properties]

        df = pandas.DataFrame(channel_matrix, columns=column_names, index=(1+numpy.arange(num_channels)))

        if '$PnE' in column_names:
            df['$PnE'] = df['$PnE'].apply(lambda x : x.split(','))

        df.index.name = 'Channel Number'
        meta['_channels_'] = df




def parse_fcs(path, meta_data_only=False, output_format='DataFrame', compensate=False, channel_naming='$PnS', reformat_meta=False):
    """
    Parse an fcs file at the location specified by the path.

    Parameters
    ----------
    path : str
        Path of .fcs file
    meta_data_only : bool
        If True, the parse_fcs only returns the meta_data (the TEXT segment of the FCS file)
    output_format : 'DataFrame' | 'ndarray'
        If set to 'DataFrame' the returned
    channel_naming : '$PnS' | '$PnN'
        Determines which meta data field is used for naming the channels.
        The default should be $PnS (even though it is not guaranteed to be unique)

        $PnN stands for the short name (guaranteed to be unique). Will look like 'FL1-H'
        $PnS stands for the actual name (not guaranteed to be unique). Will look like 'FSC-H' (Forward scatter)

        The chosen field will be used to population self.channels

        Note: These names are not flipped in the implementation.
        It looks like they were swapped for some reason in the official FCS specification.

    reformat_meta : bool
        If true, the meta data is reformatted with the channel information organized into a DataFrame an moved
        into the '_channels_' key

    Returns
    -------
    if meta_data_only is True:
        meta_data : dict
            Contains a dictionary with the meta data information
            meta_data also contains the channel_names under the '_channel_names_' key
    Otherwise:
        a 2-tuple with
            the first element the meta_data (dictionary)
            the second element the data (in either DataFrame or numpy format)

    Examples
    --------
    fname = '../tests/data/EY_2013-05-03_EID_214_PID_1120_Piperacillin_Well_B7.001.fcs'
    meta = parse_fcs(fname, meta_data_only=True)
    meta, data_pandas = parse_fcs(fname, meta_data_only=False, output_format='DataFrame')
    meta, data_numpy  = parse_fcs(fname, meta_data_only=False, output_format='ndarray')
    """
    if compensate == True:
        raise_parser_feature_not_implemented('Compensation has not been implemented yet.')


    read_data = not meta_data_only

    parsed_FCS = FCS_Parser(path, read_data=read_data, channel_naming=channel_naming)

    if reformat_meta:
        parsed_FCS.reformat_meta()

    meta = parsed_FCS.annotation
    channel_names = parsed_FCS.channel_names

    if meta_data_only:
        return meta
    elif output_format == 'DataFrame':
        """ Constructs pandas DF object """
        if pandas_found == False:
            raise ImportError('You do not have pandas installed.')
        data = parsed_FCS.data
        data = pandas.DataFrame(data, columns=parsed_FCS.channel_names)
        return meta, data
    elif output_format == 'ndarray':
        """ Constructs numpy matrix """
        return meta, parsed_FCS.data
    else:
        raise ValueError("The output_format must be either 'ndarray' or 'DataFrame'")

if __name__ == '__main__':
    import glob
    fname = glob.glob('../tests/data/Plate01/*.fcs')[0]
    #fname = '../tests/data/EY_2013-05-03_EID_214_PID_1120_Piperacillin_Well_B7.001.fcs'
    meta = parse_fcs(fname, meta_data_only=True)
    meta, data_pandas = parse_fcs(fname, meta_data_only=False, output_format='DataFrame')
    meta, data_numpy = parse_fcs(fname, meta_data_only=False, output_format='ndarray', reformat_meta=True)
    print meta['_channel_names_']
    print meta
    print meta['_channels_']




