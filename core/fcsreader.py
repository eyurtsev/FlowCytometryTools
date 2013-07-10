#!/usr/bin/env python
# A script to read FCS 3.0 formatted file.
# Eugene Yurtsev 07/08/2013
# (I do not promise this works)
# Distributed under the MIT License

import sys
import numpy
from fcm import loadFCS

def raise_parser_feature_not_implemented(message):
    print """ Some of the parser features have not yet been implemented.
    If you would like to see this feature implemented, please send a sample FCS file
    to the developers.
    The problem encountered with your FCS file is the following: """
    raise Exception(message)

class FCS_Parser(object):
    def __init__(self, filename):
        self.header = {}

        with open(filename,'rb') as f:
            self.read_header(f)
            self.read_meta(f)
            self.read_data(f)

    def get_data(self):
        """
        Returns the meta and data for the fcs file.
        """
        return self.data

    def read_header(self, file_handle):
        """
        Reads the header of the FCS file.
        The header specifies where the annotation, data and analysis are located inside the binary file.
        """
        self.header['header version'] = file_handle.read(6)

        if self.header['header version'] != 'FCS3.0':
            raise_parser_feature_not_implemented('Parser implemented only for FCS 3.0 files')

        file_handle.read(4) # 4 space characters after the header version

        for field in ['text start', 'text end', 'data start', 'data end', 'analysis start', 'analysis end']:
            self.header[field] = int(file_handle.read(8))

        if self.header['data start'] == 0 or self.header['data end'] == 0:
            raise_parser_feature_not_implemented("""The FCS file is big. The locations of data start and end are located in the TEXT section of the data. However,
            this parser cannot handle this case yet. Please send the sample fcs file to the developer. """)


    def read_meta(self, file_handle):
        """
        Reads the TEXT segment of the FCS file.
        Here, it is referred to as meta.
        Converting all meta keywords to lower case.
        """
        file_handle.seek(self.header['text start'], 0)

        raw_text = file_handle.read(self.header['text end'] - self.header['text start'] + 1)

        delimiter = raw_text[0]

        if raw_text[-1] != delimiter:
            raise_parser_feature_not_implemented('Parser expects the same delimiter character in beginning and end of TEXT segment')

        raw_text_segments = raw_text[1:-1].split(delimiter) # Using 1:-1 to remove first and last characters which should be reserved for delimiter

        keys, values = raw_text_segments[0::2], raw_text_segments[1::2]

        text = {str(key).lower() : value for key, value in zip(keys, values)} # Build dictionary

        pars = int(text['$par'])
        self.channel_names = [text['$p{0}n'.format(num+1)] for num in range(pars)]

        ## The lists are necessary to optimize the for loop. Regular expressions appear to be too heavy the way I was using them
        # TO DO Improve speed here. Stop loop through keys and access fields directly
        par_b_list = ['$p{0}b'.format(i+1) for i in range(pars)]
        par_d_list = ['$p{0}d'.format(i+1) for i in range(pars)]
        int_key_list = ['$nextdata', '$par', '$tot']

        # Converting a few of the fields into numeric values
        for key, value in text.items():
            if key in par_b_list is not None or key in int_key_list:
                text[key] = int(value)

            # Parameter that indicates log amplification
            if key in par_d_list:
                nums = value.split(',')
                text[key] = [float(num) for num in nums]

                if text[key] != [0.0, 0.0]:
                    raise_parser_feature_not_implemented('Log amplification in parameter: {0}'.format(key))

        self.header['text'] = text

        ### Keep for debugging
        #key_list = self.header['text'].keys()
        #for key in sorted(text.keys()):
            #print key, text[key]
        #raise Exception('here')

        self.check_assumptions(text)

    def check_assumptions(self, text):
        """
        Checks the FCS file to make sure that some of the assumptions made by the parser are met.
        """
        keys = text.keys()

        if '$nextdata' in text and text['$nextdata'] != 0:
            raise_parser_feature_not_implemented('Not implemented $nextdata is not 0')

        if '$mode' not in text or text['$mode'] != 'L':
            raiseParserFeaturerNotImplemented('Mode not implemented')

        if '$p0b' in keys:
            raiseParserFeaturerNotImplemented('Not expecting a parameter starting at 0')

        if text['$byteord'] not in ["1,2,3,4", "4,3,2,1", "1,2", "2,1"]:
            raiseParserFeaturerNotImplemented('$byteord {} not implemented'.format(text['$byteord']))


    def read_data(self, file_handle):
        """ Reads the DATA segment of the FCS file. """
        text = self.header['text'] # For convenience
        num_events = text['$tot'] # Number of events recorded
        num_pars   = text['$par'] # Number of parameters recorded

        # TODO: Kill white space in $byteord
        if text['$byteord'] == '1,2,3,4' or text['$byteord'] == '1,2':
            endian = '<'
        elif text['$byteord'] == '4,3,2,1' or text['$byteord'] == '2,1':
            endian = '>'

        conversion_dict = {'F' : 'f4', 'D' : 'f8'} # matching FCS naming convention with numpy naming convention f4 - 4 byte (32 bit) single precision float

        if text['$datatype'] not in conversion_dict.keys():
            raiseParserFeaturerNotImplemented('$datatype is not yet supported.')

        dtype = '{endian}{kind}'.format(endian=endian, kind=conversion_dict[text['$datatype']])

        # Calculations to figure out data types of each of parameters
        bytes_per_par_list   = [self.header['text']['$p{0}b'.format(i)] / 8  for i in range(1, num_pars+1)]
        par_numeric_type_list   = ['{endian}f{size}'.format(endian=endian, size=bytes_per_par) for bytes_per_par in bytes_per_par_list]
        bytes_per_event = sum(bytes_per_par_list)
        total_bytes = bytes_per_event * num_events

        # Parser for list mode. Here, the order is a list of tuples. where each tuples stores event related information
        file_handle.seek(self.header['data start'], 0) # Go to the part of the file where data starts

        # Read in the data
        if len(set(par_numeric_type_list)) > 1:
            data = numpy.fromfile(file_handle, dtype=','.join(par_numeric_type_list), count=num_events)
            raiseParserFeaturerNotImplemented('The different channels were saved using mixed numeric formats')
        else:
            data = numpy.fromfile(file_handle, dtype=dtype, count=num_events * num_pars)
            data = data.reshape((num_events, num_pars))

        self.data = data

###################
### Test code #####
###################

def compare_against_fcm():
    print 'Comparing fcm reader and EYs reader'
    import time
    tic = time.time()
    fname = './tests/sample_data/2.fcs'
    #fname = './tests/sample_data/Miltenyi.fcs'

    for i in range(1):
        x = FCS_Parser(fname).get_data()
        y = loadFCS(fname, transform=None, auto_comp=False)


    #import FlyingButterfly
    #from FlyingButterfly.FlyingButterfly import set_pret
    print y[:22, 6] - x[:22, 6]
    #print x[:2, :]

    toc = time.time()
    print toc-tic
    #tic = time.time()
    #toc = time.time()

    #print toc-tic


if __name__ == '__main__':
    #y = loadFCS(, transform=None)
    #print y[0, 10]


