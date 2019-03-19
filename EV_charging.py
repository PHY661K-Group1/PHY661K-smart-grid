#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  4 22:25:39 2019

@author: chiachen
"""


class EV: 
  def __init__(self, battery_capacity, battery_level, day_time, min_charge): 
    self.battery_capacity = battery_capacity # 30 kWh
    self.battery_level = battery_level #between 0~1.0
    self.battery_kWh = battery_capacity * battery_level #the battery level in units of kWh
    self.day_time = day_time
    self.min_charge = min_charge #a constraint, the minimum charge for drivable 
    self.car_not_ready = 0
    self.cost_per_day = 0 #cumulative cost for 1 day
    self.exploring = 0 #for debugging
    self.exploiting = 0 #for debugging
    self.last_policy = {}
    self.car_not_ready_day = 0

  def set(self,  actions): 
    self.actions = actions


  def set_state(self, s): 
    self.day_time = s


  def set_new_state(self, s):
    self.day_time = s[0]
    self.battery_level = s[1]

    
  def current_state(self):
    return self.day_time


  def new_current_state(self):
    return (self.day_time, self.battery_level)


  def current_battery_level(self):
    return (self.battery_level)


  def set_battery_level(self, level):
    self.battery_level = level
    self.battery_kWh = self.battery_capacity * level 
    

  def reset_cost(self):
    self.cost_per_day = 0   
    

  def drive(self, distance): 
    #distance in km, it consumes 15 kWh per 100 km
    elec_consumed = 15 * distance / 100
    
    #make sure battery level is >= electricity consume
    if self.battery_kWh >= elec_consumed:
        self.battery_kWh -= elec_consumed
        self.battery_level = self.battery_kWh / self.battery_capacity
        
    #otherwise battery level reaches 0
    else:
        self.battery_kWh = 0
        self.battery_level = 0
    
    return self.battery_level


  def charge_SC1(self, action, price): #price in units $/kWh 
   
    charge_power = 3 #units in kW, each hour can charge 3 kWh
    if action == 'C':
        old_battery_kWh = self.battery_kWh  
        self.battery_kWh += charge_power 
        
        #make sure we dont overcharge battery
        if self.battery_kWh >= self.battery_capacity:
            self.battery_kWh = self.battery_capacity
            self.battery_level = 1
            elec_cost = (self.battery_capacity - old_battery_kWh) * price
            self.cost_per_day += elec_cost
        #charging battery under normal condition
        else:    
            self.battery_level = self.battery_kWh / self.battery_capacity
            elec_cost = price * charge_power #unit = $    
            self.cost_per_day += elec_cost
            
    elif action == 'D':
        self.battery_level = self.battery_kWh / self.battery_capacity
        elec_cost = 0

        
    self.day_time += 1 #increment the time by 1
    
    if self.day_time == 8:
        if self.battery_kWh <= self.min_charge: 
            elec_cost = -60 
            self.car_not_ready +=1
            self.car_not_ready_day = 1
        self.drive(40) 
        self.day_time +=1
        
    elif self.day_time == 17:
        if self.battery_kWh <=self.min_charge: 
            elec_cost = -60
            if  self.car_not_ready_day == 0:
                self.car_not_ready += 1
                
        self.drive(40)
        self.day_time +=1
        self.car_not_ready_day = 0 
    elif self.day_time == 24:
        self.day_time = 0 

    return elec_cost


            
  def charge_SC2(self, action, price):  
    
    charge_power = 3
    
    if action == 'C':
        old_battery_kWh = self.battery_kWh
        self.battery_kWh += charge_power
        
        #make sure we dont overcharge battery
        if self.battery_kWh >= self.battery_capacity:
            self.battery_kWh = self.battery_capacity
            self.battery_level = 1
            elec_cost = (self.battery_capacity - old_battery_kWh) * price
            self.cost_per_day += elec_cost
        else:    
            self.battery_level = self.battery_kWh / self.battery_capacity
            elec_cost = price * charge_power #unit = $    
            self.cost_per_day += elec_cost
        
    elif action == 'D':
        self.battery_level = self.battery_kWh / self.battery_capacity
        if self.battery_level >=self.min_charge :
            elec_cost = 0
        #put a negative time when do nothing when battery level is low
        else:
            elec_cost = 0
       
    elif action == 'S':
        self.battery_kWh -= charge_power
        self.battery_level = self.battery_kWh / self.battery_capacity
        
        #assign negative reward to selling when battery is 0
        if self.battery_level < 0: 
            elec_cost = -1
            self.battery_kWh = 0
            self.battery_level = 0 #set to zero make sure battery level is not negative
        #selling battery under normal condition 
        else: 
            elec_cost = -price * charge_power 
            self.cost_per_day += elec_cost
            
    self.day_time += 1 
    

    if self.day_time == 8:
        if self.battery_kWh <= self.min_charge: 
            elec_cost = -60 
            self.car_not_ready +=1
            self.car_not_ready_day = 1
        self.drive(40) 
        self.day_time +=1
        
    elif self.day_time == 17:
        if self.battery_kWh <=self.min_charge: 
            elec_cost = -60
            if  self.car_not_ready_day == 0:
                self.car_not_ready += 1
        self.drive(40)
        self.day_time +=1
        self.car_not_ready_day = 0 
    
    
    if self.day_time == 24:
        self.day_time = 0 
        
    
    return elec_cost


  def charge_SC3(self, action, price):  
    
    charge_power = 3
    
    if action == 'C':
        old_battery_kWh = self.battery_kWh
        self.battery_kWh += charge_power
        
        #make sure we dont overcharge battery
        if self.battery_kWh >= self.battery_capacity:
            self.battery_kWh = self.battery_capacity
            self.battery_level = 1
            elec_cost = (self.battery_capacity - old_battery_kWh) * price
            self.cost_per_day += elec_cost
        else:    
            self.battery_level = self.battery_kWh / self.battery_capacity
            elec_cost = price * charge_power #unit = $    
            self.cost_per_day += elec_cost
       
    elif action == 'S':
        self.battery_kWh -= charge_power
        self.battery_level = self.battery_kWh / self.battery_capacity
        
        #assign negative reward to selling when battery is 0
        if self.battery_level < 0: 
            elec_cost = -1
            self.battery_kWh = 0
            self.battery_level = 0 #set to zero make sure battery level is not negative   
        #selling battery under normal condition 
        else: 
            elec_cost = -price * charge_power 
            self.cost_per_day += elec_cost

    self.day_time += 1 
    
    if self.day_time == 8:
        if self.battery_kWh <= self.min_charge: 
            elec_cost = -60 
            self.car_not_ready +=1
            self.car_not_ready_day = 1
        self.drive(40) 
        self.day_time +=1
        
    elif self.day_time == 17:
        if self.battery_kWh <=self.min_charge: 
            elec_cost = -60
            if  self.car_not_ready_day == 0:
                self.car_not_ready += 1
        self.drive(40)
        self.day_time +=1
        self.car_not_ready_day = 0 
    
    
    if self.day_time == 24:
        self.day_time = 0 
        
    
    return elec_cost

    
     
     
  def all_states(self):
      return set(self.actions.keys())  
            


def scenario_SC1():
    
  '''scenario 1, 
     1) 30 kWh battery, 
     2) we can charge at home and at work 
     3) charger (3 kW) = 0.1 battery level per 1 hour charge
     4) electricity price: peak (7 am - 10 am & 17 - 21) 
     5) must have > 30% battery at 8 am and 5 pm
     6) drives 40 km to work which requires 6 kWh which is 20% of battery life
     7) states = (day_time , battery_level)
     8) battery is reset at day_time == 0
     9) penalty of car not ready = -60 since taxi 40 km is about 60 euros
  '''
  
  ev = EV(30, 0, 0, 9) 
  states = []
  for i in range(0,24):
      for j in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
          states.append((i,j))        
      
  actions = {}
  for i in states:
      actions[i] = ('C', 'D')
          

  ev.set(actions)  
  return ev



def scenario_SC2():
  
  '''scenario 2
     1) senario 1
        +
     2) action = buy, sell, charge
     3) sell at same electricy price (peak or off peak)
  '''
  ev = EV(30, 0, 0, 9) 
  states = []
  for i in range(0,24):
      for j in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
          states.append((i,j))        
          
  actions = {}
  for i in states:
      if i[1] ==0:
          actions[i] = ('C', 'D')
      elif i[1] == 1:
          actions[i] = ('D', 'S')
      else:    
          actions[i] = ('C', 'D', 'S')
         
  ev.set(actions)  
  return ev    


def scenario_SC3():
      
  '''scenario 2
     1) senario 1
        +
     2) action = buy, sell, charge
     3) sell at same electricy price (peak or off peak)
  '''
  ev = EV(30, 0, 0, 9) 
  states = []
  for i in range(0,24):
      for j in [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]:
          states.append((i,j))        
          
  actions = {}
  for i in states:    
      actions[i] = ('C', 'S')
         
  ev.set(actions)  
  return ev  

    
