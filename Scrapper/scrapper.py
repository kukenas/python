#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Nov 20 20:49:20 2020

Scraping data genererated by Mastercard Currency Converter Calculator

@author: Aurimas

"""

import re
import random
import time
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

class scrapper(object):
    
    ADDITIONAL_TIME = 0.5
    
    def __init__(self, drivers, delay, randomInitial, randomFinal, 
                 amount, fee, base_currency):
        self.browser = self.get_browser(drivers)
        self.delay = delay
        self.randomInitial = randomInitial
        self.randomFinal = randomFinal
        self.amount = amount
        self.fee = fee
        self.base_currency = base_currency
    
    def get_browser(self,drivers):
        
        try:
        
            if (drivers.lower() == "safari"):
                return webdriver.Safari()
            if (drivers.lower() == "chrome"):
                return webdriver.Chrome()
            if (drivers.lower == "firefox"):
                return webdriver.Firefox()
            
        except Exception:
            print ("Not able to select drivers!")

    
    # Call once to accept all cookies
    def acceptCookies(self):
        
        # Accept All Cookies:
        WebDriverWait(self.browser, self.delay).until(
            EC.element_to_be_clickable(
                (By.XPATH,"//*[@id='onetrust-accept-btn-handler']"))).click()
        
        time.sleep(random.uniform(self.randomInitial+self.ADDITIONAL_TIME,
                                  self.randomFinal+self.ADDITIONAL_TIME))
    
    # Call multiple times to cover all the elements in $currencies
    def selectCurrency(self,curr,id1,id2):
        
        # Open the list of available currencies
        WebDriverWait(self.browser, self.delay).until(
        EC.element_to_be_clickable(
            (By.XPATH,"//*[@id="+"'"+str(id1)+"'"+"]"))).send_keys(Keys.RETURN)
        
        time.sleep(random.uniform(self.randomInitial,self.randomFinal))
        
        # Parent element:
        parent_element = WebDriverWait(self.browser, self.delay).until(
            EC.presence_of_element_located( (By.XPATH, "//li[@id=" + "'" + id2 + "'" + "]")))
        
        # Collect available items presented to a user
        child_elements = parent_element.find_element_by_class_name(
                "dropdown-menu").find_elements_by_class_name("ng-binding")
        
        # Looping through all the items
        for item in child_elements:
            # Must split the string to be able to rely on currency ticker
            if str(curr) in item.text.split("-")[1].strip():
                # Selecting currency matching the one passed as a parameter:
                item.send_keys(Keys.RETURN)
                # Stop looping!
                break
        
        time.sleep(random.uniform(self.randomInitial, self.randomFinal))
        
    # Called only from selectYearMonthDay
    def scrape(self, curr, dataset):
        
        # Wait until element is clickable
        if WebDriverWait(self.browser, self.delay).until(
                    EC.element_to_be_clickable(
                (By.XPATH,'//td[@data-handler="selectDay"]'))):
        
            # Retrieving available days
            selectDays = self.browser.find_elements_by_xpath('//td[@data-handler="selectDay"]')
        
        # Proceed if that's not the case
        if not (not selectDays):
            # Select every single day in a month
            for selectedDay in range(len(selectDays)):
                
                # Selecting i-th item from the list
                self.browser.find_elements_by_xpath('//td[@data-handler="selectDay"]')[selectedDay].click()
                # Clicking anywhere on the main container:
                WebDriverWait(self.browser, self.delay).until(
                        EC.element_to_be_clickable((By.XPATH,"//div[@id='zermattCtrl']"))).click()
                
                # encapsulating with sleeps to make sure data is available
                time.sleep(random.uniform(self.randomInitial + (self.ADDITIONAL_TIME*3), 
                                          self.randomFinal + (self.ADDITIONAL_TIME*3)))
                
                # Scraping a rate presented to a user
                rate = self.getRate(selectedDay+1)
                
                # Date is used as an index. Must be unique values:
                if self.getCurrentDate().strftime('%Y-%m-%d') not in dataset.get("Date"):
                    dataset["Date"].append(self.getCurrentDate().strftime('%Y-%m-%d'))
                
                # Adding items to a dictionary
                dataset[curr].append(rate)
                
                # print ("Date: " + self.getCurrentDate().strftime('%Y-%m-%d') + " Currency: " + curr + " Rate: " + rate)
                
                # Preparing for the upcoming cycle
                WebDriverWait(self.browser, self.delay).until(EC.element_to_be_clickable((By.ID,'getDate'))).click()
                
                # Additional wait time
                time.sleep(random.uniform(self.randomInitial+self.ADDITIONAL_TIME, 
                                          self.randomFinal+self.ADDITIONAL_TIME))
            
            try:
               
                # Select "Next", if present
                WebDriverWait(self.browser, self.delay).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, "//a[@class='ui-datepicker-next ui-corner-all']/span[text()='Next']"))).click()   
                
                # Calling recursively
                self.scrape(curr, dataset)
            
            except Exception:
                # Clicking anywhere on the main container:
                self.browser.find_element_by_xpath("//div[@id='zermattCtrl']").click()
                return
        
    # Undetectable behavior
    def typeAmount(self,id1,amount):
        
        # Field
        elem = WebDriverWait(self.browser, self.delay).until(
            EC.presence_of_element_located((By.ID,id1)))
    
        # Amount to be type:
        text = str(amount)
        # Split into characters:
        for ch in text:
            actions = ActionChains(self.browser)
            # Additional precautiousness:
            if elem.is_displayed():
                # Selecting a field
                actions.click(elem)
                # Typing a character:
                actions.send_keys(ch)
                
                actions.perform()
                # Sleep for random time
                time.sleep(random.uniform(self.ADDITIONAL_TIME/2.0 , self.ADDITIONAL_TIME))
                
    # Scrapping reloaded rate
    def getRate (self,count):
        
        ordinal_number = self.make_ordinal(count)
        
        # Loaded date for additional check
        date = WebDriverWait(
            self.browser, self.delay).until(
                EC.element_to_be_clickable(
                    (By.XPATH,"//div[@class='p-zero dxp-col-md-12 dxp-col-12 selected-currency-rate ng-binding']/span[@class='ng-binding']")))
        
        # Target element
        element = WebDriverWait(
            self.browser, self.delay).until(
                EC.element_to_be_clickable(
                    (By.XPATH,"//div[@class='p-zero dxp-col-md-12 dxp-col-12 rateView one-currency-amount ng-binding']")))
           
        alldigits = re.sub("\D", "", date.text.split()[1])
        
        if WebDriverWait(self.browser, self.delay).until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, "//div[@class='p-zero dxp-col-md-12 dxp-col-12 selected-currency-rate ng-binding']/span[@class='ng-binding']"), 
                    ordinal_number)):
            
            if count == int(alldigits):
            
                # Target element as a text
                string = element.text
                # Format & take a float value
                frmtRate = re.findall("[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?", string)[1]
                #to scroll try use the following command
            
                # Encapsulating with sleeps to make sure data is available
                time.sleep(random.uniform(self.randomInitial, self.randomFinal))
            
                return frmtRate
            else:
                print ("Error occured! Rate hasn't been loaded yet!")
    
    def goToStartMonth(self, startMonth):
        
        # Opening the calendar:
        WebDriverWait(self.browser, self.delay).until(
             EC.element_to_be_clickable((By.ID,"getDate"))).click()
        
        time.sleep(random.uniform(self.randomInitial,self.randomFinal))
        
        # While condition is satisfied:
        while ( WebDriverWait(self.browser, self.delay).until(EC.presence_of_element_located(
                 (By.XPATH, "//select[@class='ui-datepicker-month']/option[@selected='selected']"))).text !=  startMonth):
            # Go back one month back:
            WebDriverWait(self.browser, self.delay).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//a[@class='ui-datepicker-prev ui-corner-all']/span[text()='Prev']"))).click()
            
            time.sleep(random.uniform(self.randomInitial, self.randomFinal))
        
        # If above condition is not satisfied, sleep,
        # so the next procedure could be safely performed
        time.sleep(random.uniform(self.randomInitial, self.randomFinal))
    
    # Currently selected date found with the assistance of this function:
    def getCurrentDate(self):
        
        # Current month:
        month = WebDriverWait(self.browser, self.delay).until(
             EC.presence_of_element_located(
                 (By.XPATH,'//select[@class="ui-datepicker-month"]/option[@selected="selected"]'))).text
        
        # Current year:
        year = WebDriverWait(self.browser, self.delay).until(
             EC.presence_of_element_located(
                 (By.XPATH,'//select[@class="ui-datepicker-year"]/option[@selected="selected"]'))).text
        # Current day:  
        current_day = WebDriverWait(self.browser, self.delay).until(
             EC.presence_of_element_located(
                 (By.CLASS_NAME,"ui-datepicker-current-day"))).text
    
        # Converting month name to a number
        month_number = time.strptime(month, '%B').tm_mon
        # Date as a String
        date_string = str(year)+"-"+str(month_number)+"-"+str(current_day)
        # Converting to datetime object:
        date_time_obj = datetime.strptime(date_string, '%Y-%m-%d')
        
        return date_time_obj.date()
    
    # Initializing static settings
    def initialize(self):
        
        # Accept Cookies:
        self.acceptCookies()
    
        # To (Currency)/ base currency:
        self.selectCurrency(self.base_currency,"cardCurrency","mczRowD")
    
        # Amount field:
        self.typeAmount ("txtTAmt", self.amount)
    
        # Bank Fee (%) field:
        self.typeAmount("BankFee", self.fee)
    
    # Convert to ordinal numbers:
    def make_ordinal(self,number):
        
        # Takes the lowest one along with its index
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(number % 10, 4)]
        
        if 11 <= (number % 100) <= 13:
            suffix = 'th'
       
        return str(number) + suffix
        
    def start(self, uri, currencies, startMonth):
        
        df_columns = df_columns = ["Date"]  + currencies
        
        dataset = dict (zip ( df_columns, [ [] for _ in range(len(df_columns)) ]))
        
        # Maximizing the opened window
        self.browser.maximize_window()
        
        self.browser.get(uri)
        
        # Sleep for 1s - 1.5s
        time.sleep(random.uniform(self.randomInitial, self.randomFinal))
        
        # Default configuration
        self.initialize()
        
        for curr in currencies:
            
            # From (Currency):
            self.selectCurrency(curr,"tCurrency","mczRowC")
            
            time.sleep(random.uniform(self.randomInitial, self.randomFinal))
            
            # Go to the very beginning
            # Depents on field startMonth
            self.goToStartMonth(startMonth)
            
            #Iterate through the calendar
            self.scrape(curr, dataset)
        
        '''Initiating DataFrame with pre-set column names'''
        df = pd.DataFrame(dataset, columns = df_columns)
        
        df.set_index('Date', inplace=True)
        
        df.to_csv('mastercard_currencies.csv')
        
        print ("Task has been completed!")
        
        self.browser.quit()