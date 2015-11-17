from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import urllib2

def open_site(driver):
    """
    Open a <driver> instance and locate the button for switching to audio CAPTCHA.
    If the button is found, it is clicked.
    :param driver: The browser driver to use
    """
    try:
        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "recaptcha_switch_audio_btn")))
    except TimeoutException:
        print "Timed out. (open_site)"
    element.click()
    try:
        element.click() # Sometimes the first click only puts focus on the browser window.
    except:
        driver.quit()



def get_mp3(driver):
    """
    Locate the link for downloading audio CAPTCHA mp3 file.
    If found, the mp3 file will be downloaded.
    :param driver: The browser driver to use
    :return response: Data of mp3 file
    """
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "recaptcha_audio_download")))
    except TimeoutException:
        print "Timed out (get_mp3)"
        return False

    mp3 = driver.find_element_by_id("recaptcha_audio_download")
    url = mp3.get_attribute('href')
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)

    return response

def write_mp3(response, fout="audio.mp3"):
    """
    Writes mp3 data to file on hard disc
    :param response: Data of mp3 file
    :param fout: Path of output file to store data in
    """
    data = response.read()
    fid = open(fout, "w")
    fid.write(data)
    fid.close()

def push_response(driver, answer):
    """
    Locate the CAPTCHA response field, populate it with a string and press 'submit'
    :param driver: The browser driver to use
    :param response: The string to submit
    """
    text = driver.find_element_by_id('recaptcha_response_field')
    text.send_keys(answer)

    next = driver.find_element_by_name('submit')
    next.click()


driver = webdriver.Chrome()
driver.get("http://webinsight.cs.washington.edu/projects/audiocaptchas/")

done = False
while not done:
    open_site(driver)
    re = get_mp3(driver)
    if re:
        write_mp3(re)
        done = True
