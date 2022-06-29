
from email import header
from tkinter import Button
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
import requests,json
import time

driver = webdriver.Chrome()
driver.get('http://auth.jianke-inc.com/login?redirect=https%3A%2F%2Fissue-tracking.jianke-inc.com%2FissueSystem%2Fall%3F%26token%3D72ac2f62-2e34-431d-bfe1-285014c4a03e&token=72ac2f62-2e34-431d-bfe1-285014c4a03e&type=logout')
driver.maximize_window()
WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'userName')))
driver.find_element_by_xpath('//*[@id="userName"]').send_keys('taosen')
driver.find_element_by_xpath('//*[@id="password"]').send_keys('QWEasdzxc123')
driver.find_element_by_xpath('//*[@id="root"]/div[2]/div/div/div/div/form/div[3]/div/div/span/button').click()
time.sleep(3)
# token = driver.execute_script('return window.localStorage.getItem("tokenInfo");')
driver.get('https://issue-tracking.jianke-inc.com/issueSystem/all?&token=b37f1c08-1a1f-4014-96d8-52bed2ebb58b')
driver.find_element_by_xpath('//*[@id="catalogId"]').click()
                              
driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/div/div[2]/div/div/div[1]/span[2]').click()
driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/form/div[1]/div[3]/div/div[2]/div/div/div/div[1]/input').send_keys('2021-01-01 00:00:00')
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[2]/ul/li/button').click()
driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/form/div[1]/div[3]/div/div[2]/div/div/div/div[3]/input').send_keys('2022-01-01 00:00:00')
driver.find_element_by_xpath('/html/body/div[3]/div/div/div/div[2]/div[2]/ul/li/button').click()
driver.find_element_by_xpath('//*[@id="status"]').click()
driver.find_element_by_xpath('/html/body/div[4]/div/div/div/div[2]/div/div/div[3]').click()
# driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/form/div[2]/div[5]/div/div/div/div/button[1]').click()
# tbody = driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody')
time.sleep(5)
for i in range(2,12):
  print(i)
  driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody/tr['+ str(i)+']/td[3]/span/span/a').click()
  WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div/div/div[2]/div/div[1]/div[2]')))
  verifyElement = driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[2]/div/div[1]')
  year = driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody/tr['+str(i)+']/td[10]').text[0:4]
  number = driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody/tr['+str(i)+']/td[2]').text
  verifyImg = verifyElement.screenshot(str(year)+ "完成"+'/' + number +'.png')

while(True):
  # button= driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/ul/li[9]/a')
  button= driver.find_element_by_class_name('ant-pagination-next')
  driver.execute_script('arguments[0].click();',button)
  WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]')))
  time.sleep(5)
  for i in range(2,12):
    driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody/tr['+ str(i)+']/td[3]/span/span/a').click()
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[5]/div/div/div/div/div[2]/div/div[1]/div[2]')))
    verifyElement = driver.find_element_by_xpath('/html/body/div[5]/div/div/div/div/div[2]/div/div[1]')
    year = driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody/tr['+str(i)+']/td[10]').text[0:4]
    number = driver.find_element_by_xpath('//*[@id="root"]/div/section/section/div/main/div/div/div/div/div[2]/div/div/div/div/div/div[2]/table/tbody/tr['+str(i)+']/td[2]').text
    verifyImg = verifyElement.screenshot(str(year)+ "完成"+'/' + number +'.png')
# for year in range(2021, 2022):
#   url ='https://issue-tracking.jianke-inc.com/issue-track/tickets/all/handles?page=1&size=500&workHourStart=0&catalogId=5ee1f3e686224300575d6869&startDate='+str(year)+'-01-01%2000%3A00%3A00&endDate='+str(year+1)+'-01-01%2000%3A00%3A00'

#   token = driver.execute_script('return window.localStorage.getItem("tokenInfo");')
#   print(token)
#   tokenjson=json.loads(token)
#   tokenl = tokenjson['token']['access_token']
#   headers = {'Authorization': 'Bearer '+ tokenl}
#   print(headers)
#   res = requests.get(url, headers = headers)
#   content = res.content.decode('utf-8')
#   result = json.loads(content)
#   print(result)
#   dataList= result['data']['dataList']
#   for d in dataList:
#     driver.get('https://issue-tracking.jianke-inc.com/issueSystem/myHandle?ticketId='+ d['id'])
#     WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'root')))
#     time.sleep(2)
#     verifyElement = driver.find_element_by_id('root')
#     verifyImg = verifyElement.screenshot(str(year)+ '/' + d['id']+'.png')