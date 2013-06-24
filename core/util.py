from utilities.util import initialize_object_by_folder_grouping
import os
from containers import FCPlate

def build_FCplate_collection(dirname=None, pattern='*.fcs', recursive=True):
    '''
    Constructs a list of FCPlates by traversing recusively through the file hierarchy.
    All the fcs files under a given directory (on the same level) are grouped into a single FCPlate.
    The FCPlates are assigned the folders name as their ID.
    (NOTE: This means that the ID is not guaranteed to be unique.)
    '''
    return initialize_object_by_folder_grouping(FCPlate, dirname, pattern, recursive)

