import time

from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# local
from webapp.model import Players


def update_player_values():
    driver = webdriver.Chrome()
    driver.get("http://www.dynastyfftools.com/tools/players")
    # FIXME hacky. was fucking around with the below but wasn't working
    time.sleep(10) # seconds
    # try:
    #     WebDriverWait(driver, delay).until(EC.presence_of_element_located(driver.find_elements_by_class_name('playersTableHeader')))
    #     print("Page is ready!")
    # except TimeoutException:
    #     print("Loading took too much time!")

    html = driver.page_source
    driver.close()
    soup = BeautifulSoup(html, 'html.parser')

    player_rows = soup.find('tbody').find_all('tr')


    for row in player_rows:
        player_attributes = row.find_all('td')

        name = player_attributes[0].string
        position = player_attributes[1].string
        value = int(player_attributes[5].string)

        Players.new_player_value(name, position, value)
