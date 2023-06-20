# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import datetime
import time
import tkinter as tk
import tkinter.font as tkFont
import pyperclip


# text_to_copy = "This is some text that I want to copy."
# pyperclip.copy(text_to_copy)

class get_futures_data:
    def __init__(self):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " +\
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 " +\
            "Safari/605.1.15 [ip:80.95.207.194]"
        self.headers = {'User-Agent': USER_AGENT}
        # self.today = datetime.datetime.now()
        self.today = datetime.datetime(2023, 6, 19)

        self.get_futures_name()
        # 確認日期
        self.days_ago = self.today - datetime.timedelta(days=50)
        if self.days_ago.isoweekday() in (6, 7):
            difference = 8 - self.days_ago.isoweekday()
            self.days_ago += datetime.timedelta(days=difference)

        self.write_in_csv()

    def get_futures_name(self):
        url = "https://www.taifex.com.tw/cht/2/stockLists"
        raw_data = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(raw_data.text, "html.parser")
        tr_tags = soup.find_all("tr")

        self.company_name = {}
        n = 0
        for tag in tr_tags:
            n += 1
            if n < 3 or n == 260:
                continue
            else:
                attributes = {"style": "text-align: left"}
                company = tag.find_all("td", attrs=attributes)[1]
                attributes = {"align": "center"}
                symbol = tag.find_all("td", attrs=attributes)[1]
                self.company_name[company.text] = symbol.text

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
        while days_ago_price is None:
            # print(self.days_ago)
            self.days_ago += datetime.timedelta(days=1)
            days_ago_price = find_date(self, self.days_ago)

        return today_price, days_ago_price

    def write_in_csv(self):
        # open file abd write header
        path = Path(__file__).parent.joinpath(f"Futures_\
            {self.today.strftime('%y%m%d')}.csv")
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

        # turn to string
        today_str = self.today.strftime("%Y-%m-%d")
        days_ago_str = self.days_ago.strftime("%Y-%m-%d")
        writer.writerow({
            "公司": "備註",
            "股價 (50 Days ago)": f"50天前日期：{days_ago_str}",
            "股價 (Today)": f"今天日期：{today_str}"
            })
        fh.close()

class show_rank(tk.Tk):
    Font = "Hannotate TC"
    BG_color = "#E8E9DC"
    Text_color = "#606153"

    def __init__(self, name):
        create_data = get_futures_data()
        self.geometry("300x200")
        self.configure(bg=BG_color)
        self.title(name)

        self.my_font = tkFont.Font(family=Font, size=12, weight="bold")
        self.Label = tk.Label(self, width=250, height=160, bg=BG_color, text="", font=self.my_font)




App = show_rank("Heyyyyy~")

