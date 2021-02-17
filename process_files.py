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

#===========================================#
# Description of captured metrics
#===========================================#
# state (tx, rx, fwd)
# mgstype lte 0  wlan 1
# sender -> Node that creates the msg
# msgsize size of message (just application)
# msgId -> unique ID
# msgCt -> message creation time 
# time -> simulation time
#===========================================#

# Statistics file as in omnet.ini
cars = "/root/EPN/statistics.csv"
# Header of stistic file
stics_header = ['srctype','srcindex', 'dsttype', 'state', 'srcId', 'msgtype', 'sender', 'msgsize', 'msgId','msgCT','Time']
stics_df = pd.read_csv(cars, names=stics_header)


def pdr():
    # Computed from source node[x] to server node
    # pdr = (rx/tx)  
    
    # Filter Send msgs from src node[x]
    wlan_node_tx_msgs_df = stics_df.loc[(stics_df['state'] == "tx")]
    # Filter Received msgs at the server 
    lte_server_rx_msgs_df = stics_df.loc[(stics_df['state'] == "rx") &
                                        (stics_df['srctype'] == "server")]
    # Compute PDR
    pdr = lte_server_rx_msgs_df['state'].count()/wlan_node_tx_msgs_df['state'].count()
    
    print(f" PDR {pdr*100}%")
    plot_pdr(pdr);
    
    return (wlan_node_tx_msgs_df, lte_server_rx_msgs_df)
 

      
def e2e_delay(tx,rx):
    # Computed from source node[x] till server node
    # e2e delay = car 2 car delay +  car 2 server 
    
    # Group tx with rx correspondent packet ID
    tx_rx_df = pd.concat([tx, rx])  
    msg_filtered = tx_rx_df.filter(items=['msgId','Time'])
    
    print(msg_filtered)
    
    temp_e2e_delay_df = msg_filtered.groupby(by='msgId', dropna=True).diff().dropna(axis=0).reset_index(drop=True)
    
    
    print(temp_e2e_delay_df)
    # Statistics 
    e2e_delay_df = pd.DataFrame()
    e2e_delay_df['Mean'] = temp_e2e_delay_df.mean() # in miliseconds
    e2e_delay_df['SD'] = temp_e2e_delay_df.std()
    e2e_delay_df['Type'] = 'wlan+LTE'
    
   
    print(e2e_delay_df)
    # Simple Bar Plot
    plot_tx_time(e2e_delay_df, 'End-to-End Delay')

    

def plot_pdr(pdr):
    # Prepare dataframe to plot
    pdr_df = pd.DataFrame(data=[pdr], columns=['PDR'])
    # Plot PDR 
    fig, ax = plt.subplots(figsize=(2,3))
    plt.bar('one-way',pdr_df['PDR'], width=0.5)
    plt.ylabel(r'PDR') # Label on Y axis
    
    

def plot_tx_time(df, y_label):
    #mpl.style.use('default')
    fig, ax = plt.subplots(figsize=(2,3))
    
    plt.errorbar(df['Type'], df['Mean'])
    plt.bar(df['Type'], df['Mean'], width=0.5, tick_label = df[r'Type'])
        
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ylabel(r'{} [s]'.format(y_label)) ##Label on Y axis
    #plt.grid(True, linewidth=0.2, linestyle='--')      


  
# Call functions
tx, rx = pdr()
e2e_delay(tx, rx)