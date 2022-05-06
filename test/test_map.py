from genericpath import exists
import os
import configparser
from sqlite3 import Connection
import sqlite3
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)

from pytest import raises
from lib.tools import init, initialize_db


def init_ok():
    # First, check if the inifile exists and has all the required keys
    with raises(ValueError):
        init('wrong_name')
    configinlist = init('map_indicators.ini')
    assert 'DEFAULT' in configinlist[0]
    # Second, load all the files in the database
    conninlist = initialize_db(':memory', configinlist )
    cur = conninlist[0]
    cur.execute("select * from path")
    assert len(cur.fetchall()) > 0

if __name__=="__main__":
    init_ok()
