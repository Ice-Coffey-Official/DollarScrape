from util.config import baseURL, saveName, saveAs
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
page = requests.get(baseURL, headers=headers)

soup = BeautifulSoup(page.text, 'lxml')

mylinks = soup.findAll("a", { "class" : "ga_w2gi_lp" })

states = []
cities = []
stores = []
pandasList = [['Store Name', 'Store Number', 'Phone Number', 'Address', 'Url', 'Longitude', 'Latitude', 'City', 'State']]

print('Extracting State Links...')
for i in tqdm(range(len(mylinks))):
    link = mylinks[i]
    stateLink = link['href']
    states.append(stateLink) if stateLink.startswith(baseURL) else False

print('Extracting City Links...')
for j in tqdm(range(len(states))):
    link = states[j]
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')
    mylinks = soup.findAll("a", { "class" : "ga_w2gi_lp" })
    for cityHref in mylinks:
        cityLink = cityHref['href']
        cities.append(cityLink) if (cityLink.startswith(baseURL) and len(cityLink) > len(baseURL)) else False

print('Extracting Store Links...')
for k in tqdm(range(len(cities))):
    link = cities[k]
    page = requests.get(link, headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')
    mylinks = soup.findAll("a", { "class" : "bold_blue" })
    for l in mylinks:
        storeLink = l['href']
        stores.append(storeLink) if storeLink.startswith(baseURL) else False

print('Extracting Store Information...')
for x in tqdm(range(len(stores))):
    store = stores[x]
    page = requests.get(store, headers=headers)
    soup = BeautifulSoup(page.text, 'lxml')
    mylinks = soup.findAll("script", { "type" : "application/ld+json" })
    storeNum = store.split('/')[-2]
    city = store.split('/')[-3]
    state = store.split('/')[-4]
    name = soup.find("h1", { "class" : "h1_custom" }).text
    phoneNumber = soup.find("a", { "class" : "phonelink ga_w2gi_lp" }).text

    spanStreet = soup.find("span", { "itemprop" : "streetAddress" }).text
    spanCity = soup.find("span", { "itemprop" : "addressLocality" }).text
    spanState = soup.find("span", { "itemprop" : "addressRegion" }).text
    spanPostal = soup.find("span", { "itemprop" : "postalCode" }).text
    spanCountry = soup.find("span", { "itemprop" : "addressCountry" }).text
    address = "{street}\n{city} {state}, {postal} {country}".format(street = spanStreet, city = spanCity, state = spanState, postal = spanPostal, country = spanCountry)
    latitude = None
    longitude = None
    for l in mylinks:
        scriptText = l.text
        if '"latitude":' in scriptText and '"longitude":' in scriptText:
            splittextLat = scriptText.split('"latitude":')
            splittextLong = scriptText.split('"longitude":')
            latitude = splittextLat[-1].split(',')[0].split('\n')[0]
            longitude = splittextLong[-1].split(',')[0].split('\n')[0]
            break
        else:
            continue

    pandasList.append([name, storeNum, phoneNumber, address, store, longitude, latitude, city, state])

print('Saving...')
df = pd.DataFrame(pandasList[1:],columns=pandasList[0])

if('csv' in saveAs):
    df.to_csv('{data}.csv'.format(data=saveName), index=False)
if('excel' in saveAs):
    df.to_excel("{data}.xlsx".format(data=saveName), index=False)
