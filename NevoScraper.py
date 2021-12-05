from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By


# shouldn't change these:
domain = "https://www.nevo.co.il"
login_url = "https://www.nevo.co.il/Authentication/UserLogin.aspx"

## initialize parameters
url = "https://www.nevo.co.il/SearchResults.aspx?query=ad27800a-3816-4206-b059-4690ecc2ffd3"  # search result URL
driver_path = 'C:/Users/noammaeir/Downloads/chromedriver_win32/chromedriver.exe'  # path to where Chromedriver was downloaded
folder_path = "C:\\Users\\noammaeir\\Nevo" #path to folder where files will be downloaded
USER = 'noam.maeir@mail.huji.ac.il'  # username
PASSWORD = 'BLABLABLA'  # password


def log_in():
    chrome = webdriver.ChromeOptions()
    chrome.add_experimental_option("prefs", {'download.default_directory': folder_path})
    driver = webdriver.Chrome(driver_path, options=chrome)
    driver.get(login_url)
    username = driver.find_element(By.ID, "ContentPlaceHolder1_LoginForm1_Login1_UserName")
    password = driver.find_element(By.ID, "ContentPlaceHolder1_LoginForm1_Login1_Password")
    username.send_keys(USER)
    password.send_keys(PASSWORD)
    driver.find_element(By.ID, "ContentPlaceHolder1_LoginForm1_Login1_LoginButton").click()
    return driver


def scrape_from_link(url, driver):
    print(f'starting to scrape {url}')
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html')
    textlinks = soup.find_all(class_="docLink")
    for link in textlinks:
        print(domain + link.get('href'))
        driver.get(domain + link.get('href'))
    print(f"done scraping from {url}")
    check_next_page(url, driver)


def check_next_page(url, driver):
    driver.find_element(By.ID, "ContentPlaceHolder1_SearchResultsTemplate1_Paging2_btnNext").click()
    if driver.current_url != url:
        scrape_from_link(driver.current_url, driver)
    else:
        print("done scraping all pages")


def run_scraper():
    driver = log_in()
    scrape_from_link(url, driver)
    time.sleep(10)
    driver.quit()


run_scraper()
