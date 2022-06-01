import glob
import os

def get_files(input_path, extension):
    '''
        parse all the files of the specified dir that have the specified extension
        for each file, place its name in a dictionary with an empty dictionary for the value
                       (that will get the details later )
        dicOfFiles = {filename : {emptyDictionary}}
    '''
    listOfFiles = []

    for file in (glob.glob(input_path + "*." + extension,recursive=False)):
        listOfFiles.append(file)
    return listOfFiles

def file_exists(fullpath: str, typeExtraction: str, dir=['dir', 'file']) -> list():
    '''
       Check if the specified path exist.
       If so : return head, tail from os.path.split()
       If not : raise an exception
    '''
    if (dir=='file'):
        if not os.path.isfile(fullpath):
            print('arg {v} : The specified file does not exist'.format(v=typeExtraction))
            raise FileExistsError()
    else:
        if not os.path.isdir(fullpath):
            print('arg {v} : The specified path does not exist'.format(v=typeExtraction))
            raise FileExistsError()

    head, tail = os.path.split(fullpath)
    return [head, tail]

def file_exists_TrueFalse(head: str, tail: str, typeExtraction: str, dir=['dir', 'file']) -> bool:
    '''
       Check if the specified path exist.
       Return True or False
    '''
    if (dir=='file'):
        fullpath = head + os.path.sep + tail
        if not os.path.isfile(fullpath):
            print('arg {v} : The specified file does not exist'.format(v=typeExtraction))
            return False
        else:
            return True
    else:
        if not os.path.isdir(head):
            print('arg {v} : The specified path does not exist'.format(v=typeExtraction))
            return False
        else:
            return True
