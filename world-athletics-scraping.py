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

def add_athlete(d, data, year):
    name = data['Name']
    place = data['Place']
    mark = data['Mark']
    country = data['Country']

    yc = 'years_competed'
    fp = 'finish_placements'
    fm = 'finish_marks'

    if name in d.keys():
        athlete_dict = d[name]
        athlete_dict[yc].append(year)
        athlete_dict[fp].append(place)
        athlete_dict[fm].append(mark)
    else:
        d[name] = {yc:[year], fp:[place], fm:[mark], 'country':country}

def scrape_event(event_url, meet_year):
    page = requests.get(event_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    athletes = soup.find('tbody').find_all('tr')
    list_of_rows = []
    for row in athletes:
        cells = row.find_all('td')
        cells = [i.get_text().strip() for i in cells]
        list_of_rows.append(cells)

    df = pd.DataFrame(list_of_rows)
    df.rename(columns={0:'Place', 1:'Bib', 2:'Name', 3:'Country', 4:'Mark'}, inplace=True)
    df['Mark'] = df['Mark'].apply(lambda mark : mark.split()[0])

    event_name = soup.find('h1').get_text().strip().split()
    event_sex = 'Womens' if event_name[-1] == 'women' else 'Mens' # to append for event dict
    event_name = event_name[:-1]
    if 'Metres' in event_name:
        metre_index = event_name.index('Metres')
        event_name[metre_index] = 'Meters' # USA USA USA
        if 'Steeplechase' in event_name or 'Hurdles' in event_name:
            event_name.remove('Meters')
    if 'Throw' in event_name:
        event_name.remove('Throw')
    if '10,000' in event_name:
        tenk_index = event_name.index('10,000')
        event_name[tenk_index] = '10000'

    tfrrs_style_name = event_sex + '-' + '-'.join(event_name)

    # add to the big event dictionary
    for idx, row in df.iterrows():
        add_athlete(EVENT_DICTS[tfrrs_style_name], row, meet_year)

    return df


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

    # meet_name = soup.find('h1').get_text().strip()
    meet_year = soup.find('span', {'class': '_label date'}).get_text().strip()[-4:]

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
            results_cell = final.parent.find_all('td')[5]
            results_url = WA_URL + results_cell.find('a', href=True)['href']
            scrape_event(results_url, meet_year)

    
    # need to do multis separately
    # look for 1500/800 with round == decathlon/heptathlon

    # write all event dicts to new folder of csvs

def main():
    all_champs_url = 'https://worldathletics.org/results/world-athletics-championships'

    page = requests.get(all_champs_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    meetings = soup.find('tbody').find_all('a', href=True)
    meet_urls = [i['href'] for i in meetings]

    for meet in meet_urls:
        url = WA_URL + meet
        # print(meet)
        scrape_meet(url)
        break

    # scrape_event("https://worldathletics.org/results/world-athletics-championships/2023/world-athletics-championships-budapest-2023-7138987/men/1500-metres/final/result#resultheader")

    print(EVENT_DICTS)

main()