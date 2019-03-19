#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 10 14:02:42 2019

@author: chiachen
"""

import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from EV_charging import scenario_SC1
import matplotlib.pyplot as plt
import time


ALL_POSSIBLE_ACTIONS = ['C', 'D']
battery_states = [0, 0.1, 0.2, 0.3, 0.4, 0.5,
                    0.6, 0.7, 0.8, 0.9, 1]
GAMMA = 0.75 
ALPHA = 0.5 

def max_dict(d): 
  # returns the argmax (key) and max (value) from a dictionary
  max_key = None
  max_val = float('-inf')
  for k, v in d.items():
    if v > max_val:
      max_val = v
      max_key = k
  return max_key, max_val


def random_action(a, eps=0.1):
  # we'll use epsilon-soft to ensure all states are visited
  # what happens if you don't do this? i.e. eps=0
  p = np.random.random()
  #print('eps' , "%.2f" %eps)
  if p < (1 - eps):
    ev.exploiting += 1 #for debugging
    return a

  else:
    ev.exploring += 1 #for debugging
    return np.random.choice(ALL_POSSIBLE_ACTIONS)

    

#first implement using sarsa
if __name__ == '__main__':
    
    t0 = time.process_time()
    ev = scenario_SC1()
   
    elec_price = {}
    states = ev.actions.keys()
    
    #set electricity price
    for s in states:
        if s[0] in range(7,11):
            elec_price[s[0]] = -0.4 #peak price
        elif s[0] in range(17,22):
            elec_price[s[0]] = -0.4 #peak price
        else:
            elec_price[s[0]] = -0.1 #off peak price
     
    Q = {}
    for i in states:
        Q[i] = {}
        for j in ALL_POSSIBLE_ACTIONS:
            Q[i][j] = 0
    
    update_counts = {}  #for debugging  
    update_counts_sa = {}   #for adaptive learning rate
    
    for k in states:  
        update_counts_sa[k] = {}
        for a in ALL_POSSIBLE_ACTIONS:
            update_counts_sa[k][a] = 1.0        
           
    t = 1.0
    deltas = []
    cost_dict = {} #a dictionary where key = day, value = the cost for that day
    car_not_ready_list = [] #a list to key track of number of times car is not ready
    for day in range(1000): #need 10000 to converge
        if day % 10 == 0:
            t += 0.1 
            #print('t', t)
            
        if day % 100 == 0: 
            print("day", day)
            
        cost_dict[day] = 0 #stores the cost for 1 day = 1 episode
        
        s = (0,0) 
        ev.set_new_state(s) #set day_time = 0, set battery_level = 0 
        
        a, _ = max_dict(Q[s])
        biggest_change = 0
        
        for i in range(0,22): #1 episdoe = 24-2 = 22hours (2 hours of driving)
            
            if day ==999:
                a, _ = max_dict(Q[s])
                ev.last_policy[(ev.day_time, ev.battery_level)] = a
                cost_last_day = ev.cost_per_day
            else: 
                a = random_action(a, eps=0.9/t) 
                
            r = ev.charge_SC1(a, elec_price[s[0]]) 
            s2 = ev.new_current_state()
            
            alpha = ALPHA/update_counts_sa[s][a] 
            update_counts_sa[s][a] += 0.005
            
            old_qsa = Q[s][a]
            
            a2, max_q_s2a2 = max_dict(Q[s2])
            Q[s][a] = Q[s][a] + alpha*(r + GAMMA*max_q_s2a2 - Q[s][a])
            biggest_change = max(biggest_change, np.abs(old_qsa - Q[s][a]))
            
            s = s2
            a = a2
        t0 = time.time() 
        
        cost_dict[day] = ev.cost_per_day #stores cost for 1 day
        ev.reset_cost() #reset variable cost_per_day 
        
        deltas.append(biggest_change)
        ev.set_battery_level(0) #reset battery level to 0
        
        car_not_ready_list.append(ev.car_not_ready) #keep track of car not ready
    
    
    #print('car not ready', ev.car_not_ready, 'days')
    plt.rcParams['figure.figsize'] = 7, 5
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 16
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14   
    plt.rcParams['axes.titlesize'] = 18
    
    plt.plot(car_not_ready_list)
    plt.title('Number of Days Car is not Ready')
    plt.ylabel("Days Car is not Ready")
    plt.xlabel("Days")
    plt.show()
   
    cost_list = []
    list_reward = [] 
    cumulative_reward = 0
    for i in cost_dict.keys():
        cost_list.append(cost_dict[i]) 
        cumulative_reward += cost_dict[i]
        list_reward.append(np.mean(cost_list))
        
    plt.plot(list_reward)
    plt.title('Mean Electricity Cost')
    plt.ylabel("Cost of Electricity Consumed [Euro]")
    plt.xlabel("Days")
    plt.show()
    
    print('final policy')
    for i in ev.last_policy.keys():
        print('(t=', i[0], ', b_lv=', int(i[1]*100), '%)   action =',ev.last_policy[i])
    print('charging cost today = $', "%.2f" % cost_last_day )
    print('time = ',time.time() - t0,'seconds')
        
     
    