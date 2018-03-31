
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import os
import shutil
import requests
import zipfile

from config import user,passwd



datadir="/media/utpal/c6eb1258-a481-402c-837e-44fc98cb675c/Dropbox/WORK/Typhoon_finite_fault_inversion/Data/F_net_data"



def page_is_loaded(br):
    return br.find_element_by_tag_name("body") != None



fnet=pd.read_csv('F_net_stations.txt',delimiter='\s+',header=None,names=['Station','stn','Lat','Lon','Alt','tt1','tt2','tt3'])
nfnet=fnet.iloc[::2, 0:5]
nfnet.set_index('Station',inplace=True)
nfnet.head()



comps=['BHZ','BHN','BHE']
for i in range(3): #range(len(nfnet)):
    ss=nfnet.iloc[i,0]
    for j in range(len(comps)):
        command1='get {} {} 2017/10/17,12:00:00 2017/11/05,12:00:00'.format(ss,comps[j])
        print('Working on Station: {}, Component: {}'.format(ss,comps[j]))
        #open up firefox browser and navigate to web page
        br=webdriver.Firefox() #or webdriver.Chrome() but needs chromedriver or geockodriver
        br.get("http://{}:{}@www.fnet.bosai.go.jp/auth/dataget/?LANG=en".format(user,passwd))
        timeout=20 #wait for 20 sec to load
        try:
            wait=WebDriverWait(br,timeout)
            wait.until(page_is_loaded)
        except TimeoutException:
            print("The requested web page is taking long to load!")
            br.quit()
        assert "Retrieval of Waveforms" in br.title #look for the title on the page
        br.find_element_by_xpath("/html/body/form/table[1]/tbody/tr[3]/td/ul[1]/label[1]").click() #select data format MSEED

        elem=br.find_element_by_name('commands')
        elem.clear()
        elem.send_keys(command1)
        # elem.send_keys(Keys.RETURN)

        br.find_element_by_xpath("/html/body/form/table[1]/tbody/tr[3]/td/div[8]/button").click()

        try:
            # wait to make sure there are two windows open
            WebDriverWait(br, 10).until(lambda d: len(d.window_handles) == 2)

            # switch windows
            br.switch_to_window(br.window_handles[1])

            element = WebDriverWait(br, 40).until(EC.element_to_be_clickable((By.XPATH, "/html/body/a[1]")))
            linktosave=element.get_attribute("href")
            filename=linktosave.split("=")[1]
            fullfilename = os.path.join(datadir, filename)

            response = requests.get(linktosave, stream=True, auth=(user, passwd))
            with open(fullfilename, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            # element.click()
            zip_ref = zipfile.ZipFile(fullfilename, 'r')
            zip_ref.extractall(datadir)
            zip_ref.close()
            os.remove(fullfilename)
        except:
            print("TIMEOUT: Loading file is taking way too long!")

        # print(br.current_url)
        br.quit()


