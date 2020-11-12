import bs4
import requests
import re
import logging
import shutil

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

logging.debug('Start of a program')

wikipedia_url = 'https://pl.wikipedia.org/'
africa_countries_url = 'https://pl.wikipedia.org/wiki/Kategoria:Pa%C5%84stwa_w_Afryce'

res = requests.get(africa_countries_url)
res.raise_for_status()

countries_html_list = bs4.BeautifulSoup(res.text, 'html.parser')

africa = []

# name_regex = re.compile(r'[\w\s]')
address_regex = re.compile(r'href="/(wiki/[\w%]*)')
digit_regex = re.compile(r'>([\d\stys]*)<')
area_regex = re.compile(r'>([\d\s,]*[\styskm²]*)<')
flag_regex = re.compile(r'//upload.wikimedia.org/wikipedia/commons/thumb/[\w\d\-_%./]*.png')


def print_list_of_dicts(list):
    for country in list:
        print("Name:\t\t" + country["name"])
        print("Capital:\t" + str(country["capital"]))
        print("Population:\t" + country["population"])
        print("Area:\t\t" + country["area"])
        print("Flag:\t\t" + country["flag"])
        print("Emblem:\t\t" + country["emblem"])
        print("Url:\t\t" + country["url"])
        print("")


def find_name(text):
    county = {
        "name": text
    }
    africa.append(county)

    return text


def find_address(text, name):
    address = address_regex.findall(text)

    for country in africa:
        if country['name'] == name:
            country.update({'url': wikipedia_url + address[0]})

    return wikipedia_url + address[0]


def find_details(url, name):
    res_country = requests.get(url)
    res_country.raise_for_status()

    country_page_html = bs4.BeautifulSoup(res_country.text, "html.parser")

    label_image = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(1) > div > a > img')
    emblem = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td:nth-child(2) > a > img')
    for i in range(1,15):
        label_link = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(1) > a')
        label_not_link = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(1)')
        if label_link:
            logging.debug(label_link[0].text)
            if label_link[0].text == 'Stolica':
                logging.info(name + ": ")
                value = country_page_html.select( '#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(2) > a')
                capitals = []
                for j in range(0, len(value)):          # Drukuj wszystkie stolice
                    logging.info("Capital: " + value[j].text + " ")
                    for country in africa:
                        if country['name'] == name:
                            capitals.append(value[j].text)
                            country.update({'capital': capitals})
        #print(label_not_link[0].text)
        if "Liczba ludności" in label_not_link[0].text:
            value_ = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(2)')
            # print(label_not_link[0].text)
            result = digit_regex.findall(str(value_[0]))
            amount = "".join(result).strip()
            for country in africa:
                if country['name'] == name:
                    country.update({'population': amount})
            logging.info("Population: " + amount)
        elif "Powierzchnia" in label_not_link[0].text:
            value_ = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(2)')
            # print(label_not_link[0].text)
            result = area_regex.findall(str(value_[0]))
            amount = "".join(result).strip()
            for country in africa:
                if country['name'] == name:
                    country.update({'area': amount})
            logging.info("Area: " + amount)
    flag = flag_regex.findall(str(label_image[0]))
    logging.info(flag[2])
    emblem = flag_regex.findall(str(emblem[0]))
    logging.info(emblem[2])
    for country in africa:
        if country['name'] == name:
            country.update({'flag': flag[2]})
            country.update({'emblem': emblem[2]})

            # save_images('http:' + flag[2], 'flags', name)
            # save_images('http:' + emblem[2], 'emblems', name)


def save_images(url, kind, name):
    res = requests.get(url, stream=True)
    res.raise_for_status()

    res.raw.decode_content = True

    with open(kind + '/' + name + '.png', 'wb') as f:
        shutil.copyfileobj(res.raw, f)


for sekcja in range(2, 20):
    for pozycja in range(1, 8):
        country_in_html = countries_html_list.select('#mw-pages > div > div > div:nth-child(' + str(sekcja) + ') > ul > li:nth-child(' + str(pozycja) + ') > a')

        if country_in_html:
            name = find_name(country_in_html[0].text)
            address = find_address(str(country_in_html[0]), name)
            find_details(address, name)


print_list_of_dicts(africa)

