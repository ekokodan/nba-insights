import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.errorhandler import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import os
import time

adblock_crx_path = '/Users/danielekoko/Desktop/adblockercrx.crx'  
player_gamelogs = '/Users/danielekoko/Desktop/nba_plays/player_logs'
raw_player_urls = '/Users/danielekoko/Desktop/nba_plays/player_urls.txt' 
player_teams_file = '/Users/danielekoko/Desktop/nba_plays/player_teams.txt'
# Set up the Selenium driver
options = webdriver.ChromeOptions()
options.add_extension(adblock_crx_path)
options.headless = True  # Optional: Run in headless mode
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)


def save_to_file(data, filename, index=False):
    """
    Save data to a file. The format is inferred from the file extension.
    If the data is a DataFrame and the filename ends in .csv, it is saved as a CSV.
    If the data is a list and the filename ends in .txt, it is saved as a text file with one entry per line.
    """
    file_extension = os.path.splitext(filename)[1]
    
    if isinstance(data, pd.DataFrame) and file_extension == '.csv':
        data.to_csv(filename, index=index)
    elif isinstance(data, list) and file_extension == '.txt':
        with open(filename, 'w') as file:
            for line in data:
                file.write(f"{line}\n")
    else:
        raise ValueError(f"Unsupported data type or file extension: {file_extension}")
    
def initialize_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.set_page_load_timeout(90)
    return driver

def fetch_years(driver, url):
    wait = WebDriverWait(driver, 60)
    driver.get(url)
    dropdown = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "select.dropdown__select")))[-2]
    years = [option.get_attribute('value') for option in dropdown.find_elements(By.TAG_NAME, 'option')]
    print(years)
    return years

def scrape_table_data(driver, url, player_name, player_team, year):
    wait = WebDriverWait(driver, 60)
    year_url = f"{url[:-4]}/year/{year}"
    print(year_url)
    driver.get(year_url)
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table")))
    tables = driver.find_elements(By.CSS_SELECTOR, "table")
    # print(tables)
    all_data = []
    for table in tables:
        headers = [th.text for th in table.find_elements(By.CSS_SELECTOR, "thead th")]
        rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        data = []
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            row_data = handle_colspan(cells) + [player_name, player_team, year]
            data.append(row_data)
        headers.extend(['Player Name', 'Player Team', 'Year'])
        all_data.append(pd.DataFrame(data, columns=headers))
    return pd.concat(all_data, ignore_index=True)

def scrape_data_from_urls(url_groups, output_directory):
    for group in url_groups:
        player_name, player_team = get_player_info(group[0])  # Assuming first URL has player ID and name

        # Initialize all_data_frames outside of the years loop
        all_data_frames = []
        for url in group:
            retries = 0
            while retries < 3:
                try:
                    driver = initialize_driver()
                    years = fetch_years(driver, url)
                    # print(years)
                    for year in years:
                        final_df = scrape_table_data(driver, url, player_name, player_team, year)
                        final_df.reset_index(drop=True, inplace=True)  # Reset index to avoid overlapping indices

                        all_data_frames.append(final_df)
                    print(f"Data retrieved successfully for {player_name} for the year .")
                    break
                except Exception as e:
                    print(f"Attempt {retries + 1} failed for {player_name} for the year : {e}")
                    retries += 1
                    if retries < 3:
                        time.sleep(2)
                finally:
                    driver.quit()

            if retries == 3:
                print(f"Failed to retrieve data after several attempts for {player_name} for the year.")

        # Save all years data after the year's loop
        if all_data_frames:
            final_df = pd.concat(all_data_frames, ignore_index=True)
            save_dataframe_to_csv(final_df, output_directory, player_name, player_team)
            print(f"All data for {player_name}_{player_team} saved successfully")

def save_dataframe_to_csv(df, output_directory, player_name, player_team):
    csv_path = os.path.join(output_directory, f'{player_name}_{player_team}.csv')
    df.to_csv(csv_path, index=False)

def get_player_info(url):
# Extract player ID and name from URL, or implement the appropriate logic to get these details
    parts = url.split('/')
    player_id = parts[-2]
    player_name = parts[-1].replace('-', '_').title() # Assuming URL format is consistent
    player_team = get_player_team(player_id, player_teams_file)[0][1]
    return player_name, player_team




def get_player_team(player_id, file_path):
    success = False
    player_details = []
    with open(file_path, 'r') as file:
        while success != True:
            for line in file.readlines():
                info = line.strip()
                parts = info.split('-') 
                team = parts[1]
                id = parts[2]
                name = parts[0]
                if player_id == id:
                    player_team = team
                    player_details.append([name, player_team ,player_id])
                    success = True
                    # print(player_team)
        

    return player_details
# print(get_player_team('4433627', player_teams_file))



def process_player_urls(file_path):
    current_year = 2024  # Set the current year

    url_groups = []  # This will hold groups of URLs, each group for one player
    player_info = []  # To hold player information
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    for line in lines:
        # Remove newline characters and any surrounding whitespace
        player_page = line.strip()
        parts = player_page.split('/')
        player_id = parts[-2]
        player_name = parts[-1].replace('-', '_')
        url = f"https://www.espn.com/nba/player/gamelog/_/id/{player_id}/{player_name}"
        # available_years = get_available_years(url) # Set how many years of data you want to fetch
        # print(available_years)
        # years_to_fetch = len(available_years)
        # print(years_to_fetch)

        
        # Initialize a list to hold URLs for one player
        player_urls = []
        
        # Generate URLs for the past five years
        # for year in range(current_year, current_year - years_to_fetch, -1):
        #     year_url = f"https://www.espn.com/nba/player/gamelog/_/id/{player_id}/type/nba/year/{year}"
        player_urls.append(url)
        player_info.append((player_name, player_id))
        
        # Add the list of URLs for one player to the group
        url_groups.append(player_urls)

    # Optionally write the processed URLs to a file, grouped by player
    processed_urls_file = '/Users/danielekoko/Desktop/nba_plays/processed_player_urls.txt'
    with open(processed_urls_file, 'w') as file:
        for group in url_groups:
            for url in group:
                file.write(url + '\n')
            file.write('\n')  # Optional: write a newline to separate groups for readability
    
    return url_groups, player_info



# Function to handle possible 'colspan'
def handle_colspan(cells):
    row_data = []
    for cell in cells:
        cell_text = cell.text.strip()
        colspan = cell.get_attribute('colspan')
        if colspan:
            colspan_count = int(colspan)
            row_data.append(cell_text)
            for _ in range(1, colspan_count):
                row_data.append("")  # Fill the spanned columns with empty strings
        else:
            row_data.append(cell_text)
    return row_data

# Function to load the page and return tables
def load_page(url):
    driver.get(url)
    return WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table.Table")))



def get_available_years(player_url):
    # Setup the driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True  # Run in headless mode
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)  # Wait 20 seconds for elements to appear

    try:
        # Load the player's game log page
        driver.get(player_url)
        driver.set_page_load_timeout(30)


        # Wait for the dropdown to be present and then find it
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "select[class*='dropdown__select']")))
        dropdown = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "select.dropdown__select")))[-2]
        # Extract the years from the dropdown options
        years = [option.get_attribute('value') for option in dropdown.find_elements(By.TAG_NAME, 'option')]

        # Print or return the years list, depending on your needs
        # print(f"Available years for {player_url}: {years}")
        return years
    except TimeoutException:
        print(f"Timed out waiting for page to load for URL: {player_url}")
        return []
    finally:
        driver.quit()

# Example usage:
# player_url = 'https://www.espn.com/nba/player/gamelog/_/id/1966/lebron-james'
# print(get_available_years(player_url))




raw_player_urls = '/Users/danielekoko/Desktop/nba_plays/player_urls.txt'
# processed_gamelog_urls = process_player_urls(raw_player_urls)
url_groups = process_player_urls(raw_player_urls)[0]
# print(url_groups)
scrape_data_from_urls(url_groups, player_gamelogs)

# processed_urls, player_info = process_player_urls(raw_player_urls)


# test_list =['https://www.espn.com/nba/player/gamelog/_/id/4397885/dalano-banton', 'https://www.espn.com/nba/player/gamelog/_/id/3917376/jaylen-brown']
# scrape_data_from_urls(test_list ,'/Users/danielekoko/Desktop/Player2')


