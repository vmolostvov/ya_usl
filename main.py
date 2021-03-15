import sqlite3
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import re
import csv


class Parsing:
    def __init__(self, driver, conn, url):
        self.driver = driver
        self.conn = conn
        self.url = url

        self.inf = []
        self.test2()

    def test1(self):
        self.driver.get(self.url)
        time.sleep(5)  # время ожидания при появлении капчи на старте'
        ilist = [[3], [2], '']
        for i in ilist:
            try:
                kat = self.driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div/div/div/div/div[2]/div[2]/div/div{}/div[1]/div/div'.format(i))
            except:
                pass
        time.sleep(2)
        elms = kat.find_elements_by_tag_name('a')
        elms[-1].click() if re.match('Ещё', elms[-1].text) else elms
        for i in ilist:
            try:
                kat = self.driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div/div/div/div/div[2]/div[2]/div/div{}/div[1]/div/div'.format(i))
            except:
                pass
        time.sleep(2)
        elms = kat.find_elements_by_tag_name('a')
        return elms

    def test2(self):
        categories = self.test1()
        list_of_href = []
        for cat in categories:
            try:
                list_of_href.append(cat.get_attribute('href'))
            except:
                continue
        for href in list_of_href[2:]:  # здесь 0 означает первую категорию, например, если поставить 5 парсинг начнется с 6-ой категории
            try:
                self.driver.get(href + '?msp=no&p=0&text=&wizextra=ydofilters%3Dfeature%3As_features%3Aor%3Aworker_type_private')
            except:
                continue
            try:
                offer = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/div/div/div/div/div[1]/div/h1'))).text
            except:
                res = self.check_captcha()
                if res == 'bad':
                    continue
                else:
                    offer = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@id="app"]/div/div[1]/div/div/div/div/div[1]/div/h1'))).text
            for i in range(9):
                time.sleep(3)
                cards = self.driver.find_elements_by_css_selector('a.Link')
                if cards is None:
                    res = self.check_captcha()
                    if res == 'bad':
                        continue
                    else:
                        cards = self.driver.find_elements_by_css_selector('a.Link')
                links = []
                for card in cards:
                    try:
                        if re.search('/profile/', card.get_attribute('href')):
                            try:
                                links.append(card.get_attribute('href'))
                            except:
                                pass
                    except:
                        pass
                for link in links[::4]:
                    self.inf = []
                    self.driver.execute_script("window.open('{}')".format(link))
                    tabs = self.driver.window_handles
                    self.driver.switch_to.window(tabs[1])
                    try:
                        name = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/div/div/div/div/div[1]/div/div[1]/div/div[1]/div[1]/div[2]/b'))).text
                    except:
                        res = self.check_captcha()
                        if res == 'bad':
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            continue
                        else:
                            name = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/div/div/div/div/div[1]/div/div[1]/div/div[1]/div[1]/div[2]/b'))).text
                    res = self.is_in_base(name)
                    if res == 'y':
                        self.driver.close()
                        self.driver.switch_to.window(tabs[0])
                        continue
                    print(name)
                    c_url = self.driver.current_url
                    print(c_url)
                    self.inf.append(c_url)
                    self.inf.append(name)
                    self.inf.append(offer)
                    age = 'Отсутствует'
                    try:
                        elms = self.driver.find_elements_by_class_name('WorkerAbout2-Item')
                        for elm in elms:
                            span = elm.find_element_by_tag_name('span')
                            print(span.text)
                            if re.search('года', span.text) or re.search('лет', span.text) or \
                                    re.search('год', span.text):
                                if len(span.text) < 7:
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
                            res2 = self.find_elems_by_tag_name(['span'], ['WhatsApp'], 1, 'click')
                        except:
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            continue
                        if res2 != 'bad':
                            tabs = self.driver.window_handles
                            self.driver.switch_to.window(tabs[2])
                            try:
                                tel = WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main_block"]/div[1]/h1/p/span'))).text
                                print(tel)
                            except:
                                res = self.check_captcha()
                                if res == 'bad':
                                    self.driver.close()
                                    self.driver.switch_to.window(tabs[0])
                                    continue
                                else:
                                    tel = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main_block"]/div[1]/h1/p/span'))).text
                            self.inf.append(tel)
                            self.inf.append('WhatsApp')
                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                        else:
                            tel = self.take_tel(tabs)
                            if tel == 'bad':
                                self.driver.close()
                                self.driver.switch_to.window(tabs[0])
                                continue

                    else:
                        mail = 'Отсутствует'
                        self.inf.append(mail)
                        tel = self.take_tel(tabs)
                        if tel == 'bad':
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                            continue

                    self.inf.append(age)
                    self.w_to_cvs()
                try:
                    self.find_elems_by_tag_name(['span'], ['Далее'], 1, 'click')
                except:
                    pass

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

    def take_tel(self, tabs):
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
        self.driver.close()
        self.driver.switch_to.window(tabs[0])
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
    url = input('Введите ссылку:')
    connect = sqlite3.connect('names_yausl.db')
    driver = webdriver.Chrome(executable_path='C:\ya_usl\chromedriver.exe')
    parse = Parsing(driver, connect, url)


if __name__ == '__main__':
    main()
