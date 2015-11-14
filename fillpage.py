from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("http://webinsight.cs.washington.edu/projects/audiocaptchas/")
#assert "Python" in driver.title
#elem1 = driver.find_element_by_id("recaptcha_response_field")
driver.find_element_by_id("recaptcha_switch_img_btn").click()
#driver.find_element_by_id("submit").click()

#elem1.send_keys("32")
assert "No results found." not in driver.page_source
#driver.close()