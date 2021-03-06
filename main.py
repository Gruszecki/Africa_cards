import bs4
import requests
import re
import logging
import shutil
from PIL import Image, ImageDraw, ImageFont
from selenium import webdriver
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

logging.debug('Start of a program')

card_fill = (255, 250, 210)

wikipedia_url = 'https://pl.wikipedia.org/'
africa_countries_url = 'https://pl.wikipedia.org/wiki/Kategoria:Pa%C5%84stwa_w_Afryce'

res = requests.get(africa_countries_url)
res.raise_for_status()

countries_html_list = bs4.BeautifulSoup(res.text, 'html.parser')

# name_regex = re.compile(r'[\w\s]')
address_regex = re.compile(r'href="/(wiki/[\w%]*)')
digit_regex = re.compile(r'>([\d\stys]*)<')
area_regex = re.compile(r'>([\d\s,]*[\styskm²]*)<')
flag_regex = re.compile(r'//upload.wikimedia.org/wikipedia/commons/thumb/[\w\d\-_%./]*.png')



def go(continent):
    for sekcja in range(2, 20):
        for pozycja in range(1, 8):
            country_in_html = countries_html_list.select(
                '#mw-pages > div > div > div:nth-child(' + str(sekcja) + ') > ul > li:nth-child(' + str(
                    pozycja) + ') > a')

            if country_in_html:
                name = find_name(continent, country_in_html[0].text)
                address = find_address(continent, str(country_in_html[0]), name)
                find_details(continent, address, name)

    for country in continent:
        if country["name"] == "Kongo":
            country["area"] = country["area"][:-4]


def print_list_of_dicts(continent):
    for country in continent:
        print("Name:\t\t" + country["name"])
        print("Capital:\t" + str(country["capital"]))
        print("Population:\t" + country["population"])
        print("Area:\t\t" + country["area"])
        print("Motto:\t\t" + country["motto"])
        print("Flag:\t\t" + country["flag"])
        print("Emblem:\t\t" + country["emblem"])
        print("Url:\t\t" + country["url"])
        print("")


def find_name(continent, text):
    county = {
        "name": text
    }
    continent.append(county)

    return text


def find_address(continent, text, name):
    address = address_regex.findall(text)

    for country in continent:
        if country['name'] == name:
            country.update({'url': wikipedia_url + address[0]})

    return wikipedia_url + address[0]


def find_details(continent, url, name):
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
                    for country in continent:
                        if country['name'] == name:
                            capitals.append(value[j].text)
                            country.update({'capital': capitals})


        #print(label_not_link[0].text)
        if "Liczba ludności" in label_not_link[0].text:
            value_ = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(2)')
            # print(label_not_link[0].text)
            result = digit_regex.findall(str(value_[0]))
            amount = "".join(result).strip()
            for country in continent:
                if country['name'] == name:
                    country.update({'population': amount})
            logging.info("Population: " + amount)
        elif "Powierzchnia" in label_not_link[0].text:
            value_ = country_page_html.select('#mw-content-text > div.mw-parser-output > table.infobox > tbody > tr:nth-child(' + str(i) + ') > td:nth-child(2)')
            # print(label_not_link[0].text)
            result = area_regex.findall(str(value_[0]))
            amount = "".join(result).strip()
            for country in continent:
                if country['name'] == name:
                    country.update({'area': amount})
            logging.info("Area: " + amount)

    flag = flag_regex.findall(str(label_image[0]))
    logging.info(flag[2])
    emblem = flag_regex.findall(str(emblem[0]))
    logging.info(emblem[2])
    for country in continent:
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


def draw_a_card(side='front'):
    img = Image.new('RGB', (900, 1350))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (900, 1350)], fill=card_fill, outline=0, width=50)

    if side == 'front':
        coor_elephant = (70, 1080)
        elephant_foreground = Image.open('elephant_1.png')
        elephant_foreground = elephant_foreground.resize((int(elephant_foreground.width*0.3), int(elephant_foreground.height*0.3)))
        # coor_elephant = (70, 920)
        # elephant_foreground = Image.open('elephant_2.png')
        # elephant_foreground = elephant_foreground.resize((int(elephant_foreground.width*0.25), int(elephant_foreground.height*0.25)))
        elephant_foreground.load()
        elephant = Image.new('RGB', elephant_foreground.size, card_fill)
        elephant.paste(elephant_foreground, mask=elephant_foreground.split()[3])
        img.paste(elephant, coor_elephant)
    else:
        font_signature  = ImageFont.truetype("fonts/AmaticSC-Regular.ttf", 40)
        coor_signature = (400, 1250)
        draw = ImageDraw.Draw(img)
        draw.text(coor_signature, "Gruszecki", font=font_signature, fill=0)

    return img


def insert_details(img, country):
    font_name       = ImageFont.truetype("fonts/huxtable.ttf", 80)     # 70
    font_name_small = ImageFont.truetype("fonts/huxtable.ttf", 65)     # 55
    font_details    = ImageFont.truetype("fonts/huxtable.ttf", 50)     # 40
    font_motto      = ImageFont.truetype("fonts/huxtable.ttf", 40)     # 40
    coor_name       = (100, 100)
    coor_capital    = (100, 660)    # 550
    coor_area       = (100, 740)    # 630
    coor_population = (100, 820)    # 710
    coor_flag       = (100, 250)
    coor_emblem     = (537, 250)
    coor_map        = (470, 941)
    coor_motto      = (100, 550)    # 790
    resize_factor   = 1.4

    flag = Image.open('flags/' + country['name'] + '.png')
    emblem = Image.open('emblems/' + country['name'] + '.png')
    map = Image.open('maps/' + country['name'] + '.png')

    if country['name'] == 'Somalia':
        flag = flag.resize((int(flag.width * 0.8), int(flag.height * 0.8)))
    if country['name'] == 'Niger':
        flag = flag.resize((int(flag.width * 1.2), int(flag.height * 1.2)))
    else:
        flag = flag.resize((int(flag.width*resize_factor), int(flag.height*resize_factor)))

    flag_background = Image.new("RGB", (flag.width+4, flag.height+4))
    flag_background.paste(flag, (2, 2))
    map = map.resize((int(map.width*0.6), int(map.height*0.6)))

    if country['name'] == 'Botswana':
        emblem = emblem.resize((int(emblem.width*1.2), int(emblem.height*1.2)))
    elif country['name'] == 'Eswatini':
        emblem = emblem.resize((int(emblem.width * 1.6), int(emblem.height * 1.6)))
    elif country['name'] == 'Ghana':
        emblem = emblem.resize((int(emblem.width * 1.6), int(emblem.height * 1.6)))
    elif country['name'] == 'Niger':
        emblem = emblem.resize((int(emblem.width*0.17), int(emblem.height*0.17)))
    elif country['name'] == 'Nigeria':
        emblem = emblem.resize((int(emblem.width * 1.5), int(emblem.height * 1.5)))
    elif country['name'] == 'Mauritius':
        emblem = emblem.resize((int(emblem.width * 1.6), int(emblem.height * 1.6)))
    elif country['name'] == 'Tunezja':
        emblem = emblem.resize((int(emblem.width*1.2), int(emblem.height*1.2)))
    elif country['name'] == 'Somalia':
        emblem = emblem.resize((int(emblem.width * 1.8), int(emblem.height * 1.8)))
    elif country['name'] == 'Wybrzeże Kości Słoniowej':
        emblem = emblem.resize((int(emblem.width * 1.6), int(emblem.height * 1.6)))
    else:
        emblem = emblem.resize((int(emblem.width*resize_factor), int(emblem.height*resize_factor)))

    emblem_x = int(100 + flag.width + (900 - 100 - flag.width - 50 - emblem.width) / 2)

    if country['name'] == "Tunezja":
        coor_emblem = (emblem_x, 200)
    elif country['name'] == "Egipt":
        coor_emblem = (emblem_x, 200)
    elif country['name'] == "Gwinea":
        coor_emblem = (emblem_x, 200)
    else:
        coor_emblem = (emblem_x, 250)



    emblem.load()
    emblem_background = Image.new("RGB", emblem.size, card_fill)

    if len(emblem.split()) == 4:
        emblem_background.paste(emblem, mask=emblem.split()[3])
    else:
        img.paste(emblem, coor_emblem)

    draw = ImageDraw.Draw(img)
    img.paste(flag_background, coor_flag)
    img.paste(emblem_background, coor_emblem)
    img.paste(map, coor_map)

    if len(country["name"]) <= 18:
        draw.text(coor_name, country['name'], fill=0, font=font_name)
    elif len(country["name"]) <= 23:
        draw.text(coor_name, country['name'], fill=0, font=font_name_small)
    elif country["name"] == "Wyspy Świętego Tomasza i Książęca":
        draw.text(coor_name, "Wyspy Świętego Tomasza \ni Książęca", fill=0, font=font_details)
    else:
        draw.text(coor_name, country['name'], fill=0, font=font_details)

    draw.text(coor_capital, 'Stolica: ' + ', '.join(country['capital']), fill=0, font=font_details)
    draw.text(coor_area, 'Powierzchnia: ' + country['area'], fill=0, font=font_details)
    draw.text(coor_population, 'Liczba ludności: ' + country['population'], fill=0, font=font_details)
    draw.text(coor_motto, 'Dewiza:\n' + country['motto'], fill=0, font=font_motto)


def prepare_qr(continent):
    url = 'https://www.qr-online.pl/index.php'

    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    for country in continent:
        text_box = browser.find_element_by_css_selector('#qr_url > div.form-group > div > input')
        text_box.clear()
        text_box.send_keys(country['url'])

        size_checkbox = browser.find_element_by_css_selector(
            '#msgtopdiv > div:nth-child(1) > div.col-md-9 > div.panel.panel-primary > div.panel-body > form > div.form-group > div:nth-child(4) > select')
        size_checkbox.send_keys('10')

        button = browser.find_element_by_css_selector(
            '#msgtopdiv > div:nth-child(1) > div.col-md-9 > div.panel.panel-primary > div.panel-body > form > div.form-group > div.col-sm-1 > input')
        button.click()

        time.sleep(2)

        browser.save_screenshot('qrs/' + country['name'] + '.png')

        qr_code = browser.find_element_by_css_selector(
            '#msgtopdiv > div:nth-child(1) > div.col-md-9 > div.contentBox > div:nth-child(1) > img')
        qr_code_location = qr_code.location
        qr_code_size = qr_code.size

        x = qr_code_location['x']
        y = qr_code_location['y']
        width = x + qr_code_size['width']
        height = y + qr_code_size['height']

        qr_code_image = Image.open('qrs/' + country['name'] + '.png')
        qr_code_image = qr_code_image.crop((int(x), int(y), int(width), int(height)))
        qr_code_image.save('qrs/' + country['name'] + '.png')

    browser.close()


def get_map(continent):
    url = 'https://www.google.com/maps/'

    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    for country in continent:
        text_box = browser.find_element_by_css_selector('#searchboxinput')
        text_box.clear()
        text_box.send_keys(country['name'] + '\n')

        time.sleep(2)

        button = browser.find_element_by_css_selector('#widget-zoom-out')
        for i in range(7):
            button.click()

        time.sleep(3)

        browser.save_screenshot('maps/' + country['name'] + '.png')

    browser.close()


def get_motto(continent):
    url = 'https://pl.wikiquote.org/wiki/Dewizy_pa%C5%84stwowe,_narodowe_i_regionalne'

    res = requests.get(url)
    res.raise_for_status()

    mottos_list = bs4.BeautifulSoup(res.text, 'html.parser')

    with open('mottos.txt', 'w') as f:
        for country in continent:
            for i in range(4, 109):
                name = mottos_list.select('#mw-content-text > div.mw-parser-output > ul:nth-child(' + str(i) + ') > li > a')
                if len(name) > 0:
                    if name[0].text.strip() == country['name']:
                        logging.info('Country found: ' + country['name'])
                        f.write(country['name'] + ': \n')


def get_motto(continent, file):
    with open(file, 'r') as f:

        mottos_regex = re.compile((r'([\w\s]*): ([\w\s,–\-]*)'))
        for line in f:
            for country in continent:
                motto = mottos_regex.findall(line)
                if country['name'].strip() == motto[0][0].strip():
                    logging.debug(country['name'] + " motto: " + motto[0][1].strip())
                    country.update({'motto': motto[0][1].strip()})


def insert_qr(img, country):
    qr = Image.open('qrs/' + country['name'] + '.png')
    qr = qr.resize((400, 400))
    coor_qr = (int(img.width/2 - qr.width/2), 350)
    img.paste(qr, coor_qr)


def prepare_front(continent):
    for country in continent:
        img = draw_a_card()
        insert_details(img, country)
        img.save("cards/" + country['name'] + ".png", "PNG")


def prepare_back(continent):
    for country in continent:
        img = draw_a_card('back')
        insert_qr(img, country)
        img.save("back/" + country['name'] + ".png", "PNG")


# Zbieranie informacji
africa = []
go(africa)
get_motto(africa, 'mottos.txt')

# Dodatkowe (jednokrotne)
# get_map(africa)
# prepare_qr(africa)

# Kreowanie kart
prepare_front(africa)
# prepare_back(africa)

# print_list_of_dicts(africa)
