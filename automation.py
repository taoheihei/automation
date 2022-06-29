from cgitb import handler
from math import fabs
from multiprocessing import Value
from os import access
import time
from requests import request
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import pandas as pd
import ddddocr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
import numpy as np
from sqlalchemy import false, true
import queue
import json

driver = webdriver.Chrome()
driver.maximize_window()
ourPhoneList= ['18620263644','18680556344']
queue = queue.Queue()
queue.put('18102274068')
queue.put('13238387927')
# queue.put('18550109050')
year='2021'
zipCode='510000'
signColumn ='是否申报'
excelName='report.xlsx'
gudongDate= '2050-07-01'

def getVerifyCodeAndSubmit(verifyElement: WebElement, inputElement: WebElement, butnElement: WebElement, errorMsg, isDetail):
  verifyImg = verifyElement.screenshot('verify.png')
  ocr=ddddocr.DdddOcr()
  with open('verify.png', 'rb') as f:
    img_bytes = f.read()
  code = ocr.classification(img_bytes)
  # code.replace('o','0')
  inputElement.clear()
  inputElement.send_keys(str(code))
  time.sleep(1)
  butnElement.click()
  WebDriverWait(driver, 60).until(EC.alert_is_present())
  time.sleep(1)
  alert = driver.switch_to.alert
  if(alert.text == errorMsg):
    alert.accept()
    time.sleep(1)
    if(isDetail):
      verifyElement.click()
    time.sleep(1)
    getVerifyCodeAndSubmit(verifyElement, inputElement, butnElement, errorMsg, isDetail )
  elif alert.text == "企业为注销或吊销状态！":
    alert.accept()
    return False
  elif alert.text != "信息修改成功":
    alert.accept()
    return False
  else:
    alert.accept()

def isExistElement(by, ele):
  try:
    driver.find_element(by, ele)
  except Exception as e:
    return False
  return True

def isAlertPersent():
  try:
    driver.switch_to.alert
    return True
  except Exception as e:
    return False


def dataRecord(reports):
  # pd.set_option('display.float_format',lambda x : '%.3f' % x)
  try:
    reports['注册证号']=reports['注册证号'].astype(str)
    reports['联络员电话']=reports['联络员电话'].astype(str)
    reports['法定代表人身份证']= reports['法定代表人身份证'].astype(str)
    reports['联络员身份证']= reports['联络员身份证'].astype(str)
  except Exception as e:
    print(e)
  with pd.ExcelWriter(excelName) as writer:
    reports.to_excel(writer,index = False, header= True)
def init():
  np.set_printoptions(formatter={'all': lambda x: str(x)})
  np.set_printoptions(suppress=True)
  reports = pd.read_excel(excelName, dtype=str)
  row=0
  for data in reports.values:
    try:
      youxian =False
      if(reports.at[row, signColumn] =='已申报' or reports.at[row, signColumn] =='完成申报' or  reports.at[row, signColumn] =='联络员修改失败'):
        row=row+1
        continue
      print(reports.at[row, '企业名称'])
      if("有限公司" in reports.at[row, '企业名称'] or "有限责任公司" in reports.at[row, '企业名称']):
        youxian =True
      isNew = False
      res = requests.post('http://cnpn.gzaic.gov.cn:9080/aiceps/initLiaisonsLoginInput.html?&regNo='+data[1])
      
      content = res.content.decode('utf-8')
      isOurPhone = False
      if content == "\"联络人不存在，请重新输入\"":
        isNew = True

      if isNew:
        #registry
        driver.get('http://cnpn.gzaic.gov.cn:9080/aiceps/record/registUser.html')
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'RecordForm')))
        driver.find_element_by_xpath('//*[@id="regNo"]').send_keys(str(data[1]))
        driver.find_element_by_xpath('//*[@id="leRep"]').send_keys(str(data[3]))
        driver.find_element_by_xpath('//*[@id="certId"]').send_keys(str(data[5]))
        driver.find_element_by_xpath('//*[@id="liaName"]').send_keys(str(data[4]))
        dropdown = Select(driver.find_element_by_id('cerIdType'))
        dropdown.select_by_value('中华人民共和国居民身份证')
        driver.find_element_by_xpath('//*[@id="liaCertId"]').send_keys(str(data[5]))
        phonecall=queue.get()
        queue.put(phonecall)
        driver.find_element_by_xpath('//*[@id="mobileTel"]').send_keys(phonecall)
        verifyElement = driver.find_element_by_id('vimg')
        inputElement = driver.find_element_by_id('verifyCode')
        btnElement = driver.find_element_by_id('subBtn')
        issuccess = getVerifyCodeAndSubmit(verifyElement, inputElement, btnElement, '验证码有误,请重新输入！',False )
        if(issuccess==False):
          time.sleep(1)
          reports.loc[row, signColumn] = '联络员修改失败'
          dataRecord(reports)
          row=row+1
          continue
      else :
        # change
        driver.get('http://cnpn.gzaic.gov.cn:9080/aiceps/record/initResetLiaison.html');
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'login_3')))
        
        time.sleep(1)
        driver.find_element_by_id('regNo').send_keys(str(data[1]))
        driver.find_element_by_id('div2').click()
        timewait = 0
        while driver.execute_script('return $("#shieldTraName").val();')=='':
          timewait= timewait +1
          if timewait>= 60 :
              reports.loc[row, signColumn] = '申报失败'
              dataRecord(reports)
              row=row+1
              continue

        driver.find_element_by_id('leRep').send_keys(str(data[3]))
        driver.find_element_by_id('certId').send_keys(str(data[5]))
        driver.find_element_by_id('liaName_xin').send_keys(str(data[6]))
        dropdown = Select(driver.find_element_by_id('cerIdType_xin'))
        dropdown.select_by_value('中华人民共和国居民身份证')
        driver.find_element_by_id('liaCertId_xin').send_keys(str(data[7]))
        phoneCall = queue.get()
        queue.put(phoneCall)
        driver.find_element_by_id('mobileTel_xin').send_keys(str(phoneCall))
        # verifyElement = driver.find_element_by_id('vimg')
        inputElement = driver.find_element_by_id('verifyCode')
        btnElement = driver.find_element_by_id('subBtn')
        # issuccess = getVerifyCodeAndSubmit(verifyElement, inputElement, btnElement, '验证码有误,请重新输入！',False )
        driver.find_element_by_xpath('//*[@id="butn"]').click()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
        #等短信2分钟获取不到自动失败
        changeWaitTime = 0
        isChangeContinue = False
        changemsgCount=len(open('phoneCode.txt').readlines())
        while(len(open('phoneCode.txt').readlines())==changemsgCount):
          time.sleep(1)
          changeWaitTime=changeWaitTime+1
          if(changeWaitTime>60):
            isChangeContinue = True
            break
        else:
          with open('phoneCode.txt', 'r') as f:  #打开文件
            last_line = f.readlines()[-1] #读取所有行
          inputElement.send_keys(str(last_line))
        if(isChangeContinue):
          reports.loc[row, signColumn] = '申报失败'
          dataRecord(reports)
          row=row+1
          continue
        btnElement.click()
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        driver.switch_to.alert.accept()
      # login
      driver.get('http://cnpn.gzaic.gov.cn:9080/aiceps/liaisonsLogin.html')
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'dzpinss')))
      time.sleep(1)
      driver.find_element_by_id('divClose').click()
      msgCount=len(open('phoneCode.txt').readlines())
      driver.find_element_by_id('regNo').send_keys(str(data[1]))
      # /html/body/div[2]/div[3]/form/div/div[6]/div[4]/div[6]/div[2]/a
      driver.find_element_by_xpath('//*[@id="ptvcode"]').click()
      time.sleep(1)
      timewait = 0
      while driver.execute_script('return $("#shieldlLiaName").val();') == '':
        time.sleep(1)
        timewait= timewait +1
        if timewait> 60 :
          reports.loc[row, signColumn] = '申报失败'
          dataRecord(reports)
          row=row+1
          continue
      driver.find_element_by_xpath('//*[@id="ptvcode"]/div/a').click()
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'vimgs')))
      time.sleep(1)
      verifyE2lement = driver.find_element_by_id('vimgs')
      input2Element = driver.find_element_by_id('verifyCode')
      btn2Element = driver.find_element_by_xpath('//*[@id="woaicss_con1"]/div[2]/a')

      getVerifyCodeAndSubmit(verifyE2lement, input2Element, btn2Element ,'验证码输入错误',True)
      #等短信2分钟获取不到自动失败
      waitTime = 0
      isContinue = False
      while(len(open('phoneCode.txt').readlines())==msgCount):
        time.sleep(1)
        waitTime=waitTime+1
        if(waitTime>60):
          isContinue = True
          break
      else:
        with open('phoneCode.txt', 'r') as f:  #打开文件
          last_line = f.readlines()[-1] #读取所有行
        driver.find_element_by_id('vcode').send_keys(str(last_line))
      if(isContinue):
        reports.loc[row, signColumn] = '申报失败'
        dataRecord(reports)
        row=row+1
        continue
      time.sleep(1)
      driver.find_element_by_xpath('//*[@id="ptDiv"]/a[1]').click()
      time.sleep(1)
      if(isAlertPersent() and driver.switch_to.alert.text == "该企业为注销状态"):
        time.sleep(1)
        reports.loc[row, signColumn] = '已注销'
        dataRecord(reports)
        row=row+1
        continue

      #myTask
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'table_2')))
      time.sleep(1)
      #查看是否有年报记录
      yearRecordxpath ='/html/body/div[1]/div[1]/div[3]/div/table/tbody/tr[5]/td[2]'
      if(isExistElement(By.XPATH, yearRecordxpath) and str.strip(driver.find_element_by_xpath(yearRecordxpath).text)==year+'年年度报告'):
        reports.loc[row, signColumn] = '已申报'
        dataRecord(reports)
        row=row+1
        continue

      driver.find_element_by_xpath('//*[@id="table_2"]/tbody/tr[2]/td/ul/li[1]/a ').click()
      yearSelect = Select(driver.find_element_by_id('reportYear'))
      yearSelect.select_by_index(1)
      # yearSelect.select_by_value(year)
      driver.find_element_by_xpath('//*[@id="woaicss_con1"]/div[2]/a').click()
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'noticeIframe')))
      driver.switch_to.frame('noticeIframe')
      driver.find_element_by_id('flag').click()
      driver.find_element_by_id('closeB').click()

      #reportonline 企业基本信息
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.CLASS_NAME, 'qiye-biaoge')))
      time.sleep(1)
      # for ele in driver.find_element_by_tag_name('input'):
      #   ele.clear()
      driver.find_element_by_id('entAddress').clear()
      driver.find_element_by_id('entZip').clear()
      driver.find_element_by_id('entPhone').clear()
      driver.find_element_by_id('entEmail').clear()
      driver.find_element_by_id('mainBusiact').clear()
      driver.find_element_by_id('empNumber').clear()
      driver.find_element_by_id('womEmpNum').clear()
      try:
        driver.find_element_by_id('colGraNum').clear()
        driver.find_element_by_id('graduatesNum').clear()
        driver.find_element_by_id('retSolNum').clear()
        driver.find_element_by_id('soldiersNum').clear()
        driver.find_element_by_id('disPerNum').clear()
        driver.find_element_by_id('disabilityNum').clear()
        driver.find_element_by_id('uneNum').clear()
        driver.find_element_by_id('unemploymentNum').clear()
      except Exception as e:
        print(0)
      #set
      driver.find_element_by_id('entAddress').send_keys(str(data[9]))
      driver.find_element_by_id('entZip').send_keys(str(zipCode))
      if data[8] == "" or data[8]=="nan" or data[8] ==np.nan :
        data[8] = "13600000000"
      driver.find_element_by_id('entPhone').send_keys(str(data[8]))
      driver.find_element_by_id('entEmail').send_keys(str(str(data[8])+'@qq.com'))
      driver.find_element_by_id('mainBusiact').send_keys(str(1))
      driver.find_element_by_id('empNumber').send_keys(str(1))
      driver.find_element_by_id('empnumberisshow2').click()
      driver.find_element_by_id('womEmpNum').send_keys(str(0))
      kongGuSelect = Select(driver.find_element_by_id('holdingsMsg'))
      kongGuSelect.select_by_value('3')
      # driver.find_element_by_xpath('//*[@id="individualReportForm"]/div[1]/table[1]/tbody/tr[6]/td[2]/input[3]').click()
      # driver.find_element_by_xpath('//*[@id="individualReportForm"]/div[1]/table[1]/tbody/tr[6]/td[4]/input[3]').click()
      # driver.find_element_by_xpath('//*[@id="individualReportForm"]/div[1]/table[1]/tbody/tr[7]/td[4]/input[2]').click()
      # driver.find_element_by_xpath('//*[@id="individualReportForm"]/div[1]/table[1]/tbody/tr[8]/td[2]/input[3]').click()
      # driver.find_element_by_xpath('//*[@id="individualReportForm"]/div[1]/table[1]/tbody/tr[8]/td[4]/input[3]').click()
      # 从业 女性从业 企业控股
      driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(6) > td:nth-child(2) > input[type=radio]:nth-child(4)').click()
      driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(6) > td:nth-child(4) > input[type=radio]:nth-child(4)').click()
      driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(7) > td:nth-child(4) > input[type=radio]:nth-child(4)').click()
      #对外担保  网站或网店  股东股权转让  购买其他公司股权
      try:
        driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(8) > td:nth-child(2) > input[type=radio]:nth-child(4)').click()
        driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(8) > td:nth-child(4) > input[type=radio]:nth-child(4)').click()
        driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(9) > td:nth-child(2) > input[type=radio]:nth-child(4)').click()
        driver.find_element_by_css_selector('div.qiye-biaoge table > tbody > tr:nth-child(9) > td:nth-child(4) > input[type=radio]:nth-child(4)').click()
        # if(youxian):
        #   driver.find_element_by_xpath('//*[@id="individualReportForm"]/div[1]/table[1]/tbody/tr[9]/td[4]/input[3]').click()
      except Exception as e:
        print(0)
      try:
        driver.find_element_by_id('colGraNum').send_keys(str(0))
        driver.find_element_by_id('graduatesNum').send_keys(str(0))
        driver.find_element_by_id('retSolNum').send_keys(str(0))
        driver.find_element_by_id('soldiersNum').send_keys(str(0))
        driver.find_element_by_id('disPerNum').send_keys(str(0))
        driver.find_element_by_id('disabilityNum').send_keys(str(0))
        driver.find_element_by_id('uneNum').send_keys(str(0))
        driver.find_element_by_id('unemploymentNum').send_keys(str(0))
      except Exception as e:
        print(0)
      driver.find_element_by_css_selector('div.table-bottom > input[type=button]:nth-child(1)').click()
      WebDriverWait(driver, 60).until(EC.alert_is_present())
      time.sleep(1)
      driver.switch_to.alert.accept()
      

      #pageLeap
      #特种设备
      try:
        WebDriverWait(driver, 5).until(EC.alert_is_present())
        time.sleep(1)
        driver.switch_to.alert.accept()
        time.sleep(1)
      except Exception as e:
        print(0)
      try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'SpeEquipmentSaveNormal')))
        time.sleep(1)
        #clear
        driver.find_element_by_id('SPEEQUIPMENTUSAGE').clear()
        driver.find_element_by_id('SPEEQUIPMENTVALID').clear()
        #set
        driver.find_element_by_id('SPEEQUIPMENTUSAGE').send_keys(str(0))
        driver.find_element_by_id('SPEEQUIPMENTVALID').send_keys(str(0))
        driver.find_element_by_id('SpeEquipmentSaveNormal').click()
      except Exception as e:
        print(0)
      # 股东
      print(youxian)
      if(youxian):
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'infoDivCzqk')))
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="infoDivCzqk"]/div[3]/input[2]').click()
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'iframeCzqk')))
        time.sleep(1)
        driver.switch_to.frame('iframeCzqk')
        driver.find_element_by_xpath('//*[@id="userName"]').send_keys(str(data[3]))
        driver.find_element_by_xpath('//*[@id="capShould"]').send_keys(str(0))
        driver.find_element_by_xpath('//*[@id="capShouldDate"]').send_keys(str(gudongDate))
        driver.find_element_by_xpath('//*[@id="capShouldType_C"]').click()
        driver.find_element_by_xpath('//*[@id="capReal"]').send_keys(str(0))
        driver.find_element_by_xpath('//*[@id="capDate"]').send_keys(str(gudongDate))
        driver.find_element_by_xpath('//*[@id="capType_C"]').click()
        driver.find_element_by_xpath('//*[@id="czid"]').click()
        time.sleep(1)
        driver.switch_to.default_content()
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'table_2')))
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="infoDivCzqk"]/div[3]/input[3]').click()
        
      #网站和网店信息
      
      # driver.find_element_by_xpath('/html/body/div[1]/div/div[5]/div[2]/div[3]/input[1]').click()
      # WebDriverWait(driver, 60).until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'editIframeWljy')))
      # driver.find_element_by_id('SpeEquipmentSaveNormal').click()
      WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'table_1')))
      time.sleep(1)
      driver.find_element_by_xpath('//*[@id="wljy"]/div[3]/input[2]').click()

      
      if(youxian):
        # 股东变更
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'infoDiv')))
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="infoDiv"]/div[3]/input[2]').click()

        # 对外投资
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'infoDivDwtz')))
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="infoDivDwtz"]/div[3]/input[2]').click()
        
      #资产状况
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'zcform')))
      time.sleep(1)
      #clear
      driver.find_element_by_id('assetsTotalAmount').clear()
      driver.find_element_by_id('equityAmount').clear()
      driver.find_element_by_id('salesAmount').clear()
      driver.find_element_by_id('businessAmount').clear()
      driver.find_element_by_id('profitsAmount').clear()
      driver.find_element_by_id('netProfitAmount').clear()
      driver.find_element_by_id('taxAmount').clear()
      driver.find_element_by_id('liabilitiesAmount').clear()

      #set
      driver.find_element_by_id('assetsTotalAmount').send_keys(str(0))
      driver.find_element_by_id('equityAmount').send_keys(str(0))
      driver.find_element_by_id('salesAmount').send_keys(str(0))
      driver.find_element_by_id('businessAmount').send_keys(str(0))
      driver.find_element_by_id('profitsAmount').send_keys(str(0))
      driver.find_element_by_id('netProfitAmount').send_keys(str(0))
      driver.find_element_by_id('taxAmount').send_keys(str(0))
      driver.find_element_by_id('liabilitiesAmount').send_keys(str(0))

      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[1]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[2]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[3]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[4]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[5]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[6]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[7]/td[3]/input[2]').click()
      driver.find_element_by_xpath('//*[@id="zcform"]/div/table/tbody/tr[8]/td[3]/input[2]').click()

      if(youxian):
        driver.find_element_by_id('zczkcomeOne').click()
      else:
        driver.find_element_by_id('zczkcomeTwo').click()
      if(youxian==False):
      #对外投资信息
        WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'infoDivDwtz')))
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="infoDivDwtz"]/div[3]/input[2]').click()

      #对外担保信息
      WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'infoDivDwdb')))
      time.sleep(1)
      
      driver.find_element_by_xpath('//*[@id="infoDivDwdb"]/div[3]/input[2]').click()
      
      #社保信息 
      try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'sociafrom')))
        time.sleep(1)
        #clear
        driver.find_element_by_id('townNum').clear()
        driver.find_element_by_id('unemploymentNum1').clear()
        driver.find_element_by_id('medicalNum').clear()
        driver.find_element_by_id('injuryNum').clear()
        driver.find_element_by_id('birthNum').clear()
        driver.find_element_by_id('TOTALWAGES_SO110').clear()
        driver.find_element_by_id('TOTALWAGES_SO210').clear()
        driver.find_element_by_id('TOTALWAGES_SO310').clear()
        driver.find_element_by_id('TOTALWAGES_SO510').clear()

        driver.find_element_by_id('TOTALPAYMENT_SO110').clear()
        driver.find_element_by_id('TOTALPAYMENT_SO210').clear()
        driver.find_element_by_id('TOTALPAYMENT_SO310').clear()
        driver.find_element_by_id('TOTALPAYMENT_SO410').clear()
        driver.find_element_by_id('TOTALPAYMENT_SO510').clear()

        driver.find_element_by_id('UNPAIDSOCIALINS_SO110').clear()
        driver.find_element_by_id('UNPAIDSOCIALINS_SO210').clear()
        driver.find_element_by_id('UNPAIDSOCIALINS_SO310').clear()
        driver.find_element_by_id('UNPAIDSOCIALINS_SO410').clear()
        driver.find_element_by_id('UNPAIDSOCIALINS_SO510').clear()

        #set
        driver.find_element_by_id('townNum').send_keys(str(0))
        driver.find_element_by_id('unemploymentNum1').send_keys(str(0))
        driver.find_element_by_id('medicalNum').send_keys(str(0))
        driver.find_element_by_id('injuryNum').send_keys(str(0))
        driver.find_element_by_id('birthNum').send_keys(str(0))
        driver.find_element_by_id('TOTALWAGES_SO110').send_keys(str(0))
        driver.find_element_by_id('TOTALWAGES_SO210').send_keys(str(0))
        driver.find_element_by_id('TOTALWAGES_SO310').send_keys(str(0))
        driver.find_element_by_id('TOTALWAGES_SO510').send_keys(str(0))

        driver.find_element_by_id('TOTALPAYMENT_SO110').send_keys(str(0))
        driver.find_element_by_id('TOTALPAYMENT_SO210').send_keys(str(0))
        driver.find_element_by_id('TOTALPAYMENT_SO310').send_keys(str(0))
        driver.find_element_by_id('TOTALPAYMENT_SO410').send_keys(str(0))
        driver.find_element_by_id('TOTALPAYMENT_SO510').send_keys(str(0))

        driver.find_element_by_id('UNPAIDSOCIALINS_SO110').send_keys(str(0))
        driver.find_element_by_id('UNPAIDSOCIALINS_SO210').send_keys(str(0))
        driver.find_element_by_id('UNPAIDSOCIALINS_SO310').send_keys(str(0))
        driver.find_element_by_id('UNPAIDSOCIALINS_SO410').send_keys(str(0))
        driver.find_element_by_id('UNPAIDSOCIALINS_SO510').send_keys(str(0))

        driver.find_element_by_xpath('//*[@id="sociafrom"]/div/table[3]/tbody/tr[1]/td[4]/input[2]').click()
        driver.find_element_by_xpath('//*[@id="sociafrom"]/div/table[3]/tbody/tr[5]/td[4]/input[2]').click()
        driver.find_element_by_xpath('//*[@id="sociafrom"]/div/table[3]/tbody/tr[10]/td[4]/input[2]').click()
        driver.find_element_by_id('socialNormal').click()
      except Exception as e:
        print(0)
      try:
        #党建信息 
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'partyform')))
        time.sleep(1)
        #clear
        driver.find_element_by_id('numParM').clear()
        #set
        driver.find_element_by_id('numParM').send_keys(str(0))
                                      
        driver.find_element_by_xpath('//*[@id="partyform"]/div[1]/table/tbody/tr[2]/td[2]/input[1]').click()
        driver.find_element_by_xpath('//*[@id="partyform"]/div[1]/table/tbody/tr[3]/td[2]/input[2]').click()
        driver.find_element_by_xpath('//*[@id="partyform"]/div[1]/table/tbody/tr[4]/td[2]/input[2]').click()
        driver.find_element_by_id('partySaveNormal').click()
      except Exception as e:
        print(0)

      #公示previewBefore
      WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'submitReportButton')))
      time.sleep(1)
      driver.find_element_by_id('submitReportButton').click()
      time.sleep(1)
      WebDriverWait(driver, 60).until(EC.alert_is_present())
      time.sleep(1)
      driver.switch_to.alert.accept()
      WebDriverWait(driver, 60).until(EC.alert_is_present())
      time.sleep(1)
      driver.switch_to.alert.accept()
      reports.loc[row, signColumn] = '完成申报'
      dataRecord(reports)
      time.sleep(1)
    except Exception as e:
      print(e)
      reports.loc[row, signColumn] = '申报失败'
      dataRecord(reports)
    row=row + 1
  open("phoneCode.txt", 'w').close()
  init()
  driver.quit()

init()

