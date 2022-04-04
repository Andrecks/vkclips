
import datetime
import os.path
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def open_chrome():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    return driver


def scroll_down_url(group_name):
    filepath = ('/Users/nick/Downloads/Telegram Desktop/'
                f'project/_vkparser/urls/{group_name}/'
                f'{group_name}_all_clips')
    urls_directory = os.path.join(os.getcwd(), 'urls')
    final_directory = os.path.join(urls_directory, group_name)
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    if os.path.exists(filepath):
        update_list = input('обновить список ссылок? y/n: ')
        if update_list == 'y':
            pass
        elif update_list == 'n':
            return
    driver = open_chrome()
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
    create_url_list(driver, group_name)
    driver.close()
    return


def create_url_list(driver, group):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    html_output_name = ('/Users/nick/Downloads/Telegram Desktop/'
                        f'project/_vkparser/urls/{group}/'
                        f'{group}_all_clips')
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
        print('Дата не введена или введена через жопу, '
              'используется сегоднящняя дата...')
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
        raw_date = date_codes[raw_date[0]]

    day = raw_date[0]
    month = month_codes[raw_date[1]]
    year = raw_date[2]
    date_input = f'{day}.{month}.{year}'
    date_format = date_entry(date_input)
    if date >= date_format and not f:
        return True
    else:
        return date > date_format


def search_dates(date1, date2, group):
    driver = open_chrome()
    m1 = m2 = 0
    f1 = f2 = False
    counter = 0
    filename = ('/Users/nick/Downloads/Telegram Desktop/'
                f'project/_vkparser/urls/{group}/'
                f'{group}_all_clips')
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


def url_output(date1, date2, group, lines):
    filename = ('/Users/nick/Downloads/Telegram Desktop/'
                f'project/_vkparser/urls/{group}/'
                f'{group}_all_clips')
    crimefile = open(filename, 'r')
    full_list = [line.strip('\n') for line in crimefile.readlines()]
    if date1 != date2:
        output_list_file = ('/Users/nick/Downloads/Telegram Desktop/'
                            f'project/_vkparser/urls/{group}/ '
                            f'{group} clips {date1} - {date2}')
    else:
        output_list_file = ('/Users/nick/Downloads/Telegram Desktop/'
                            f'project/_vkparser/urls/{group}/ '
                            f'{group} clips {date1}')

    with open(output_list_file, 'w') as f:
        for i in range(len(full_list)):
            if i >= lines[0] and i <= lines[1]:
                f.write(full_list[i] + '\n')
    crimefile = open(output_list_file, 'r')
    full_list = [line.strip('\n') for line in crimefile.readlines()]
    if len(full_list) == 0:
        print('КЛИПОВ.НЕТ')
        os.remove(output_list_file)


if __name__ == '__main__':
    current_directory = os.getcwd()
    final_directory = os.path.join(current_directory, 'urls')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    group_name = input('Введи url-название группы или ее id: ')
    date1 = date_entry(input('Введите первую дату (в формате DD.MM.YY) : '))
    date2 = date_entry(input('Введите вторую дату (в формате DD.MM.YY) : '))
    scroll_down_url(group_name)
    lines = search_dates(date1, date2, group_name)
    url_output(date1, date2, group_name, lines)
