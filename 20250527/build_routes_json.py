import json
import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# === 網頁 URL ===
ROUTE_LIST_URL = "https://ebus.gov.taipei/Route"
ROUTE_STOPS_URL = "https://ebus.gov.taipei/Route/StopsOfRoute?routeid={}"

# === 抓取所有路線代碼與名稱 ===
async def fetch_all_routes():
    routes = {}
    async with async_playwright() as p:
        # 改為非無頭模式 + 模擬操作延遲
        browser = await p.chromium.launch(headless=False, slow_mo=100)
        page = await browser.new_page()
        await page.goto(ROUTE_LIST_URL)

        # 加入延遲等待 JS 載入
        await asyncio.sleep(3)

        # 等待路線元素載入
        await page.wait_for_selector("div.route-list-item", timeout=30000)

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        for item in soup.select("div.route-list-item"):
            route_id = item.get("data-id")
            route_name = item.select_one("h4").get_text(strip=True)
            if route_id and route_name:
                routes[route_id] = {"name": route_name, "stops": []}

        await browser.close()
    return routes

# === 抓取每條路線的站名資料 ===
async def fetch_stops_for_route(route_id):
    url = ROUTE_STOPS_URL.format(route_id)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # 保持 headless 抓資料快
        page = await browser.new_page()
        await page.goto(url)
        try:
            await page.wait_for_selector("div#GoDirectionRoute li", timeout=10000)
            html = await page.content()
        except:
            await browser.close()
            return []
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    stations = []
    for li in soup.select("div#GoDirectionRoute li"):
        spans = li.select("span.auto-list-stationlist span")
        inputs = li.select("input")
        try:
            stop_name = spans[2].get_text(strip=True)
            stop_id = inputs[0]['value']
            lat = float(inputs[1]['value'])
            lon = float(inputs[2]['value'])
            stations.append({"name": stop_name, "stop_id": stop_id, "lat": lat, "lon": lon})
        except:
            continue
    return stations

# === 主程序：整合路線與站名資料並儲存為 routes.json ===
async def build_routes_json(output_path="routes.json"):
    all_routes = await fetch_all_routes()
    print(f"✅ 找到 {len(all_routes)} 條路線，開始抓取各路線站點...")

    for i, route_id in enumerate(all_routes.keys()):
        print(f"▶ ({i+1}/{len(all_routes)}) 抓取路線 {route_id} - {all_routes[route_id]['name']}")
        stations = await fetch_stops_for_route(route_id)
        all_routes[route_id]["stops"] = stations

    # 儲存成 JSON 檔
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_routes, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 所有路線已儲存到：{output_path}")

# === 執行程式 ===
if __name__ == "__main__":
    asyncio.run(build_routes_json())
