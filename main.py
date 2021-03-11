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
        time.sleep(15)
        kat = self.driver.find_element_by_xpath('//*[@id="app"]/div/div[1]/div/div/div/div/div[2]/div[2]/div/div[3]/div[1]/div/div')
        time.sleep(3)
        elms = kat.find_elements_by_tag_name('a')
        print(len(elms))
        return elms

    def test2(self):
        categories = self.test1()
        for cat in categories[1:]:
            print(cat.get_attribute('href'))
            self.driver.get(cat.get_attribute('href') + '&wizextra=ydofilters%3Dfeature%3As_features%3Aor%3Aworker_type_private')
            offer = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div[1]/div/div/div/div/div[1]/div/h1'))).text
            for i in range(9):
                time.sleep(3)
                cards = self.driver.find_elements_by_css_selector('a.Link')
                if cards is None:
                    self.check_captcha()
                    cards = self.driver.find_elements_by_css_selector('a.Link')
                links = []
                for card in cards:
                    try:
                        if re.search('/profile/', card.get_attribute('href')):
                            links.append(card.get_attribute('href'))
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
                        self.check_captcha()
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
                    chat = self.find_elems_by_tag_name(['button'], ['Чат'], 1, 'click')
                    if chat != 'bad':
                        res1 = self.find_elems_by_tag_name(['span'], ['Эл. почта'], 1)
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
                            print(mail)
                        except:
                            pass
                        res2 = self.find_elems_by_tag_name(['span'], ['WhatsApp'], 1, 'click')
                        if res2 != 'bad':
                            tabs = self.driver.window_handles
                            self.driver.switch_to.window(tabs[2])
                            try:
                                tel = WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main_block"]/div[1]/h1/p/span'))).text
                                print(tel)
                            except:
                                self.check_captcha()
                                tel = WebDriverWait(self.driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main_block"]/div[1]/h1/p/span'))).text
                            self.inf.append(tel)
                            self.driver.close()
                            self.driver.switch_to.window(tabs[1])
                            self.driver.close()
                            self.driver.switch_to.window(tabs[0])
                        else:
                            tel = self.take_tel(tabs)
                            if tel == 'bad':
                                continue

                    else:
                        tel = self.take_tel(tabs)
                        if tel == 'bad':
                            continue
                    self.w_to_cvs()
                self.find_elems_by_tag_name(['span'], ['Далее'], 1, 'click')

    def check_captcha(self):
        try:
            WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.NAME, 'rep')))
            print('Обнаружена капча!')
            time.sleep(30)
        except:
            pass

    def take_tel(self, tabs):
        res_tel = self.find_elems_by_tag_name(['button'], ['Телефон'], 1, 'click')
        if res_tel == 'bad':
            self.driver.close()
            self.driver.switch_to.window(tabs[0])
            return 'bad'
        time.sleep(1)
        elem_b = self.driver.find_elements_by_tag_name('b')
        for elem in elem_b:
            if re.search('7 9', elem.text):
                tel = elem.text.replace("‑", "")
                print(tel)
        self.driver.close()
        self.driver.switch_to.window(tabs[0])
        try:
            self.inf.append(tel)
        except:
            pass
        self.inf.append('Да')

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
        with open('it.csv', "a", newline="") as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerows([self.inf])

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
    driver = webdriver.Chrome(executable_path='путь до драйвер')
    parse = Parsing(driver, connect, url)


if __name__ == '__main__':
    main()