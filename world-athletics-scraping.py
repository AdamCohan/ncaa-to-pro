import requests
from bs4 import BeautifulSoup
import pandas as pd

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
    print(df)
    return df


def scrape_meet(meet_url):
    page = requests.get(meet_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # will need something before this to go through the different tabs

    finals = soup.find('tbody').find_all('td', {'data-er': 'Final'})
    for final in finals:
        results_cell = final.parent.find_all('td')[5]
        results_url = WA_URL + results_cell.find('a', href=True)['href']
        scrape_event(results_url) # need to check for events I care about




all_champs_url = 'https://worldathletics.org/results/world-athletics-championships'

page = requests.get(all_champs_url)
soup = BeautifulSoup(page.content, 'html.parser')

meetings = soup.find('tbody').find_all('a', href=True)
meet_urls = [i['href'] for i in meetings]

for meet in meet_urls:
    url = WA_URL + meet
    scrape_meet(url)
    break