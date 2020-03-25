import pandas as pd
import random
import re

import IJsselsteinloop

def test_get_urls():
    assert len(IJsselsteinloop.get_urls(2003, 2019)) == 253, "Should be 253"

def test_get_results():
    assert IJsselsteinloop.get_results(IJsselsteinloop.get_urls(2003, 2003)[:2]).shape == (242, 7), "Should be (242, 7)"

def test_get_data_2002():
    assert IJsselsteinloop.get_data_2002().shape == (301, 7), "Should be (20, 7)"

def test_get_data_2001():
    assert IJsselsteinloop.get_data_2001().shape == (20, 7), "Should be (20, 7)"

def test_get_data_1999():
    assert IJsselsteinloop.get_data_1999().shape == (6, 7), "Should be (6, 7)"

def test_get_data_2000():
    assert IJsselsteinloop.get_data_2000().shape == (20, 7), "Should be (20, 7)"

def test_get_data():
    assert IJsselsteinloop.get_data_2002().shape == (301, 7), "Should be (20, 7)"

def test_ophalen_data():
    assert IJsselsteinloop.ophalen_data(2019).shape == (27175, 7), "Should be (27175, 7)"

def test_category():
    assert IJsselsteinloop.category(25, [10, 20, 30, 40, 50]) == 30, "Should be 30"

def test_category_labels():
    assert IJsselsteinloop.category_labels([10, 20, 30, 40, 50]) == {10: '1 - 10', 20: '11 - 20', 30: '21 - 30', 40: '31 - 40', 50: '41 - 50'}, "Should be {10: '1 - 10', 20: '11 - 20', 30: '21 - 30', 40: '31 - 40', 50: '41 - 50'}"

def test_time_to_seconds():
    assert IJsselsteinloop.time_to_seconds('12:34:56') == 45296, "Should be 45296"

def test_nettotijd():
    assert sum([bool(re.match('0[0-6]:[0-5][0-9]:[0-5][0-9]', tijd)) for tijd in IJsselsteinloop.nettotijd(pd.DataFrame({'nettotijd': ['01.23.45', '01:23:45']})).nettotijd]) == 2

def test_gemeente():
    assert IJsselsteinloop.gemeenten(pd.DataFrame({'startnummer': [random.randint(0, 9999) for _ in range(20)], 'woonplaats': ['Zevenhuizen', 'Hoorn', 'Laren', 'Noordwijk', 'Beek', 'Scherpenzeel', 'Oosterhout', 'Achterveld', 'Nes', 'Voorst', 'Alphen', 'Buren', 'Den Hoorn', 'Huis ter Heide', 'Baarlo', 'Velp', 'Winsum', 'Klarenbeek', 'Rossum', 'Serooskerke'], 'jaar': random.choices(range(2000, 2004), k=20), 'afstand': random.choices(['5 km', '10 km', '21.1 km'], k=20), 'klassement': random.choices(['Damesklassement', 'Herenklassement'], k=20)})).shape[0] == 20, "Should be 20"

