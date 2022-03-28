import random
import string
import time
import requests

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidArgumentException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# private constants
api_key = "I35ANFTXENWADIBMUKSZPAGNU2TY64SHSJYA"

# api url
url = "https://api.vultr.com/v2/instances"
headers = {"Authorization": "Bearer {}".format(api_key),
           "Content-Type": "application/json"}
data = {
    "region": "mex",
    "plan": "vc2-1c-1gb",
    "label": ''.join(random.choice(string.ascii_letters) for _ in range(10)),
    "app_id": 36
}


def config_driver():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-notifications")
    # chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--headless')

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=chrome_options)
    return driver


def random_email_generator(char_num):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(char_num))


def create_vps(api_key, url, headers, data, number):
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    instance_id, password = None, None
    try:
        instance_id = response_data['instance']['id']
        password = response_data['instance']['default_password']
        print("Instance ID: {}".format(instance_id))
        print("Password: {}".format(password))
    except Exception as e:
        print("Error: {}".format(e))

    # wait a minute until the VPS is ready
    time.sleep(120)

    # get instance ip address
    instance_url = "{}/{}".format(url, instance_id)
    instance_response = requests.get(instance_url, headers=headers)

    # print(instance_response.json())

    response_data = instance_response.json()
    ip_address = response_data['instance']['main_ip']
    print("Vultr Server", number + 1)
    print(f"Instance ID: {instance_id}, IP Address: {ip_address}, Username : root, Password: {password}")

    return instance_id, password, ip_address


def turn_off_firewall(driver, wait):
    # turn off firewall
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH,
                                               '//*[@id="main"]/div/div/div[1]/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div/div/div[3]'))).click()
        time.sleep(random.uniform(1, 3))

        # turn off firewall
        wait.until(
            EC.element_to_be_clickable((By.ID, 'ruleEngine-Off'))).click()
        time.sleep(random.uniform(1, 2))

        # apply changes
        wait.until(
            EC.element_to_be_clickable((By.ID, 'btn-apply'))).click()
        time.sleep(random.uniform(1, 2))
        # print(driver.find_element(By.ID, 'btn-apply'))

        print('firewall turned off')

    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)
    except InvalidArgumentException as ia_element:
        print(ia_element)


def remove_imunify_extension(driver, wait, URL_AV):
    # remove ImunifyAV Extension
    try:
        driver.get(URL_AV)
        time.sleep(random.uniform(2, 4))

        if driver.find_element(By.XPATH, '//*[@id="main"]/div/div/form/div[2]/div/div[2]/div/button'):
            wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="main"]/div/div/form/div[2]/div/div[2]/div/button'))).click()
        time.sleep(random.uniform(3, 4))

    except TimeoutException as e:
        # print("Wait Timed out")
        # print(e)
        pass
    except NoSuchElementException as ne_element:
        # print(ne_element)
        pass

    try:
        driver.get(URL_AV)
        time.sleep(random.uniform(2, 4))

        if driver.find_element(By.XPATH,
                               '//*[@id="main"]/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div/div/div/div[1]/div[4]/div/button'):
            wait.until(
                EC.element_to_be_clickable((By.XPATH,
                                            '//*[@id="main"]/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div/div/div/div[1]/div[4]/div/button'))).click()
            time.sleep(random.uniform(1, 2))

        # print(driver.find_element(By.CSS_SELECTOR, 'button[data-type="remove-button"]'))
        # print(driver.find_element(By.XPATH, '//*[@id="main"]/div/div/div[2]/div[2]/div/div/div[1]/div[1]/div/div/div/div[1]/div[4]/div/div[2]/div/button[2]'))

        # '/html/body/div[11]/div/div/div[2]'
        # driver.find_element(By.CSS_SELECTOR, 'data-type["remove-button"]')
        if driver.find_element(By.CSS_SELECTOR, 'div[data-type="remove-button"]'):
            wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-type="remove-button"]'))).click()
            time.sleep(random.uniform(1, 2))
        else:
            wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-type="remove-button"]'))).click()
            time.sleep(random.uniform(1, 2))
        wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn.btn-danger'))).click()
        time.sleep(random.uniform(1, 2))

        print('removed imunifyAV')

    except TimeoutException as e:
        # print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)
        pass


def create_domain(driver, wait, URL_DOMAIN, option_file, FILE_PATH, FILE_NAME, domain_number):
    # create domain
    try:
        driver.get(URL_DOMAIN)
        time.sleep(random.uniform(2, 4))
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="menuId-hosting"]/li[3]'))).click()
        time.sleep(random.uniform(1, 3))

        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="buttonAddDomain"]'))).click()
        time.sleep(random.uniform(1, 3))

        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 '//*[@id="smb-form-final-web-adddomain"]/div[1]/div[2]/div[2]/div/div/div/div[2]/div'))).click()

        time.sleep(random.uniform(4, 6))

        # check for domain username, password
        try:

            try:
                wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="domainInfo"]/div/button'))).click()
                time.sleep(random.uniform(1, 3))
            except TimeoutException as e:
                print("Wait Timed out")
                print(e)
            except NoSuchElementException as ne_element:
                print(ne_element)
            try:
                domain_name = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="smb-form-final-web-adddomain"]/div[2]/div[1]/div[2]/div/span'))).text
                domain_username = driver.find_element(By.ID, "domainInfo-userName").get_attribute("value")
                domain_password = driver.find_element(By.ID, "domainInfo-password").get_attribute("value")
                print(f"{domain_number + 1}. {domain_name}")
                print(f"{domain_username}:{domain_password}")

            except TimeoutException as e:
                print("Wait Timed out")
                print(e)
            except NoSuchElementException as ne_element:
                print(ne_element)

        except TimeoutException as e:
            print("Wait Timed out")
            print(e)
        except NoSuchElementException as ne_element:
            print(ne_element)

        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-send"]'))).click()

        time.sleep(random.uniform(18, 20))
        print('domain created')

        print('turning off firewall...')
        turn_off_firewall(driver, wait)

        try:
            # scroll to bottom
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            wait.until(EC.element_to_be_clickable((
                By.XPATH, '//*[@id="page"]/div/div/div/div/div/div/div/div[2]/div/h1/a'))).click()

            time.sleep(random.uniform(1, 3))
            # print('return to main menu')
        except TimeoutException as e:
            print("Wait Timed out")
            print(e)
        except NoSuchElementException as ne_element:
            print(ne_element)

        time.sleep(random.uniform(1, 3))

        if option_file.strip().lower() == 'yes':
            print('handle zip file started...')
            handle_zip_file(driver, wait, FILE_PATH, FILE_NAME)

    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)


def create_sub_domain(driver, wait, URL_DOMAIN):
    # create sub-domain
    try:
        driver.get(URL_DOMAIN)
        time.sleep(random.uniform(2, 4))
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="buttonAddSubDomain"]'))).click()
        time.sleep(random.uniform(1, 3))

        try:
            driver.find_element(By.XPATH, '//*[@id="domainName-name"]').clear()
            driver.find_element(By.XPATH, '//*[@id="domainName-name"]').send_keys(
                ''.join(random.choice(string.ascii_letters) for _ in range(8)))
            time.sleep(random.uniform(1, 3))
        except TimeoutException as e:
            print("Wait Timed out")
            print(e)
        except NoSuchElementException as ne_element:
            print(ne_element)

        try:
            driver.find_element(By.XPATH, '//*[@id="hostingSettings-root"]').clear()
            driver.find_element(By.XPATH, '//*[@id="hostingSettings-root"]').send_keys('httpdocs')
            time.sleep(random.uniform(1, 3))
        except TimeoutException as e:
            print("Wait Timed out")
            print(e)
        except NoSuchElementException as ne_element:
            print(ne_element)

        print('you may click on the button to create sub-domain')
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-send"]'))).click()

        time.sleep(random.uniform(18, 20))
        print('sub-domain created')

        turn_off_firewall(driver, wait)
        time.sleep(random.uniform(1, 3))

    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)


def handle_zip_file(driver, wait, FILE_PATH, FILE_NAME):
    # handle file manager

    try:
        if driver.find_element(By.XPATH, '//*[@id="asyncProgressBar"]/span/div/span[3]/button'):
            driver.find_element(By.XPATH, '//*[@id="asyncProgressBar"]/span/div/span[3]/button').click()
            time.sleep(random.uniform(1, 2))
    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)
    except ElementClickInterceptedException as ne_element:
        print(ne_element)
    except InvalidArgumentException as ia_element:
        print(ia_element)


    try:
        # click menu  file manager
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/div/div/div[1]/div[2]/div/div[2]/div/div/div['
                                                         '1]/div/div[1]/div/div/div[2]'))).click()
        time.sleep(random.uniform(1, 3))

        # click upload (plus) sign
        wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="fm-container"]/div[1]/div/div[2]/div/button'))).click()
        time.sleep(random.uniform(1, 2))

        # to identify element
        # s = driver.find_element(By.XPATH, "//input[@type='file']")
        s = driver.find_element(By.XPATH, '//*[@id="file-upload-input"]')

        # file path specified with send_keys
        s.send_keys(FILE_PATH)
        print('file uploaded')

    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)
    except InvalidArgumentException as ia_element:
        print(ia_element)

    time.sleep(random.uniform(3, 5))

    try:
        while driver.find_element(By.XPATH, '//*[@id="asyncProgressBar"]/span/div/span[3]/button'):
            driver.find_element(By.XPATH, '//*[@id="asyncProgressBar"]/span/div/span[3]/button').click()
            time.sleep(random.uniform(1, 2))
    except TimeoutException as e:
        # print("Wait Timed out")
        # print(e)
        pass
    except NoSuchElementException as ne_element:
        # print(ne_element)
        pass
    except ElementClickInterceptedException as ne_element:
        # print(ne_element)
        pass
    except InvalidArgumentException as ia_element:
        # print(ia_element)
        pass
    # comment this section to ignore unzipping files
    # extract zip files
    try:
        file = driver.find_element(By.CSS_SELECTOR, 'table#fm-table a[data-file="' + FILE_NAME + '"]')
        # file = wait.until(EC.element_to_be_clickable(
        #     driver.find_element(By.XPATH, '//*[@id="fm-table"]/tbody/tr[4]/td[2]/a')))

        actions = ActionChains(driver)
        actions.move_to_element(file)
        actions.click(file)
        actions.perform()
        time.sleep(random.uniform(1, 3))

        wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="fm-extract-archive-right-action-buttons-area"]/button[1]'))).click()
        time.sleep(random.uniform(1, 3))
        print('zip extracted')
    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)
    except InvalidArgumentException as ia_element:
        print(ia_element)


def login_plesk(driver, wait, username, password):
    # handle chrome https certificate error
    # print(driver.page_source)
    try:
        if driver.find_element(By.XPATH, '//*[@id="details-button"]'):
            driver.find_element(By.XPATH, '//*[@id="details-button"]').click()
            driver.find_element(By.XPATH, '//*[@id="proceed-link"]').click()
            time.sleep(2)
    except TimeoutException as e:
        # print("Wait Timed out")
        # print(e)
        pass
    except NoSuchElementException as ne_element:
        print(ne_element)
        pass

    time.sleep(2)

    # login
    try:
        driver.find_element(By.ID, "login_name").send_keys(username)
        driver.find_element(By.ID, "passwd").send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="form-login"]/div[3]/div/div[2]/div/button'))).click()

        # '//*[@id="form-login"]/div[2]/div/div[2]/div/button' or '//*[@id="form-login"]/div[3]/div/div[2]/div/button'

        time.sleep(random.uniform(1.5, 3.9))
        print('login successful')
    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)


def automate_plesk_app(driver, wait, username, password, URL_AV, URL_DOMAIN, domain_number, option_file, FILE_PATH,
                       FILE_NAME):
    login_plesk(driver, wait, username, password)
    # print(driver.page_source)
    # create admin user credentials
    try:
        if driver.find_element(By.ID, "contactInfo-contactName"):
            driver.find_element(By.ID, "contactInfo-contactName").clear()
            driver.find_element(By.ID, "contactInfo-contactName").send_keys('Administrator')

            driver.find_element(By.ID, "contactInfo-email").clear()

            # generate random email
            driver.find_element(By.ID, "contactInfo-email").send_keys(
                random_email_generator(7) + "@" + random_email_generator(5) + ".com")
            time.sleep(random.uniform(5, 6))

            # scroll to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # generate random password
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="main"]/form/div[2]/div[2]/div[2]/div/div/button'))).click()

            # check for eula agreement checkbox
            if not driver.execute_script("return document.getElementById('eula-eulaAgreement').checked"):
                # driver.find_element(By.ID, 'eula-eulaAgreement').click()
                driver.execute_script("document.getElementById('eula-eulaAgreement').click()")

            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn-send"]'))).click()

            time.sleep(random.uniform(18, 20))
            print('admin user created')
    except TimeoutException as e:
        print("Wait Timed out")
        print(e)
    except NoSuchElementException as ne_element:
        print(ne_element)

    print('removing imunify')
    remove_imunify_extension(driver, wait, URL_AV=URL_AV)

    if domain_number is None:
        domain_number = 1

    for i in range(0, int(domain_number)):
        print('creating domains')
        create_domain(driver, wait, URL_DOMAIN=URL_DOMAIN, option_file=option_file, FILE_PATH=FILE_PATH,
                      FILE_NAME=FILE_NAME, domain_number=i)


def setup_plesk_app_config(number=None):
    _, password, ip_address = create_vps(api_key, url, headers, data, number)

    time.sleep(15)

    # test cases
    # password = "B4w}J6MK6k4Vdb,m"
    # ip_address = "216.238.70.78"

    URL = "https://" + ip_address + ":8443/login"
    URL_AV = 'https://' + ip_address + ':8443/modules/catalog/index.php/installed/revisium-antivirus'
    URL_DOMAIN = 'https://' + ip_address + ':8443/admin/domain/list'

    FILE_PATH = "C:\\Users\\Administrator\\Documents\\VultrPlesk\\phpmini.zip"

    FILE_NAME = "phpmini.zip"

    return URL, URL_AV, URL_DOMAIN, FILE_PATH, FILE_NAME, password, ip_address


def automate_server_domain(option_1_server_num=None, option_2_random_domain=None, option_file=None):
    username = 'root'

    for i in range(0, int(option_1_server_num)):
        URL, URL_AV, URL_DOMAIN, FILE_PATH, FILE_NAME, password, ip_address = setup_plesk_app_config(number=i)

        driver = config_driver()
        driver.maximize_window()
        driver.set_window_size(1920, 1080)
        wait = WebDriverWait(driver, 10)

        driver.get(URL)
        time.sleep(random.uniform(1, 2))

        automate_plesk_app(driver, wait, username, password, URL_AV, URL_DOMAIN=URL_DOMAIN,
                           domain_number=option_2_random_domain,
                           option_file=option_file, FILE_PATH=FILE_PATH,
                           FILE_NAME=FILE_NAME)
        driver.close()
        driver.quit()

    # testing

    # login_plesk(driver, wait, username, password)

    # create_domain(driver, wait, URL_DOMAIN=URL_DOMAIN, option_file=option_file, FILE_PATH=FILE_PATH, FILE_NAME=FILE_NAME)
    # automate_plesk_app(driver, wait, username, password, URL_AV, URL_DOMAIN=URL_DOMAIN, domain_number=option_2,
    #                    option_file=option_file, FILE_PATH=FILE_PATH, FILE_NAME=FILE_NAME)


print("1) How many servers?")
option_1_server_num = input("Enter Option: ").strip()
print("You selected option : " + option_1_server_num)

print("2) How many random plesk in each server?")
option_2_random_domain = input("Enter Option: ").strip()
print("You selected option : " + option_2_random_domain)

print("3) Upload file.zip and extract it")
option_file = input("Enter Option: ").strip()
print("You selected option : " + option_file)

automate_server_domain(option_1_server_num, option_2_random_domain, option_file)