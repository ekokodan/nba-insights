from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
import time
from selenium.webdriver.remote.errorhandler import StaleElementReferenceException
import pandas as pd
import os

adblock_crx_path = '/Users/danielekoko/Desktop/adblockercrx.crx/'  
# roster_urls = '/Users/danielekoko/Desktop/team_urls.txt/'  
# Set up the Selenium driver
# options = webdriver.ChromeOptions()
# options.add_extension(adblock_crx_path)
# options.headless = True  # Run in headless mode
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=options)
# wait = WebDriverWait(driver, 10)



player_selector = "tr td .inline a.AnchorLink"
teams_section_selector = "ul.small-logos li a"  


# def get_roster_url():
#     # Initialize WebDriverWait and wait for the teams to load
#     wait = WebDriverWait(driver, 20)  # Increased timeout period
#     try:
#         driver.get('https://www.espn.com/nba/players')
#         # Adjust the selector if necessary
#         teams = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, teams_section_selector)))

#         team_urls = [team.get_attribute('href') for team in teams][1 :: 2]
#         print(team_urls)


#         # Add the rest of your code here to navigate team URLs and get player URLs...
#         # Save the player URLs to a file
#         with open('/Users/danielekoko/Desktop/nba_plays/team_urls.txt', 'w') as f:
#             for url in team_urls:
#                 f.write(url + '\n')
#         print("Got roster urls succesfully")
#         return team_urls

#     except TimeoutError as e:
#         print("Timeout occurred while waiting for team URLs to load.")
#         print(e.msg)
#     finally:
#         # Quit the driver
#         driver.quit()


team_urls_file = '/Users/danielekoko/Desktop/nba_plays/team_urls.txt'
pt_output_file = '/Users/danielekoko/Desktop/nba_plays/player_teams.txt'        

def get_player_urls_from_file(team_urls_file, output_file):
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in headless mode
    player_team_info = []

    with open(team_urls_file, 'r') as file:
        roster_urls = [line.strip() for line in file]

    for roster_url in roster_urls:
        attempts = 0
        success = False
        team_code = roster_url.split('=')[-1]  # Extract the team code from the URL

        while attempts < 3 and not success:  # Retry up to 3 times
            try:
                # Use a fresh instance of the WebDriver for each team URL
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                driver.get(roster_url)
                wait = WebDriverWait(driver, 30)
                players = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, player_selector)))
                team_player_urls = [player.get_attribute('href') for player in players][1 :: 2]

                for player_url in team_player_urls:
                    player_id = player_url.split('/')[-2]
                    player_name = player_url.split('/')[-1].replace('-', '_')
                    player_team_info.append(f"{player_name}-{team_code}-{player_id}")
                success = True  # If no exception was raised, mark as success

            except WebDriverException as e:
                print(f"Attempt {attempts + 1} failed for URL {roster_url}")
                print(str(e))
                attempts += 1
            finally:
                driver.quit()

    # Save all the player and team info to the output file
    with open(output_file, 'w') as file:
        for info in player_team_info:
            file.write(info + '\n')
    print("All player urls along with team info have been successfully written to the file.")

    return player_team_info

# Usage:
get_player_urls_from_file(team_urls_file, pt_output_file)




# def get_player_urls_from_file(team_urls_file, output_file):
#     with open(team_urls_file, 'r') as file:
#         roster_urls = [line.strip() for line in file]

#     player_urls = []
#     for roster_url in roster_urls:
#         attempts = 0
#         success = False
#         while attempts < 3 and not success:  # Retry up to 3 times
#             try:
#                 # Use a fresh instance of the WebDriver for each team URL
#                 driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
#                 driver.get(roster_url)
#                 wait = WebDriverWait(driver, 60)
#                 players = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, player_selector)))
#                 team_player_urls = [player.get_attribute('href') for player in players][1 :: 2]
#                 player_urls.extend(team_player_urls)
#                 success = True  # If no exception was raised, mark as success
#             except WebDriverException as e:
#                 print(f"Attempt {attempts + 1} failed for URL {roster_url}")
#                 print(str(e))
#                 attempts += 1
#             finally:
#                 driver.quit()

#     # Save all the player URLs to the output file
#     with open(output_file, 'w') as file:
#         for url in player_urls:
#             file.write(url + '\n')
#     print("All player urls have been successfully written to the file.")

#     return player_urls       

# Path to the file with roster URLs and output file
# team_urls_file = '/Users/danielekoko/Desktop/nba_plays/team_urls.txt'
# output_file = '/Users/danielekoko/Desktop/nba_plays/player_urls.txt'

# Get player URLs and save to file
# player_urls = get_player_urls_from_file(team_urls_file, output_file)
    

# Get team roster URLs
# roster_urls = get_roster_url()

# Setup driver again since it was closed in the get_roster_url function
# driver = webdriver.Chrome(service=service, options=options)


# Quit the driver
# driver.quit()

