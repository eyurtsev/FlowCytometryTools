import os
from containers import FCPlate

def build_FCplate_collection(dirname=None, pattern='*.fcs', recursive=True):
    '''
    Constructs a dictionary of FCPlates by traversing recusively through the file hierarchy.
    All the fcs files under a given directory (on the same level) are grouped into a single FCPlate.
    The FCPlates are assigned the folders name as their ID.
    (NOTE: This means that the ID is not guaranteed to be unique.)
    '''
    return initialize_object_by_folder_grouping(FCPlate, dirname, pattern, recursive)

def build_hierarchy(fileList):
    '''
    Returns a dictionary in which each key corresponds
    to a list of files that are found in that directory.
    '''
    directoryDict = {}

    for thisFile in fileList:
        splitPath = thisFile.split(os.path.sep)
        if len(splitPath) > 1:
            directoryName = splitPath[-2]
        else:
            directoryName = '.'
        if directoryName not in directoryDict.keys():
            directoryDict[directoryName] = [thisFile]
        else:
            directoryDict[directoryName].append(thisFile)

    return directoryDict


def initialize_object_by_folder_grouping(_class, dirname=None, pattern='*.*', recursive=True, validiator=None):
    '''
    Walks recusively through the file hierarchy identifying all files matching the specified pattern.
    All files under a directory's level are grouped together and passed
    into _class as a list.
    _class is used to instantiate an object based on the file group.
    validiator : function
        gets two arguments (dirname and fileList) if function returns True then object is constructed
    '''
    fileList = get_files(dirname=dirname, pattern=pattern, recursive=recursive)
    if fileList is None:
        return None

    directoryDict = build_hierarchy(fileList)
    collection = {}

    for dirname, fileList in directoryDict.iteritems():
        if validiator is not None and hasattr(validiator, '__call__'):
            if validiator(dirname, fileList) is None:
                break
        obj_instance = _class('{}'.format(dirname), datafiles = fileList)

        if dirname not in collection:
            collection[dirname] = obj_instance
        else:
            raiseWithMessage("""Found two different folders with the same folder name.
            You should rename one of the folder while the developers decide what is logical to implement here.""")

    return collection




