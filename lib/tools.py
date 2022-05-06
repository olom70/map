import platform
import configparser
from prompt_toolkit import print_formatted_text, HTML, prompt
import sqlite3

def init(inifile: str) -> list():
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
            and len(config['Sessions']['map_tables']) > 0
            and len(config['Sessions']['toolkit_tables']) > 0
            and 'dateOfLastSession' in config['Sessions']
            and 'lastSessionIncrement' in config['Sessions']):
        return [config]
    else:
        raise ValueError('ini file {inifile} not found'.format(inifile=inifile))

def initialize_db(db_full_path : str, config : list) -> list:
    '''
        Load all the files in the database
    '''


    #TO DO check file instead opening the connection
    conn = sqlite3.connect(db_full_path)
    return [conn]