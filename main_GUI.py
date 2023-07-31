import tkinter as tk
import tkinter.font as tkFont
import tkmacosx as tkmac
import csv
from pathlib import Path
import datetime
import time
import pyperclip
from find_stock import get_futures_data

Font = "BiauKaiTC"

class mainApp(tk.Tk):
    def __init__(self, name):
        tk.Tk.__init__(self)
        self.geometry("500x250")
        self.configure(bg="white")
        self.title(name)

        # creating a container
        self.container = tk.Frame(self)
        self.container.pack(expand=True, fill="both")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.page1 = Page1(self.container, self)
        self.page1.grid(row=0, column=0, sticky="nsew")
        self.page1.tkraise()


class Page1(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=500, height=250, bg="white")
        self.controller = controller

        self.bgcanvas = tk.Canvas(
            self, width=500, height=250, bg="white", bd=0, highlightthickness=0
        )
        self.bgcanvas.grid(row=0, column=0, sticky="nsew")

        self.my_font1 = tkFont.Font(family=Font, size=25, weight="bold")
        self.my_font2 = tkFont.Font(family=Font, size=12, weight="bold")
        self.my_font3 = tkFont.Font(family=Font, size=20, weight="bold")
        self.Label1 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text="Welcome~", font=self.my_font1
        )
        # 下拉選單
        now = datetime.datetime.now()
        year = [now.year - 1, now.year]
        month = list(
            map(lambda m: "%02d" % m, list(range(1, 13)))
        )
        day = list(
            map(lambda d: "%02d" % d, list(range(1, 32)))
        )

        self.Label_y = tk.Label(
            self.bgcanvas, width=80, height=30, bg="white", fg="black",
            text="Year", font=self.my_font2
        )
        self.value_y = tk.StringVar()
        self.value_y.set(now.year)
        self.select_y = tk.OptionMenu(
            self.bgcanvas,
            self.value_y,
            *year
        )

        self.Label_m = tk.Label(
            self.bgcanvas, width=80, height=30, bg="white", fg="black",
            text="Month", font=self.my_font2
        )
        self.value_m = tk.StringVar()
        self.value_m.set(now.month)
        self.select_m = tk.OptionMenu(
            self.bgcanvas,
            self.value_m,
            *month,
        )
        self.Label_d = tk.Label(
            self.bgcanvas, width=80, height=30, bg="white", fg="black",
            text="Day", font=self.my_font2
        )
        self.value_d = tk.StringVar()
        self.value_d.set(now.day)
        self.select_d = tk.OptionMenu(
            self.bgcanvas,
            self.value_d,
            *day,
        )
        for menu in (self.select_y, self.select_m, self.select_d):
            menu["bg"]="white"
            menu["fg"]="black"
            menu["activeforeground"]="gray"

        self.start = tkmac.Button(
            self.bgcanvas,
            text="開始處理資料",
            font=self.my_font2,
            bg="white",
            fg="black",
            bd=1,
            borderless=True,
            activebackground="#9BAA9D",
            highlightthickness=1,
            highlightcolor="black",
            focuscolor="",
            width=110,
            height=50,
            cursor="hand1",
            command=lambda: self.create_page2(),
        )
        self.bgcanvas.create_window(
            250, 40, width=300, height=50, window=self.Label1
        )
        self.bgcanvas.create_window(
            125, 100, width=80, height=30, window=self.Label_y
        )
        self.bgcanvas.create_window(
            140, 130, width=80, height=30, window=self.select_y
        )
        self.bgcanvas.create_window(
            235, 100, width=80, height=30, window=self.Label_m
        )
        self.bgcanvas.create_window(
            250, 130, width=80, height=30, window=self.select_m
        )
        self.bgcanvas.create_window(
            345, 100, width=80, height=30, window=self.Label_d
        )
        self.bgcanvas.create_window(
            360, 130, width=80, height=30, window=self.select_d
        )
        self.bgcanvas.create_window(
            250, 180, width=100, height=30, window=self.start
        )

    def create_page2(self):
        try:
            self.controller.date_required = datetime.datetime(
                int(self.value_y.get()),
                int(self.value_m.get()),
                int(self.value_d.get()),
            )
            if self.controller.date_required.isoweekday() in (6, 7):
                raise ValueError("You Selected the Date Which\nis Sat. or Sun.")

            self.controller.page2 = Page2(self.controller.container, self.controller)
            self.controller.page2.grid(row=0, column=0, sticky="nsew")
            self.controller.page2.tkraise()

        except ValueError as error:
            self.Label1.config(text=str(error).title(), font=self.my_font3)


class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, width=500, height=250, bg="white")
        self.controller = controller

        self.bgcanvas = tk.Canvas(
            self, width=500, height=250, bg="white", bd=0, highlightthickness=0
        )
        self.bgcanvas.grid(row=0, column=0, sticky="nsew")

        self.my_font1 = tkFont.Font(family=Font, size=35, weight="bold")
        self.my_font2 = tkFont.Font(family=Font, size=20, weight="bold")
        self.Label1 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text="Welcome~", font=self.my_font1
        )
        self.Label2 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text="資料處理完畢", font=self.my_font1
        )
        self.bgcanvas.create_window(
            250, 40, width=300, height=50, window=self.Label1
        )
        self.bgcanvas.create_window(
            250, 95, width=300, height=50, window=self.Label2
        )

        self.get_data()
        self.n = 0
        self.rank = sorted(self.good_com.keys(), key=lambda c: -self.good_com[c][1])
        # 取前30
        self.rank = self.rank[:31]

        self.Label3 = tk.Label(
            self.bgcanvas, width=350, height=50, bg="white", fg="black",
            text=f"用時 {self.create_data.run_time:0.2f} s", font=self.my_font2
        )
        self.bgcanvas.create_window(
            250, 155, width=300, height=30, window=self.Label3
        )

        self.next = tkmac.Button(
            self.bgcanvas,
            text="NEXT",
            font=self.my_font2,
            bg="white",
            fg="black",
            bd=1,
            borderless=True,
            activebackground="#9BAA9D",
            highlightthickness=1,
            highlightcolor="black",
            focuscolor="",
            width=100,
            height=50,
            cursor="hand1",
            command=lambda: self.show_company(self.n),
        )
        self.bgcanvas.create_window(
            250, 200, width=100, height=40, window=self.next
        )

    def get_data(self):
        self.create_data = get_futures_data(self.controller.date_required)
        path = Path(__file__).parent.joinpath(f"Futures_{self.controller.date_required.strftime('%y%m%d')}.csv")
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

    def show_company(self, n):
        if n < 30:
            company = self.rank[n]
            symbol = self.good_com[company][0]

            self.Label1.config(text=f"{n + 1}. {company}")
            self.Label2.config(text=symbol)
            self.Label3.config(text=f"成長率{self.good_com[company][1]}%")
            pyperclip.copy(symbol)
            self.n += 1
        else:
            self.Label1.config(text="Thanks~")
            self.Label2.config(text="任務完成！")
            self.Label3.config(text="")


App = mainApp("Heyyyyy~")
App.mainloop()


