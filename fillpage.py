from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import urllib2
import re

def open_site(driver):
    """
    Open a <driver> instance and locate the button for switching to audio CAPTCHA.
    If the button is found, it is clicked.
    :param driver: The browser driver to use
    """
    try:
        element = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "recaptcha_switch_audio_btn")))
        element.click()
    except TimeoutException:
        print "Timed out. (open_site). Retrying."
    try:
        element.click() # Sometimes the first click only puts focus on the browser window.
    except:
        driver.quit()

def push_information(driver):
    name_field = driver.find_element_by_id("signup_username")
    email_field = driver.find_element_by_id("signup_email_first")
    email_confirm_field = driver.find_element_by_id("signup_email")
    password_field = driver.find_element_by_id("signup_password")
    password_confirm_field = driver.find_element_by_id("signup_password_confirm")


    name_field.send_keys("Johnny")
    email_field.send_keys("johnny@johnson.john")
    email_confirm_field.send_keys("johnny@johnson.john")
    password_field.send_keys("123456")
    password_confirm_field.send_keys("123456")

def get_mp3(driver):
    """
    Locate the link for downloading audio CAPTCHA mp3 file.
    If found, the mp3 file will be downloaded.
    :param driver: The browser driver to use
    :return response: Data of mp3 file
    """
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "recaptcha_audio_download")))
    except TimeoutException:
        print "Timed out (get_mp3). Retrying."
        return False

    mp3 = driver.find_element_by_id("recaptcha_audio_download")
    url = mp3.get_attribute('href')
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)

    print "mp3 successfully located"
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
    print "{} successfully downloaded and saved".format(fout)

def push_response(driver, answer):
    """
    Locate the CAPTCHA response field, populate it with a string and press 'submit'
    :param driver: The browser driver to use
    :param response: The string to submit
    """
    text = driver.find_element_by_id('recaptcha_response_field')
    text.send_keys(answer)

    submit_button = driver.find_element_by_id("submit")
    submit_button.click()
    wait = WebDriverWait(driver, 1)

    src = driver.page_source
    text_found = re.search(r'You got it!', src)
    if text_found:
        print "Completed! CAPTCHA was: {}".format(answer)
        return True
    else:
        return False

