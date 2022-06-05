import os
import configparser
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)
from pytest import raises
import map.tools as tools
import map.process as mapprocess
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
    logger.info('content of variable backward_in_week : {v}'.format(v=variables_from_ini_in_dic['backward_in_week']))
    assert len(variables_from_ini_in_dic['backward_in_week']) > 0
    logger.info('content of variable number_of_weeks_to_remove : {v}'.format(v=variables_from_ini_in_dic['number_of_weeks_to_remove']))
    assert len(variables_from_ini_in_dic['number_of_weeks_to_remove']) > 0

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
    
    current_session, current_date = tools.create_current_session(variables_from_ini_in_dic['maindir'],
                                                                    variables_from_ini_in_dic['prefix'],
                                                                    variables_from_ini_in_dic['context'],
                                                                    variables_from_ini_in_dic['separator'])
    assert current_session is not None                                                                    
    backup_full_path_name = current_session + variables_from_ini_in_dic['backup_name']
    assert mapprocess.backup_ok(conninlist, backup_full_path_name)


    backup_full_path_name = variables_from_ini_in_dic['iniFilesDir'] + os.path.sep + variables_from_ini_in_dic['backup_name']
    assert mapprocess.backup_ok(conninlist, backup_full_path_name)
    assert tools.queries_are_ok(conninlist, configinlist, variables_from_ini_in_dic)
    assert mapprocess.indicator_connected_at_least_once(conninlist, configinlist, variables_from_ini_in_dic, current_session, current_date)
    assert mapprocess.indicator_connected_at_least_once(conninlist, configinlist, variables_from_ini_in_dic, current_session, current_date)

    y = 2022
    w = 20
    b = 4
    r = 0
    year_week = mapprocess.year_week_to_begin(y, w, b, r)
    assert year_week == 202216

    assert mapprocess.usage_by_teams(conninlist, configinlist, variables_from_ini_in_dic, current_session, current_date)



    fh.close()
