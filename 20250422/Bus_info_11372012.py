# %% 公車爬蟲主程式（完整版 + 中文顯示修正）
import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def scrape_bus_stops(route_id: str, output_file: str):
    # 建立目標網址
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"
    print(f"\n🔗 正在爬取：{url}")

    # 設定瀏覽器為無頭模式
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    # 啟動瀏覽器並取得頁面內容
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(3)  # 等待 JavaScript 載入
    html = driver.page_source
    driver.quit()

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, "html.parser")
    stops = soup.find_all("a", class_="auto-list-link auto-list-stationlist-link")

    # 建立儲存資料夾
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 寫入 CSV，並同步印出資料
    with open(output_file, mode="w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"])

        print("\n📋 公車站點資訊：")
        for stop in stops:
            span = stop.find("span", class_="auto-list auto-list-stationlist")
            if span:
                # ✅ 抓取進站中 / 尚未發車 / 幾分鐘
                arrival = (
                    span.find("span", class_="auto-list-stationlist-position auto-list-stationlist-position-time") or
                    span.find("span", class_="auto-list-stationlist-position auto-list-stationlist-position-now") or
                    span.find("span", class_="auto-list-stationlist-position auto-list-stationlist-position-none")
                )
                number = span.find("span", class_="auto-list-stationlist-number")
                name = span.find("span", class_="auto-list-stationlist-place")
                stop_id = span.find("input", id="item_UniStopId")
                lat = span.find("input", id="item_Latitude")
                lon = span.find("input", id="item_Longitude")

                row = [
                    arrival.text.strip() if arrival else "無資料",
                    number.text.strip() if number else "",
                    name.text.strip() if name else "",
                    stop_id["value"] if stop_id else "",
                    lat["value"] if lat else "",
                    lon["value"] if lon else ""
                ]
                
                # ✅ 終端顯示
                print(",".join(row))
                
                # ✅ 寫入 CSV
                writer.writerow(row)

    print(f"\n✅ 完成！資料已儲存至：\n📄 {os.path.abspath(output_file)}")

# === 主程式入口 ===
if __name__ == "__main__":
    # 使用者輸入公車代碼（預設值）
    route_input = input("請輸入公車代碼（預設：0100000A00）：").strip() or "0100000A00"

    # 自動偵測桌面路徑
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_path = os.path.join(desktop_path, "cycu_oop_11372012", "20250415", "bus_stops.csv")

    # 執行爬蟲
    scrape_bus_stops(route_id=route_input, output_file=output_path)