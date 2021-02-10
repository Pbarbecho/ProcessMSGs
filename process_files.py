#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 19:12:31 2021

@author: Pablo Barbecho
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from matplotlib import rc
import matplotlib.colors as mcolors
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator

rc('text', usetex=False)


# PATH TO FILES
ips = "/root/EPN/ips.csv"
server = "/root/EPN/msgs_server.csv"
cars = "/root/EPN/msgs.csv"
# READ FILES
ip_header = ['id', 'fullname','IP','MAC','Time']
ip_df = pd.read_csv(ips, names=ip_header)
common_header = ['type', 'tx_rx','node','msg_type','source','destination','msgID','Time']
server_df = pd.read_csv(server, names=common_header)
cars_df = pd.read_csv(cars, names=common_header)



def plot_tx_time(df, y_label):
    #mpl.style.use('default')
    fig, ax = plt.subplots(figsize=(2.5,2))
    plt.errorbar(df['Type'], df['Mean'], yerr=df['SD'], fmt='o', color='Black', elinewidth=1,capthick=3,errorevery=1, alpha=1, ms=4, capsize = 5)
    plt.bar(df['Type'], df['Mean'], width=0.5, tick_label = df[r'Type'])
        
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ylabel(r'{} [ms]'.format(y_label)) ##Label on Y axis
    #plt.grid(True, linewidth=0.2, linestyle='--')      

    
def plot_pdr(df):
    print(df.keys())
    fig, ax = plt.subplots(figsize=(2.5,2.5))
    plt.bar(df['Type'], df['PDR'], width=0.5, tick_label = df[r'Type'])
        
    #ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ylabel(r'PDR') ##Label on Y axis
    
   
    
def merge_files():
    frames = [cars_df, server_df]
    df = pd.concat(frames)
    
    # Count Send msgs
    car_tx_dsrc_msgs = df.loc[(df['type'] == "car") & (df['tx_rx'] == "tx") & (df['msg_type'] == 101)]
    car_tx_lte_msgs = df.loc[(df['type'] == "car") & (df['tx_rx'] == "tx") & (df['msg_type'] == 100)]
    
    car_rx_dsrc_msgs = df.loc[(df['type'] == "car") & (df['tx_rx'] == "rx") & (df['msg_type'] == 101)]
    car_rx_lte_msgs = df.loc[(df['type'] == "car") & (df['tx_rx'] == "rx") & (df['msg_type'] == 100)]
    
    server_tx_lte_msgs = df.loc[(df['type'] == "server") & (df['tx_rx'] == "tx") & (df['msg_type'] == 100)]
    server_rx_lte_msgs = df.loc[(df['type'] == "server") & (df['tx_rx'] == "rx") & (df['msg_type'] == 100)]
   
    dsrc =  [car_tx_dsrc_msgs, car_rx_dsrc_msgs]
    dsrc_df = pd.concat(dsrc)
    
    lte_rtt_time = [car_tx_lte_msgs, car_rx_lte_msgs]
    lte_rtt_df = pd.concat(lte_rtt_time)
    
    #=============================================================================================
    # PDR 
    #=============================================================================================
    pdr_dsrc = car_rx_dsrc_msgs['msgID'].count()/car_tx_dsrc_msgs['msgID'].count()
    pdr_lte = car_rx_lte_msgs['msgID'].count()/car_tx_lte_msgs['msgID'].count()
    pdr_dic = {'DSRC':pdr_dsrc, 'LTE':pdr_lte}
    pdr_df = pd.DataFrame(pdr_dic, index=[0])
    pdr_df = pdr_df.T.reset_index()
    pdr_df = pdr_df.rename(columns={'index':'Type', 0:'PDR'})
    plot_pdr(pdr_df)
    #=============================================================================================
    # E2E DELAY / RTT
    #=============================================================================================
   
    
    # DSRC Tx time 
    dsrc_df_filtered = dsrc_df.filter(items=['msgID','Time'])
    dsrc_tx_time = dsrc_df_filtered.groupby(by='msgID', dropna=True).diff().dropna(axis=0).reset_index(drop=True)
    
    dsrc_final = pd.DataFrame()
    dsrc_final['Mean'] = dsrc_tx_time.mean()*1000
    dsrc_final['SD'] = dsrc_tx_time.std()
    dsrc_final['Type'] = 'DSRC'
    
    # LTE Tx Time
    lte_tx_time = [car_tx_lte_msgs, server_rx_lte_msgs]
    lte_tx_df = pd.concat(lte_tx_time)
    lte_df_filtered = lte_tx_df.filter(items=['msgID','Time'])
    lte_tx_time = lte_df_filtered.groupby(by='msgID', dropna=True).diff().dropna(axis=0).reset_index(drop=True)
   
    lte_final = pd.DataFrame()
    lte_final['Mean'] = lte_tx_time.mean()*1000
    lte_final['SD'] = lte_tx_time.std()
    lte_final['Type'] = 'LTE'
    
    #end to end results
    time_results_frame = [dsrc_final, lte_final]
    time_results = pd.concat(time_results_frame)
    
    plot_tx_time(time_results, 'End-to-End Delay')
    
    # LTE RTT  ********* DSRC RTT estimated from end to end delay
        
    lte_rtt_filtered = lte_rtt_df.filter(items=['msgID','Time'])
    lte_rtt_time = lte_rtt_filtered.groupby(by='msgID', dropna=True).diff().dropna(axis=0).reset_index(drop=True)
   
    lte_rtt_final = pd.DataFrame()
    lte_rtt_final['Mean'] = lte_rtt_time.mean()*1000
    lte_rtt_final['SD'] = lte_rtt_time.std()
    lte_rtt_final['Type'] = 'LTE'
    
    
    dscr_rtt_final = pd.DataFrame()
    dscr_rtt_final['Mean'] = dsrc_final['Mean']*2
    dscr_rtt_final['SD'] = dsrc_final['SD']
    dscr_rtt_final['Type'] = 'DSRC'
    
    # RTT results
    rtt_time_results_frame = [dscr_rtt_final, lte_rtt_final]
    rtt_time_results = pd.concat(rtt_time_results_frame)
    
    plot_tx_time(rtt_time_results, 'Round Trip Time')
   
    
merge_files()    