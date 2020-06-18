'''
Created on Jun 16, 2020

@author: micha
'''

import selenium
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException

driver = webdriver.Chrome()
driver.get('https://finance.yahoo.com/quote/INTC/key-statistics/')

element = driver.find_element_by_xpath('//*[@id="Col1-0-KeyStatistics-Proxy"]//section/div[3]/div[2]/div/div[2]/div/div/table/tbody/tr[4]/td[2]')
float = element.text
print(float)
