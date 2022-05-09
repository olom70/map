from genericpath import exists
import os
import configparser
from sqlite3 import Connection, OperationalError
import sqlite3
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)

from pytest import raises
from lib.tools import check_ini_files_and_return_config_object, initialize_db, create_main_variables_from_config


def init_ok():
    # Firstly, check if the inifile exists and has all the required keys
    with raises(ValueError):
        check_ini_files_and_return_config_object('wrong_name')
    config = check_ini_files_and_return_config_object('map_indicators.ini')[0]
    assert 'DEFAULT' in config
    #Secondly, check if all the required files exists
    maindir, separator, dateOfLastSession, lastSessionIncrement, file_ext, iniFilesDir = str(), str(), str(), str(), str(), str()
    retailers, toolkit_tables = list(), list()
    retailers_tables = dict()
    maindir, separator, retailers, retailers_tables, toolkit_tables, dateOfLastSession, lastSessionIncrement, file_ext, iniFilesDir = create_main_variables_from_config([config])
    print('content of variable maindir : {v}'.format(v=maindir))
    assert len(maindir) > 0
    print('content of variable iniFilesDir : {v}'.format(v=iniFilesDir))
    assert len(iniFilesDir) > 0
    print('content of variable separator : {v}'.format(v=separator))
    assert len(separator) > 0
    print('content of variable retailers : {v}'.format(v=retailers))
    assert len(retailers) > 0
    print('content of variable retailers_tables : {v} '.format(v=retailers_tables))
    assert len(retailers_tables) > 0
    print('content of variable toolkit_tables : {v}'.format(v=toolkit_tables))
    assert len(toolkit_tables) > 0
    print('content of variable dateOfLastSession : {v}'.format(v=dateOfLastSession))
    print('content of variable lastSessionIncrement : {v}'.format(v=lastSessionIncrement))
    print('content of variable file_ext : {v}'.format(v=file_ext))
    assert len(file_ext) > 0

    # Thirdly, load all the files in the database
    conn = initialize_db(':memory', [config])[0]
    cur = conn.cursor()
    with not raises(OperationalError):
        cur.execute("select * from path")
        assert len(cur.fetchall()) > 0

if __name__=="__main__":
    init_ok()
