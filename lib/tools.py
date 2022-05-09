import os
import platform
import configparser
from prompt_toolkit import print_formatted_text, HTML, prompt
import sqlite3

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
            and 'dateOfLastSession' in config['Sessions']
            and 'lastSessionIncrement' in config['Sessions']):
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
    #TODO : add a globa ltry / catch and return None for alla variables when an exception occurs
    try:
        maindir, separator, dateOfLastSession, lastSessionIncrement, file_ext, iniFilesDir = str(), str(), str(), str(), str(), str()
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
        dateOfLastSession = config['Sessions']['dateOfLastSession']
        lastSessionIncrement = config['Sessions']['lastSessionIncrement']
        file_ext = config['Sessions']['file_ext']

        for retailer in retailers:
            retailer_tables = [ f'{retailer}{separator}{table}' for table in tables]
            retailers_tables[retailer] = retailer_tables
        
        for retailer in retailers:
            for table in retailers_tables[retailer]:
                if not file_exists_TrueFalse(head=iniFilesDir, tail=table+file_ext, typeExtraction='retailersFiles', dir='file'):
                    raise(ValueError('file {file} does not exists in dir {dir}'.format(file=table+file_ext, dir=iniFilesDir)))

        return [maindir, separator, retailers, retailers_tables, toolkit_tables, dateOfLastSession, lastSessionIncrement, file_ext, iniFilesDir]
    except ValueError as vr:
        print(f'One of the file specified in the .ini does not exist : {vr.args[0]}')
        return None, None, None, None, None, None, None, None
    except BaseException as be:
        print(f'Erreur inatendue dans la fonction create_main_variables_from_config() : {be.args}')
        return None, None, None, None, None, None, None, None



def initialize_db(db_full_path : str, config : list) -> list:
    '''
        Load all the files in the database
    '''
    #TO DO check file instead opening the connection
    conn = sqlite3.connect(db_full_path)
    return [conn]