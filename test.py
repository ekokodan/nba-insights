from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.remote.errorhandler import StaleElementReferenceException
import pandas as pd
import os

adblock_crx_path = '/Users/danielekoko/Desktop/adblockercrx.crx/'  
# Set up the Selenium driver
options = webdriver.ChromeOptions()
options.add_extension(adblock_crx_path)
options.headless = True  # Run in headless mode
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# Open the NBA teams page
# driver.get('https://www.espn.com/nba/players')

player_selector = "tr td .inline a.AnchorLink"
teams_section_selector = "ul.small-logos li a"  


def get_player_urls(roster_urls):
    wait = WebDriverWait(driver, 20)  # Increased timeout period
    player_urls = []
    for roster_url in roster_urls:
        # Navigate to the team's roster page
        driver.get(roster_url)
        
        # Wait for the player links to be loaded
        try:
            players = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, player_selector)))
            team_player_urls = [player.get_attribute('href') for player in players][1 :: 2]
            print(team_player_urls)
            # player_urls.append(team_player_urls)
        except TimeoutError as e:
            print(f"Timeout occurred while loading players from roster page: {roster_url}")
            print(e.msg)

        # Save the player URLs to a file
        with open('/Users/danielekoko/Desktop/nba_plays/player_urls.txt', 'w') as f:
            for url in team_player_urls:
                f.write(url + '\n')
        
        print("Got player urls succesfully")
        driver.quit()

        return player_urls


get_player_urls(['https://www.espn.com/nba/teams/roster?team=Phi'])