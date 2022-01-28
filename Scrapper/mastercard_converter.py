#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 01:39:49 2020

@author: kukenas
"""

import scrapper

#Currencies in scope
currencies = ["EUR","USD","NOK","DKK","GBP","PLN","THB","HKD","AED","AUD"]


#Months in scope
months = ["February","March","April","May","June","July",
          "August","September","October","November"]

startMonth = months[0]

# Years in scope
years = [2020]

# makes the browser wait if it can't find an element
delay = 5 # seconds

# The mimimum delay time
randomInitial = 1
# The maximum delay time
randomFinal = 1.5

# Against SEK
base_currency = "SEK"
# Hard-coded value
amount = 10000
# Hard-coded value. Not that relevant in this case
fee = 0

# Works with Safari, Chrome, Firefox browsers
# Experimental features must be enabled, in some cases!

drivers = "Safari"

uri = "https://www.mastercard.us/en-us/personal/get-support/convert-currency.html"

scrapper_init = scrapper.scrapper(drivers, delay, randomInitial, randomFinal, 
                          amount, fee, base_currency)

scrapper_init.start(uri, currencies, startMonth)