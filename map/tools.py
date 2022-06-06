import os
import datetime
import platform
import configparser
import sqlite3
from xmlrpc.client import Boolean
import pandas as pd
from glob import glob
import logging
import functools
import map.fileutil as fileutil

mlogger = logging.getLogger('map_indicator_app.tools')

def log_function_call(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        mlogger.info(f'Start of the function {func.__name__}')
        response = func(*args, *kwargs)
        mlogger.info(f'End of the function {func.__name__}')
        return response
    return wrapper

@log_function_call
def check_ini_files_and_return_config_object(inifile: str) -> list:
    '''
        check if the ini file is OK
        if so, return the config object in a list
        if not return None
    '''
    config = configparser.ConfigParser()
    config.read(inifile)
    if ('Main' in config
         and 'Sessions' in config
            and len(config['Main']['mainDirLinux']) > 0
            and len(config['Main']['mainDirWindows']) > 0
            and len(config['Main']['iniFilesDir']) > 0
            and len(config['Main']['SQLiteDB']) > 0
            and len(config['Main']['tables']) > 0
            and len(config['Main']['toolkit_tables']) > 0
            and len(config['Main']['file_ext']) > 0
            and len(config['Sessions']['prefix']) > 0
            and len(config['Sessions']['context']) > 0
            and len(config['Sessions']['backup_name']) > 0
            and len(config['Sessions']['backward_in_week']) > 0
            and len(config['Sessions']['number_of_weeks_to_remove']) > 0
            and len(config['Main']['log_level'])
            and (config['Main']['log_level'] == 'DEBUG'
                    or config['Main']['log_level'] == 'INFO'
                    or config['Main']['log_level'] == 'WARNING'
                    or config['Main']['log_level'] == 'ERROR'
                    or config['Main']['log_level'] == 'CRITICAL')):
        mlogger.info('function check_ini_files_and_return_config_object : execution OK. Returning config as expected')
        return [config]
    else:
        if 'Main' not in config:
            mlogger.critical('ini file lacks the Main section')
        if 'Sessions' not in config:
            mlogger.critical('ini file lacks the Sessions section')
        if 'mainDirLinux' not in config['Main']:
            mlogger.critical('ini file lacks the entry mainDirLinux in the Main section')
        if 'mainDirWindows' not in config['Main']:
            mlogger.critical('ini file lacks the entry mainDirWindows in the Main section')
        if 'iniFilesDir' not in config['Main']:
            mlogger.critical('ini file lacks the entry iniFilesDir in the Main section')
        if 'SQLiteDB' not in config['Main']:
            mlogger.critical('ini file lacks the entry SQLiteDB in the Main section')
        if 'tables' not in config['Main']:
            mlogger.critical('ini file lacks the entry tables in the Main section')
        if 'toolkit_tables' not in config['Main']:
            mlogger.critical('ini file lacks the entry toolkit_tables in the Main section')
        if 'file_ext' not in config['Main']:
            mlogger.critical('ini file lacks the entry file_ext in the Main section')
        if 'prefix' not in config['Sessions']:
            mlogger.critical('ini file lacks the entry prefix in the Sessions section')
        if 'log_level' not in config['Main']:
            mlogger.critical('ini file lacks the entry log_level in the Main section')
        if 'context' not in config['Sessions']:
            mlogger.critical('ini file lacks the entry context in the Sessions section')
        if 'backup_name' not in config['Sessions']:
            mlogger.critical('ini file lacks the entry backup_name in the Sessions section')
        if 'backward_in_week' not in config['Sessions']:
            mlogger.critical('ini file lacks the entry backward_in_week in the Sessions section')
        if 'number_of_weeks_to_remove' not in config['Sessions']:
            mlogger.critical('ini file lacks the entry number_of_weeks_to_remove in the Sessions section')
        if (config['Main']['log_level'] not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')):
            mlogger.critical('the entry log_level is not amongst DEBUG, INFO, WARNING, ERROR, CRITICAL')
        return None

@log_function_call
def create_main_variables_from_config(configinlist: list) -> dict:
    '''
        from the ini file,  create all the variables from the sections 'Main' and 'Sessions' and return them in a dictionary
        return a tuple of None in case of a problem
    '''
    try:
        config = configinlist[0]

        variables_from_ini_in_dic = dict(iter(config.items('Main')))
        variables_from_ini_in_dic.update(dict(iter(config.items('Sessions'))))
        
        variables_from_ini_in_dic['retailers'] = variables_from_ini_in_dic['retailers'].split()
        variables_from_ini_in_dic['toolkit_tables'] = variables_from_ini_in_dic['toolkit_tables'].split()
        variables_from_ini_in_dic['tables'] = variables_from_ini_in_dic['tables'].split()

        if (platform.system() == 'Linux'):
            variables_from_ini_in_dic['maindir'] = config['Main']['mainDirLinux']
        else:
            variables_from_ini_in_dic['maindir'] = config['Main']['mainDirWindows']

        if not fileutil.file_exists_TrueFalse(head=variables_from_ini_in_dic['maindir'], tail='', typeExtraction='mainDir', dir='dir'):
            raise ValueError('mainpath {mainDir} not found'.format(mainDir=variables_from_ini_in_dic['maindir']))    

        variables_from_ini_in_dic['iniFilesDir'] = variables_from_ini_in_dic['maindir'] + os.path.sep + config['Main']['iniFilesDir']
        if not fileutil.file_exists_TrueFalse(head=variables_from_ini_in_dic['iniFilesDir'], tail='', typeExtraction='mainDir', dir='dir'):
            raise ValueError('mainpath {iniFilesDir} not found'.format(mainDir=variables_from_ini_in_dic['iniFilesDir']))    

        retailers_tables = dict()
        # build the name of the tables for all retailers. e.g. jules_adm_role
        for retailer in variables_from_ini_in_dic['retailers']:
            retailer_tables = [ f"{retailer}{variables_from_ini_in_dic['separator']}{table}" for table in variables_from_ini_in_dic['tables']]
            retailers_tables[retailer] = retailer_tables
        variables_from_ini_in_dic['retailers_tables'] = retailers_tables

        # check if each table as its corresponding file 
        for retailer in variables_from_ini_in_dic['retailers']:
            for table in retailers_tables[retailer]:
                if not fileutil.file_exists_TrueFalse(head=variables_from_ini_in_dic['iniFilesDir'],
                                                        tail=table+variables_from_ini_in_dic['file_ext'],
                                                        typeExtraction='retailersFiles', dir='file'):
                    raise(ValueError('file {file} does not exists in dir {dir}'.format(file=table+variables_from_ini_in_dic['file_ext'], dir=variables_from_ini_in_dic['iniFilesDir'])))
        
        for table in variables_from_ini_in_dic['toolkit_tables']:
            if not fileutil.file_exists_TrueFalse(head=variables_from_ini_in_dic['iniFilesDir'],
                                                    tail=table+variables_from_ini_in_dic['file_ext'],
                                                    typeExtraction='toolkitFiles', dir='file'):
                    raise(ValueError('file {file} does not exists in dir {dir}'.format(file=table+variables_from_ini_in_dic['file_ext'], dir=variables_from_ini_in_dic['iniFilesDir'])))

        mlogger.info('function create_main_variables_from_config : execution OK. Returning the entries of the ini file as expected')
        return variables_from_ini_in_dic

    except ValueError as vr:
        mlogger.critical(f'One of the file specified in the .ini does not exist : {vr.args[0]}')
        return None
    except BaseException as be:
        mlogger.critical(f'unexpected error in the function create_main_variables_from_config() : {type(be)}{be.args}')
        return None

@log_function_call
def initialize_db(db_full_path : str, retailers: str, retailers_tables: str, toolkit_tables: str, file_ext: str, iniFilesDir: str) -> list:
    '''
        Load all the files in the database
        return a list with the connection object or None
    '''
    try:
        df = pd.DataFrame()
        conn = sqlite3.connect(db_full_path)
        for retailer in retailers:
            for table in retailers_tables[retailer]:
                file_to_load = iniFilesDir + os.path.sep + table + file_ext
                mlogger.info(f'loading {file_to_load}')
                df = pd.read_csv(file_to_load)
                df.to_sql(name=table, con=conn)

        for table in toolkit_tables:
                file_to_load = iniFilesDir + os.path.sep + table + file_ext
                mlogger.info(f'loading {file_to_load}')
                df = pd.read_csv(file_to_load)
                df.to_sql(name=table, con=conn)
        mlogger.info('function initialize_db : execution OK. Returning connection object as expected')
        return [conn]
    except BaseException as be:
        mlogger.critical(f'U initialize_db() : {type(be)}{be.args}')
        return None

@log_function_call
def create_current_session(maindir: str, prefix: str, context: str, separator: str) -> tuple:
    '''
        create the folder where all the files à the current execution will lies.
        by default the format of the name of this folder is {prefix}{separator}{date|datetime}{Number of the session for this date/datetime}
        e.g : Session-2022-05-10-1 or Session-2022-05-10 22:52:04.106532-1

        returns the full path and the session (that is a date)
        returns None, None if a problem occurs


    '''
    current_date = str(datetime.date.today() if context == 'date' else datetime.datetime.today())

    path_to_create = None
    try :
        path_to_find = maindir + os.path.sep + prefix + separator + current_date 
        returned_paths =  glob(path_to_find + '*', recursive=False)
        if len(returned_paths) == 0:
            path_to_create = path_to_find+separator+'1'
            os.mkdir(path_to_create)
        else:
            sessions = list()
            for path in returned_paths:
                if os.path.isdir(path):
                    pos = path.rfind(separator)+1
                    sessions.append(int(path[pos:]))
            path_to_create = path_to_find+separator+str((max(sessions)+1))
            os.mkdir(path_to_create)
        mlogger.info(f'function get_current_session : execution OK. Returning path to create "{path_to_create}" as expected')
        return path_to_create+os.path.sep, current_date
    except BaseException as be:
        mlogger.critical(f'unexpected error in the function get_current_session() : {type(be)}{be.args}')
        return None, None

def progress(status, remaining, total):
    mlogger.info(f'Status of operation : {status}')
    mlogger.info(f'Copied {total-remaining} of {total} pages...')

@log_function_call
def backup_in_memory_db_to_disk(conn_in_list: list, backup_full_path_name: str ) -> list:
    '''
        Backup the sqlite db in the specified path
        return de connection object in a list or None
    '''
    try:
        conn_backup = sqlite3.connect(backup_full_path_name)
        with conn_backup:
            conn_in_list[0].backup(conn_backup, progress=progress)
        mlogger.info('function backup_in_memory_db_to_disk : execution OK. Returning backup db connection as expected')
        return [conn_backup]
    except BaseException as be:
        mlogger.critical(f'unexpected error in the function backup_in_memory_db_to_disk() : {type(be)}{be.args}')
        return None

@log_function_call
def get_queries(configinlist: list) -> dict:
    '''
        Load all the queries in a dictionary or None
    '''
    try:
        config = configinlist[0]
        queries_in_a_dict = dict()
        if 'Queries' in config:
            for val in config['Queries']:
                queries_in_a_dict[val] = config['Queries'][val]
        else:
            mlogger.critical('Section Queries does not exists')
            return None
        return queries_in_a_dict
    except BaseException as be:
        mlogger.critical(f'unexpected error in the function get_queries() : {type(be)}{be.args}')
        return None

@log_function_call
def brand_query(query: str, tables: list, brand: str, separator: str) -> str:
    '''
    Turn the generic query received into a query related to a brand
    e.g. : adm_profile -> jules_adm_profile
    returns the query or None if a problem occurs
    '''
    mlogger.info(f'query received for input : {query}')
    try:
        branded_tables = [ f'{brand}{separator}{table}' for table in tables ]
        for r in zip(tables, branded_tables):
            query = query.replace(*r)
        # the tables contains "adm_profile" twice, so one need to delete the extra prefix added
        query = query.replace(f'{brand}{separator}{brand}{separator}', brand+separator)
        
        query = query.replace('#', '%')    
        branded_query = query.replace('$brand', brand)

        mlogger.info(f'branded query returned : {branded_query}')
        return branded_query
    except BaseException as be:
        mlogger.critical(f'unexpected error in the function brand_query() : {type(be)}{be.args}')
        return None

@log_function_call
def queries_are_ok(conninlist: list, configinlist: list, variables_from_ini_in_dic: list) -> Boolean:
    '''
        Check all the queries against a retailer to validate that they execute well
    '''
    try:
        all_queries_in_a_dict = dict()
        all_queries_in_a_dict =  get_queries(configinlist)

        cur = conninlist[0].cursor()

        for query in all_queries_in_a_dict.values():
            mlogger.info(f'query being checked : {query}')
            branded_query = brand_query(
                                                query,
                                                variables_from_ini_in_dic['tables'],
                                                variables_from_ini_in_dic['retailers'][0],
                                                variables_from_ini_in_dic['separator'])
            assert len(cur.execute(branded_query).fetchall()) > 0
        return True
    except BaseException as be:
        mlogger.critical(f'unexpected error in the function check_query() : {type(be)}{be.args}')
        return False
