import json
import requests
import pandas as pd
import time
import numpy as np
import os
import re
from tqdm import tqdm
import datetime
from send_email import email_sender
#=====定义函数====
from HTMLTable import HTMLTable
'''
生成html表格
传入一个dataframe, 设置一个标题， 返回一个html格式的表格
'''
def create_html_table(df, title):
    table = HTMLTable(caption=title)

    # 表头行
    table.append_header_rows((tuple(df.columns),))

    # 数据行
    for i in range(len(df.index)):
        table.append_data_rows((
            tuple(df.iloc[df.index[i],]),
        ))

    # 标题样式
    table.caption.set_style({
        'font-size': '15px',
    })

    # 表格样式，即<table>标签样式
    table.set_style({
        'border-collapse': 'collapse',
        'word-break': 'keep-all',
        'white-space': 'nowrap',
        'font-size': '14px',
    })

    # 统一设置所有单元格样式，<td>或<th>
    table.set_cell_style({
        'border-color': '#000',
        'border-width': '1px',
        'border-style': 'solid',
        'padding': '5px',
        'text-align': 'center',
    })

    # 表头样式
    table.set_header_row_style({
        'color': '#fff',
        'background-color': '#48a6fb',
        'font-size': '15px',
    })

    # 覆盖表头单元格字体样式
    table.set_header_cell_style({
        'padding': '15px',
    })

    # 调小次表头字体大小
    table[0].set_cell_style({
        'padding': '8px',
        'font-size': '15px',
    })

    html_table = table.to_html()
    return html_table

# ======= 正式开始执行

def cal(x):
    if x>= pd.to_datetime('2013-01-01') and x<= pd.to_datetime('2016-10-31'):
        y = 'Second cycle'
    elif x>= pd.to_datetime('2016-11-01') and x<= pd.to_datetime('2020-04-30'):
        y = 'Third cycle'
    else:
        y = 'Fourth cycle'
    return y
url_address = ['https://api.glassnode.com/v1/metrics/indicators/puell_multiple',
                'https://api.glassnode.com/v1/metrics/indicators/sopr_adjusted',
                'https://api.glassnode.com/v1/metrics/market/mvrv_z_score',
                'https://api.glassnode.com/v1/metrics/indicators/rhodl_ratio',
                'https://api.glassnode.com/v1/metrics/indicators/net_realized_profit_loss',
                'https://api.glassnode.com/v1/metrics/market/price_usd_close',
                'https://api.glassnode.com/v1/metrics/supply/profit_relative',
                'https://api.glassnode.com/v1/metrics/transactions/transfers_volume_to_exchanges_sum',
                'https://api.glassnode.com/v1/metrics/transactions/transfers_volume_from_exchanges_sum']
url_name = ['Puell Multiple', 'aSOPR','MVRV Z-Score','RHODL Ratio','Net Realized Profit/Loss','Price','Percent Supply in Profit','in_exchanges', 'out_exchanges']
# insert your API key here
API_KEY = '26BLocpWTcSU7sgqDdKzMHMpJDm'
data_list = []
for num in range(len(url_name)):
    print(num)
    addr = url_address[num]
    name = url_name[num]
    # make API request
    res_addr = requests.get(addr,params={'a': 'BTC', 'api_key': API_KEY})
    # convert to pandas dataframe
    ins = pd.read_json(res_addr.text, convert_dates=['t'])
    ins['date'] =  ins['t']
    ins[name] =  ins['v']
    ins = ins[['date',name]]
    data_list.append(ins)

result_data = data_list[0][['date']]
for i in range(len(data_list)):
    df = data_list[i]
    result_data = result_data.merge(df,how='left',on='date')
#last_data = result_data[(result_data.date>='2016-01-01') & (result_data.date<='2020-01-01')]
last_data = result_data[(result_data.date>='2012-10-01')]
last_data = last_data.sort_values(by=['date'])
last_data = last_data.reset_index(drop=True)
date = []
pm = []
mvrv = []
rhold = []
net = []
price = []
sopr_7 = []
sopr_50 = []
supply = []
for j in range(len(last_data)-49):
    ins = last_data[j:j+50]
    ins = ins.reset_index(drop=True)
    date.append(ins['date'][49])
    pm.append(ins['Puell Multiple'][49])
    mvrv.append(ins['MVRV Z-Score'][49])
    rhold.append(ins['RHODL Ratio'][49])
    sopr_50.append(np.mean(ins['aSOPR']))
    supply.append(ins['Percent Supply in Profit'][49])
    price.append(ins['Price'][49])
    #短期指标
    net.append(np.mean(ins['Net Realized Profit/Loss'][-7:]))
    sopr_7.append(np.mean(ins['aSOPR'][-7:]))
res_df = pd.DataFrame({'date':date,'Puell Multiple':pm,'MVRV Z-Score':mvrv,'RHODL Ratio':rhold,'Net Realized Profit/Loss':net,'Price':price,'Percent Supply in Profit':supply,'7MA aSOPR':sopr_7,'50MA aSOPR':sopr_50})
res_df = res_df[(res_df.date>='2013-01-01')]
res_df['cycle'] = res_df['date'].apply(lambda x:cal(x))
res_df['log(BTC price)'] = np.log(res_df['Price'])
res_df['log(RHODL Ratio)'] = np.log(res_df['RHODL Ratio'])
res_df['x1'] = 7
res_df['x2'] = 0
res_df['y1'] = 4
res_df['y2'] = 0.5
res_df['z1'] = np.log(49000)
res_df['z2'] = np.log(350)
res_df['w'] = 1
res_df['p1'] = 0.9
res_df['p2'] = 0.5

url_address = ['https://api.glassnode.com/v1/metrics/market/mvrv_z_score',
                'https://api.glassnode.com/v1/metrics/market/price_usd_close']
url_name = ['MVRV Z-Score','Price']
# insert your API key here
API_KEY = '26BLocpWTcSU7sgqDdKzMHMpJDm'
data_list = []
for num in range(len(url_name)):
    print(num)
    addr = url_address[num]
    name = url_name[num]
    # make API request
    res_addr = requests.get(addr,params={'a': 'ETH', 'api_key': API_KEY})
    # convert to pandas dataframe
    ins = pd.read_json(res_addr.text, convert_dates=['t'])
    ins['date'] =  ins['t']
    ins[name] =  ins['v']
    ins = ins[['date',name]]
    data_list.append(ins)

result_data = data_list[0][['date']]
for i in range(len(data_list)):
    df = data_list[i]
    result_data = result_data.merge(df,how='left',on='date')
#last_data = result_data[(result_data.date>='2016-01-01') & (result_data.date<='2020-01-01')]
last_data = result_data[(result_data.date>='2015-01-01')]
last_data = last_data.sort_values(by=['date'])
last_data = last_data.reset_index(drop=True)
date = []
mvrv = []
price = []
for j in range(len(last_data)-49):
    ins = last_data[j:j+50]
    ins = ins.reset_index(drop=True)
    date.append(ins['date'][49])
    mvrv.append(ins['MVRV Z-Score'][49])
    price.append(ins['Price'][49])
eth_df = pd.DataFrame({'date':date,'MVRV Z-Score':mvrv,'Price':price})
eth_df = eth_df[(eth_df.date>='2015-01-01')]
eth_df['cycle'] = eth_df['date'].apply(lambda x:cal(x))
eth_df['log(ETH price)'] = np.log(eth_df['Price'])
eth_df['x1'] = 7
eth_df['x2'] = 0

url_address = ['https://api.glassnode.com/v1/metrics/market/price_usd_close']
url_name = ['Price']
# insert your API key here
API_KEY = '26BLocpWTcSU7sgqDdKzMHMpJDm'
data_list = []
for num in range(len(url_name)):
    print(num)
    addr = url_address[num]
    name = url_name[num]
    # make API request
    res_addr = requests.get(addr,params={'a': 'BTC', 'api_key': API_KEY})
    # convert to pandas dataframe
    ins = pd.read_json(res_addr.text, convert_dates=['t'])
    ins['date'] =  ins['t']
    ins[name] =  ins['v']
    ins = ins[['date',name]]
    data_list.append(ins)

result_data = data_list[0][['date']]
for i in range(len(data_list)):
    df = data_list[i]
    result_data = result_data.merge(df,how='left',on='date')
#last_data = result_data[(result_data.date>='2016-01-01') & (result_data.date<='2020-01-01')]
last_data = result_data[(result_data.date>='2010-01-01')]
from dateutil.relativedelta import relativedelta 
#last_data['new_date'] = last_data['date'].apply(lambda x:x + relativedelta(years=1))
last_data = last_data.sort_values(by=['date'])
last_data = last_data.reset_index(drop=True)
date = []
price_raw = []
price_ma120 = []
price_ma200 = []
price_ma1y = []
price_ma4y = []
price_ma3_5y = []
price_ma1_2y = []
for j in range(len(last_data)-1824):
    ins = last_data[j:j+1825]
    ins = ins.sort_values(by='date')
    ins = ins.reset_index(drop=True)
    date.append(ins['date'][1824])
    price_raw.append(ins['Price'][1824])
    price_ma3_5y.append(np.mean(ins['Price'][0:730]))
    price_ma1_2y.append(np.mean(ins['Price'][-730:-365]))
    price_ma4y.append(np.mean(ins['Price'][-1459:]))
    price_ma1y.append(np.mean(ins['Price'][-364:]))
    price_ma200.append(np.mean(ins['Price'][-199:]))
    price_ma120.append(np.mean(ins['Price'][-119:]))
jun_df = pd.DataFrame({'date':date,'price_raw':price_raw,'price_ma120':price_ma120,'price_ma200':price_ma200,'price_ma1y':price_ma1y,'price_ma4y':price_ma4y,'price_ma3_5y':price_ma3_5y,'price_ma1_2y':price_ma1_2y})
jun_df = jun_df[(jun_df.date>='2018-12-01')]
jun_df['cycle'] = jun_df['date'].apply(lambda x:cal(x))

# 表格
date_value = eth_df['date'][len(eth_df)-1] #+ datetime.timedelta(days=1)

jun_df = jun_df.sort_values(by='date')
jun_df = jun_df.reset_index(drop=True)
sub_jun_df = jun_df[['date','price_raw','price_ma120','price_ma200','price_ma4y']][-5:-1]
sub_jun_df = sub_jun_df.set_index('date')
col_name = []
for ele in list(sub_jun_df.index):
    col_name.append(str(ele)[0:10])
sub_jun_df_T = pd.DataFrame(sub_jun_df.values.T,columns=col_name,index=['price_close','price_ma120','price_ma200','price_ma4y'])
sub_jun_df_T = sub_jun_df_T.round(0)
res_df = res_df.sort_values(by='date')
res_df = res_df.reset_index(drop=True)
sub_res_df = res_df[['date','Puell Multiple','MVRV Z-Score','RHODL Ratio','Net Realized Profit/Loss','Percent Supply in Profit','7MA aSOPR','50MA aSOPR']][-4:]
sub_res_df = sub_res_df.set_index('date')
sub_res_df_T = pd.DataFrame(sub_res_df.values.T,columns=col_name,index=['Puell Multiple','BTC MVRV Z-Score','RHODL Ratio','Net Realized Profit/Loss','Percent Supply in Profit','7MA aSOPR','50MA aSOPR'])
eth_df = eth_df.sort_values(by='date')
eth_df = eth_df.reset_index(drop=True)
sub_eth_df = eth_df[['date','MVRV Z-Score']][-4:]
sub_eth_df = sub_eth_df.set_index('date')
sub_eth_df_T = pd.DataFrame(sub_eth_df.values.T,columns=col_name,index=['ETH MVRV Z-Score'])
sub_eth_df_T = sub_eth_df_T.round(4)
combine_df = pd.concat([sub_res_df_T,sub_eth_df_T,sub_jun_df_T])
combine_df = combine_df.applymap(lambda x: format(x, '.4'))
combine_df = combine_df.reset_index(drop=False)
#图片
#全局牛熊市指标
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['figure.figsize'] = (80.0, 160.0)
plt.rc('legend', fontsize=30)
fig = plt.figure(dpi=100)
# 设定图表颜色
#fig.set(alpha=0.2)
# 第一张小图
# 绘画折线图
axes1 = plt.subplot2grid((9,1),(0,0))
axes_fu1 = axes1.twinx()
ax1 = sns.lineplot(x="date", y="x1", data=res_df, color = 'green',ax=axes_fu1)
ax1 = sns.lineplot(x="date", y="x2", data=res_df, color='red',ax=axes_fu1)
ax11 = sns.lineplot(x="date", y="MVRV Z-Score",color='black',data=res_df,ax=axes_fu1)
ax1 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=res_df,ax=axes1)
ax1.tick_params(labelsize=20)
ax11.tick_params(labelsize=20)
plt.title('MVRV Z-Score —— log(BTC price)', fontsize=50) 
#plt.show()
#plt.savefig('MVRV Z-Score.png')
axes7 = plt.subplot2grid((9,1),(1,0))
axes_fu7 = axes7.twinx()
ax7 = sns.lineplot(x="date", y="x1", data=eth_df, color = 'green',ax=axes_fu7)
ax7 = sns.lineplot(x="date", y="x2", data=eth_df, color='red',ax=axes_fu7)
ax71 = sns.lineplot(x="date", y="MVRV Z-Score",color='black',data=eth_df,ax=axes_fu7)
ax7 = sns.lineplot(x="date", y="Price",hue = 'cycle', data=eth_df,ax=axes7)
ax7.legend(loc='upper left')
ax7.tick_params(labelsize=20)
ax71.tick_params(labelsize=20)
plt.title('MVRV Z-Score —— ETH Price', fontsize=50) 
# 绘画折线图
axes2 = plt.subplot2grid((9,1),(2,0))
axes_fu2 = axes2.twinx()
ax2 = sns.lineplot(x="date", y="y1", data=res_df, color = 'green', ax=axes_fu2)
ax2 = sns.lineplot(x="date", y="y2", data=res_df, color='red', ax=axes_fu2)
ax21 = sns.lineplot(x="date", y="Puell Multiple",color='black',data=res_df, ax=axes_fu2)
ax2 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=res_df, ax=axes2)
ax2.tick_params(labelsize=20)
ax21.tick_params(labelsize=20)
plt.title('Puell Multiple —— log(BTC price)', fontsize=50) 
#plt.show()
#plt.savefig('Puell.png')
#plt.close()
# 绘画折线图
axes3 = plt.subplot2grid((9,1),(3,0))
axes_fu3 = axes3.twinx()
ax3 = sns.lineplot(x="date", y="z1", data=res_df, color = 'green',ax=axes_fu3)
ax3 = sns.lineplot(x="date", y="z2", data=res_df, color='red', ax=axes_fu3)
ax31 = sns.lineplot(x="date", y="log(RHODL Ratio)",color='black',data=res_df, ax=axes_fu3)
ax3 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=res_df, ax=axes3)
ax3.tick_params(labelsize=20)
ax31.tick_params(labelsize=20)
plt.title('log(RHODL Ratio) —— log(BTC price)', fontsize=50) 
#plt.show()
#plt.savefig('RHODL.png')
#plt.close()
# 绘画折线图
axes4 = plt.subplot2grid((9,1),(4,0))
axes_fu4 = axes4.twinx()
ax4 = sns.lineplot(x="date", y="w", data=res_df, color='red', ax=axes_fu4)
ax41 = sns.lineplot(x="date", y="50MA aSOPR",color='black',data=res_df,ax=axes_fu4)
ax4 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=res_df,ax=axes4)
ax4.tick_params(labelsize=20)
ax41.tick_params(labelsize=20)
plt.title('50MA aSOPR —— log(BTC price)', fontsize=50) 
#plt.show()
#plt.savefig('50MA aSOPR.png')
# 绘画折线图
res_df['w1'] = 0.95
res_df['w2'] = 0.65
res_df['w3'] = 0.5
axes91 = plt.subplot2grid((9,1),(6,0))
axes_fu91 = axes91.twinx()
ax91 = sns.lineplot(x="date", y="w1", data=res_df, color='green',  ax=axes_fu91)
ax91 = sns.lineplot(x="date", y="w2", data=res_df, color='red',  ax=axes_fu91)
ax91 = sns.lineplot(x="date", y="w3", data=res_df, color='black',  ax=axes_fu91)
ax911 = sns.lineplot(x="date", y="Percent Supply in Profit",color='black',data=res_df, ax=axes_fu91)
ax91 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=res_df, ax=axes91)
ax91.tick_params(labelsize=20)
ax911.tick_params(labelsize=20)
plt.title('Percent Supply in Profit —— log(BTC price)', fontsize=50) 
ax91.legend(loc='upper left')

# 绘画折线图
sub_res_df = res_df[res_df.date>='2022-01-01']
axes5 = plt.subplot2grid((9,1),(6,0))
axes_fu5 = axes5.twinx()
ax5 = sns.lineplot(x="date", y="w", data=sub_res_df, color='red',  ax=axes_fu5)
ax51 = sns.lineplot(x="date", y="Net Realized Profit/Loss",color='black',data=sub_res_df, ax=axes_fu5)
ax5 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=sub_res_df, ax=axes5)
ax5.tick_params(labelsize=20)
ax51.tick_params(labelsize=20)
plt.title('7MA Net Realized Profit/Loss —— log(BTC price)', fontsize=50) 
ax5.legend(loc='upper left')
axes6 = plt.subplot2grid((9,1),(7,0))
axes_fu6 = axes6.twinx()
ax6 = sns.lineplot(x="date", y="w", data=sub_res_df, color='red', ax=axes_fu6)
ax61 = sns.lineplot(x="date", y="7MA aSOPR",color='black',data=sub_res_df, ax=axes_fu6)
ax6 = sns.lineplot(x="date", y="log(BTC price)",hue = 'cycle', data=sub_res_df, ax=axes6)
ax6.tick_params(labelsize=20)
ax61.tick_params(labelsize=20)
plt.title('7MA aSOPR —— log(BTC price)', fontsize=50) 
ax6.legend(loc='upper left')
#axes6.yticks(size=30,weight='bold')#设置大小及加粗
axes8 = plt.subplot2grid((9,1),(8,0))
sub_jun_df = jun_df[(jun_df.date>='2018-11-01') & (jun_df.date<='2023-06-01')]
ax8 = sns.lineplot(x="date", y="price_raw", data=sub_jun_df, color = 'black',ax=axes8)
ax8 = sns.lineplot(x="date", y="price_ma120",color='red',data=sub_jun_df, ax=axes8)
ax8 = sns.lineplot(x="date", y="price_ma200",color='green', data=sub_jun_df, ax=axes8)
ax8 = sns.lineplot(x="date", y="price_ma4y", data=sub_jun_df, color='blue', ax=axes8)
ax8.tick_params(labelsize=20)
plt.title('Moving Average Trend', fontsize=50) 
plt.legend(labels=['price_ma4y',"price_ma200","price_ma120"],loc="upper left",fontsize=30)  
#plt.show()
fig.savefig('chain_data_picture.png')
plt.close()
#plt.savefig('50MA aSOPR.png')
#======自动发邮件
content = create_html_table(combine_df, f'链上数据一览{date_value}')
#设置服务器所需信息
#163邮箱服务器地址
mail_host = 'smtp.163.com'  
#163用户名
mail_user = 'lee_daowei@163.com'  
#密码(部分邮箱为授权码) 
mail_pass = 'GKXGKVGTYBGRMAVE'   
#邮件发送方邮箱地址
sender = 'lee_daowei@163.com'
#邮件接受方邮箱地址，注意需要[]包裹，这意味着你可以写多个邮件地址群发
receivers = ['lee_daowei@163.com']  
context = f'区块链链上数据{date_value}'
email_sender(mail_host,mail_user,mail_pass,sender,receivers,context,content)