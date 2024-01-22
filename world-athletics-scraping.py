import requests
from bs4 import BeautifulSoup
import pandas as pd

# literally copied from tfrrs-scraping.py maybe a better way to do it oh well
EVENT_DICTS = {
    'Mens-100-Meters': {},
    'Mens-200-Meters': {},
    'Mens-400-Meters': {},
    'Mens-800-Meters': {},
    'Mens-1500-Meters': {},
    'Mens-5000-Meters': {},
    'Mens-10000-Meters': {},
    'Mens-110-Hurdles': {},
    'Mens-400-Hurdles': {},
    'Mens-3000-Steeplechase': {},
    # 'Mens-4-x-100-Relay': {},
    # 'Mens-4-x-400-Relay': {},
    'Mens-High-Jump': {},
    'Mens-Pole-Vault': {},
    'Mens-Long-Jump': {},
    'Mens-Triple-Jump': {},
    'Mens-Shot-Put': {},
    'Mens-Discus': {},
    'Mens-Hammer': {},
    'Mens-Javelin': {},
    'Mens-Decathlon': {},
    'Womens-100-Meters': {},
    'Womens-200-Meters': {},
    'Womens-400-Meters': {},
    'Womens-800-Meters': {},
    'Womens-1500-Meters': {},
    'Womens-5000-Meters': {},
    'Womens-10000-Meters': {},
    'Womens-100-Hurdles': {},
    'Womens-400-Hurdles': {},
    'Womens-3000-Steeplechase': {},
    # 'Womens-4-x-100-Relay': {},
    # 'Womens-4-x-400-Relay': {},
    'Womens-High-Jump': {},
    'Womens-Pole-Vault': {},
    'Womens-Long-Jump': {},
    'Womens-Triple-Jump': {},
    'Womens-Shot-Put': {},
    'Womens-Discus': {},
    'Womens-Hammer': {},
    'Womens-Javelin': {},
    'Womens-Heptathlon': {},
}

WA_URL = 'https://worldathletics.org'

def scrape_event(event_url):
    page = requests.get(event_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    athletes = soup.find('tbody').find_all('tr')

    list_of_rows = []
    for row in athletes:
        cells = row.find_all('td')
        cells = [i.get_text().strip() for i in cells]
        list_of_rows.append(cells)
    
    df = pd.DataFrame(list_of_rows)
    # print(df)
    return df
    # here should call a function that adds the df to the global event dfs (similar to how they are for ncaa)


def scrape_meet(meet_url):

    def wa_style_to_tfrrs(event_name, sex):
        if 'Hurdles' in event_name:
            event_name = event_name[:-14] + 'Hurdles'
        if 'Steeplechase' in event_name:
            event_name = event_name[:-19] + 'Steeplechase'
        if 'Throw' in event_name:
            event_name = event_name[:-6]
        if 'Metres' in event_name:
            event_name = event_name[:-6] + 'Meters' # USA USA USA

        if sex == 'W':
            event_name = 'Womens-' + event_name
        else:
            event_name = 'Mens-' + event_name

        return event_name

    page = requests.get(meet_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    meet_name = soup.find('h1').get_text().strip()

    tables = soup.find_all('tbody')
    finals = []
    for table in tables:
        finals += table.find_all('td', {'data-er': 'Final'})

    for final in finals:
        event_sex = final.parent.find_all('td')[1].get_text().strip() # haha sex
        event_name_og = final.parent.find_all('td')[2].get_text().strip().replace(' ', '-').replace(',','')

        tfrrs_style_name = wa_style_to_tfrrs(event_name_og, event_sex)

        
        is_ncaa_event = tfrrs_style_name in EVENT_DICTS.keys()
        
        if is_ncaa_event:
            print(tfrrs_style_name)
            results_cell = final.parent.find_all('td')[5]
            results_url = WA_URL + results_cell.find('a', href=True)['href']
            # scrape_event(results_url)

    return meet_name

    # need to do multis separately
    # look for 1500/800 with round == decathlon/heptathlon

all_champs_url = 'https://worldathletics.org/results/world-athletics-championships'

page = requests.get(all_champs_url)
soup = BeautifulSoup(page.content, 'html.parser')

meetings = soup.find('tbody').find_all('a', href=True)
meet_urls = [i['href'] for i in meetings]

for meet in meet_urls:
    url = WA_URL + meet
    meet_name = scrape_meet(url)
    break