import configparser
import logging
import map.tools as tools
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import decouple
import yagmail
import glob
import sqlite3

mlogger = logging.getLogger('map_indicator_app.tools')

@tools.log_function_call
def backup_ok(myconn: list, backup_full_path_name) -> bool:
    '''
    Backup the in memory database in the specified file
    '''
    try:
        conn_backup = tools.backup_in_memory_db_to_disk(myconn, backup_full_path_name)
        if conn_backup is not None:
            mlogger.info('The in-memory DB has just been dumped to : {v}'.format(v=backup_full_path_name))
            conn_backup.close()
            return True
        else:
            mlogger.critical(f"The copy of the database in {backup_full_path_name} has failed")
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function backup() : {type(be)}{be.args}')
        return False

@tools.log_function_call
def indicator_connected_at_least_once(myconn: list, myconfig: configparser.ConfigParser, variables_from_ini_in_dic: list, backup_path: str, current_date: str) -> bool:
    '''
        Generate the indicator "Connected at least once"
        The goal is to follow if each of the declared users in map has connected at least once.
    '''
    try:
        for brand in variables_from_ini_in_dic['retailers']:
            branded_query = tools.brand_query(tools.get_queries(myconfig)['connected_at_least_once_v2'],
                                                variables_from_ini_in_dic['tables'],
                                                brand, variables_from_ini_in_dic['separator'])
            sql_query = pd.read_sql(branded_query, myconn)
            df = pd.DataFrame(sql_query)
            try:
                df.plot.barh(stacked=True,
                            x='Teams',
                            title=f'{brand.capitalize()} : status of connections on {current_date}',
                            figsize= (12,7),
                            fontsize=13)
            except IndexError:
                continue
            plt.savefig(backup_path+
                        brand+
                        variables_from_ini_in_dic['separator']+
                        current_date+
                        'connected.jpg')
        return True
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function indicator_connected_at_least_once() : {type(be)}{be.args}')
        return False

@tools.log_function_call
def send_yagmail(variables_from_ini_in_dic: list, current_session_path: str, current_date: str) -> bool:
    try:
        mypassword = decouple.config('gmail_password', default=None)
        mysmtp = decouple.config('smtp', default=None)
        myport = int(decouple.config('port', default=None))
        source = decouple.config('from', default=None)
        recipient = decouple.config('to', default=None)
        if (mypassword is None or mysmtp is None or myport is None or source is None or recipient is None ):
            mlogger.warning('Gmail config not found. Unable to generate mail')
        else:
            try:
                content = [str(variables_from_ini_in_dic['beginning']).replace("#date", current_date)]
            except:
                content = [variables_from_ini_in_dic['beginning']]
            for file in (glob.glob(current_session_path + "*.jpg",recursive=False)):
                content.append(yagmail.inline(file))
            content.append(variables_from_ini_in_dic['ending'])
            
            with yagmail.SMTP(source, mypassword) as mymail:
                mymail.send(to=recipient,
                            subject=variables_from_ini_in_dic['title'],
                            contents=content)
            return True
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function send_email() : {type(be)}{be.args}')
        return False



@tools.log_function_call
def year_week_to_begin(year: int, week:int, backward_in_week: int, number_of_weeks_to_remove: int) -> int:
    '''
        input a year, a week and a number of weeks to substracts.
        output : year concatenated to the calculated week
    '''
    mlogger.info('input : year = {year}, week={week}, backward_in_week={backward_in_week}, number_of_weeks_to_remove = {number_of_weeks_to_remove}'.format(
        year=year,
        week=week,
        backward_in_week=backward_in_week,
        number_of_weeks_to_remove=number_of_weeks_to_remove)
    )
    theorical_week = week - number_of_weeks_to_remove
    theorical_week = theorical_week - backward_in_week
    if theorical_week <= 0:
        week = 52 + theorical_week
        year = year -1
    else:
        week = theorical_week
        year = year
    year_week = int(str(year) + str(week))
    mlogger.info(f'output :{year_week}')
    return  year_week

@tools.log_function_call
def map_usage(myconn: sqlite3.connect, myconfig: configparser.ConfigParser, variables_from_ini_in_dic: list, backup_path: str, current_date: str) -> bool:
    '''
        Generate the indicator "usage"
        The use of the last 4 weeks
        break down by teams the nby entreprise
        
    '''
    try:
        for retailer in variables_from_ini_in_dic['retailers']:
            branded_query = tools.brand_query(tools.get_queries(myconfig)['request_history_v2'],
                                                variables_from_ini_in_dic['tables'],
                                                retailer, variables_from_ini_in_dic['separator'])
            sql_query = pd.read_sql(branded_query, myconn)
            dfrq = pd.DataFrame(sql_query)

            # enrich the dataframe with the values needed by the indicator
            #dfrq["access_year"] = list(map(lambda x: str(x[0:4]), dfrq['access_date_to_path']))
            dfrq["access_year"] = dfrq['access_date_to_path'].map(lambda x: str(x[0:4]))
            dfrq["access_month"] = dfrq['access_date_to_path'].map(lambda x: str(x[5:7]))
            dfrq["access_day"] = dfrq['access_date_to_path'].map(lambda x: str(x[8:]))
            dfrq["access_week"] = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').isocalendar().week, dfrq["access_date_to_path"]))
            dfrq["access_year_week"] = dfrq['access_year'].map(str) + dfrq['access_week'].map(str)
            dfrq['access_year_month'] = dfrq['access_year'].map(str) + dfrq['access_month'].map(str)


            # get the most recent usage of CGI MAP and filter the dataframe
            year = int(dfrq['access_year'].max())
            dly = dfrq.loc[dfrq['access_year'] == dfrq['access_year'].max()]
            week = int(dly['access_week'].max())
            backward_in_week = int(variables_from_ini_in_dic['backward_in_week'])
            number_of_weeks_to_remove = int(variables_from_ini_in_dic['number_of_weeks_to_remove'])
            year_week = year_week_to_begin(year,
                                            week,
                                                backward_in_week,
                                                number_of_weeks_to_remove)

            filtered_dfrq = dfrq.loc[
                        dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].loc[
                            dfrq['access_year_week'].map(int) >= year_week
                        ]

            if len(filtered_dfrq.index) == 0:
                continue

            # for each retailer and cgi compute the views and contribution
            retailers_and_cgi = variables_from_ini_in_dic['retailers'] + ['cgi']
            for entreprise in retailers_and_cgi:
                # ---------------------------------------
                # compute the count of "read only" usage (Entreprise / team)
                # ---------------------------------------
                try:
                    filtered_dfrq.loc[
                                filtered_dfrq['read'] == 'Y'
                            ].loc[
                                    filtered_dfrq['entreprise'].str.lower() == str(entreprise).lower()
                                ].groupby(
                                            [
                                                filtered_dfrq['access_year_week'],
                                                filtered_dfrq['entreprise'],
                                                filtered_dfrq['team']
                                            ]
                                        ).count().plot.bar(y='access_date_to_path',
                                                            stacked=True,
                                                            title=f'{retailer.capitalize()} : VIEW activity up to {current_date} (by Team, YearWeekNumber)',
                                                            figsize= (15,10),
                                                            fontsize=13)
                except IndexError:
                    continue

                plt.savefig(backup_path+
                    retailer
                    +variables_from_ini_in_dic['separator']+
                    entreprise+
                    variables_from_ini_in_dic['separator']+
                    current_date+
                    variables_from_ini_in_dic['separator']+
                    'byTeam'+
                    variables_from_ini_in_dic['separator']+
                    'view'+
                    '.jpg',
                    bbox_inches='tight')
                # ---------------------------------------
                # compute the count of "write" usage (Entreprise / team)
                # ---------------------------------------
                try:
                    filtered_dfrq.loc[
                                filtered_dfrq['write'] == 'Y'
                            ].loc[
                                    filtered_dfrq['entreprise'].str.lower() == str(entreprise).lower()
                                ].groupby(
                                            [
                                                filtered_dfrq['access_year_week'],
                                                filtered_dfrq['entreprise'],
                                                filtered_dfrq['team']
                                            ]
                                        ).count().plot.bar(y='access_date_to_path',
                                                            stacked=True,
                                                            title=f'{retailer.capitalize()} : VIEW activity up to {current_date} (by Team, YearWeekNumber)',
                                                            figsize= (15,10),
                                                            fontsize=13)
                except IndexError:
                    continue

                plt.savefig(backup_path+
                    retailer
                    +variables_from_ini_in_dic['separator']+
                    entreprise+
                    variables_from_ini_in_dic['separator']+
                    current_date+
                    variables_from_ini_in_dic['separator']+
                    'byTeam'+
                    variables_from_ini_in_dic['separator']+
                    'contribute'+
                    '.jpg',
                    bbox_inches='tight')
                # ---------------------------------------
                # compute the count of "read only" usage (Entreprise)
                # ---------------------------------------
                try:
                    filtered_dfrq.loc[
                                filtered_dfrq['read'] == 'Y'
                            ].loc[
                                    filtered_dfrq['entreprise'].str.lower() == str(entreprise).lower()
                                ].groupby(
                                            [
                                                filtered_dfrq['access_year_week'],
                                                filtered_dfrq['entreprise'],
                                            ]
                                        ).count().plot.bar(y='access_date_to_path',
                                                            stacked=True,
                                                            title=f'{retailer.capitalize()} : VIEW activity up to {current_date} (by Entreprise, YearWeekNumber)',
                                                            figsize= (15,10),
                                                            fontsize=13)
                except IndexError:
                    continue

                plt.savefig(backup_path+
                    retailer
                    +variables_from_ini_in_dic['separator']+
                    entreprise+
                    variables_from_ini_in_dic['separator']+
                    current_date+
                    variables_from_ini_in_dic['separator']+
                    'byEntreprise'+
                    variables_from_ini_in_dic['separator']+
                    'view'+
                    '.jpg',
                    bbox_inches='tight')
                # ---------------------------------------
                # compute the count of "write" usage (Entreprise / team)
                # ---------------------------------------
                try:
                    filtered_dfrq.loc[
                                filtered_dfrq['write'] == 'Y'
                            ].loc[
                                    filtered_dfrq['entreprise'].str.lower() == str(entreprise).lower()
                                ].groupby(
                                            [
                                                filtered_dfrq['access_year_week'],
                                                filtered_dfrq['entreprise'],
                                            ]
                                        ).count().plot.bar(y='access_date_to_path',
                                                            stacked=True,
                                                            title=f'{retailer.capitalize()} : VIEW activity up to {current_date} (by Entreprise, YearWeekNumber)',
                                                            figsize= (15,10),
                                                            fontsize=13)
                except IndexError:
                    continue

                plt.savefig(backup_path+
                    retailer
                    +variables_from_ini_in_dic['separator']+
                    entreprise+
                    variables_from_ini_in_dic['separator']+
                    current_date+
                    variables_from_ini_in_dic['separator']+
                    'byEntreprise'+
                    variables_from_ini_in_dic['separator']+
                    'contribute'+
                    '.jpg',
                    bbox_inches='tight')

        return True
    except BaseException as be:
        mlogger.critical(f'Unexpected error in the function usage_by_teams() : {type(be)}{be.args}')
        return False

    
