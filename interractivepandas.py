#%%
from calendar import week
import configparser
import os
# ------------
## First STEP : initialize
#-------------
from openpyxl import Workbook
from lib.tools import check_ini_files_and_return_config_object, create_main_variables_from_config, initialize_db, get_current_session, get_queries, brand_query
INIFILE = 'map_indicators.ini'
config = configparser.ConfigParser()
config = check_ini_files_and_return_config_object(INIFILE)[0]
variables_from_ini_in_list = create_main_variables_from_config([config])
maindir, separator, retailers, tables, retailers_tables, toolkit_tables, file_ext, iniFilesDir, prefix, context, backup_name, log_level = variables_from_ini_in_list
conn = initialize_db(':memory:', retailers, retailers_tables, toolkit_tables, file_ext, iniFilesDir)[0]
backup_path, current_date = get_current_session(maindir, prefix, context, separator)
backup_path = backup_path+ os.path.sep
all_queries_in_a_dict =  get_queries([config])
#%%
# ------------
## 2nd STep : back up DB
#-------------

from lib.tools import backup_in_memory_db_to_disk
backup_full_path_name = backup_path + backup_name
conn_backup = backup_in_memory_db_to_disk([conn], backup_full_path_name)[0]

# %%
# ------------
## Load CONNECTIONS query
#-------------

import pandas as pd
brand = 'jules'
branded_query = brand_query(all_queries_in_a_dict['connected_at_least_once_v2'], tables, brand, separator)
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
plt.savefig(backup_path+brand+separator+'connected.jpg')
#%%
# ------------
## USAGE QUERY LOAD
#-------------

import pandas as pd
brand = 'jules'
branded_query = brand_query(all_queries_in_a_dict['request_history'], tables, brand, separator)
sql_query = pd.read_sql(branded_query, conn)
dfrq = pd.DataFrame(sql_query)

#%%
# ------------
## Différents test
#-------------


dfrq.columns
dfrq.index
dfrq["req_user"]
dfrq["req_user_date"] = dfrq["req_user"]  + dfrq['access_date_to_path']
del dfrq["req_user_date"]
dfrq.insert(1, "req_user_date", dfrq["req_user"]  + dfrq['access_date_to_path'])
dfrq
#%%
# ------------
## Différents tests
#-------------

import datetime as dt
mydate = '2022-03-20'
dt.datetime.strptime(mydate, '%Y-%m-%d').isocalendar().week
#dfrq["myweek"] = dt.datetime.strptime(dfrq['access_date_to_path'], '%Y-%m-%d').isocalendar().week
#dfrq.assign(myweek = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').isocalendar().week, dfrq["access_date_to_path"])))
#dfrq.assign(myweek2= pd.to_datetime(dfrq["access_date_to_path"]))
dfrq.assign(
        myyear = list(map(lambda x: x[0:4], dfrq['access_date_to_path'])),
        mymonth = list(map(lambda x: x[5:7], dfrq['access_date_to_path'])),
        myday = list(map(lambda x: x[8:], dfrq['access_date_to_path'])),
        myweek = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').isocalendar().week, dfrq["access_date_to_path"]))
            )

dfrq["access_year2"] = list(map(lambda x: x[0:4], dfrq['access_date_to_path']))
dfrq["access_month2"] = list(map(lambda x: x[5:7], dfrq['access_date_to_path']))
dfrq["access_day2"] = list(map(lambda x: x[8:], dfrq['access_date_to_path']))
dfrq["access_week2"] = list(map(lambda x: dt.datetime.strptime(x, '%Y-%m-%d').isocalendar().week, dfrq["access_date_to_path"]))
dfrq["access_year_week2"] = dfrq['access_year'] + '-' + dfrq['access_week']
dfrq['access_year_month2'] = dfrq['access_year'] + '-' + dfrq['access_month']
dfrq
dfrq.loc[
        dfrq['read'] == 'Y'].loc[
            dfrq['entreprise'] == 'CGI'].loc[
                dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].loc[
                    dfrq['access_week2'] < 21
                ]



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
                    dfrqjules['doNotBotherWith_connectionReminder'] != 'Oui'
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
plt.savefig(backup_path+'Instance-'+brand+separator+entreprise+separator+'view.jpg', bbox_inches='tight')

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
plt.savefig(backup_path+'Instance-'+brand+separator+entreprise+separator+'contribute.jpg', bbox_inches='tight')

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
plt.savefig(backup_path+'Instance-'+brand+separator+entreprise+separator+'view.jpg', bbox_inches='tight')

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

plt.savefig(backup_path+'Instance-'+brand+separator+entreprise+separator+'contribute.jpg', bbox_inches='tight')

#%%
# ------------
## USAGE Pimkie GRAPH
#-------------
import pandas as pd
import matplotlib.pyplot as plt
brand = 'pimkie'
branded_query = brand_query(all_queries_in_a_dict['request_history'], tables, brand, separator)
sql_query = pd.read_sql(branded_query, conn)
dfrqpmk = pd.DataFrame(sql_query)
# dfrq.loc[dfrq['read'] == 'Y'].loc[dfrq['entreprise'] == 'CGI'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
# plt.savefig(backup_path+brand+separator+brand+separator+'CGI_view.jpg')
# dfrq.loc[dfrq['write'] == 'Y'].loc[dfrq['entreprise'] == 'CGI'].loc[dfrq['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrq['access_year_week'], dfrq['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
# plt.savefig(backup_path+brand+separator+brand+separator+'CGI_contribute.jpg')
dfrqpmk.loc[dfrqpmk['read'] == 'Y'].loc[dfrqpmk['entreprise'] == 'Pimkie'].loc[dfrqpmk['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrqpmk['access_year_week'], dfrqpmk['entreprise'], dfrqpmk['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : VIEW activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+brand+separator+'view.jpg')
dfrqpmk.loc[dfrqpmk['write'] == 'Y'].loc[dfrqpmk['entreprise'] == 'Pimkie'].loc[dfrqpmk['doNotBotherWith_connectionReminder'] != 'Oui'].groupby([dfrqpmk['access_year_week'], dfrqpmk['entreprise'], dfrq['team']]).sum().plot.barh(stacked=True, title=f'{brand.capitalize()} : CONTRIBUTE activity up to {current_date} (by Team, Year-WeekNumber)', figsize= (15,10), fontsize=13)
plt.savefig(backup_path+brand+separator+brand+separator+'contribute.jpg')

#%%
dfrq.groupby([dfrq['access_date_to_path'],dfrq['entreprise']]).sum().plot.bar()
#%%
# ------------
## Différents tests
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