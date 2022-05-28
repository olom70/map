from genericpath import exists
import os
import configparser
from sqlite3 import Connection, OperationalError
import sqlite3
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from pytest import raises
from lib.tools import check_ini_files_and_return_config_object, initialize_db
from lib.tools import create_main_variables_from_config, backup_in_memory_db_to_disk
from lib.tools import get_current_session, get_queries, brand_query
import logging

def init_ok():
    # Firstly, check if the inifile exists and has all the required keys
    config = check_ini_files_and_return_config_object('map_indicators.ini')[0]
    assert isinstance(config, configparser.ConfigParser)
    assert 'Main' in config

    #Secondly, check if all the required files exists
    maindir, separator, file_ext, iniFilesDir, prefix, context, backup_name, log_level = str(), str(), str(), str(), str(), str(), str(), str()
    retailers, tables, toolkit_tables = list(), list(), list()
    retailers_tables = dict()
    variables_from_ini_in_list = create_main_variables_from_config([config])
    assert variables_from_ini_in_list is not None
    maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
    assert maindir is not None
    logger.info('content of variable maindir : {v}'.format(v=maindir))
    assert len(maindir) > 0
    logger.info('content of variable iniFilesDir : {v}'.format(v=iniFilesDir))
    assert len(iniFilesDir) > 0
    logger.info('content of variable separator : {v}'.format(v=separator))
    assert len(separator) > 0
    logger.info('content of variable retailers : {v}'.format(v=retailers))
    assert len(retailers) > 0
    logger.info('content of variable tables : {v} '.format(v=tables))
    assert len(tables) > 0

    logger.info('content of variable retailers_tables : {v} '.format(v=retailers_tables))
    assert len(retailers_tables) > 0
    logger.info('content of variable toolkit_tables : {v}'.format(v=toolkit_tables))
    assert len(toolkit_tables) > 0
    logger.info('content of variable file_ext : {v}'.format(v=file_ext))
    assert len(file_ext) > 0
    logger.info('content of variable prefix : {v}'.format(v=prefix))
    assert len(prefix) > 0
    logger.info('content of variable context : {v}'.format(v=context))
    assert len(context) > 0
    logger.info('content of variable backup_name : {v}'.format(v=backup_name))
    assert len(backup_name) > 0
    logger.info('content of variable log_level : {v}'.format(v=log_level))
    assert len(log_level) > 0

    #Thirdly, load all the files in the database
    conn = initialize_db(':memory:', retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir)[0]
    assert conn is not None
    cur = conn.cursor()
    cur.execute("select * from path")
    assert len(cur.fetchall()) > 0


    return [[conn], [config], variables_from_ini_in_list]


def backup(conninlist: list, variables_from_ini_in_list: list) -> str:
    conn = conninlist[0]
    maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list

    # Time to save a backup of the database
    current_session, current_date = get_current_session(maindir, prefix, context, separator)
    assert current_session is not None
    assert current_date is not None
    logger.info('content of variable current_session : {v}'.format(v=current_session))

    backup_full_path_name = current_session + os.path.sep + backup_name
    backup_path = current_session + os.path.sep
      
    conn_backup = backup_in_memory_db_to_disk([conn], backup_full_path_name)[0]
    cur_backup = conn_backup.cursor()
    cur_backup.execute("select * from path")
    assert len(cur_backup.fetchall()) > 0
    conn_backup.close()

    return backup_path, backup_full_path_name


def check_queries(conninlist: list, configinlist: list, backup_path: str) -> None:
    #check if the queries are present in the inifile
    all_queries_in_a_dict = dict()
    all_queries_in_a_dict =  get_queries(configinlist)
    assert all_queries_in_a_dict is not None
    variables_from_ini_in_list = create_main_variables_from_config(configinlist)
    maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
    branded_query = brand_query(all_queries_in_a_dict['connected_at_least_once'], tables, 'jules', separator)
    cur = conninlist[0].cursor()
    assert len(cur.execute(branded_query).fetchall()) > 0
    branded_query = brand_query(all_queries_in_a_dict['connected_at_least_once_v2'], tables, 'jules', separator)
    assert len(cur.execute(branded_query).fetchall()) > 0
    branded_query = brand_query(all_queries_in_a_dict['request_history'], tables, 'jules', separator)
    assert len(cur.execute(branded_query).fetchall()) > 0
    branded_query = brand_query(all_queries_in_a_dict['request_history_v2'], tables, 'jules', separator)
    assert len(cur.execute(branded_query).fetchall()) > 0

if __name__=="__main__":

    logger = logging.getLogger('map_indicator_app')
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('map_indicator.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('Start of the test suite')


    conninlist, configinlist, variables_from_ini_in_a_list = init_ok()
    backup_path, backup_full_path_name = backup(conninlist, variables_from_ini_in_a_list)
    check_queries(conninlist, configinlist, backup_path)


    fh.close()
