import numpy as np
import pandas as pd
import geopandas as gpd
import requests
from bs4 import BeautifulSoup
from scrapy import Selector
from tqdm import tqdm
from pathlib import Path


def get_urls(start_year, end_year):
    """
    Get the urls for the pages on which the race results are published
    """

    base_url = 'https://www.ijsselsteinloop.nl/'
    urls = list()
    for year in [str(year) for year in range(start_year, end_year + 1)]:
        r = requests.get(base_url + 'uitslag/' + year + '/index.htm')
        soup = BeautifulSoup(r.content, 'lxml')
        results_urls = [url['href'] for url in soup.find_all('a') if url['href'][:7] == 'uitslag']
        for results_url in ['{}uitslag/{}/{}'.format(base_url, year, results_url) for results_url in results_urls]:
            urls.append(results_url)
    return urls


def get_results(urls):
    """
    Get the actual race results from the pages on which they are published
    urls: page urls on which the race results are published
    """
    
    totals = pd.DataFrame()
    
    for url in tqdm(urls):
        df = pd.DataFrame()
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        table_rows = soup.find('table').find_all('tr')

        for table_row in table_rows[1:]:
            variables = table_row.find_all('td')
            if len(variables) >= 6:
                row = [variable.text for variable in [variables[col] for col in [1, 2, 3, 5]]]
            elif len(variables) == 5:
                row = [variable.text for variable in [variables[col] for col in [1, 2, 3, 4]]]
            
            df = df.append(pd.Series(row), ignore_index=True)
        
        df.columns = ['startnummer', 'naam', 'woonplaats', 'nettotijd']
        
        df['jaar'] = int(url[39:43])
        
        if url[55:].split('.')[0] == 'h12':
            df['klassement'] = 'Herenklassement'
            df['afstand'] = '21.1 km'
        elif url[55:].split('.')[0] == 'd12':
            df['klassement'] = 'Damesklassement'
            df['afstand'] = '21.1 km'
        elif url[55:].split('.')[0] == 'h10':
            df['klassement'] = 'Herenklassement'
            df['afstand'] = '10 km'
        elif url[55:].split('.')[0] == 'd10':
            df['klassement'] = 'Damesklassement'
            df['afstand'] = '10 km'
        elif url[55:].split('.')[0] == 'h5':
            df['klassement'] = 'Herenklassement'
            df['afstand'] = '5 km'
        elif url[55:].split('.')[0] == 'd5':
            df['klassement'] = 'Damesklassement'
            df['afstand'] = '5 km'
        else:
            df['afstand'] = np.nan
            df['klassement'] = np.nan

        totals = pd.concat([totals, df], sort=False)
        
    return totals


def get_data_2002():
    """
    Returns a DataFrame with the data
    """
    
    base_url = 'https://www.ijsselsteinloop.nl/uitslag/2002/'
    sel = Selector(text = requests.get(base_url + 'index.htm').content)
    urls = sel.xpath('//a/@href').extract()[1:3] # halve marathon

    # men
    heren = pd.read_excel(base_url + urls[0]).dropna()
    heren['jaar'] = 2002
    heren['klassement'] = 'Herenklassement'

    # women
    dames = pd.read_excel(base_url + urls[1]).dropna()
    dames['jaar'] = 2002
    dames['klassement'] = 'Damesklassement'
    
    # total
    df_2002 = pd.concat([heren, dames.rename(columns={'WOONPLAATS':'PLAATS'})], sort=False, ignore_index=True)
    df_2002['afstand'] = '21.1 km'
    
    df_2002.columns = ['startnummer', 'naam', 'woonplaats', 'nettotijd', 'jaar', 'klassement', 'afstand']
    
    return df_2002


def get_data_2001():
    """
    Returns a DataFrame with the data
    """
    
    base_url = 'https://www.ijsselsteinloop.nl/uitslag/2001/'
    r = requests.get(base_url + 'index.htm')
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.find_all('table')
    
    colnames = ['startnummer', 'naam', 'woonplaats', 'nettotijd']
    
    # men
    lines = list()
    for rows in tables[0].find_all('tr'):
        line = list()
        for cell in rows.find_all('td')[1:]:
            line.append(cell.text.strip())
        lines.append(line)
    
    heren = pd.DataFrame()
    for line in lines[1:]:
        heren = heren.append(pd.Series(line), ignore_index=True)
    heren.columns = colnames
    heren['klassement'] = 'Herenklassement'
    
    # women
    lines = list()
    for rows in tables[1].find_all('tr'):
        line = list()
        for cell in rows.find_all('td')[1:]:
            line.append(cell.text.strip())
        lines.append(line)
    
    dames = pd.DataFrame()
    for line in lines[1:]:
        dames = dames.append(pd.Series(line), ignore_index=True)
    dames.columns = colnames
    dames['klassement'] = 'Damesklassement'
    
    # total
    df_2001 = pd.concat([heren, dames], sort=False, ignore_index=True)
    df_2001['jaar'] = 2001
    df_2001['afstand'] = '21.1 km'
    
    return df_2001

def get_data_2000():
    """
    Returns a DataFrame with the data
    """
    
    base_url = 'https://www.ijsselsteinloop.nl/uitslag/2000/'
    r = requests.get(base_url + 'index.htm')
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.find_all('table')
    
    colnames = ['naam', 'nettotijd']
    
    # men
    lines = list()
    for rows in tables[0].find_all('tr'):
        line = list()
        for cell in rows.find_all('td')[1:]:
            line.append(cell.text.strip())
        lines.append(line)
    
    heren = pd.DataFrame()
    for line in lines:
        heren = heren.append(pd.Series(line), ignore_index=True)
    heren.columns = colnames
    heren['klassement'] = 'Herenklassement'
    
    # women
    lines = list()
    for rows in tables[1].find_all('tr'):
        line = list()
        for cell in rows.find_all('td')[1:]:
            line.append(cell.text.strip())
        lines.append(line)
    
    dames = pd.DataFrame()
    for line in lines:
        dames = dames.append(pd.Series(line), ignore_index=True)
    dames.columns = colnames
    dames['klassement'] = 'Damesklassement'
    
    # total
    df_2000 = pd.concat([heren, dames], sort=False, ignore_index=True)
    df_2000['startnummer'] = np.nan
    df_2000['woonplaats'] = np.nan
    df_2000['jaar'] = 2000
    df_2000['afstand'] = '21.1 km'
    
    return df_2000


def get_data_1999():
    """
    Returns a DataFrame with the data
    """

    base_url = 'https://www.ijsselsteinloop.nl/uitslag/1999/'
    r = requests.get(base_url + 'index.htm')
    soup = BeautifulSoup(r.content, 'lxml')
    tables = soup.find_all('table')
    
    colnames = ['naam', 'nettotijd']
    
    # men
    lines = list()
    for rows in tables[0].find_all('tr'):
        line = list()
        for cell in rows.find_all('td')[1:]:
            line.append(cell.text.strip())
        lines.append(line)
    
    heren = pd.DataFrame()
    for line in lines:
        heren = heren.append(pd.Series(line), ignore_index=True)
    heren.columns = colnames
    heren['klassement'] = 'Herenklassement'
    
    # women
    lines = list()
    for rows in tables[2].find_all('tr'):
        line = list()
        for cell in rows.find_all('td')[1:]:
            line.append(cell.text.strip())
        lines.append(line)
    
    dames = pd.DataFrame()
    for line in lines:
        dames = dames.append(pd.Series(line), ignore_index=True)
    dames.columns = colnames
    dames['klassement'] = 'Damesklassement'
    
    # total
    df_1999 = pd.concat([heren, dames], sort=False, ignore_index=True)
    df_1999['startnummer'] = np.nan
    df_1999['woonplaats'] = np.nan
    df_1999['jaar'] = 1999
    df_1999['afstand'] = '21.1 km'
    
    return df_1999


def ophalen_data(jaar):
    """
    """

    # 2003 - jaar (settings)
    if not Path(f'data/uitslagen_2003_{jaar}.csv').is_file():
        urls = get_urls(2003, jaar)
        klassementen = ['h12', 'd12', 'h10', 'd10', 'h5', 'd5'] # h=heren, d=dames, 12=21.1K, 10=10K en 5=5K
        klassement_urls = [url for url in urls if url[55:].split('.')[0] in klassementen]
        get_results(klassement_urls).to_csv(f'data/uitslagen_2003_{jaar}.csv', index=False)
    
    # 1999 - 2002
    if not Path('data/uitslagen_1999_2002.csv').is_file():
        pd.concat([get_data_1999(), get_data_2000(), get_data_2001(), get_data_2002()], sort=False, ignore_index=True).to_csv('data/uitslagen_1999_2002.csv', index=False)
    
    # inlezen ruwe dataset
    onbekend = ['-', '--', 'onbekend', '-- onbekend --']
    uitslagen = pd.concat([pd.read_csv('data/uitslagen_1999_2002.csv', dtype={'startnummer':'str'}, na_values=onbekend), pd.read_csv(f'data/uitslagen_2003_{jaar}.csv', dtype={'startnummer':'str'}, na_values=onbekend)], sort=False).reset_index(drop=True)

    return uitslagen


def  ophalen_weer(start_jaar, eind_jaar):
    """
    Ophalen datums IJsselsteinloop en de gemiddelde temperatuur in De Bilt.
    """

    datums_ijsselsteinloop = dict()
    for jaar in range(start_jaar, eind_jaar + 1):
        r = requests.get(f'https://www.kalender-365.nl/kalender-{jaar}.html')
        soup = BeautifulSoup(r.content, 'lxml')
        table = soup.find('table', {'id':'legenda_right'}).find_all('tr')
        feestdagen = [list(row.stripped_strings) for row in table]
        
        for i, v in enumerate(feestdagen):
            if (v[1]).lower() == '1e pinksterdag':
                datums_ijsselsteinloop[jaar] = '{}-{}-{}'.format(int(v[0].split()[0])-1, v[0].split()[1], jaar)
    
        maanden = dict(zip(['januari', 'februari', 'maart', 'april', 'mei', 'juni',
                            'juli', 'augustus', 'september', 'oktober', 'november', 'december'],
                           range(1, 13)))

    temperaturen_ijsselsteinloop = dict()
    for datum in tqdm(datums_ijsselsteinloop.values()):
        url = 'http://www.wetterzentrale.de/weatherdata.aspx?jaar={}&maand={}&dag={}&station=260'.format(datum.split('-')[2], maanden[datum.split('-')[1]], datum.split('-')[0])
        temperaturen_ijsselsteinloop[datum] = float(pd.read_html(url)[0].iat[3, 1])
    
    data = pd.DataFrame.from_dict(temperaturen_ijsselsteinloop, orient='index', columns=['temperatuur'])
    data.index.name = 'datum'

    data.to_csv(f'data/weer_{start_jaar}_{eind_jaar}.csv')
    return data


def category(num, categories):
    """
    Returns the upper category boundary for a given number based on a list met upper category boundaries.

    Example
    =======
    category(25, [10, 20, 30, 40, 50])
    30
    """

    for boundary in categories:
        if num <= boundary:
            return boundary


def category_labels(categories):
    """
    Returns a dictionary with upper category boundaries and a category label.
    The lower boundary for the first category is set to one.

    Example
    =======
    category_labels([10, 20, 30, 40, 50])
    {10: '1 - 10', 20: '11 - 20', 30: '21 - 30', 40: '31 - 40', 50: '41 - 50'}
    """

    boundaries = [0] + categories
    labels = dict()
    for i in range(1, len(categories) + 1):
        labels[boundaries[i]] = f'{boundaries[i-1] + 1} - {boundaries[i]}'
    return labels


def time_to_seconds(time):
    """
    Convert a timestring in 'HH:MM:SS' format to seconds
    """

    hrs_min_sec = map(int, time.split(':')) # hours, minutes and seconds
    multipliers = {'hour': 3600, 'minute': 60, 'second': 1}
    return sum([x*y for x, y in zip(hrs_min_sec, multipliers.values())])


def replace_legend_items(legend, mapping):
    """
    Function to replace legend item lables in a figure.

    Example
    =======
    replace_legend_items(ax.get_legend(), {10: '1 - 10', 20: '11 - 20', 30: '21 - 30', 40: '31 - 40', 50: '41 - 50'})
    """
    
    for txt in legend.texts:
        for k, v in mapping.items():
            if txt.get_text() == str(k):
                txt.set_text(v)


def nettotijd(uitslagen):
    """
    Format nettotijd to "HH:MM:SS"
    """

    uitslagen['nettotijd'] = uitslagen.nettotijd.str.replace('.', ':')

    return uitslagen


def nettotijd_sec(uitslagen):
    """
    Convert nettotijd to nettotijd in seconds
    """

    uitslagen['nettotijd_sec'] = uitslagen.nettotijd.apply(time_to_seconds)

    uitslagen = uitslagen.sort_values(by=['jaar', 'afstand', 'klassement', 'nettotijd_sec']).reset_index(drop=True)

    return uitslagen


def gemeenten(uitslagen):
    """
    Toevoegen gemeenten incl. afstand tot het centrum van de gemeente IJsselstein in kilometers
    """

    # make copy
    uitslagen_org = uitslagen.copy()

    # add municipality data
    uitslagen = pd.merge(uitslagen, pd.read_csv('data/plaatsnaam_gemeente.csv'), how='left', left_on='woonplaats', right_on='plaatsnaam')
    uitslagen.drop('plaatsnaam', axis=1, inplace=True)

    # read shapefile municipality borders
    gemeenten = gpd.read_file('data/2019_gemeentegrenzen_kustlijn.gpkg')

    # merge shapefile with race results
    uitslagen = pd.merge(gemeenten, uitslagen, how='left', left_on='gemeentenaam', right_on='gemeente')

    # add distance to IJsselstein
    IJsselstein = gemeenten[gemeenten.gemeentenaam == 'IJsselstein'].iloc[0]['geometry'].centroid
    uitslagen['tot_ijsselstein'] = uitslagen.geometry.apply(lambda x: round(x.centroid.distance(IJsselstein) / 1000, 2)) # distance in km

    # select municipality nearest to IJsselstein
    uitslagen = uitslagen.loc[uitslagen.groupby(['startnummer', 'jaar', 'afstand', 'klassement']).tot_ijsselstein.idxmin()].sort_values(by=['jaar', 'klassement', 'afstand', 'tot_ijsselstein'])

    # drop columns
    uitslagen.drop(['id', 'gid', 'code', 'gemeentenaam', 'geometry'], axis=1, inplace=True)

    # add rows with woonplaats is NA
    uitslagen_wpl_na = uitslagen_org[uitslagen_org.woonplaats.isna()].copy()
    uitslagen_wpl_na['tot_ijsselstein'] = np.nan
    uitslagen_wpl_na['gemeente'] = np.nan
    uitslagen = pd.concat([uitslagen, uitslagen_wpl_na], sort=False).sort_values(by=['jaar', 'afstand', 'klassement'])

    # set dtypes
    uitslagen['jaar'] = uitslagen.jaar.astype(int)

    # reset index
    uitslagen.reset_index(drop=True, inplace=True)

    return uitslagen


def namen(uitslagen):
    """
    Opschonen namen
    """
    
    uitslagen['naam'] = uitslagen.naam.str.strip()
    
    uitslagen.loc[uitslagen.woonplaats == 'Erik Vijverberg', ['naam']] = 'Erik Vijverberg'
    uitslagen.loc[uitslagen.woonplaats == 'Fiso Glansdorp', ['naam']] = 'Fiso Glansdorp'
    uitslagen.loc[uitslagen.woonplaats == 'Toby scharing', ['naam']] = 'Toby scharing'
    uitslagen.loc[uitslagen.woonplaats == 'Carola sijbrandij', ['naam']] = 'Carola sijbrandij'

    return uitslagen


def woonplaatsen(uitslagen):
    """
    Opschonen woonplaatsen
    """
    
    uitslagen['woonplaats'] = uitslagen.woonplaats.str.strip()
    
    uitslagen.loc[uitslagen.woonplaats.isin(['Kampen Ov']), ['woonplaats']] = 'Kampen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Woerdense Verlaat']), ['woonplaats']] = 'Woerden'
    uitslagen.loc[uitslagen.woonplaats.isin(['BabyloniÃ«nbroek']), ['woonplaats']] = 'Babyloniënbroek'
    uitslagen.loc[uitslagen.woonplaats.isin(['Breukelen ut']), ['woonplaats']] = 'Breukelen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Buren gld', 'Buren', 'Buren Gld']), ['woonplaats']] = 'Buren'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hengelo ov']), ['woonplaats']] = 'Hengelo'
    uitslagen.loc[uitslagen.woonplaats.isin(['Driehuis']), ['woonplaats']] = 'Driehuis NH'
    uitslagen.loc[uitslagen.woonplaats.isin(['LEIDEN']), ['woonplaats']] = 'Leiden'
    uitslagen.loc[uitslagen.woonplaats.isin(['LOPIKERKAPEL']), ['woonplaats']] = 'Lopikerkapel'
    uitslagen.loc[uitslagen.woonplaats.isin(['TIel']), ['woonplaats']] = 'Tiel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nieukoop']), ['woonplaats']] = 'Nieuwkoop'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nederhorst Den Berg', 'Nederhorst d Berg']), ['woonplaats']] = 'Nederhorst den Berg'
    uitslagen.loc[uitslagen.woonplaats.isin(['Vianen', 'VIanen', 'Vianen UT', 'Vianen ut', 'Vianen zh', 'Vianen Ut', 'Vianen (Ut)', 'Vianen        Utr']), ['woonplaats']] = 'Vianen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Veenedaal', 'Veendendaal']), ['woonplaats']] = 'Veenendaal'
    uitslagen.loc[uitslagen.woonplaats.isin(['IJsselsein', 'IJsseltein', 'IJSSELSTEIN', 'IJsselsstein','IJsselstein Ut', 'Ysselstein', 'IJsselstein', 'Ijsselstein ut', 'IJsselstein ut', 'ijsselstein', 'IJsselsetin', 'IJsslestein', 'IJselstein', 'IJsselstraat', 'IJsselstein NL', 'IJsselstein UT']), ['woonplaats']] = 'IJsselstein'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nieuw Vennep', 'Nieuw vennep']), ['woonplaats']] = 'Nieuw-Vennep'
    uitslagen.loc[uitslagen.woonplaats.isin(['Tull en T Waal', 'Tull en t Waal', 'Tull en  t Waal']), ['woonplaats']] = 'Tull en \'t Waal'
    uitslagen.loc[uitslagen.woonplaats.isin(['AlpheN aan den Rijn', 'Alphen aan den rijn', 'Alphen a.d. Rijn', 'Alphen a d Rijn', 'Alphen a d rijn', 'Alphen aan de Rijn', 'Alphen aan den Rijn', 'Alphen aan den Rijn ', 'Alphen ad Rijn', 'Alpen aan de Rijn', 'Aphen a d Rijn', 'Alphen a/d Rijn']), ['woonplaats']] = 'Alphen aan den Rijn'
    uitslagen.loc[uitslagen.woonplaats.isin(['Utrecht  Apeldoorn', 'Aïdadreef 8', 'Utercht', 'Utrecgt', 'Utrecht', 'UTRECHT', 'Leidsche Rijn', 'Utreecht', 'Utreht', 'Uttrecht', 'utrecht']), ['woonplaats']] = 'Utrecht'
    uitslagen.loc[uitslagen.woonplaats.isin(['Niewegein', 'Jupthaas', 'Nieuwegin', 'Nieuwgein', 'NIEUWEGEIN', 'Neiuwegein', 'NIeuwegein', '3435 BL Nieuwegein', 'Nieuwergein']), ['woonplaats']] = 'Nieuwegein'
    uitslagen.loc[uitslagen.woonplaats.isin(['Maarssenbroek', 'Oud Maarsseveen', 'Maarsen']), ['woonplaats']] = 'Maarssen'
    uitslagen.loc[uitslagen.woonplaats.isin(['t Goy']), ['woonplaats']] = '\'t Goy'
    uitslagen.loc[uitslagen.woonplaats.isin(['S-Graveland', 's Graveland']), ['woonplaats']] = '\'s-Graveland'
    uitslagen.loc[uitslagen.woonplaats.isin(['Ameorngen']), ['woonplaats']] = 'Amerongen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Cabauw']), ['woonplaats']] = 'Lopik'
    uitslagen.loc[uitslagen.woonplaats.isin(['Beek - Berg en Dal']), ['woonplaats']] = 'Berg en Dal'
    uitslagen.loc[uitslagen.woonplaats.isin(['Houten Netherlands', 'Houten', 'HOUTEN']), ['woonplaats']] = 'Houten'
    uitslagen.loc[uitslagen.woonplaats.isin(['Oenkerk', 'Tytsjerksteradiel']), ['woonplaats']] = 'Tytsjerk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Elst Gld']), ['woonplaats']] = 'Elst'
    uitslagen.loc[uitslagen.woonplaats.isin(['Bleskensgraaf']), ['woonplaats']] = 'Bleskensgraaf ca'
    uitslagen.loc[uitslagen.woonplaats.isin(['S-Gravenhage', 's-Gravenhage', 'Den Haag', 'S gravenhage', 'Den haag', 'Scheveningen', 's Gravenhage','\'s Gravenhage']), ['woonplaats']] = '\'s-Gravenhage'
    uitslagen.loc[uitslagen.woonplaats.isin(['Loik', 'Uitweg']), ['woonplaats']] = 'Lopik'
    uitslagen.loc[uitslagen.woonplaats.isin(['Oude Tonge']), ['woonplaats']] = 'Oude-Tonge'
    uitslagen.loc[uitslagen.woonplaats.isin(['Alphen NB', 'Alphen nb']), ['woonplaats']] = 'Alphen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Sint Oedenrode']), ['woonplaats']] = 'Sint-Oedenrode'
    uitslagen.loc[uitslagen.woonplaats.isin(['Polsbroek', 'Poslbroek']), ['woonplaats']] = 'Polsbroek'
    uitslagen.loc[uitslagen.woonplaats.isin(['Beneden Leeuwen', 'Beneden-Leeuwen']), ['woonplaats']] = 'Beneden-Leeuwen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Bergsche Hoek', 'Bergschenhoek']), ['woonplaats']] = 'Bergschenhoek'
    uitslagen.loc[uitslagen.woonplaats.isin(['Bunschoten', 'Bunschoten-Spakenburg', 'Spakenburg', 'Bunschoten Spakenburg', 'Bunschoten-spakemburg']), ['woonplaats']] = 'Bunschoten-Spakenburg'
    uitslagen.loc[uitslagen.woonplaats.isin(['Capelle aan de ijssel', 'Capelle ad IJssel', 'Capelle a d IJssel', 'Capelle a d ijssel', 'Capelle aan den IJssel', 'Capelle aan den Yssel', 'Capelle aan den ijssel', 'Capelle a/d IJssel']), ['woonplaats']] = 'Capelle aan den IJssel'
    uitslagen.loc[uitslagen.woonplaats.isin(['De Meern', 'De meern', 'de Meern', 'DE MEERN']), ['woonplaats']] = 'De Meern'
    uitslagen.loc[uitslagen.woonplaats.isin(['Driebergen', 'Driebergen Rijsenburg', 'Driebergen-Rijsenburg', 'Driebergen-Rijssenburg', 'Driebergen-rijsenburg']), ['woonplaats']] = 'Driebergen-Rijsenburg'
    uitslagen.loc[uitslagen.woonplaats.isin(['Groot - Ammers', 'Groot Ammers', 'Groot-Ammera', 'Groot-Ammers', 'Groot-ammers']), ['woonplaats']] = 'Groot-Ammers'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hardinxveld', 'Hardinxveld-giessendam', 'Hardingsveld Giesendam', 'Hardinxveld - giessendam', 'Hardinxveld - Giessendam', 'Hardinxveld Giessendam', 'Hardinxveld giessendam', 'Hardinxveld-Giessendam']), ['woonplaats']] = 'Hardinxveld-Giessendam'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hazerswoude-dorp', 'Hazerswoude', 'Hazerswoude-Rijndijk', 'Hazerswoude-rijndijk']), ['woonplaats']] = 'Hazerswoude-Rijndijk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hei en Boeicop', 'Hei- en Boeicop']), ['woonplaats']] = 'Hei- en Boeicop'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hendrik Ido Ambacht', 'Hendrik Ido ambacht', 'Hendrik ido ambacht', 'Hendrik-Ido-Ambacht', 'H I  Ambacht']), ['woonplaats']] = 'Hendrik-Ido-Ambacht'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hoef en Haag', 'Hoef en haag']), ['woonplaats']] = 'Hoef en Haag'
    uitslagen.loc[uitslagen.woonplaats.isin(['IJaselstein', 'IJsselsteijn', 'IJsselstein', 'IJsselstien', 'IJsselstijn', 'IJsselstrein', 'YSSELSTEIN', 'Ijsselstein']), ['woonplaats']] = 'IJsselstein'
    uitslagen.loc[uitslagen.woonplaats.isin(['Huis Ter Heide', 'Huis ter Heide']), ['woonplaats']] = 'Huis ter Heide'
    uitslagen.loc[uitslagen.woonplaats.isin(['Katwijk', 'Katwijk ZH', 'Katwijk Zh', 'Katwijk z-h', 'Katwijk zh']), ['woonplaats']] = 'Katwijk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Krimpen a d IJssel', 'Krimpen aan de IJssel', 'Krimpen aan den IJssel', 'Krimpen aan den ijssel', 'Krimpen a/d IJssel']), ['woonplaats']] = 'Krimpen aan den IJssel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Krimpen a d Lek', 'Krimpen aan de Lek', 'Krimpen aan de lek', 'Krimpen a/d Lek']), ['woonplaats']] = 'Krimpen aan de Lek'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nieuwerkerk aan den ijssel', 'Nieuwekerk a d IJssel', 'Nieuwerkerk a d IJssel', 'Nieuwerkerk aan den IJssel', 'Nieuwerkerk ad IJssel', 'Niewerkerk a d IJssel']), ['woonplaats']] = 'Nieuwerkerk aan den IJssel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nijkerk', 'Nijkerk gld']), ['woonplaats']] = 'Nijkerk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nieuwerbrug', 'Nieuwerbrug aan den Rijn']), ['woonplaats']] = 'Nieuwerbrug aan den Rijn'
    uitslagen.loc[uitslagen.woonplaats.isin(['Oud Beijerland', 'Oud-Beijerland']), ['woonplaats']] = 'Oud-Beijerland'
    uitslagen.loc[uitslagen.woonplaats.isin(['Oude Wetering', 'Oude-Wetering']), ['woonplaats']] = 'Oude Wetering'
    uitslagen.loc[uitslagen.woonplaats.isin(['Ouderkerk a d IJssel', 'Ouderkerk aan den IJssel', 'Ouderkerk ad IJssel', 'Ouderkerk AD IJssel', 'Ouderkerk aan den IJssel']), ['woonplaats']] = 'Ouderkerk aan den IJssel'
    uitslagen.loc[uitslagen.woonplaats.isin(['S-Graveland', 'SGraveland']), ['woonplaats']] = '\'s-Graveland'
    uitslagen.loc[uitslagen.woonplaats.isin(['Wijk bij Duurstede', 'Wijk bij duurstede', 'Wijkbeduurstede']), ['woonplaats']] = 'Wijk bij Duurstede'
    uitslagen.loc[uitslagen.woonplaats.isin(['s Hertogenbosch', 's Hertogenbosch', 'Hertogenbosch', 'S-Hertogenbosch', 'Den Bosch', 'S hertogenbosch', 's-Hertogenbosch', 'Den bosch']), ['woonplaats']] = '\'s-Hertogenbosch'
    uitslagen.loc[uitslagen.woonplaats.isin(['Kerk Avezaath']), ['woonplaats']] = 'Kerk-Avezaath'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hoogvliet']), ['woonplaats']] = 'Rotterdam'
    uitslagen.loc[uitslagen.woonplaats.isin(['Amsterdam Zuidoost', 'Amsterdam ZO']), ['woonplaats']] = 'Amsterdam'
    uitslagen.loc[uitslagen.woonplaats.isin(['s-Gravenzande', 'S-Gravenzande']), ['woonplaats']] = '\'s-Gravenzande'
    uitslagen.loc[uitslagen.woonplaats.isin(['Ouderkerk a  d Amstel']), ['woonplaats']] = 'Ouderkerk aan de Amstel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Ede gld', 'Ede (Gelderland)']), ['woonplaats']] = 'Ede'
    uitslagen.loc[uitslagen.woonplaats.isin(['Elst ut', 'Elst UT']), ['woonplaats']] = 'Elst Ut'
    uitslagen.loc[uitslagen.woonplaats.isin(['5629 RD Eindhovewn']), ['woonplaats']] = 'Eindhoven'
    uitslagen.loc[uitslagen.woonplaats.isin(['Anersfoort']), ['woonplaats']] = 'Amersfoort'
    uitslagen.loc[uitslagen.woonplaats.isin(['benschop']), ['woonplaats']] = 'Benschop'
    uitslagen.loc[uitslagen.woonplaats.isin(['Bocholt']), ['woonplaats']] = 'Bocholtz'
    uitslagen.loc[uitslagen.woonplaats.isin(['zeist']), ['woonplaats']] = 'Zeist'
    uitslagen.loc[uitslagen.woonplaats.isin(['Oude wetering']), ['woonplaats']] = 'Oude Wetering'
    uitslagen.loc[uitslagen.woonplaats.isin(['Aarle rixtel']), ['woonplaats']] = 'Aarle-Rixtel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Nieuwe wetering']), ['woonplaats']] = 'Nieuwe Wetering'
    uitslagen.loc[uitslagen.woonplaats.isin(['Zevenhuizen-Moerkapelle', 'Zevenhuizen zh']), ['woonplaats']] = 'Zevenhuizen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Loenen aan de vecht', 'Loenen ad Vecht']), ['woonplaats']] = 'Loenen aan de Vecht'
    uitslagen.loc[uitslagen.woonplaats.isin(['Almer', 'PlantijnCasparie Almere', 'Almere-Haven']), ['woonplaats']] = 'Almere'
    uitslagen.loc[uitslagen.woonplaats.isin(['De bilt']), ['woonplaats']] = 'De Bilt'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hei- en boeicop']), ['woonplaats']] = 'Hei- en Boeicop'
    uitslagen.loc[uitslagen.woonplaats.isin(['Millingen a d Rijn']), ['woonplaats']] = 'Millingen aan de Rijn'
    uitslagen.loc[uitslagen.woonplaats.isin(['Dordecht']), ['woonplaats']] = 'Dordrecht'
    uitslagen.loc[uitslagen.woonplaats.isin(['BUSSUM']), ['woonplaats']] = 'Bussum'
    uitslagen.loc[uitslagen.woonplaats.isin(['Tienhoven UT', 'Tienhoven zh', 'Tienhoven ut']), ['woonplaats']] = 'Tienhoven'
    uitslagen.loc[uitslagen.woonplaats.isin(['Katwijk aan zee']), ['woonplaats']] = 'Katwijk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Rijsenhoud']), ['woonplaats']] = 'Rijsenhout'
    uitslagen.loc[uitslagen.woonplaats.isin(['Beek-Ubbergen']), ['woonplaats']] = 'Beek'
    uitslagen.loc[uitslagen.woonplaats.isin(['Est Gem. Neerijnen', 'Est gem Neerijnen', 'Est gem.Neerijnen']), ['woonplaats']] = 'Neerijnen'
    uitslagen.loc[uitslagen.woonplaats.isin(['SOEST']), ['woonplaats']] = 'Soest'
    uitslagen.loc[uitslagen.woonplaats.isin(['WErkendam']), ['woonplaats']] = 'Werkendam'
    uitslagen.loc[uitslagen.woonplaats.isin(['Koog a d Zaan']), ['woonplaats']] = 'Koog aan de Zaan'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hoorn nh']), ['woonplaats']] = 'Hoorn'
    uitslagen.loc[uitslagen.woonplaats.isin(['Roelofsarendsveen', 'Roelofsarendveen']), ['woonplaats']] = 'Roelofarendsveen'
    uitslagen.loc[uitslagen.woonplaats.isin(['Laaren', 'Laren NH']), ['woonplaats']] = 'Laren'
    uitslagen.loc[uitslagen.woonplaats.isin(['Huis ter Heide ut']), ['woonplaats']] = 'Huis ter Heide'
    uitslagen.loc[uitslagen.woonplaats.isin(['Cuemborg']), ['woonplaats']] = 'Culemborg'
    uitslagen.loc[uitslagen.woonplaats.isin(['Geertruideberg', 'Geertrudenberg']), ['woonplaats']] = 'Geertruidenberg'
    uitslagen.loc[uitslagen.woonplaats.isin(['Winsum gn']), ['woonplaats']] = 'Winsum'
    uitslagen.loc[uitslagen.woonplaats.isin(['Den Hoorn Z-H', 'Den Hoorn ZH']), ['woonplaats']] = 'Den Hoorn'
    uitslagen.loc[uitslagen.woonplaats.isin(['Z.O. Beemster']), ['woonplaats']] = 'Zuidoostbeemster'
    uitslagen.loc[uitslagen.woonplaats.isin(['Berkel en rodenrijs']), ['woonplaats']] = 'Berkel en Rodenrijs'
    uitslagen.loc[uitslagen.woonplaats.isin(['Ravenswaay']), ['woonplaats']] = 'Ravenswaaij'
    uitslagen.loc[uitslagen.woonplaats.isin(['Sint-Michielgestel', 'Sint Michielsgestel']), ['woonplaats']] = 'Sint-Michielsgestel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Berkel Enschot']), ['woonplaats']] = 'Berkel-Enschot'
    uitslagen.loc[uitslagen.woonplaats.isin(['Beek lb']), ['woonplaats']] = 'Beek'
    uitslagen.loc[uitslagen.woonplaats.isin(['Vleuren']), ['woonplaats']] = 'Vleuten'
    uitslagen.loc[uitslagen.woonplaats.isin(['Beuningen gld']), ['woonplaats']] = 'Beuningen Gld'
    uitslagen.loc[uitslagen.woonplaats.isin(['Sint Jacobiparochie']), ['woonplaats']] = 'St.-Jacobiparochie'
    uitslagen.loc[uitslagen.woonplaats.isin(['Berlicum nb']), ['woonplaats']] = 'Berlicum'
    uitslagen.loc[uitslagen.woonplaats.isin(['Loo gld', 'Loo']), ['woonplaats']] = 'Loo Gld'
    uitslagen.loc[uitslagen.woonplaats.isin(['Voorst gem Voorst']), ['woonplaats']] = 'Voorst'
    uitslagen.loc[uitslagen.woonplaats.isin(['T Harde']), ['woonplaats']] = '\'t Harde'
    uitslagen.loc[uitslagen.woonplaats.isin(['REEUWIJK']), ['woonplaats']] = 'Reeuwijk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Rijswijk zh']), ['woonplaats']] = 'Rijswijk'
    uitslagen.loc[uitslagen.woonplaats.isin(['S-Gravenmoer']), ['woonplaats']] = '\'s Gravenmoer'
    uitslagen.loc[uitslagen.woonplaats.isin(['Langerak zh']), ['woonplaats']] = 'Langerak'
    uitslagen.loc[uitslagen.woonplaats.isin(['Heerhugowaaard']), ['woonplaats']] = 'Heerhugowaard'
    uitslagen.loc[uitslagen.woonplaats.isin(['s-Gravendeel']), ['woonplaats']] = '\'s-Gravendeel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Oosterhout nb']), ['woonplaats']] = 'Oosterhout'
    uitslagen.loc[uitslagen.woonplaats.isin(['Huizen N-H']), ['woonplaats']] = 'Huizen'
    uitslagen.loc[uitslagen.woonplaats.isin(['De Hoef']), ['woonplaats']] = 'de Hoef'
    uitslagen.loc[uitslagen.woonplaats.isin(['Noordwijk zh']), ['woonplaats']] = 'Noordwijk'
    uitslagen.loc[uitslagen.woonplaats.isin(['Son']), ['woonplaats']] = 'Son en Breugel'
    uitslagen.loc[uitslagen.woonplaats.isin(['LOPIK']), ['woonplaats']] = 'Lopik'
    uitslagen.loc[uitslagen.woonplaats.isin(['Koudekerk aan de IJssel']), ['woonplaats']] = 'Koudekerk aan den Rijn'
    uitslagen.loc[uitslagen.woonplaats.isin(['Scherpenzeel gld']), ['woonplaats']] = 'Scherpenzeel'
    uitslagen.loc[uitslagen.woonplaats.isin(['Marssum']), ['woonplaats']] = 'Ootmarsum'
    uitslagen.loc[uitslagen.woonplaats.isin(['Hoogvliet rt']), ['woonplaats']] = 'Hoogvliet Rotterdam'
    uitslagen.loc[uitslagen.woonplaats.isin(['Neerbeek']), ['woonplaats']] = 'Eerbeek'

    uitvallijst = set(uitslagen.woonplaats) - set(pd.read_csv('data/plaatsnaam_gemeente.csv').plaatsnaam)
    uitslagen.loc[uitslagen.woonplaats.isin(uitvallijst), ['woonplaats']] = np.nan

    return uitslagen
