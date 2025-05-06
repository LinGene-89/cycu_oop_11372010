import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import folium
import csv
import json
import os
from shapely.geometry import Point
from PIL import Image, ImageDraw


async def fetch_bus_stations(route_id: str, output_dir: str):
    """
    1. 取得公車站牌資料
    2. 存成 CSV 與 GeoJSON
    """
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id.strip()}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        try:
            await page.wait_for_selector("div#GoDirectionRoute li", timeout=10000)
        except:
            print("網頁載入超時，請確認公車代碼是否正確。")
            return None

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    station_items = soup.select("div#GoDirectionRoute li")

    if not station_items:
        print("未找到任何站牌資料。")
        return None

    all_stations = []
    geojson_features = []

    for idx, li in enumerate(station_items, start=1):
        try:
            spans = li.select("span.auto-list-stationlist span")
            inputs = li.select("input")

            stop_time = spans[0].get_text(strip=True)
            stop_number = spans[1].get_text(strip=True)
            stop_name = spans[2].get_text(strip=True)

            stop_id = inputs[0]['value']
            latitude = float(inputs[1]['value'])
            longitude = float(inputs[2]['value'])

            all_stations.append([stop_time, stop_number, stop_name, stop_id, latitude, longitude])

            # 加入GeoJSON格式的資料
            geojson_features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [longitude, latitude]
                },
                "properties": {
                    "stop_time": stop_time,
                    "stop_number": stop_number,
                    "stop_name": stop_name,
                    "stop_id": stop_id
                }
            })
        except Exception as e:
            print(f"第 {idx} 筆資料處理錯誤：{e}")

    # 輸出 CSV
    csv_path = os.path.join(output_dir, f"bus_stations_{route_id}.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["到站時間", "站牌編號", "站牌名稱", "站牌ID", "緯度", "經度"])
        writer.writerows(all_stations)
    print(f"站牌資訊已儲存至 {csv_path}")

    # 輸出 GeoJSON
    geojson_path = os.path.join(output_dir, f"bus_stations_{route_id}.geojson")
    geojson_data = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)
    print(f"站牌GeoJSON已儲存至 {geojson_path}")

    return geojson_path

def plot_static_map(geojson_file: str, output_image: str):
    """
    畫靜態PNG地圖
    """
    try:
        gdf = gpd.read_file(geojson_file)
        if gdf.empty or gdf.geometry.is_empty.all():
            print("GeoJSON 檔案中沒有幾何資料。")
            return
        
        fig, ax = plt.subplots(figsize=(10, 10))
        gdf.plot(ax=ax, color='blue', markersize=10, alpha=0.7)
        ax.set_title("Bus Stops", fontsize=16)
        ax.set_xlabel("Longitude", fontsize=12)
        ax.set_ylabel("Latitude", fontsize=12)
        plt.savefig(output_image, dpi=300)
        plt.close()
        print(f"靜態地圖儲存至 {output_image}")
    
    except Exception as e:
        print(f"靜態地圖產生錯誤：{e}")

def plot_interactive_map_with_person(geojson_file: str, output_html: str, selected_stop_name: str, person_icon_path: str):
    """
    畫加上小人Icon的互動式 HTML 地圖
    """
    try:
        with open(geojson_file, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)

        # 建立地圖
        m = folium.Map(location=[25.0330, 121.5654], zoom_start=13)

        for feature in geojson_data["features"]:
            properties = feature["properties"]
            coordinates = feature["geometry"]["coordinates"]
            lon, lat = coordinates[0], coordinates[1]
            stop_name = properties.get("stop_name", "未知站名")

            if stop_name == selected_stop_name:
                # 用小人 Icon
                icon = folium.CustomIcon(
                    person_icon_path,
                    icon_size=(40, 40)
                )
                folium.Marker(
                    location=[lat, lon],
                    tooltip=stop_name,
                    icon=icon
                ).add_to(m)
            else:
                # 一般小藍點
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=6,
                    color='blue',
                    fill=True,
                    fill_color='blue',
                    fill_opacity=0.7,
                    tooltip=stop_name
                ).add_to(m)

        folium.LayerControl().add_to(m)
        m.save(output_html)
        print(f"含小人站點的互動地圖已儲存至 {output_html}")

    except Exception as e:
        print(f"互動地圖產生錯誤：{e}")

def show_image(image_path: str):
    """
    顯示靜態圖片
    """
    try:
        img = mpimg.imread(image_path)
        plt.imshow(img)
        plt.axis('off')
        plt.show()
    except Exception as e:
        print(f"無法顯示圖片：{e}")
def create_person_icon(output_path="person_icon.png"):
    # 建立透明背景的圖片
    img = Image.new("RGBA", (40, 40), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 畫小小人的身體
    draw.ellipse((15, 5, 25, 15), fill="black")  # 頭 (圓形)
    draw.line((20, 15, 20, 30), fill="black", width=2)  # 身體
    draw.line((20, 20, 15, 25), fill="black", width=2)  # 左手
    draw.line((20, 20, 25, 25), fill="black", width=2)  # 右手
    draw.line((20, 30, 15, 35), fill="black", width=2)  # 左腳
    draw.line((20, 30, 25, 35), fill="black", width=2)  # 右腳

    # 儲存成 PNG
    img.save(output_path)
    print(f"小小人圖示已儲存為 {output_path}")

if __name__ == "__main__":
    route_id = input("請輸入想查詢的公車代碼：").strip()
    output_dir = input("請輸入想儲存的資料夾路徑：").strip()
    create_person_icon()
    os.makedirs(output_dir, exist_ok=True)

    # 抓資料 + 存 GeoJSON
    geojson_file = asyncio.run(fetch_bus_stations(route_id, output_dir))

    if geojson_file:
        # 讀取 GeoJSON，列出所有站名
        with open(geojson_file, "r", encoding="utf-8") as f:
            geojson_data = json.load(f)
        
        stop_names = [feature["properties"]["stop_name"] for feature in geojson_data["features"]]
        
        print("\n以下是可選的站牌名稱：")
        for idx, name in enumerate(stop_names):
            print(f"{idx + 1}. {name}")
        
        selected_idx = int(input("\n請輸入你想標示小人的站牌編號（數字）：")) - 1
        selected_stop_name = stop_names[selected_idx]

        print(f"你選擇的小人站牌是：{selected_stop_name}")

        output_html = os.path.join(output_dir, f"bus_stops_{route_id}_with_person.html")

        # 小人圖示路徑（預設）
        person_icon_path = "person_icon.png"

        # 畫地圖（有小人）
        plot_interactive_map_with_person(geojson_file, output_html, selected_stop_name, person_icon_path)

        print("完成！可以打開HTML檔看效果！")