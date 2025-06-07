# %%
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from tqdm import tqdm
from data import *
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.stderr = open(os.devnull, "w")
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 無頭模式

# 建立 driver（建議使用 webdriver-manager 自動處理）
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# %% 取得所有公車路線
def get_all_bus_line():
    driver.get("https://ebus.gov.taipei/ebus")
    time.sleep(1)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for section in soup.find_all("section", class_="busline"):
        for li in section.find_all("li"):
            a = li.find("a")
            if a:
                bus_line_name = a.text.strip()
                bus_line_id = a["href"].replace("javascript:go('", "").replace("')", "")
                all_bus_line[bus_line_name] = bus_line_id

# %% 取得單一路線詳細站點資訊
def get_bus_line_detail(bus_line_name):
    bus_line_id = all_bus_line[bus_line_name]
    driver.get(f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={bus_line_id}")
    time.sleep(0.5)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    bus_stops_0 = {}
    bus_stop_already = set()
    for li in soup.find_all("li"):
        a = li.find("a", class_="auto-list-link auto-list-stationlist-link")
        if a:
            stop_name = a.find("span", class_="auto-list-stationlist-place").text.strip()
            stop_number = a.find("span", class_="auto-list-stationlist-number").text.strip()
            stop_status = a.find("span", class_="auto-list-stationlist-position").text.strip()
            stop_latitude = a.find("input", id="item_Latitude")["value"]
            stop_longitude = a.find("input", id="item_Longitude")["value"]
            key = (stop_name + "_0") if stop_name not in bus_stop_already else (stop_name + "_1")
            bus_stops_0[key] = {
                "stop_number": stop_number,
                "stop_status": stop_status,
                "stop_latitude": stop_latitude,
                "stop_longitude": stop_longitude,
            }
            bus_stop_already.add(stop_name)

    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "返程")]'))
        ).click()
        time.sleep(0.5)
    except:
        all_bus_line_detail[bus_line_name] = [bus_stops_0, {}]
        return

    soup = BeautifulSoup(driver.page_source, "html.parser")
    bus_stops_1 = {}
    bus_stop_already = set()
    for li in soup.find_all("li"):
        a = li.find("a", class_="auto-list-link auto-list-stationlist-link")
        if a:
            stop_name = a.find("span", class_="auto-list-stationlist-place").text.strip()
            stop_number = a.find("span", class_="auto-list-stationlist-number").text.strip()
            stop_status = a.find("span", class_="auto-list-stationlist-position").text.strip()
            stop_latitude = a.find("input", id="item_Latitude")["value"]
            stop_longitude = a.find("input", id="item_Longitude")["value"]
            key = (stop_name + "_0") if stop_name not in bus_stop_already else (stop_name + "_1")
            bus_stops_1[key] = {
                "stop_number": stop_number,
                "stop_status": stop_status,
                "stop_latitude": stop_latitude,
                "stop_longitude": stop_longitude,
            }
            bus_stop_already.add(stop_name)

    all_bus_line_detail[bus_line_name] = [bus_stops_0, bus_stops_1]

# %% 批量抓取全部路線詳細資訊
def get_all_bus_line_detail():
    for bus_line_name in tqdm(all_bus_line.keys(), desc="獲取公車路線詳情"):
        for i in range(5):
            try:
                get_bus_line_detail(bus_line_name)
                break
            except Exception as e:
                print(f"獲取 {bus_line_name} 詳情失敗，重試 {i+1}/5: {e}")

# %% 查詢：站名查上車時間
def search_fr_to():
    fr = input("請輸入起點站(例:景美國中): ")
    to = input("請輸入終點站(例:木柵): ")
    print(f"起點站: {fr}, 終點站: {to}")
    lines_to_search = []

    for bus_line_name, stops in all_bus_line_detail.items():
        if fr + "_0" in stops[0] and to + "_0" in stops[0]:
            lines_to_search.append(bus_line_name)

    res = []
    for line in tqdm(lines_to_search):
        get_bus_line_detail(line)
        line_name = line
        line = all_bus_line_detail[line]
        for direction in ["_0", "_1"]:
            for way in line:
                if fr + direction not in way or to + direction not in way:
                    continue
                if int(way[fr + direction]["stop_number"]) < int(way[to + direction]["stop_number"]):
                    if way[fr + direction]["stop_status"] not in ["尚未發車", "末班已過", ""]:
                        res.append(f"公車路線: {line_name}, 上車時間: {way[fr + direction]['stop_status']}")
    if not res:
        print("沒有找到符合條件的公車路線")
    for r in res:
        print(r)

# %% 查詢：經緯度查最近站名
def search_near():
    latitude = input("請輸入緯度: ")
    longitude = input("請輸入經度: ")
    print(f"緯度: {latitude}, 經度: {longitude}")
    latitude = float(latitude)
    longitude = float(longitude)

    dist = {}
    for _, stops in all_bus_line_detail.items():
        for direction in [0, 1]:  # 去程 + 返程
            for stop_name, stop_info in stops[direction].items():
                if stop_info["stop_latitude"] and stop_info["stop_longitude"]:
                    stop_lat = float(stop_info["stop_latitude"])
                    stop_lon = float(stop_info["stop_longitude"])
                    d = ((latitude - stop_lat) ** 2 + (longitude - stop_lon) ** 2) ** 0.5
                    dist[stop_name.split("_")[0]] = d

    dist_arr = sorted(dist.items(), key=lambda x: x[1])
    print("最近的公車站:")
    for stop_name, d in dist_arr[:5]:
        print(f"站名: {stop_name}, 距離: {d*111:.2f} 公里")  # 每度大約 111 公里

# %% 主程式
print("請忽略所有警告")
print("正在抓取公車路線與站點資料...")
get_all_bus_line()
get_all_bus_line_detail()

while True:
    print("\n歡迎使用公車路線查詢系統")
    print("1. 查詢最近上車時間")
    print("2. 查詢最近上車地點")
    print("exit. 退出系統")
    choice = input("請輸入選項: ")
    if choice == "1":
        search_fr_to()
    elif choice == "2":
        search_near()
    elif choice == "exit":
        break
    else:
        print("無效的選項，請重新輸入。")