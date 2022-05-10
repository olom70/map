from lib2to3.pytree import Base
import os
import datetime
import platform
import configparser
from prompt_toolkit import print_formatted_text, HTML, prompt
import sqlite3
from pandas import read_csv, DataFrame
from glob import glob

from pytest import Session
from lib.fileutil import file_exists_TrueFalse

def check_ini_files_and_return_config_object(inifile: str) -> list():
    '''
        check if the ini file is OK
        if so, return the config object in a list
    '''
    config = configparser.ConfigParser()
    config.read(inifile)
    if ('DEFAULT' in config
         and 'Sessions' in config
            and len(config['Sessions']['mainDirLinux']) > 0
            and len(config['Sessions']['mainDirWindows']) > 0
            and len(config['Sessions']['iniFilesDir']) > 0
            and len(config['Sessions']['SQLiteDB']) > 0
            and len(config['Sessions']['tables']) > 0
            and len(config['Sessions']['toolkit_tables']) > 0
            and len(config['Sessions']['file_ext']) > 0
            and len(config['Sessions']['prefix']) > 0
            and len(config['Sessions']['context']) > 0
            and len(config['Sessions']['backup_name']) > 0):
        return [config]
    else:
        return None

def create_main_variables_from_config(configinlist: list()) -> list():
    '''
        from the ini file,  create all the variables and return them in a dictionary
        key                 : type of value         value
        maindir             : string                mainDirWindows or mainDirLinux
        separator           : string                separator
        retailers           : list                  retailers
        retailers_tables    : list of dictionary    [{retailer: list of tables}, {retailer : list of tables}]
        toolkit_tables      : list                  toolkit_tables
        dateOfLastSession   : string                dateOfLastSession
        lastSessionIncrement: string                lastSessionIncrement
        file_ext            : string                file_ext
        iniFilesDir         : string                iniFilesDir

        NB : list of tables is made up from all the tables from 'tables'. To each table a prefix is added : {retailer}{separator}.
            e.g adm_user -> jules_adm_user
    '''
    try:
        maindir, separator, file_ext, iniFilesDir, prefix, context, backup_name = str(), str(), str(), str(), str(), str(), str()
        retailers, toolkit_tables, tables = list(), list(), list()
        retailers_tables = dict()
        config = configinlist[0]
        if (platform.system() == 'Linux'):
            maindir = config['Sessions']['mainDirLinux']
        else:
            maindir = config['Sessions']['mainDirWindows']

        if not file_exists_TrueFalse(head=maindir, tail='', typeExtraction='mainDir', dir='dir'):
            raise ValueError('mainpath {mainDir} not found'.format(mainDir=maindir))    

        iniFilesDir = maindir + os.path.sep + config['Sessions']['iniFilesDir']
        if not file_exists_TrueFalse(head=iniFilesDir, tail='', typeExtraction='mainDir', dir='dir'):
            raise ValueError('mainpath {iniFilesDir} not found'.format(mainDir=iniFilesDir))    

        separator = config['Sessions']['Separator']
        retailers = config['Sessions']['retailers'].split()
        tables = config['Sessions']['tables'].split()
        toolkit_tables = config['Sessions']['toolkit_tables'].split()
        file_ext = config['Sessions']['file_ext']
        prefix = config['Sessions']['prefix']
        context = config['Sessions']['context']
        backup_name = config['Sessions']['backup_name']

        # build the name of the tables for all retailers. e.g. jules_adm_role
        for retailer in retailers:
            retailer_tables = [ f'{retailer}{separator}{table}' for table in tables]
            retailers_tables[retailer] = retailer_tables
        
        # check if each table as its corresponding file 
        for retailer in retailers:
            for table in retailers_tables[retailer]:
                if not file_exists_TrueFalse(head=iniFilesDir, tail=table+file_ext, typeExtraction='retailersFiles', dir='file'):
                    raise(ValueError('file {file} does not exists in dir {dir}'.format(file=table+file_ext, dir=iniFilesDir)))
        
        for table in toolkit_tables:
            if not file_exists_TrueFalse(head=iniFilesDir, tail=table+file_ext, typeExtraction='toolkitFiles', dir='file'):
                    raise(ValueError('file {file} does not exists in dir {dir}'.format(file=table+file_ext, dir=iniFilesDir)))

        return [maindir, separator, retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name]

    except ValueError as vr:
        print(f'One of the file specified in the .ini does not exist : {vr.args[0]}')
        return None, None, None, None, None, None, None, None
    except BaseException as be:
        print(f'Erreur inatendue dans la fonction create_main_variables_from_config() : {be.args}')
        return None, None, None, None, None, None, None, None



def initialize_db(db_full_path : str, variables_from_ini_in_list : list) -> list:
    '''
        Load all the files in the database
    '''
    maindir, separator, file_ext, iniFilesDir, prefix, context, backup_name = str(), str(), str(), str(), str(), str(), str()
    retailers, toolkit_tables = list(), list()
    retailers_tables = dict()
    try:
        maindir, separator, retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name = variables_from_ini_in_list


        df = DataFrame()
        conn = sqlite3.connect(db_full_path)
        for retailer in retailers:
            for table in retailers_tables[retailer]:
                file_to_load = iniFilesDir + os.path.sep + table + file_ext
                print(f'loading {file_to_load}')
                df = read_csv(file_to_load)
                df.to_sql(name=table, con=conn)

        for table in toolkit_tables:
                file_to_load = iniFilesDir + os.path.sep + table + file_ext
                print(f'loading {file_to_load}')
                df = read_csv(file_to_load)
                df.to_sql(name=table, con=conn)

        return [conn]
    except BaseException as e:
        return None


def get_current_session(maindir: str, prefix: str, context: str, separator: str) -> str:
    '''
        create the folder where all the files à the current execution will lies.
        by default the format of the name of this folder is {prefix}{separator}{date|datetime}{Number of the session for this date/datetime}
        e.g : Session-2022-05-10-1 or Session-2022-05-10 22:52:04.106532-1


    '''
    current_context = str(datetime.date.today() if context == 'date' else datetime.datetime.today())

    path_to_create = None
    try :
        path_to_find = maindir + os.path.sep + prefix + separator + current_context 
        returned_paths =  glob(path_to_find + '*', recursive=False)
        if len(returned_paths) == 0:
            path_to_create = current_context+separator+'1'
            os.mkdir(path_to_create)
        else:
            sessions = list()
            for path in returned_paths:
                if os.path.isdir(path):
                    sessions = sessions.append(int(path[path.rfind('-')+1:]))
            path_to_create = current_context+separator+str((max(sessions)+1))
            os.mkdir(path_to_create)
        return path_to_create
    except BaseException as e:
        return None

def backup_in_memory_db_to_disk(conn: sqlite3.connect, backup_full_path_name: str ) -> list:
    
    datetime.date.today()