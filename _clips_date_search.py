
import datetime
import os.path
import time
import shutil

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def get_public_list(n: int, ids: list, flag: str,
                    date1: datetime, date2: datetime,
                    search_date_time: datetime):

    driver = open_chrome()
    f = False
    if flag == 'y':
        f = True
    groups_directory = create_path('groups/')
    if not os.path.exists(groups_directory):
        os.makedirs(groups_directory)
    for id in ids:
        filepath = groups_directory + f'{id}_all_clips'
        if not(os.path.exists(filepath)) or f:
            scroll_down_url(id, driver, search_date_time)
        lines = search_dates(date1, date2, id, driver, search_date_time)
        url_output(date1, date2, id, lines, search_date_time)


def create_path(path):
    pwd = os.getcwd()
    path = os.path.join(pwd, path)
    return path


def open_chrome():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver


def scroll_down_url(group_name, driver, search_date_time):
    driver.get(f"https://vk.com/clips/{group_name}")
    time.sleep(3)
    scroll_pause_time = 1
    screen_height = driver.execute_script("return window.screen.height;")
    i = 1
    while True:
        driver.execute_script(
            "window.scrollTo(0, {screen_height}*{i});".format(
                screen_height=screen_height, i=i))
        i += 1
        time.sleep(scroll_pause_time)
        scroll_height = driver.execute_script(
            "return document.body.scrollHeight;")
        if (screen_height) * i > scroll_height:
            break
    return create_url_list(driver, group_name, search_date_time)


def create_url_list(driver, group, search_date_time):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    filepath = f'groups/{group}_all_clips'
    # html_output_name = (os.path.join(os.getcwd(), filepath))
    html_output_name = create_path(filepath)
    with open(html_output_name, 'w') as f:
        for parent in soup.find_all(class_="ShortVideoGridItem"):
            base = "https://www.vk.com"
            link = parent.attrs['href']
            f.write(base + link + '\n')
    return


def date_entry(date_input):
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    try:
        day, month, year = map(int, date_input.split('.'))
    except ValueError:
        print(f'DATA BBEDEHA HE BEPHO, 6YDET {datetime.date.today()}')
    if year < 2000:
        year += 2000
    return datetime.date(year, month, day)


def date_check(raw_date, date, f):
    today = datetime.date.today()
    month_codes = {'янв': 1,
                   'фев': 2,
                   'мар': 3,
                   'апр': 4,
                   'май': 5,
                   'июн': 6,
                   'июл': 7,
                   'авг': 8,
                   'сен': 9,
                   'окт': 10,
                   'ноя': 11,
                   'дек': 12}
    date_codes = {'сегодня': today,
                  'вчера': today - datetime.timedelta(days=1)}
    if raw_date[0] in date_codes.keys():
        date_format = date_codes[raw_date[0]]
    else:
        day = raw_date[0]
        month = month_codes[raw_date[1]]
        year = raw_date[2]
        date_input = f'{day}.{month}.{year}'
        date_format = date_entry(date_input)
    if date >= date_format and not f:
        return True
    else:
        return date > date_format


def search_dates(date1, date2, group, driver, search_date_time):
    m1 = m2 = 0
    f1 = f2 = False
    counter = 0
    filename = create_path(f'groups/{group}_all_clips')
    crimefile = open(filename, 'r')
    url_list = [line.strip('\n') for line in crimefile.readlines()]
    for url in url_list:
        driver.get(url)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        raw_date = soup.find(class_='VerticalVideoLayerInfo__date')
        raw_date = raw_date.contents[0].split()
        if not f1:
            clip_date_check = date_check(raw_date, date2, f1)
            if clip_date_check:
                f1 = True
                m1 = counter
        if f1 and (not f2):
            clip_date_check = date_check(raw_date, date1, f1)
            if clip_date_check:
                f2 = True
                m2 = counter - 1
        elif f1 and f2:
            return [m1, m2]
        counter += 1
    if f1 and (not f2):
        return [m1, len(url_list)-1]
    return [0, len(url_list)-1]


def url_output(date1, date2, group, lines, search_date_time):
    filename = create_path(f'groups/{group}_all_clips')
    crimefile = open(filename, 'r')
    full_list = [line.strip('\n') for line in crimefile.readlines()]
    if date1 != date2:
        output_list_file = create_path(f'search_history/{search_date_time}/'
                                       f'{group} clips {date1} - {date2}')
    else:
        output_list_file = create_path(f'search_history/{search_date_time}/'
                                       f'{group} clips {date1}')

    with open(output_list_file, 'w') as f:
        for i in range(len(full_list)):
            if i >= lines[0] and i <= lines[1]:
                f.write(full_list[i] + '\n')
    crimefile = open(output_list_file, 'r')
    full_list = [line.strip('\n') for line in crimefile.readlines()]
    if len(full_list) == 0:
        print('!!! KJINIIOB B {group} NE HANDEHO !!!')
    return


def unite_search_results(search_directory):
    file_output = create_path(f'{search_directory}' + 'full_list')
    with open(file_output, 'wb') as outfile:
        for filename in os.listdir(search_directory):
            if filename == file_output:
                # don't want to copy the output into the output
                continue
            with open(search_directory+filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, outfile)
    return


if __name__ == '__main__':
    groups_directory = create_path('groups')
    if not os.path.exists(groups_directory):
        os.makedirs(groups_directory)
    n = int(input('CKOJLKO IIA6JLNKOV?: '))
    print('KOIINIIACTN CIINCOK: ')
    group_list = [input().strip() for i in range(n)]
    flag = str(input('O6HOBNTb CIINCKN KJINIIOB?: [y/n]: '))
    date1 = date_entry(input('BBEDI IIEPBYU DATY (DD.MM.YY): '))
    date2 = date_entry(input('BBEDI BTORYU DATY (DD.MM.YY): '))
    search_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    search_directory = create_path(f'search_history/{search_date_time}/')
    if not os.path.exists(search_directory):
        os.makedirs(search_directory)
    get_public_list(n, group_list, flag, date1, date2, search_date_time)
    unite_search_results(search_directory)
