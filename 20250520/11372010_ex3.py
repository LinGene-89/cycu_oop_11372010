import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.patheffects as path_effects
from shapely.geometry import LineString, Point
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# === 中文字型設定 ===
rcParams['font.family'] = 'Microsoft JhengHei'
rcParams['axes.unicode_minus'] = False

# ✅ 主程式功能：抓取站點 + 繪製地圖
async def find_bus_and_plot(route_id: str):
    """
    抓取公車站點資訊，並將路線繪製於北北基桃行政區地圖上。
    """
    route_id = route_id.strip()
    url = f"https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        try:
            await page.wait_for_selector("div#GoDirectionRoute li", timeout=10000)
        except:
            print("❌ 網頁載入超時，請確認公車代碼是否正確。")
            return

        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    station_items = soup.select("div#GoDirectionRoute li")

    if not station_items:
        print("❌ 未找到任何站牌資料，請確認公車代碼是否正確。")
        return

    all_stations = []
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
            station = [stop_time, stop_number, stop_name, stop_id, latitude, longitude]
            all_stations.append(station)
        except Exception as e:
            print(f"⚠️ 第 {idx} 筆資料處理錯誤：{e}")

    if not all_stations:
        print("⚠️ 沒有成功抓取到任何站牌資訊。")
        return

    # 輸出所有站名
    print("\n✅ 抓到的站牌資訊如下：")
    for station in all_stations:
        print(f"站名: {station[2]}")

    # 建立 GeoDataFrame
    line_coords = [(station[5], station[4]) for station in all_stations]  # (lon, lat)
    bus_route = gpd.GeoDataFrame(geometry=[LineString(line_coords)], crs="EPSG:4326")
    bus_stops = gpd.GeoDataFrame(geometry=[Point(coord) for coord in line_coords], crs="EPSG:4326")

    # 讀取北北基桃圖層
    shapefile_path = '20250520/COUNTY_MOI_1091124/TOWN_MOI_1140318.shp'
    gdf = gpd.read_file(shapefile_path, encoding='utf-8')
    target_cities = ['臺北市', '新北市', '基隆市', '桃園市']
    filtered_gdf = gdf[gdf['COUNTYNAME'].isin(target_cities)]

    # 計算縣市中心點
    city_centroids = filtered_gdf.dissolve(by='COUNTYNAME', as_index=False)
    city_centroids['centroid'] = city_centroids.geometry.centroid

    # 繪製地圖
    fig, ax = plt.subplots(figsize=(12, 14))
    filtered_gdf.plot(ax=ax, column='COUNTYNAME', cmap='Set3', edgecolor='black', legend=False)
    bus_route.plot(ax=ax, color="red", linewidth=2, label="公車路線")
    bus_stops.plot(ax=ax, color="black", markersize=10)

    # 標註縣市名稱（紅字＋白色描邊）
    for _, row in city_centroids.iterrows():
        x, y = row['centroid'].x, row['centroid'].y
        text = ax.text(
            x, y, row['COUNTYNAME'],
            fontsize=14, color='red', ha='center', va='center', weight='bold'
        )
        text.set_path_effects([
            path_effects.Stroke(linewidth=3, foreground='white'),
            path_effects.Normal()
        ])

    plt.title('北北基桃行政區圖 + 公車去程路線', fontsize=16)
    ax.axis('off')
    plt.tight_layout()
    plt.text(0.01, 0.98, "承德幹線", transform=ax.transAxes,
         fontsize=20, color='black', weight='bold',
         ha='left', va='top')
    plt.show()

# ▶ 執行主程式
if __name__ == "__main__":
    route_id = input("請輸入巴士路線 ID（如 0161000900）：").strip()
    asyncio.run(find_bus_and_plot(route_id))
