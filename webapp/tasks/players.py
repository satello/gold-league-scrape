import os
import time

from urllib import urlopen
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# local
from webapp.model import Players
from webapp.db import mem_db
from config import config

# can use either postgres or in memory storage
USE_MEM_DB = os.environ.get('USE_MEM_DB', True)


def update_player_values():
    # driver = webdriver.Chrome()
    # driver.get("http://www.dynastyfftools.com/tools/players")
    # # FIXME hacky. was fucking around with the below but wasn't working
    # time.sleep(30) # seconds
    # # try:
    # #     WebDriverWait(driver, delay).until(EC.presence_of_element_located(driver.find_elements_by_class_name('playersTableHeader')))
    # #     print("Page is ready!")
    # # except TimeoutException:
    # #     print("Loading took too much time!")
    #
    # html = driver.page_source
    # driver.close()
    # soup = BeautifulSoup(html, 'html.parser')
    #
    # player_rows = soup.find('tbody').find_all('tr')
    #
    #
    # for row in player_rows:
    #     player_attributes = row.find_all('td')
    #
    #     name = player_attributes[0].string
    #     position = player_attributes[1].string
    #     value = int(player_attributes[5].string)
    #
    #     Players.new_player_value(name, position, value)
    pass

def get_player_redraft_data(raw=False):
    # webpage url
    url = "https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php"

    # get page source
    response = urlopen(url)
    page_source = response.read()
    soup = BeautifulSoup(page_source, 'html.parser')

    player_rows = soup.find('tbody').find_all('tr')
    raw_data = []
    # print(player_rows[2])
    tier = 0
    first = True
    for row in player_rows[1:]:
        if row.has_key('class') and row['class'][0] == 'tier-row':
            tier += 1
            continue

        cols = row.find_all('td')
        if first:
            print(len(cols))
            print(cols)
            first = False
        if len(cols) != 9:
            continue

        player_name = cols[2].find('a').find('span', {'class': 'full-name'}).string
        if config["name_differences"].get(player_name):
            player_name = config["name_differences"][player_name]

        position = ''.join([i for i in (cols[3].string) if not i.isdigit()])

        player_rank = cols[0].string
        player_bye = cols[4].string

        # if you want raw data instead of inserting to db
        # FIXME split this up. confusing
        if raw:
            raw_data.append({
                "name": player_name,
                "position": position,
                "redraft_tier": tier,
                "redraft_rank": player_rank,
                "bye": player_bye
            })
            continue

        if USE_MEM_DB:
            mem_db.add_redraft_data(player_name, tier, player_rank, player_bye)
        else:
            Players.add_redraft_data(player_name, tier, player_rank, player_bye)

    if raw:
        return raw_data
