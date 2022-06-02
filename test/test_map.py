from genericpath import exists
import os
import configparser
from sqlite3 import Connection, OperationalError
import sqlite3
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from pytest import raises
import map.tools as tools
import map.process as process
import logging

def init_ok():
    # Firstly, check if the inifile exists and has all the required keys
    config = tools.check_ini_files_and_return_config_object('map_indicators.ini')[0]
    assert isinstance(config, configparser.ConfigParser)
    assert 'Main' in config

    #Secondly, check if all the required files exists
    variables_from_ini_in_dic = tools.create_main_variables_from_config([config])
    assert variables_from_ini_in_dic is not None
    
    assert variables_from_ini_in_dic['maindir'] is not None
    logger.info('content of variable maindir : {v}'.format(v=variables_from_ini_in_dic['maindir']))
    assert len(variables_from_ini_in_dic['maindir']) > 0
    logger.info('content of variable iniFilesDir : {v}'.format(v=variables_from_ini_in_dic['iniFilesDir']))
    assert len(variables_from_ini_in_dic['iniFilesDir']) > 0
    logger.info('content of variable separator : {v}'.format(v=variables_from_ini_in_dic['separator']))
    assert len(variables_from_ini_in_dic['separator']) > 0
    logger.info('content of variable retailers : {v}'.format(v=variables_from_ini_in_dic['retailers']))
    assert len(variables_from_ini_in_dic['retailers']) > 0
    logger.info('content of variable tables : {v} '.format(v=variables_from_ini_in_dic['tables']))
    assert len(variables_from_ini_in_dic['tables']) > 0

    logger.info('content of variable retailers_tables : {v} '.format(v=variables_from_ini_in_dic['retailers_tables']))
    assert len(variables_from_ini_in_dic['retailers_tables']) > 0
    logger.info('content of variable toolkit_tables : {v}'.format(v=variables_from_ini_in_dic['toolkit_tables']))
    assert len(variables_from_ini_in_dic['toolkit_tables']) > 0
    logger.info('content of variable file_ext : {v}'.format(v=variables_from_ini_in_dic['file_ext']))
    assert len(variables_from_ini_in_dic['file_ext']) > 0
    logger.info('content of variable prefix : {v}'.format(v=variables_from_ini_in_dic['prefix']))
    assert len(variables_from_ini_in_dic['prefix']) > 0
    logger.info('content of variable context : {v}'.format(v=variables_from_ini_in_dic['context']))
    assert len(variables_from_ini_in_dic['context']) > 0
    logger.info('content of variable backup_name : {v}'.format(v=variables_from_ini_in_dic['backup_name']))
    assert len(variables_from_ini_in_dic['backup_name']) > 0
    logger.info('content of variable log_level : {v}'.format(v=variables_from_ini_in_dic['log_level']))
    assert len(variables_from_ini_in_dic['log_level']) > 0

    #Thirdly, load all the files in the database
    conn = tools.initialize_db(':memory:',
                                 variables_from_ini_in_dic['retailers'],
                                 variables_from_ini_in_dic['retailers_tables'],
                                 variables_from_ini_in_dic['toolkit_tables'],
                                 variables_from_ini_in_dic['file_ext'],
                                 variables_from_ini_in_dic['iniFilesDir'])[0]
    assert conn is not None
    cur = conn.cursor()
    cur.execute("select * from path")
    assert len(cur.fetchall()) > 0


    return ([conn], [config], variables_from_ini_in_dic)


def backup_in_session(conninlist: list, variables_from_ini_in_dic: list) -> str:
    conn = conninlist[0]
    # Time to save a backup of the database
    current_session, current_date = tools.get_current_session(variables_from_ini_in_dic['maindir'],
                                                                variables_from_ini_in_dic['prefix'],
                                                                variables_from_ini_in_dic['context'],
                                                                variables_from_ini_in_dic['separator'])
    assert current_session is not None
    assert current_date is not None
    logger.info('content of variable current_session : {v}'.format(v=current_session))

    backup_full_path_name = current_session + os.path.sep + variables_from_ini_in_dic['backup_name']
    backup_path = current_session + os.path.sep
      
    conn_backup = tools.backup_in_memory_db_to_disk([conn], backup_full_path_name)[0]
    cur_backup = conn_backup.cursor()
    cur_backup.execute("select * from path")
    assert len(cur_backup.fetchall()) > 0
    conn_backup.close()

    return backup_path, backup_full_path_name


def check_queries(conninlist: list, configinlist: list, backup_path: str) -> None:
    #check if the queries are present in the inifile
    all_queries_in_a_dict = dict()
    all_queries_in_a_dict =  tools.get_queries(configinlist)
    assert all_queries_in_a_dict is not None
    variables_from_ini_in_dic = tools.create_main_variables_from_config(configinlist)
    branded_query = tools.brand_query(all_queries_in_a_dict['connected_at_least_once'], variables_from_ini_in_dic['tables'], 'jules', variables_from_ini_in_dic['separator'])
    cur = conninlist[0].cursor()
    assert len(cur.execute(branded_query).fetchall()) > 0
    branded_query = tools.brand_query(all_queries_in_a_dict['connected_at_least_once_v2'], variables_from_ini_in_dic['tables'], 'jules', variables_from_ini_in_dic['separator'])
    assert len(cur.execute(branded_query).fetchall()) > 0
    branded_query = tools.brand_query(all_queries_in_a_dict['request_history'], variables_from_ini_in_dic['tables'], 'jules', variables_from_ini_in_dic['separator'])
    assert len(cur.execute(branded_query).fetchall()) > 0
    branded_query = tools.brand_query(all_queries_in_a_dict['request_history_v2'], variables_from_ini_in_dic['tables'], 'jules', variables_from_ini_in_dic['separator'])
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


    conninlist, configinlist, variables_from_ini_in_dic = init_ok()
    backup_path, backup_full_path_name = backup_in_session(conninlist, variables_from_ini_in_dic)
    check_queries(conninlist, configinlist, backup_path)
    backup_in_ini_full_path = process.backup(conninlist, variables_from_ini_in_dic, 'ini')
    assert backup_in_ini_full_path is not None

    fh.close()
