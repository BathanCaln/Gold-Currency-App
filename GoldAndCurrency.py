# BATUHAN ÇALIN 1221602018
import ssl
ssl._create_default_https_context = ssl._create_stdlib_context
import json
from tkinter import *
import sqlite3
from datetime import datetime
import http.client
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

conn = http.client.HTTPSConnection("api.collectapi.com")

headers = {
    'content-type': "application/json",
    'authorization': "apikey 6HhDfEVyKoL4fp0hbjQfUa:04BvAwFAyzfzNyB9qv9N26"
}

currency_rates = {}
gold_rates = {}

try:
    conn.request("GET", "/economy/currencyToAll?int=10&base=USD", headers=headers)
    res = conn.getresponse()
    data = res.read()
    currency_rates = json.loads(data.decode("utf-8"))["result"]

    conn.request("GET", "/economy/goldPrice", headers=headers)
    res = conn.getresponse()
    data = res.read()
    gold_rates = json.loads(data.decode("utf-8"))["result"].get("buying", 0)

except http.client.HTTPException as e:
    print(f"HTTP Exception: {e}")

except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

class DataBaseOperation:
    def __init__(self):
        self.baglanti = sqlite3.connect("datasForCurrency.db")
        self.cursor = self.baglanti.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Currency(
            tarih TEXT,
            dolar REAL,
            euro REAL,
            altin REAL)  
        """)

        self.baglanti.commit()

    def add_data(self, dolar, euro, altin):
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO Currency VALUES (?, ?, ?, ?)",
                            (tarih, dolar, euro, altin))

        self.baglanti.commit()
        print("Veriler Kaydedildi. :)")

    def update_data(self, dolar, euro, altin):
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("UPDATE Currency SET dolar=?, euro=?, altin=? WHERE tarih=?",
                            (dolar, euro, altin, tarih))
        self.baglanti.commit()
        print("Veriler Güncellendi ;)")

    def get_data(self):
        self.cursor.execute("SELECT * FROM Currency ORDER BY tarih")
        datas = self.cursor.fetchall()
        for data in datas:
            print(f"Tarih: {data[0]}, Dolar: {data[1]}, Euro: {data[2]}, Altın:{data[3]}")

    def get_data_by_date(self, selected_date):
        self.cursor.execute("SELECT * FROM Currency WHERE tarih LIKE ?",
                            (selected_date + "%",))
        datas = self.cursor.fetchall()
        for data in datas:
            print(f"Tarih: {data[0]}, Dolar: {data[1]}, Euro: {data[2]}, Altın:{data[3]}")

    def getTotalAssets(self):
        self.cursor.execute("SELECT SUM(dolar), SUM(euro), SUM(altin) FROM Currency")
        total_assets = self.cursor.fetchone()
        return total_assets if total_assets else(0, 0, 0)

    def get_data_for_plotting(self):
        self.cursor.execute("SELECT * FROM Currency ORDER BY tarih")
        datas = self.cursor.fetchall()
        return datas

    def calculate_profit_loss(self):
        self.cursor.execute("SELECT * FROM Currency ORDER BY tarih")
        datas = self.cursor.fetchall()
        for i in range(len(datas) - 1):
            if isinstance(datas[i][3], str) and isinstance(datas[i + 1][3], str):
                try:
                    date_start = datetime.strptime(str(datas[i][3]), "%Y-%m-%d %H:%M:%S")
                    date_end = datetime.strptime(datas[i + 1][3], "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    print(f'Hatalı tarih değeri: {datas[i][3]}, Hata: {str(e)}')
                    continue
                except NameError:
                    print("Hata: 'e' ismi tanımlanmadı :(")
            else:
                print("Hatalı tarih değeri: Veri formatı uygun değil")
                continue

            days = (date_end - date_start).days

            dolar_profit_loss = (datas[i + 1][0] - datas[i][0]) * days
            euro_profit_loss = (datas[i + 1][1] - datas[i][1]) * days
            altin_profit_loss = (datas[i + 1][2] - datas[i][2]) * days

            print(f"Tarih Aralığı: {date_start} - {date_end}")
            print(
                f"Dolar Kar/Zararı: {dolar_profit_loss:.2f} TL, Yüzdesi: {(dolar_profit_loss / datas[i][0]) * 100:.2f}%")
            print(f"Euro Kar/Zararı: {euro_profit_loss:.2f} TL, Yüzdesi: {(euro_profit_loss / datas[i][1]) * 100:.2f}%")
            print(
                f"Altın Kar/Zararı: {altin_profit_loss:.2f} TL, Yüzdesi: {(altin_profit_loss / datas[i][2]) * 100:.2f}%")
            print()

    def close_baglanti(self):
        self.baglanti.close()

class App:
    def __init__(self, mainn):
        self.mainn = mainn
        self.mainn.title("Döviz & Altın Takip Uygulaması")

        self.label_dolar = Label(mainn, text="Dolar", font="Calibri")
        self.label_dolar.pack()
        self.entry_dolar = Entry(mainn)
        self.entry_dolar.pack()

        self.label_euro = Label(mainn, text="Euro", font="Calibri")
        self.label_euro.pack()
        self.entry_euro = Entry(mainn)
        self.entry_euro.pack()

        self.label_gold = Label(mainn, text="Altın", font="Calibri")
        self.label_gold.pack()
        self.entry_gold = Entry(mainn)
        self.entry_gold.pack()

        self.button_kaydet = Button(mainn, text="Kaydet", command=self.save_datas)
        self.button_kaydet.pack()

        self.button_guncelle = Button(mainn, text="Güncelle", command=self.update_datas)
        self.button_guncelle.pack()

        self.button_getir = Button(mainn, text="Verileri Getir", command=self.get_datas)
        self.button_getir.pack()

        self.button_karzarar = Button(mainn, text="Kar/Zarar Hesapla", command=self.calculate_profit_loss)
        self.button_karzarar.pack()

        self.label_total_assets = Label(mainn, text="Toplam Varlık: 0TL", font="Calibri")
        self.label_total_assets.pack()

        self.veritabani = DataBaseOperation()
        self.update_rates()
        self.get_total_assets()

    def save_datas(self):
        dolar = float(self.entry_dolar.get())
        euro = float(self.entry_euro.get())
        altin = float(self.entry_gold.get())

        self.veritabani.add_data(dolar, euro, altin)
        self.entry_dolar.delete(0, END)
        self.entry_euro.delete(0, END)
        self.entry_gold.delete(0, END)

    def update_datas(self):
        dolar_text = self.entry_dolar.get()
        if dolar_text:
            dolar = float(dolar_text)
        else:
            dolar = 0.0

        euro_text = self.entry_euro.get()
        if euro_text:
            euro = float(euro_text)
        else:
            euro = 0.0

        altin = float(self.entry_gold.get())

        self.veritabani.update_data(dolar, euro, altin)
        self.entry_dolar.delete(0, END)
        self.entry_euro.delete(0, END)
        self.entry_gold.delete(0, END)

    def get_datas(self):
        self.veritabani.get_data()
        self.get_total_assets()

    def calculate_profit_loss(self):
        self.veritabani.calculate_profit_loss()

    def get_total_assets(self):
        total_assets = self.veritabani.getTotalAssets()
        self.label_total_assets.config(text=f"Toplam Varlık: {total_assets[0]: .2f}TL")

    def update_rates(self):
        dolar_buying = float(currency_rates.get("USD", {}).get("buying", 0))
        euro_buying = float(currency_rates.get("EUR", {}).get("buying", 0))
        gold_buying = float(gold_rates.get("buying", 0))

        self.entry_dolar.delete(0, END)
        self.entry_dolar.insert(0, dolar_buying)
        self.entry_euro.delete(0, END)
        self.entry_euro.insert(0, euro_buying)
        self.entry_gold.delete(0, END)
        self.entry_gold.insert(0, gold_buying)

    def plot_asset_changes(self):
        data_points = self.veritabani.get_data_for_plotting()

        if len(data_points) <= 1:
            print("Grafik çizilebilecek yeterli veri noktası bulunamadı.")
            return

        dates = [datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S") for data in data_points]
        dolar_values = [data[0] for data in data_points]
        euro_values = [data[1] for data in data_points]
        altin_values = [data[2] for data in data_points]

        dolar_changes = [0]
        euro_changes = [0]
        altin_changes = [0]

        for i in range(1, len(data_points)):
            dolar_change = (dolar_values[i] - dolar_values[i - 1]) / (i - 1)
            euro_change = (euro_values[i] - euro_values[i - 1]) / (i - 1)
            altin_change = (altin_values[i] - altin_values[i - 1]) / (i - 1)

            dolar_changes.append(dolar_change)
            euro_changes.append(euro_change)
            altin_changes.append(altin_change)

        plt.plot(dates, dolar_changes, label='Dolar')
        plt.plot(dates, euro_changes, label='Euro')
        plt.plot(dates, altin_changes, label='Altın')

        plt.xlabel('Tarih')
        plt.ylabel('Değişim Oranı')
        plt.title('Varlık Değişim Oranları')
        plt.legend()

        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.mainn)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def close_app(self):
        self.veritabani.close_baglanti()
        self.mainn.destroy()

root = Tk()
app = App(root)
root.protocol("WM_DELETE_WINDOW", app.close_app)
root.mainloop()
