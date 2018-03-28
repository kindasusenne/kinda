# -*- coding: utf-8 -*-
"""
Created on Tue Dec 26 10:42:35 2017

@author: MENGLU417
"""

import tushare            as ts
#import kplot              as k
#import numpy              as np
import pandas             as pd
#import read_oracle        as re
#import datetime
#import matplotlib         as mpl
#import matplotlib.pyplot  as plt
#import matplotlib.finance as mpf
#from   matplotlib.pylab   import date2num

#stock = re.read_index(index = '000001', start_date = 20170101)
#stock.index = stock['tdate']

stock = ts.get_k_data('000001', index=True, start='2011-01-01')
stock.index = pd.to_datetime(stock['date'])

k_data = stock[['high', 'low', 'close', 'open']]
k_data.columns = ['high', 'low', 'tclose', 'topen']

# 笔
def bi_class(data):
    k_data = data.copy()
    after_fenxing = pd.DataFrame()
    temp_data = k_data[:1]
    zoushi = [3]            # 3-持平    4-向下    5-向上
    
    for i in xrange(len(k_data)):
        
    #   第1根包含第2根K线
        case1_1 = temp_data.high[-1] >  k_data.high[i] and temp_data.low[-1] <  k_data.low[i]
        case1_2 = temp_data.high[-1] >  k_data.high[i] and temp_data.low[-1] == k_data.low[i]    
        case1_3 = temp_data.high[-1] == k_data.high[i] and temp_data.low[-1] <  k_data.low[i]    
        
    #   第2根包含第1根K线
        case2_1 = temp_data.high[-1] <  k_data.high[i] and temp_data.low[-1] >  k_data.low[i]    
        case2_2 = temp_data.high[-1] <  k_data.high[i] and temp_data.low[-1] == k_data.low[i]    
        case2_3 = temp_data.high[-1] == k_data.high[i] and temp_data.low[-1] >  k_data.low[i]   
        
    #   第1根等于第2根K线
        case3   = temp_data.high[-1] == k_data.high[i] and temp_data.low[-1] == k_data.low[i]    
    
    #   向下趋势
        case4   = temp_data.high[-1] >  k_data.high[i] and temp_data.low[-1] >  k_data.low[i]    
    
    #   向上趋势
        case5   = temp_data.high[-1] <  k_data.high[i] and temp_data.low[-1] <  k_data.low[i]    
        
        if case1_1 or case1_2 or case1_3:
            if zoushi[-1] == 4:
                temp_data.high[-1] = k_data.high[i]
            else:
                temp_data.low[-1] = k_data.low[i]
        
        elif case2_1 or case2_2 or case2_3:
            temp_temp = temp_data[-1:]
            temp_data = k_data[i:i+1]
            if zoushi[-1] == 4:
                temp_data.high[-1] = temp_temp.high[0]
            else:
                temp_data.low[-1] = temp_temp.low[0]
        
        elif case3:
            zoushi.append(3)
            pass
        
        elif case4:
            zoushi.append(4)
            after_fenxing = pd.concat([after_fenxing, temp_data], axis = 0)
            temp_data = k_data.iloc[i:i+1]
            
        elif case5:
            zoushi.append(5)
            after_fenxing = pd.concat([after_fenxing, temp_data], axis = 0)
            temp_data = k_data.iloc[i:i+1]
    return after_fenxing


# 找出顶和低
def up_down(data):
    after_fenxing = data.copy()
    temp_num = 0    # 上一个顶或底的位置
    temp_high = 0    # 上一个顶的high值
    temp_low = 0     # 上一个底的low值
    temp_type = 0    # 上一个记录位置的类型
    
    i = 1
    
    fenxing_type = []    #记录分型点的类型    1为顶分型   -1为底分型
    fenxing_time = []    #记录分型点的时间
    fenxing_plot = []    #记录点的数值，为顶分型去high值，为底分型去low值
    fenxing_data = pd.DataFrame()   #分型点的DataFrame值
    
    while (i < len(after_fenxing) - 1):
        case1 = after_fenxing.high[i-1] < after_fenxing.high[i] and after_fenxing.high[i] > after_fenxing.high[i+1]  #顶分型
        case2 = after_fenxing.low[i-1] > after_fenxing.low[i] and after_fenxing.low[i] < after_fenxing.low[i+1] # 底分型
        if case1:
            if temp_type == 1: #如果上一个分型为顶分型，则进行比较，选取高点更高的分型
                if after_fenxing.high[i] <= temp_high:
                    i += 1
                    continue
                else:
                    temp_high = after_fenxing.high[i]
                    temp_num = i
                    temp_type = 1
            elif temp_type == 2:   #  如果上一个分型为底分型，则记录上一个分型，用当前分型与后面的分型比较，选取同向更极端的分型
                if temp_low >= after_fenxing.high[i]:    #  如果上一个底分型的底比当前顶分型的顶高，则跳过当前顶分型
                    i += 1
                else:
                    fenxing_type.append(-1)
                    fenxing_time.append(after_fenxing.index[i].strftime("%Y-%m-%d %H:%M:%S"))
                    fenxing_data = pd.concat([fenxing_data,  after_fenxing[temp_num:temp_num+1]], axis = 0)
                    fenxing_plot.append(after_fenxing.high[i])
                    temp_high = after_fenxing.high[i]
                    temp_num = i
                    temp_type = 1
                    i += 4
            else:
                temp_high = after_fenxing.high[i]
                temp_num = i
                temp_type = 1
                i += 4
                
        elif case2:
            if temp_type == 2:   #如果上一个分型为底分型，则进行比较。选取低点更低的分型
                if after_fenxing.low[i] >= temp_low:
                    i += 1
                    continue
                else:
                    temp_low = after_fenxing.low[i]
                    temp_num = i
                    temp_type = 2
                    i += 4
            elif temp_type == 1:  #如果上一个分型为顶分型，则记录上一个分型，用当前分型与后面的分型比较，选取同向更极端的分型
                if temp_high <= after_fenxing.low[i]:   #如果上一个顶分型的底比当前底分型的底低，则跳过当前底分型
                    i += 1
                else:
                    fenxing_type.append(1)
                    fenxing_time.append(after_fenxing.index[i].strftime("%Y-%m-%d %H:%M:%S"))
                    fenxing_data = pd.concat([fenxing_data, after_fenxing[temp_num:temp_num+1]], axis = 0)
                    fenxing_plot.append(after_fenxing.low[i])
                    temp_low = after_fenxing.low[i]
                    temp_num = i
                    temp_type = 2
                    i += 4
            else:
                temp_high = after_fenxing.low[i]
                temp_num = i
                temp_type = 2
        else:
            i += 1
        
#    print fenxing_type
#    print fenxing_time
#    print fenxing_plot
#    fenxing_data
    
    result = pd.DataFrame({'tdate':fenxing_time, 'point': fenxing_plot})
    return result

#   不显示开盘价、收盘价
def display_oc(data):
    after_fenxing = data.copy()
    for i in xrange(len(after_fenxing)):
        if after_fenxing.topen[i] > after_fenxing.tclose[i]:
            after_fenxing.topen[i] = after_fenxing.high[i]
            after_fenxing.tclose[i] = after_fenxing.low[i]
        else:
            after_fenxing.topen[i] = after_fenxing.low[i]
            after_fenxing.tclose[i] = after_fenxing.high[i]
    return after_fenxing


# 笔与原高开低收图像
point_plot = pd.DataFrame({'tdate':fenxing_time, 'point': fenxing_plot})
point_plot['tdate'] = pd.to_datetime(point_plot['tdate'])
k_data['tdate'] = k_data.index
point_plot = pd.merge(point_plot, k_data, on = 'tdate', how = 'outer')
point_plot.sort_values(by = 'tdate', inplace = True)
point_plot['point'] = point_plot['point'].interpolate()
point_plot.dropna(inplace = True)
point_plot.index = point_plot['tdate']
 
#  笔与分型

point_plot = pd.DataFrame({'tdate':fenxing_time, 'point': fenxing_plot})
point_plot['tdate'] = pd.to_datetime(point_plot['tdate'])
after_fenxing['tdate'] = after_fenxing.index
point_plot = pd.merge(point_plot, after_fenxing, on = 'tdate', how = 'outer')
point_plot.sort_values(by = 'tdate', inplace = True)
point_plot['point'] = point_plot['point'].interpolate()
point_plot.dropna(inplace = True)
point_plot.index = point_plot['tdate']


#def middle_num(k_data):
#    plot_data = []
#    for i in xrange(len(k_data)):
#        temp_y = (k_data.high[i] + k_data.low[i]) / 2.0
#        plot_data.append(temp_y)
#    return plot_data
#        
#stock_middle_num = middle_num(after_fenxing)
#fig, ax = plt.subplots(figsize = (30, 15))
#fig.subplots_adjust(bottom = 0.2)
##ax.xaxis_date()
#
#after_fenxing = after_fenxing[['topen', 'high', 'low', 'tclose']]
#mpf.candlestick2_ohlc(ax, list(after_fenxing.topen), list(after_fenxing.high), list(after_fenxing.low), list(after_fenxing.tclose), width = 1, colorup = 'r', colordown = 'b', alpha = 1)
#plt.grid(True)
#dates = after_fenxing.index
#ax.set_xticklabels(dates)
##ax.xaxis_date()
#plt.plot(stock_middle_num, 'k', lw = 1)
#plt.plot(stock_middle_num, 'ko', lw = 1)
#plt.setp(plt.gca().get_xticklabels(), rotation = 30)
#
##hista = np.array(after_fenxing)
#
#stock = re.read_index(index = '000001', start_date = 20170101)
#k.kplot(stock)
#
#point_plot.index = point_plot['tdate']
#point_plot['point'].plot()
