# Import necessary libraries
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import TimeoutException
import random

driver = webdriver.Firefox()
driver.get("https://canary-gradio-vectordb.apps.ai-dev01.kni.syseng.devcluster.openshift.com")
driver.set_window_size(1084, 811)
timeout = 10

for user in range(10):
    element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "#component-0 .scroll-hide"))
    WebDriverWait(driver, timeout).until(element_present)

    # User enters a question
    project_input = driver.find_element(By.CSS_SELECTOR, "#component-3 .scroll-hide")
    project_input.clear()  # Clearing any previous input
    project_input.send_keys(f"User {user + 1}: OpenShift AI")
    customer_input = driver.find_element(By.CSS_SELECTOR, "#component-4 .scroll-hide")
    customer_input.clear()  # Clearing any previous input
    customer_input.send_keys(f"User {user + 1}: Accenture")
    question_input = driver.find_element(By.CSS_SELECTOR, "#component-5 .scroll-hide")
    question_input.clear()  # Clearing any previous input
    question_input.send_keys(f"User {user + 1}: What is OpenShift AI?")
    driver.find_element(By.ID, "component-6").click()

    label_list=[1,2,3,4,5]
    random_num = random.choice(label_list)
    labelname=str(random_num)+'-radio-label'
    label_id="label[data-testid='"+labelname+"']"

    # # Wait for and click on the feedback element
    # label_id = "label[data-testid='2-radio-label']"
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, label_id))).click()
    time.sleep(2)  # Adding a delay for better simulation of user interaction

# Close the browser after the loop completes
#driver.quit()
