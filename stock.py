# -*- coding: utf-8 -*-
import requests
import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import datetime
import time


class get_stock_data:
    def __init__(self, date_required):
        self.USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15"
        self.headers = {"User-Agent": self.USER_AGENT}
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
        # key: company, value: symbol
        self.company_name = {}
        twse_url = lambda mode: f"https://isin.twse.com.tw/isin/C_public.jsp?strMode={mode}"

        options = Options()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"user-agent={self.USER_AGENT}")
        # options.add_experimental_option("detach", True)  # show browser, for test
        chromedriver_path = Path(__file__).parent.joinpath("./chromedriver")
        chrome_service = Service(chromedriver_path)
        browser = selenium.webdriver.Chrome(options=options, service=chrome_service)
    
        url_1, url_2 = twse_url(2), twse_url(4)  # 上市, 上櫃
        for url in (url_1, url_2):
            browser.get(url)
            names_table = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(("xpath", "/html/body/table[2]/tbody")), "Time Limit Exceed!")
            source_code = BeautifulSoup(names_table.get_attribute("innerHTML"), "html.parser")
        
            tr_rows = source_code.find_all("tr")
            find_stock_row = False
            for row in tr_rows:
                td_tags = row.find_all("td")
                if find_stock_row is False:
                    find_stock_row = True if row.text.find("股票") != -1 else False
                    continue
                elif len(td_tags) != 7:
                    break
                else:
                    symbol, company = td_tags[0].text.split()
                    self.company_name[company] = symbol

        browser.quit()
        print("The number of companies:", len(self.company_name))

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
            print(f"{n} {c} ({self.company_name[c]})")
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
            "股價 (50 Days ago)": f"50 天前日期：{days_ago_str}",
            "股價 (Today)": f"今天日期：{today_str}"
            })
        fh.close()

if __name__ == "__main__":
    today = datetime.datetime(2025, 2, 25)
    # today = datetime.datetime.now()
    start = get_stock_data(today)