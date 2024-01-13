import requests
from bs4 import BeautifulSoup
import pandas as pd

YEAR_TFRRS_DICT = {
    2014: 'https://www.tfrrs.org/results/36208/NCAA_Division_I_Outdoor_Track_&_Field_Championships/',
    2015: 'https://www.tfrrs.org/results/41405/NCAA_Division_I_Outdoor_Track_&_Field_Championships/',
    2016: 'https://www.tfrrs.org/results/46699/NCAA_Division_I_Track__Field_Championships/',
    2017: 'https://www.tfrrs.org/results/51935/NCAA_Division_I_Outdoor_Track_&_Field_Championships/',
    2018: 'https://www.tfrrs.org/results/57114/NCAA_Division_I_Outdoor_Championships',
    2019: 'https://www.tfrrs.org/results/62668/NCAA_Division_I_Outdoor_Track__Field_Championships',
    2021: 'https://www.tfrrs.org/results/70445/NCAA_Division_I_Track__Field_Championships',
    2022: 'https://www.tfrrs.org/results/75224/NCAA_Division_I_Outdoor_Track__Field_Championships',
    2023: 'https://www.tfrrs.org/results/81300/NCAA_Division_I_Outdoor_Track__Field_Championships'
}

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


def add_athlete(d, data, year):
    name = data['Name']
    place = data['Place']
    mark = data['Mark']
    class_yr = data['Year']

    yc = 'years_competed'
    cc = 'classes_competed'
    fp = 'finish_placements'
    fm = 'finish_marks'

    if name in d.keys():
        athlete_dict = d[name]
        athlete_dict[yc].append(year)
        athlete_dict[cc].append(class_yr)
        athlete_dict[fp].append(place)
        athlete_dict[fm].append(mark)
    else:
        d[name] = {yc:[year], cc:[class_yr], fp:[place], fm:[mark]}


# yeah yeah technically field events aren't races idgaf I couldn't think of another word
def race_to_df(event_url):
    event_page = requests.get(event_url)
    event_soup = BeautifulSoup(event_page.content, 'html.parser')

    results_table = event_soup.find('tbody').find_all('tr')
            
    list_of_rows = []
    for row in results_table:
        values = row.find_all('td')
        values = [v.get_text().strip() for v in values]

        # doesn't include NM/DQ/DNS/DNF
        # need it for field event results formatting
        # since they go across multiple rows
        if values[0] != '':
            list_of_rows.append(values[:6])

    df = pd.DataFrame(data = list_of_rows, columns=['Place', 'Name', 'Year', 'School', 'Mark', 'Pts'])
    return df


def add_year_to_data(year, events=[]):
    url = YEAR_TFRRS_DICT[year]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # this includes the compiled pages
    event_hyperlinks = soup.find('div', {'class':'row d-flex'}).find_all('a', href=True)

    for i in event_hyperlinks:
        event_url = i['href']

        # getting rid of the compiled results pages and relays
        if '/m/' in event_url or '/f/' in event_url or 'x' in event_url:
            continue

        event_name = event_url.split('/')[-1]

        # print('\'' + event_name + '\': {},')

        if events == [] or event_name in events:
            print(event_url)
            race_df = race_to_df(event_url)
            for idx, row in race_df.iterrows():
                add_athlete(EVENT_DICTS[event_name], row, year)

def main():
    for year in YEAR_TFRRS_DICT.keys():
        add_year_to_data(year)
    
    for key in EVENT_DICTS:
        df = pd.DataFrame.from_dict(EVENT_DICTS[key], orient='index')
        df.to_csv('./ncaa-results/' + key + '.csv')
        
main()