# -*- coding: utf-8 -*-
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import datetime
import time


class get_stock_data:
    def __init__(self, date_required):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " +\
                     "AppleWebKit/605.1.15 (KHTML, like Gecko) " +\
                     "Version/16.5.2 Safari/605.1.15"
        self.headers = {'User-Agent': USER_AGENT}
        self.today = date_required

        # clock
        start = time.time()
        self.get_stock_name()
        # 確認日期
        self.days_ago = self.today - datetime.timedelta(days=50)
        if self.days_ago.isoweekday() in (6, 7):
            difference = 8 - self.days_ago.isoweekday()
            self.days_ago += datetime.timedelta(days=difference)

        self.write_in_csv()
        end = time.time()
        self.run_time = end - start

    def get_stock_name(self):
        def selectAndGet(index0, index1):
            url = "https://mops.twse.com.tw/mops/web/t51sb01"
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(("name", "code")), "Time Limit Exceed!")
            optionMenu0 = Select(driver.find_element(
                "xpath", "//*[@id=\"search\"]/table/tbody/tr/td/select[1]"
            ))
            optionMenu0.select_by_index(index0)
            time.sleep(3)

            optionMenu1 = Select(driver.find_element(
                "name", "code"
            ))
            optionMenu1.select_by_index(index1)
            ele_searchButton = driver.find_element(
                "xpath", "//*[@id=\"search_bar1\"]/div/input"
            )
            ele_searchButton.click()
            ele_table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(("xpath", "//*[@id=\"div01\"]/table[2]/tbody")),
                "Time Limit Exceed!"
            )
            rawData = ele_table.get_attribute("innerHTML")
            return rawData

        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # options.add_experimental_option("detach", True)
        options.add_argument("--headless")
        headers = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
        options.add_argument(f"user-agent={headers}")
        driver = webdriver.Chrome(executable_path="./chromedriver", options=options)

        # 上市
        tse_rawData = selectAndGet(0, 0)
        # 上櫃
        otc_rawData = selectAndGet(1, 0)
        driver.quit()


        tse_soup = BeautifulSoup(tse_rawData, "html.parser")
        otc_soup = BeautifulSoup(otc_rawData, "html.parser")
        tr_tags = tse_soup.find_all("tr") + otc_soup.find_all("tr")

        self.company_name = {}
        for tag in tr_tags:
            td_tags = tag.find_all("td")
            if len(td_tags) == 0:
                continue
            else:
                company = td_tags[2]
                symbol = td_tags[0]
                self.company_name[company.text.strip()] = symbol.text.strip()
        print("number:", len(self.company_name))

    def get_price_stock(self, symbol) -> str:
        def find_date(self, date):
            # turn to string
            mingguo = date.year - 1911
            date_str = str(mingguo) + date.strftime("/%m/%d")
            url = f"https://stock.wearn.com/cdata.asp?year={date.year - 1911}&month={date.month:02d}&kind={symbol}"
            data = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(data.text, "html.parser")
            tr_tags = soup.find_all("tr")
            tr_tags = tr_tags[2:-1]
            for tag in tr_tags:
                td_tags = tag.find_all("td")
                if td_tags[0].text == date_str:
                    text = "".join(td_tags[4].text.split())
                    return text

        today_price = find_date(self, self.today)
        days_ago_price = find_date(self, self.days_ago)
        try_round = 1
        while today_price is None:
            if try_round > 10:
                break
            else:
                changed_today = self.today - datetime.timedelta(days=try_round)
                today_price = find_date(self, changed_today)
                try_round += 1

        try_round = 1
        while days_ago_price is None:
            if try_round > 10:
                break
            else:
                # print(self.days_ago)
                changed_days_ago = self.days_ago - datetime.timedelta(days=try_round)
                days_ago_price = find_date(self, changed_days_ago)
                try_round += 1

        return today_price, days_ago_price

    def write_in_csv(self):
        # open file abd write header
        path = Path(__file__).parent.joinpath(f"Stock_{self.today.strftime('%y%m%d')}.csv")
        fh = open(path, "w", newline="", encoding="utf-8")
        fieldnames = [
            "公司",
            "代號",
            "股價 (50 Days ago)",
            "股價 (Today)",
            "漲幅"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        n = 0
        for c in list(self.company_name.keys()):
            print(n, c)
            n += 1
            try:
                today_price, days_ago_price = self.get_price_stock(
                    self.company_name[c])
                # 成長率
                rate = ((float(today_price.replace(",", "")) -
                         float(days_ago_price.replace(",", ""))) /
                        float(days_ago_price.replace(",", ""))) * 100
                c_data = {
                    "公司": c,
                    "代號": self.company_name[c],
                    "股價 (50 Days ago)": days_ago_price,
                    "股價 (Today)": today_price,
                    "漲幅": f"{rate:0.2f}%"}
                writer.writerow(c_data)
            except AttributeError:
                print("Not Found Such Data")
                pass

        # turn to string
        today_str = self.today.strftime("%Y-%m-%d")
        days_ago_str = self.days_ago.strftime("%Y-%m-%d")
        writer.writerow({
            "公司": "備註",
            "股價 (50 Days ago)": f"50天前日期：{days_ago_str}",
            "股價 (Today)": f"今天日期：{today_str}"
            })
        fh.close()

if __name__ == '__main__':
    today = datetime.datetime.now()
    start = get_stock_data(today)