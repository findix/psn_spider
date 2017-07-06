#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Spider of PlayStation Store, read by website. Black history"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup

from game_info import GameInfo, get_session
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class PsnSpider(object):
    """PSN Spider"""

    def __init__(self, init_driver=True):
        if init_driver:
            self.driver = webdriver.Chrome()
        self.session = get_session()

    def get_list(self, start_url):
        """从列表爬取信息"""
        first_page_i = 18
        last_page_i = 25
        url = start_url + str(first_page_i)
        self.get_page(url)
        first_of_last_list = None
        for page_i in range(first_page_i, last_page_i + 1):
            while True:
                body_content = self.get_bs()
                game_info_page_urls = body_content.find_all(
                    "a", "permalink")
                if not game_info_page_urls:
                    sleep(1)
                    continue
                first = game_info_page_urls[0]["href"]
                if first_of_last_list is None or game_info_page_urls and first != first_of_last_list:
                    first_of_last_list = first
                    break
                print("[Warning]", first, "and",
                      first_of_last_list, "are the same")
                sleep(3)
            for a in game_info_page_urls:
                url = "https://store.playstation.com/" + a["href"]
                cid = self.get_cid_from_url(url)
                if self.session.query(GameInfo).filter(GameInfo.cid == cid).first() is None:
                    g = GameInfo(cid=cid, url=url,
                                 update_datetime=datetime.now())
                    self.session.add(g)
            self.session.commit()
            print("# parsed list in page:", page_i)
            self.next_page()  # 加载下一页
        self.driver.close()

    def get_bs(self):
        """获取BeautifulSoup"""
        return BeautifulSoup(self.driver.page_source, "lxml")

    def get_cid_from_url(self, url):
        """从url中提取cid"""
        return url[-36:]

    def next_page(self):
        """加载下一页"""
        nav_link_next = self.driver.find_elements_by_class_name(
            "navLinkNext")[0]
        try:
            nav_link_next.click()
        except WebDriverException:
            print("[Error] WebDriverException")
        sleep(1)

    def get_all_info(self):
        """遍历 list 获取 game info"""
        game_infos = self.session.query(GameInfo)
        for i, game_info in enumerate(game_infos):
            self.get_info(game_info)
            print(i, game_info.name, "is finished")
        self.driver.close()

    def get_info(self, game_info):
        """获取信息"""
        self.get_page(game_info.url)
        while self.driver.find_elements_by_css_selector(
                'div[data-model-id="{0}"]'.format(game_info.cid)) is None:
            sleep(1)
        name_element = self.driver.find_element_by_css_selector(
            "h1.productTitle")
        genre_elements = self.driver.find_elements_by_xpath(
            r"//div[h2='Genre']/ul/li")
        content_type_element = self.driver.find_element_by_css_selector(
            "div.contentType")
        num_of_reviews_elements = self.driver.find_elements_by_css_selector(
            "span.numOfReviews")
        provider_element = self.driver.find_element_by_css_selector(
            "div.provider")
        release_date_elements = self.driver.find_elements_by_css_selector(
            "span[itemprop='releaseDate']")

        game_info.name = name_element.text
        game_info.genre = ",".join(map(lambda e: e.text, genre_elements))
        game_info.content_type = content_type_element.text
        game_info.num_of_reviews = int(num_of_reviews_elements[0].get_attribute(
            "content")) if num_of_reviews_elements else None
        game_info.provider = provider_element.text
        game_info.release_date = datetime.strptime(release_date_elements[0].get_attribute(
            "content"), '%Y-%m-%d') if release_date_elements else None
        game_info.update_datetime = datetime.now()
        self.session.commit()

    def get_page(self, url, sleep_time=5):
        """
        Get the page and raise if status_code is not equal to 200
        :param url(string): url
        :param sleep_time(int): Time to wait until take the data (default 5s)
        """

        self.driver.get(url)
        sleep(sleep_time)
        while self.driver.find_elements_by_class_name("show-wait"):
            assert "PlayStation®Store" in self.driver.title
            print("Fail, sleep_time = ", sleep_time)
            sleep(1)
            sleep_time += 1


def main():
    """ Main"""
    url = 'https://store.playstation.com/#!/en-us/all-ps4-games/cid=STORE-MSF77008-PS4ALLGAMESCATEG|game_content_type~games:platform~ps4|/'
    # url = 'https://store.playstation.com/#!/en-us/games/god-of-war/cid=UP9000-CUSA07408_00-00000000GODOFWAR'
    psnspider = PsnSpider()
    psnspider.get_list(url)
    # psnspider.get_all_info()


if __name__ == '__main__':
    main()
