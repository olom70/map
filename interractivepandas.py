#%%
from calendar import week
import configparser
from dis import code_info
import os
# ------------
## First STEP : initialize
#-------------
from openpyxl import Workbook
from map.tools import check_ini_files_and_return_config_object, create_main_variables_from_config, initialize_db, create_current_session, get_queries, brand_query
INIFILE = 'map_indicators.ini'
config = configparser.ConfigParser()
config = check_ini_files_and_return_config_object(INIFILE)
variables_from_ini_in_dic = create_main_variables_from_config(config)
conn = initialize_db(':memory:', variables_from_ini_in_dic['retailers'],
                                variables_from_ini_in_dic['retailers_tables'],
                                variables_from_ini_in_dic['toolkit_tables'],
                                variables_from_ini_in_dic['file_ext'],
                                variables_from_ini_in_dic['iniFilesDir'])
backup_path, current_date = create_current_session(variables_from_ini_in_dic['maindir'],
                                                variables_from_ini_in_dic['prefix'],
                                                variables_from_ini_in_dic['context'],
                                                variables_from_ini_in_dic['separator'])
all_queries_in_a_dict =  get_queries(config)
#%%
x = dict(iter(config.items('Sessions')))
print(x)
x.update(dict(iter(config.items('Main'))))
print(x)
x['retailers'] = x['retailers'].split()
print(x['retailers'])

#%%
# ------------
## 2nd STep : back up DB
#-------------

from map.tools import backup_in_memory_db_to_disk
backup_full_path_name = backup_path + variables_from_ini_in_dic['backup_name']
conn_backup = backup_in_memory_db_to_disk(conn, backup_full_path_name)

# %%
# ------------
## Load CONNECTIONS query
#-------------

import pandas as pd
brand = 'jules'
branded_query = brand_query(all_queries_in_a_dict['connected_at_least_once_v2'], variables_from_ini_in_dic['tables'], brand, variables_from_ini_in_dic['separator'])
sql_query = pd.read_sql(branded_query, conn)
df = pd.DataFrame(sql_query)
print(f'df.index : {df.index}')
print(f'df.columns : {df.columns}')
df
#%%
# ------------
##  CONNECTIONS grapph
#-------------

import matplotlib.pyplot as plt
df.plot.barh(stacked=True, x='Teams', title=f'{brand.capitalize()} : status of connections on {current_date}', figsize= (12,7), fontsize=13)
plt.savefig(backup_path+brand+variables_from_ini_in_dic['separator']+'connected.jpg')
#%%
# ------------
## USAGE QUERY LOAD
#-------------

import pandas as pd
brand = 'jules'
branded_query = brand_query(all_queries_in_a_dict['request_history_v2'], variables_from_ini_in_dic['tables'], brand, variables_from_ini_in_dic['separator'])
sql_query = pd.read_sql(branded_query, conn)
dfrq = pd.DataFrame(sql_query)

#%%
# ------------
## Diff??rents test
#-------------


dfrq.columns
dfrq.index
dfrq["req_user"]
dfrq["req_user_date"] = dfrq["req_user"]  + dfrq['access_date_to_path']
del dfrq["req_user_date"]
dfrq.insert(1, "req_user_date", dfrq["req_user"]  + dfrq['access_date_to_path'])
dfrq
#%%
#
# Setting the beginning of the time frame
#
def year_week_to_begin(year: int, week:int, backward_in_week: int) -> int:
    theorical_week = week - backward_in_week
    if theorical_week <= 0:
        week = 52 + theorical_week
        year = year -1
    else:
        week = theorical_week
        year = year
    return  int(str(year) + str(week))

y = 2022
w = 22
b = 4
year_week = year_week_to_begin(y, w, b)
print(y)
print(w)
print(b)
print("---")
print(year_week)

year = dfrq['access_year'].max()
print(year)
dly = dfrq.loc[dfrq['access_year'] == dfrq['access_year'].max()]
week = dly['access_week'].max()
print(week)

#%%
# ------------
## Enrich dataframe
#-------------
#https://datatofish.com/concatenate-values-python/
import datetime as dt
mydate = '2022-03-20'
dt.datetime.strptime(mydate, '%Y-%m-%d').isocalendar().week
dfrq.assign(
        myyear = list(map(lambda x: x[0:4], dfrq['access_date_to_path'])),
        mymonth = list(map(lambda x: x[5:7], dfrq['access_date_to_path'])),
        myday = list(map(lambda x: x[8:], dfrq['access_date_to_path'])),
        myweek = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').isocalendar().week, dfrq["access_date_to_path"]))
            )

# used to do like just beneath but it's better to use the map method included in Pandas
#dfrq["access_year"] = list(map(lambda x: str(x[0:4]), dfrq['access_date_to_path']))
dfrq["access_year"] = dfrq['access_date_to_path'].map(lambda x: str(x[0:4]))
dfrq["access_month"] = dfrq['access_date_to_path'].map(lambda x: str(x[5:7]))
dfrq["access_day"] = dfrq['access_date_to_path'].map(lambda x: str(x[8:]))
dfrq["access_week"] = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').isocalendar().week, dfrq["access_date_to_path"]))
dfrq["access_year_week"] = dfrq['access_year'].map(str) + dfrq['access_week'].map(str)
dfrq['access_year_month'] = dfrq['access_year'].map(str) + dfrq['access_month'].map(str)

#%%
dfrqaccess = dfrq
dfrqaccess.loc[
            dfrqaccess['read'] == 'Y'
          ].loc[
                dfrqaccess['doNotBotherWith_connectionReminder'] != 'Oui'].loc[
                    dfrq['access_year_week'].map(int) >= year_week
            ].groupby(
                    [
                        dfrqaccess['access_year_week']
                    ]
                ).count().plot.barh(y='access_date_to_path',
                                    stacked=True,
                                    title=f'{brand.capitalize()} : VIEW activity (no updates). by YearWeekNumber)',
                                    figsize= (15,10),
                                    fontsize=13)

#%%
dfrqaccess = dfrq
dfrqaccess.loc[
            dfrqaccess['write'] == 'Y'
          ].loc[
                dfrqaccess['doNotBotherWith_connectionReminder'] != 'Oui'].loc[
                    dfrq['access_year_week'].map(int) >= year_week
            ].groupby(
                    [
                        dfrqaccess['access_year_week']
                    ]
                ).count().plot.barh(y='access_date_to_path',
                                    stacked=True,
                                    title=f'{brand.capitalize()} : VIEW activity (no updates). by YearWeekNumber)',
                                    figsize= (15,10),
                                    fontsize=13)


#%%
# ------------
## USAGE JULES GRAPH
#-------------
import matplotlib.pyplot as plt
dfrqjules = dfrq
entreprise = "cgi"

# view only access
dfrqjules.loc[
            dfrqjules['read'] == 'Y'
          ].loc[
                dfrqjules['entreprise'].str.lower() == entreprise
               ].loc[
                    dfrqjules['doNotBotherWith_connectionReminder'] != 'Oui'].loc[
                        dfrq['access_year_week'].map(int) >= year_week
                ].groupby(
                        [
                            dfrqjules['access_year_week'],
                            dfrqjules['entreprise'],
                            dfrqjules['team']
                        ]
                    ).count().plot.barh(y='access_date_to_path',
                                        stacked=True,
                                        title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)',
                                        figsize= (15,10),
                                        fontsize=13)
plt.savefig(backup_path+
            'Instance-'+
            brand+variables_from_ini_in_dic['separator']+
            entreprise+
            variables_from_ini_in_dic['separator']+
            'view.jpg',
            bbox_inches='tight')

# access to contribute
dfrqjules.loc[
                dfrqjules['write'] == 'Y'
          ].loc[
                dfrqjules['entreprise'].str.lower() == entreprise
            ].loc[
                    dfrqjules['doNotBotherWith_connectionReminder'] != 'Oui'
                ].groupby(
                        [
                            dfrqjules['access_year_week'],
                            dfrqjules['entreprise'],
                            dfrqjules['team']
                        ]
                    ).count().plot.barh(y='access_date_to_path',
                                        stacked=True,
                                        title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)',
                                        figsize= (15,10),
                                        fontsize=13)
plt.savefig(backup_path+
            'Instance-'+
            brand+variables_from_ini_in_dic['separator']+
            entreprise+
            variables_from_ini_in_dic['separator']+
            'contribute.jpg',
            bbox_inches='tight')

entreprise = brand
# view only acess
dfrqjules.loc[
            dfrqjules['read'] == 'Y'
          ].loc[
              dfrqjules['entreprise'].str.lower() == entreprise
            ].loc[
                dfrqjules['doNotBotherWith_connectionReminder'] != 'Oui'
              ].groupby(
                        [
                            dfrqjules['access_year_week'],
                            dfrqjules['entreprise'],
                            dfrqjules['team']
                        ]
                ).count().plot.barh(y='access_date_to_path',
                                    stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)',
                                    figsize= (15,10),
                                    fontsize=13)
plt.savefig(backup_path+
            'Instance-'+
            brand+variables_from_ini_in_dic['separator']+
            entreprise+
            variables_from_ini_in_dic['separator']+
            'view.jpg',
            bbox_inches='tight')

#dfrqjules.loc[dfrqjules['write'] == 'Y'].loc[dfrqjules['entreprise'] == 'Jules'].loc[dfrqjules['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrqjules['access_year_week'], dfrqjules['entreprise'], dfrqjules['team']]).count().plot.barh(y='access_date_to_path', stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)

dfrqjules.loc[
                dfrqjules['write'] == 'Y'
          ].loc[
                dfrqjules['entreprise'].str.lower() == entreprise
            ].loc[
                    dfrqjules['doNotBotherWith_connectionReminder'] != 'Oui'
                ].groupby(
                        [
                            dfrqjules['access_year_week'],
                            dfrqjules['entreprise'],
                            dfrqjules['team']
                        ]
                    ).count().plot.barh(y='access_date_to_path',
                                        stacked=True,
                                        title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)',
                                        figsize= (15,10),
                                        fontsize=13)

plt.savefig(backup_path+
            'Instance-'+
            brand+variables_from_ini_in_dic['separator']+
            entreprise+
            variables_from_ini_in_dic['separator']+
            'contribute.jpg',
            bbox_inches='tight')

#%%
# ------------
## USAGE Pimkie GRAPH
#-------------
import pandas as pd
import matplotlib.pyplot as plt
brand = 'pimkie'
branded_query = brand_query(
                            all_queries_in_a_dict['request_history'],
                            variables_from_ini_in_dic['tables'],
                            brand,
                            variables_from_ini_in_dic['separator']
                            )
sql_query = pd.read_sql(branded_query, conn)
dfrqpmk = pd.DataFrame(sql_query)
dfrqpmk.loc[dfrqpmk['read'] == 'Y'
                ].loc[dfrqpmk['entreprise'] == 'Pimkie'
                ].loc[dfrqpmk['doNotBotherWith_connectionReminder'] != 'Oui'
                ].groupby(
                            [dfrqpmk['access_year_week'],
                            dfrqpmk['entreprise'],
                            dfrqpmk['team']]
                        ).sum().plot.barh(stacked=True,
                                            title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)',
                                            figsize= (15,10),
                                            fontsize=13)
plt.savefig(backup_path+
            'Instance-'+
            brand+variables_from_ini_in_dic['separator']+
            entreprise+
            variables_from_ini_in_dic['separator']+
            'view.jpg',
            bbox_inches='tight')

dfrqpmk.loc[dfrqpmk['write'] == 'Y'
                ].loc[dfrqpmk['entreprise'] == 'Pimkie'
                ].loc[dfrqpmk['doNotBotherWith_connectionReminder'] != 'Oui'
                ].groupby(
                            [dfrqpmk['access_year_week'],
                            dfrqpmk['entreprise'],
                            dfrq['team']]
                        ).sum().plot.barh(stacked=True,
                                            title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)',
                                            figsize= (15,10),
                                            fontsize=13)
plt.savefig(backup_path+
            'Instance-'+
            brand+variables_from_ini_in_dic['separator']+
            entreprise+
            variables_from_ini_in_dic['separator']+
            'contribute.jpg',
            bbox_inches='tight')

#%%
dfrq.groupby([dfrq['access_date_to_path'],dfrq['entreprise']]).sum().plot.bar()
#%%
# ------------
## Diff??rents tests
#-------------

import datetime
datetime.date(2022, 5, 23).isocalendar()[1]
d = '2022-02-15'
print(d[0:4])
print(d[5:7])
print(d[8:])

dfrq["len_check"] = dfrq['access_date_to_path'].str.len() == 10
dfrq.loc[dfrq["len_check"] == True] 

# %%
df.to_excel(backup_path+"map.xlsx", index=False, sheet_name='connected_at_teast_once')
sql_query = pd.read_sql(branded_query, conn)
df = pd.DataFrame(sql_query)
df

#%%
with pd.ExcelWriter(backup_path+'map.xlsx',
                    mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
    df.to_excel(writer, index=False, sheet_name='connected_at_teast_once')
#%%
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.worksheet.table import Table, TableStyleInfo
wb = Workbook()
ws = wb.active
index = 0
for index, r in enumerate(dataframe_to_rows(df, index=True, header=True), start=1):
    ws.append(r)
print(index)
ref = 'A1:F'+str(index)
tab = Table(displayName="connected_at_least_once", ref=ref)
style = TableStyleInfo(name="TableStyleDark12", showFirstColumn=False,
                       showLastColumn=False, showRowStripes=True, showColumnStripes=True)
tab.tableStyleInfo = style
ws.add_table(tab)
wb.save(backup_path+'map2.xlsx')
#%%
import matplotlib.pyplot as plt
df.plot.barh(stacked=True, x='Teams', title=f'{brand.capitalize()} : status of connections on {current_date}', figsize= (12,7), fontsize=13)
plt.savefig(backup_path+'jules_connected.jpg')

#%%
df.assign(entreprise_team=df["entreprise"] + " " + df["team"]+ " " + df["connected_at_least_once"]).groupby(['entreprise_team']).sum().plot.barh()

#%%
print(df)
df.groupby(['team']).sum()
#%%
for key,val in enumerate(config['Queries']):
    print(f'{key} / {val}')

for val in config['Queries']:
    print(f"{val} : {config['Queries'][val]}")