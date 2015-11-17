from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import urllib2

driver = webdriver.Chrome()
driver.get("http://webinsight.cs.washington.edu/projects/audiocaptchas/")

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "recaptcha_switch_audio_btn")))
    print "Page is ready!"
    driver.find_element_by_id("recaptcha_switch_audio_btn").click()
except TimeoutException:
    print "Loading took too much time!"

element = driver.find_element_by_id("recaptcha_switch_audio_btn")

element.click()
 
#Doesn't work every time should put a loop? Just in case to be sure that the attack succed every time

try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "recaptcha_audio_download")))
    print "Song is ready!"
except TimeoutException:
    print "Loading took too much time!"

songurl = driver.find_element_by_id("recaptcha_audio_download")

url = songurl.get_attribute('href')
req2 = urllib2.Request(url)
response = urllib2.urlopen(req2)

#grab the data
data = response.read()

mp3Name = "audio.mp3"
song = open(mp3Name, "w")
song.write(data)    # was data2
song.close()

print "Song is downloaded!"

text = driver.find_element_by_id('recaptcha_response_field')
text.send_keys('333')

print 'text saisi: 333'

next = driver.find_element_by_name('submit')
next.click()

print 'Captcha valide'

