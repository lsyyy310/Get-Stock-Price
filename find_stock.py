# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
import datetime
import time
import tkinter as tk
import tkinter.font as tkFont
import tkmacosx as tkmac
import pyperclip


# text_to_copy = "This is some text that I want to copy."
# pyperclip.copy(text_to_copy)

class get_futures_data:
    def __init__(self):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " +\
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 " +\
            "Safari/605.1.15 [ip:80.95.207.194]"
        self.headers = {'User-Agent': USER_AGENT}
        self.today = datetime.datetime.now()
        # self.today = datetime.datetime(2023, 6, 16)

        # clock
        start = time.time()
        self.get_futures_name()
        # 確認日期
        self.days_ago = self.today - datetime.timedelta(days=50)
        if self.days_ago.isoweekday() in (6, 7):
            difference = 8 - self.days_ago.isoweekday()
            self.days_ago += datetime.timedelta(days=difference)

        self.write_in_csv()
        end = time.time()
        self.run_time = end - start

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
        path = Path(__file__).parent.joinpath(f"Futures_{self.today.strftime('%y%m%d')}.csv")
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

    def __init__(self, name):
        tk.Tk.__init__(self)
        self.geometry("500x250")
        self.configure(bg="white")
        self.title(name)

        self.get_data()

        self.bgcanvas = tk.Canvas(
            self, width=500, height=250, bg="white", bd=0, highlightthickness=0
        )
        self.bgcanvas.grid(row=0, column=0, sticky="nsew")

        self.my_font1 = tkFont.Font(family=show_rank.Font, size=35, weight="bold")
        self.my_font2 = tkFont.Font(family=show_rank.Font, size=20, weight="bold")
        self.Label1 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text="Welcome~", font=self.my_font1
        )
        self.Label2 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text="資料已處理完畢", font=self.my_font1
        )
        self.Label3 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text=f"用時{self.create_data.run_time:0.2f}s", font=self.my_font2
        )
        self.Label1_w = self.bgcanvas.create_window(
            250, 40, width=300, height=50, window=self.Label1
        )
        self.Label2_w = self.bgcanvas.create_window(
            250, 95, width=300, height=50, window=self.Label2
        )
        self.Label3_w = self.bgcanvas.create_window(
            250, 155, width=300, height=30, window=self.Label3)


        self.n = 0
        self.next = tkmac.Button(
            self.bgcanvas,
            text="NEXT",
            font=self.my_font2,
            bg="white",
            fg="black",
            bd=1,
            borderless=True,
            highlightthickness=3,
            highlightcolor="black",
            focuscolor="",
            width=100,
            height=50,
            cursor="hand1",
            command=lambda: self.show_company(self.n),
        )

        self.show_on_tk()
        self.next_w = self.bgcanvas.create_window(
            250, 200, width=100, height=40, window=self.next
        )


    def get_data(self):
        self.create_data = get_futures_data()
        path = Path(__file__).parent.joinpath(f"Futures_{self.today.strftime('%y%m%d')}.csv")
        fh = open(path, "r", encoding="utf-8")
        reader = csv.DictReader(fh)
        self.good_com = {}
        for row in reader:
            if row["公司"] == "備註":
                break
            else:
                rate = float(row["漲幅"][:-1])
                if rate <= 0:
                    continue
                else:
                    self.good_com[row["公司"]] = [row["代號"], rate]
        fh.close()

        self.rank = sorted(self.good_com.keys(), key=lambda c: -self.good_com[c][1])
        # 取前30
        self.rank = self.rank[:31]

    def show_on_tk(self):
        time.sleep(1)
        self.show_company(0)

    def show_company(self, n):
        if n < 30:
            company = self.rank[n]
            symbol = self.good_com[company][0]
            # print(company, symbol)
            self.Label1.config(text=f"{n + 1}. {company}")
            self.Label2.config(text=symbol)
            self.Label3.config(text=f"成長率{self.good_com[company][1]}%")
            pyperclip.copy(symbol)
            self.n += 1
        else:
            self.Label1.config(text="Thanks~")
            self.Label2.config(text="任務完成！")
            self.Label3.config(text="")



App = show_rank("Heyyyyy~")
App.mainloop()


