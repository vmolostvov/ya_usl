import sqlite3
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import re
import csv

private_person = '?msp=no&p=0&text=&wizextra=ydofilters%3Dfeature%3As_features%3Aor%3Aworker_type_private'
admin_path = 'C:/Users/1/PycharmProjects/pythonProject/chromedriver_win32/chromedriver.exe'
user_path = 'C:\ya_usl\chromedriver.exe'


class Parsing:
    def __init__(self, driver, conn, url, mode):
        self.driver = driver
        self.conn = conn
        self.url = url
        self.mode = mode
        self.inf = []
        self.categories_list = []
        self.test2() if self.mode != 'y' else self.catalog()

    def catalog(self):
        self.driver.get(self.url)
        time.sleep(1)
        all_link = self.driver.find_elements_by_css_selector('a.Link')
        for link in all_link:
            try:
                if re.search('category/', link.get_attribute('href')):
                    self.categories_list.append(link.get_attribute('href'))
            except:
                pass
        for category in self.categories_list:
            try:
                self.test2(link_from_catalog=category)
            except:
                pass

    def test1(self, link_from_catalog=None):
        self.driver.get(self.url) if link_from_catalog is None else self.driver.get(link_from_catalog)
        time.sleep(5)  # время ожидания при появлении капчи на старте
        print('Ищем Еще')
        rubrics = self.driver.find_element_by_css_selector('div[class="Row Row_direction_col Filters-RubricsList Gap"]')
        elm = rubrics.find_element_by_partial_link_text('Ещё')
        if elm:
            elm.click()
            time.sleep(2)
            cats = self.driver.find_elements_by_css_selector('a[class="Link Filters-RubricItemLink"]')
            print(f'Найдено подкатегорий: {len(cats)}')
            return cats
        else:
            return 'one'

    def test2(self, link_from_catalog=None):
        categories = self.test1(link_from_catalog) if link_from_catalog is not None else self.test1()
        print('Добавляем ссылки на категории в один массив')
        if categories != 'one':
            list_of_href = []
            list_of_offers = []
            for cat in categories:
                try:
                    list_of_href.append(cat.get_attribute('href'))
                    list_of_offers.append(cat.text)
                except:
                    continue
            print(f'Получено ссылок: {len(list_of_href)}')
            category_number = 0  # здесь 0 означает первую категорию, например, если поставить 5 парсинг начнется с 6-ой категории
            for href, offer in zip(list_of_href[category_number:], list_of_offers[category_number:]):
                print(f'Начинаем парсить {offer}')
                self.start_parsing(href, offer)
        else:
            self.start_parsing()

    def start_parsing(self, href=None, offer=None):
        if href is not None:
            try:
                print(f'Переходим на категорию {offer} с фильтром по компаниям')
                self.driver.get(href + private_person)
            except:
                return 'bad'
        else:
            self.driver.get(self.driver.current_url + private_person)
        while True:
            time.sleep(3)
            cards = self.driver.find_elements_by_css_selector('a[class="Link WorkerCardMini-Title"]')
            if cards is None:
                res = self.check_captcha()
                if res == 'bad':
                    continue
                else:
                    cards = self.driver.find_elements_by_css_selector('a.Link')
            links = []
            for card in cards:
                try:
                    links.append(card.get_attribute('href'))
                except:
                    pass
            print(f'Найдено карточек: {len(links)}')
            for link in links:
                self.inf = []
                self.driver.execute_script("window.open('{}')".format(link))
                tabs = self.driver.window_handles
                self.driver.switch_to.window(tabs[1])
                try:
                    print('Пытаемся найти имя')
                    name = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((
                        By.CSS_SELECTOR, 'div[class="WorkerAbout2-Info"] .Text'))).text
                    print(name)
                except:
                    res = self.check_captcha()
                    if res == 'bad':
                        self.driver.close()
                        self.driver.switch_to.window(tabs[0])
                        continue
                    else:
                        name = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((
                            By.CSS_SELECTOR, 'div[class="WorkerAbout2-Info"] .Text'))).text
                res = self.is_in_base(name)
                if res == 'y':
                    self.driver.close()
                    self.driver.switch_to.window(tabs[0])
                    continue
                c_url = self.driver.current_url
                print(c_url)
                self.inf.append(c_url)
                self.inf.append(name)
                self.inf.append(offer)
                age = 'Отсутствует'
                try:
                    elms = self.driver.find_elements_by_class_name('WorkerAbout2-Item')
                except:
                    print('Информация не найдена! Перехожу к другой карточке')
                    continue
                for elm in elms:
                    try:
                        span = elm.find_element_by_tag_name('span')
                        if re.search('года', span.text) or re.search('лет', span.text) or \
                                re.search('год', span.text):
                            if len(span.text) < 8:
                                age = span.text
                                break
                    except:
                        pass
                print('Возраст: {}'.format(age))
                try:
                    chat = self.find_elems_by_tag_name(['button'], ['Чат'], 1, 'click')
                except:
                    self.driver.close()
                    self.driver.switch_to.window(tabs[0])
                    continue
                if chat != 'bad':
                    try:
                        res1 = self.find_elems_by_tag_name(['span'], ['Эл. почта'], 1)
                    except:
                        pass
                    if res1 != 'bad':
                        hrefs = self.driver.find_elements_by_css_selector('a.Link')

                        for href in hrefs:
                            try:
                                if re.search('mailto', href.get_attribute('href')):
                                    mail = href.get_attribute('href')
                            except:
                                pass
                    else:
                        mail = 'Отсутствует'
                    try:
                        self.inf.append(mail)
                    except:
                        pass
                    try:
                        wa_elm = self.driver.find_element_by_partial_link_text('WhatsApp')
                        tel = re.search(r'\d+', wa_elm.get_attribute('href'))
                        tel = tel.group(0)
                        print(tel)
                        self.inf.append(tel)
                        self.inf.append('WhatsApp')
                    except:
                        tel = self.take_tel()
                        if tel == 'bad':
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            continue
                    self.driver.close()
                    self.driver.switch_to.window(tabs[0])
                else:
                    mail = 'Отсутствует'
                    self.inf.append(mail)
                    tel = self.take_tel()
                    if tel == 'bad':
                        self.driver.close()
                        self.driver.switch_to.window(tabs[0])
                        continue

                self.inf.append(age)
                self.w_to_cvs()
            try:
                res = self.find_elems_by_tag_name(['span'], ['Далее'], 1, 'click')
                if res == 'bad':
                    break
            except:
                break

    def check_captcha(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.CheckboxCaptcha-Button'))).click()
        except:
            pass
        try:
            WebDriverWait(self.driver, 25).until(EC.element_to_be_clickable((By.NAME, 'rep')))
            print('Обнаружена капча!')
            time.sleep(120)  # время ожидания при появлении капчи в процессе парсинга
        except:
            return 'bad'

    def take_tel(self):
        res_tel = self.find_elems_by_tag_name(['button'], ['Телефон'], 1, 'click')
        if res_tel == 'bad':
            return 'bad'
        time.sleep(1)
        elem_b = self.driver.find_elements_by_tag_name('b')
        tel = None
        for elem in elem_b:
            if re.search('7 9', elem.text):
                tel = elem.text.replace("‑", "")
                print(tel)
                break
        if tel is None:
            return 'bad'
        try:
            self.inf.append(tel)
        except:
            pass
        self.inf.append('Подменный')

    def is_in_base(self, name1):
        cur = self.conn.cursor()
        cur.execute("SELECT Name FROM FIO")
        names = cur.fetchall()
        for name in names:
            if name[0] == name1:
                return 'y'
        cur.execute("INSERT INTO FIO VALUES (?, ?)", (name1, name1))
        self.conn.commit()
        return 'no'

    def w_to_cvs(self):
        try:
            with open('it.csv', "a", newline="") as file:  # тут можно поменять название csv файла
                writer = csv.writer(file, delimiter=';')
                writer.writerows([self.inf])
        except:
            pass

    def find_elems_by_tag_name(self, elements, elements_text, num, method1=None):
        global isGood
        isGood = False
        for j in range(num):
            for i in range(2):
                try:
                    time.sleep(2)
                    elm1 = self.driver.find_elements_by_tag_name(elements[j])
                    break
                except:
                    if i > 0:
                        print('Не могу найти элемент: {}'.format(elements[j]))
                        return 'bad'
                    time.sleep(10)

            for elm in elm1:
                if elm.text == elements_text[j]:
                    if method1 == 'click':
                        elm.click()
                    else:
                        return elm
                    isGood = True
                    break
            if isGood is False:
                print('Не могу найти элемент: {}'.format(elements_text[j]))
                return 'bad'


def main():
    y_n = input('Парсим по каталогам?(y/n):')
    url = input('Введите ссылку на каталог:') if y_n == 'y' else input('Введите ссылку на категорию:')
    connect = sqlite3.connect('names_yausl.db')
    driver = webdriver.Chrome(executable_path=admin_path)
    parse = Parsing(driver, connect, url, y_n)


if __name__ == '__main__':
    main()
