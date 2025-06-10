# %%
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
from data import *
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.stderr = open(os.devnull, "w")
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # 無頭模式
# service = Service(r"chromedriver-win64\chromedriver.exe")
import os
driver_path = os.path.join(os.path.dirname(__file__), "chromedriver-win64", "chromedriver.exe")
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)


# %% 取得所有公車路線
def get_all_bus_line():
    # response = requests.get("https://ebus.gov.taipei/ebus", verify=False)
    response = driver.get("https://ebus.gov.taipei/ebus")
    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    # print(soup.prettify())

    # find all <section class="busline">
    for section in soup.find_all("section", class_="busline"):
        # print(section.prettify())

        """
        <li>
            <a href="javascript:go('0100028100')">
                281
            </a>
        </li>

        to {'281': '0100028100'}
        """

        for li in section.find_all("li"):
            a = li.find("a")
            if a:
                bus_line_name = a.text.strip()
                bus_line_id = a["href"].replace("javascript:go('", "").replace("')", "")
                all_bus_line[bus_line_name] = bus_line_id


# get_all_bus_line()
# print(all_bus_line)


# %%
def get_bus_line_detail(bus_line_name):
    bus_line_id = all_bus_line[bus_line_name]
    # https://ebus.gov.taipei/Route/StopsOfRoute?routeid=0100000A00
    driver.get(f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={bus_line_id}")
    time.sleep(0.5)  # 等待頁面加載
    # print(driver.page_source)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    """
    <li>
        <a class="auto-list-link auto-list-stationlist-link" href="javascript:void(0);">
        <span class="auto-list auto-list-stationlist">
            <span class="auto-list-stationlist-position auto-list-stationlist-position-none">
                尚未發車
            </span>
            <span class="auto-list-stationlist-number">
                1
            </span>
            <span class="auto-list-stationlist-place">
                南寮(忠三街口)
            </span>
            <input id="item_UniStopId" name="item.UniStopId" type="hidden" value="1148001040"/>
            <input data-val="true" data-val-number="欄位 Latitude 必須是數字。" data-val-required="Latitude 欄位是必要項。" id="item_Latitude" name="item.Latitude" type="hidden" value="25.079068"/>
            <input data-val="true" data-val-number="欄位 Longitude 必須是數字。" data-val-required="Longitude 欄位是必要項。" id="item_Longitude" name="item.Longitude" type="hidden" value="121.623553"/>
            </span>
        </a>
    </li>
    """
    # print(soup.prettify())

    bus_stops_0 = {}
    bus_stop_already = set()  # 用於檢查是否已經添加過的站點
    for li in soup.find_all("li"):
        a = li.find("a", class_="auto-list-link auto-list-stationlist-link")
        if a:
            stop_name = a.find(
                "span", class_="auto-list-stationlist-place"
            ).text.strip()
            stop_number = a.find(
                "span", class_="auto-list-stationlist-number"
            ).text.strip()
            stop_status = a.find(
                "span", class_="auto-list-stationlist-position"
            ).text.strip()
            stop_latitude = a.find("input", id="item_Latitude")["value"]
            stop_longitude = a.find("input", id="item_Longitude")["value"]
            bus_stops_0[
                (
                    (stop_name + "_0")
                    if stop_name not in bus_stop_already
                    else (stop_name + "_1")
                )
            ] = {
                "stop_number": stop_number,
                "stop_status": stop_status,
                "stop_latitude": stop_latitude,
                "stop_longitude": stop_longitude,
            }
            bus_stop_already.add(stop_name)

    try:
        wait = WebDriverWait(driver, 10)
        link = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "返程")]'))
        )
        link.click()
        time.sleep(0.5)  # 等待頁面加載
    except Exception as e:
        all_bus_line_detail[bus_line_name] = [bus_stops_0, {}]
        return

    soup = BeautifulSoup(driver.page_source, "html.parser")
    bus_stops_1 = {}
    bus_stop_already = set()  # 用於檢查是否已經添加過的站點
    for li in soup.find_all("li"):
        a = li.find("a", class_="auto-list-link auto-list-stationlist-link")
        if a:
            stop_name = a.find(
                "span", class_="auto-list-stationlist-place"
            ).text.strip()
            stop_number = a.find(
                "span", class_="auto-list-stationlist-number"
            ).text.strip()
            stop_status = a.find(
                "span", class_="auto-list-stationlist-position"
            ).text.strip()
            stop_latitude = a.find("input", id="item_Latitude")["value"]
            stop_longitude = a.find("input", id="item_Longitude")["value"]
            bus_stops_1[
                (
                    (stop_name + "_0")
                    if stop_name not in bus_stop_already
                    else (stop_name + "_1")
                )
            ] = {
                "stop_number": stop_number,
                "stop_status": stop_status,
                "stop_latitude": stop_latitude,
                "stop_longitude": stop_longitude,
            }
            bus_stop_already.add(stop_name)
    all_bus_line_detail[bus_line_name] = [bus_stops_0, bus_stops_1]
    # print(all_bus_line_detail[bus_line_name])


# get_bus_line_detail("0東")
# print(all_bus_line_detail)


# %%
def get_all_bus_line_detail():
    for bus_line_name in tqdm(all_bus_line.keys(), desc="獲取公車路線詳情"):
        for i in range(5):
            try:
                get_bus_line_detail(bus_line_name)
                break  # 成功獲取後跳出循環
            except Exception as e:
                print(f"獲取 {bus_line_name} 詳情失敗，重試 {i+1}/5: {e}")


# print("正在獲取所有公車路線詳情...")
# get_all_bus_line_detail()
# with open("all_bus_line_detail.txt", "w", encoding="utf-8") as f:
#     f.write(str(all_bus_line_detail))
# print("所有公車路線詳情已保存到 all_bus_line_detail.txt")
# exit()
# print(all_bus_line_detail)


# %% 執行計算
def search_fr_to():
    fr = "" or input("請輸入起點站(例:景美國中): ")
    to = "" or input("請輸入終點站(例:木柵): ")
    # 測試的時候你可以直接把上面的""改成你想要的站名
    # 例如: fr = "景美國中", to = "木柵" 後面的or input就不需要輸入了

    print(f"起點站: {fr}, 終點站: {to}")

    lines_to_search = []

    for bus_line_name, stops in all_bus_line_detail.items():
        # 檢查起點站和終點站是否在公車路線中
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
                if int(way[fr + direction]["stop_number"]) < int(
                    way[to + direction]["stop_number"]
                ):
                    if way[fr + direction]["stop_status"] not in [
                        "尚未發車",
                        "末班已過",
                        "",
                    ]:
                        res.append(
                            f"公車路線: {line_name}, 上車時間: {way[fr + direction]['stop_status']}"
                        )
    if not res:
        print("沒有找到符合條件的公車路線")
    for r in res:
        print(r)


def search_near():
    try:
        latitude = float(input("請輸入您的緯度："))
        longitude = float(input("請輸入您的經度："))
    except ValueError:
        print("輸入格式錯誤，請輸入數值。")
        return

    print(f"您輸入的位置：緯度 {latitude}, 經度 {longitude}")

    dist = {}
    for _, stops in all_bus_line_detail.items():
        for stop_name, stop_info in stops[0].items():
            if stop_info["stop_latitude"] and stop_info["stop_longitude"]:
                stop_latitude = float(stop_info["stop_latitude"])
                stop_longitude = float(stop_info["stop_longitude"])
                distance = (
                    (latitude - stop_latitude) ** 2 + (longitude - stop_longitude) ** 2
                ) ** 0.5
                # stop_name 要去掉 _0或_1
                dist[stop_name.split("_")[0]] = distance

    dist_arr = sorted(dist.items(), key=lambda x: x[1])

    print("最近的公車站:")
    for stop_name, distance in dist_arr[:5]:  # 只顯示前 5 個
        print(f"站名: {stop_name}, 距離: {distance * 111:.2f} 公里")  # 約略轉換為公里


def show_google_map():
    bus_line_name = input("請輸入公車路線名稱: ")
    if bus_line_name not in all_bus_line_detail:
        print("無效的公車路線名稱")
        return

    bus_stops = all_bus_line_detail[bus_line_name][0]
    if not bus_stops:
        print("該公車路線沒有站點資訊")
        return

    stop_list = list(bus_stops.values())
    if len(stop_list) < 2:
        print("站點數不足以建立路線")
        return

    origin = f"{stop_list[0]['stop_latitude']},{stop_list[0]['stop_longitude']}"
    destination = f"{stop_list[-1]['stop_latitude']},{stop_list[-1]['stop_longitude']}"
    waypoints = "|".join(
        f"{stop['stop_latitude']},{stop['stop_longitude']}" for stop in stop_list[1:-1]
    )

    url = (
        f"https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"&travelmode=driving"
    )
    if waypoints:
        url += f"&waypoints={waypoints}"

    print(f"在 Google Maps 中顯示公車路線: {bus_line_name}")
    print(f"點擊以下連結查看: {url}")


print("請忽略所有警告")
while True:
    print("歡迎使用公車路線查詢系統")
    print("1. 查詢最近上車時間")
    print("2. 查詢最近上車地點")
    print("3. 在google map顯示某公車路線")
    print("exit. 退出系統")
    choice = input("請輸入選項: ")
    if choice == "1":
        search_fr_to()
    elif choice == "2":
        search_near()
    elif choice == "3":
        show_google_map()
    elif choice == "exit" or choice == "":
        break
    else:
        print("無效的選項，請重新輸入。")

# %%