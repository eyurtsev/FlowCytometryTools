'''
Created on Jun 14, 2013

@author: jonathanfriedman
'''
from fcm import loadFCS
from bases import BaseSample, BasePlate, to_list


class FCSample(BaseSample):
    '''
    A class for holding flow cytometry data from
    a single well or a single tube.
    '''
    
    def read_data(self, **kwargs):
        '''
        Read the datafile specified in Sample.datafile and 
        return the resulting object.
        Does NOT assign the data to self.data
        '''
        kwargs.setdefault('transform', None)
        data = loadFCS(self.datafile, **kwargs)
        return data
    
    def get_metadata(self, fields, kwargs={}):
        '''
        TODO: change to extract data from other notes fields (not just 'text')
        '''
#         if self.data is None:
#             raise Exception, 'Data must be read before extracting metadata.'
        fields = to_list(fields)
        func = lambda x: [x.notes.text[field] for field in fields]
        kwargs.setdefault('nout',len(fields))
        return self.apply(func, **kwargs)
    
    def ID_from_data(self):
        return self.get_metadata('src')[0]
    
    
class FCPlate(BasePlate):
    '''
    A class for holding flow cytometry plate data.
    '''
    _sample_class = FCSample
        
if __name__ == '__main__':
    datadir = '../tests/data/'
#     print get_files(datadir)
    plate = FCPlate('test', datadir=datadir, shape=(4,5))
#     print plate
    print plate.wells 
    print plate.well_IDS
    
    plate.apply(lambda x:x.ID, 'ID', applyto='sample', well_ids=['A1','B1'])
    plate.apply(lambda x:x.datafile, 'file', applyto='sample')
    plate.apply(lambda x:x.shape[0], 'counts', keepdata=True)
    plate.get_well_metadata(['date', 'etim'])
    print plate.extracted['file'].values
    
#     plate.wells['1']['A'].get_metadata()
#     
#     well_ids = ['A2' , 'B3']
#     print plate.get_wells(well_ids)
#     
#     plate.clear_well_data()  
#     plate.clear_well_data(well_ids)             
            
        