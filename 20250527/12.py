import json
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

SEARCH_URL = "https://ebus.gov.taipei/"

# 要搜尋的關鍵字，可擴充
KEYWORDS = [str(i) for i in range(10)] + ["紅", "綠", "藍", "幹線", "市區", "小", "內", "南", "北", "東", "西"]

async def fetch_routes_from_search():
    routes = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=80)
        page = await browser.new_page()
        await page.goto(SEARCH_URL)

        # 點開右上角的查詢欄
        await page.click("#navSearchBtn")
        await page.wait_for_selector("input#SearchInput", timeout=10000)

        for keyword in KEYWORDS:
            print(f"🔍 搜尋關鍵字: {keyword}")
            await page.fill("input#SearchInput", "")
            await page.fill("input#SearchInput", keyword)
            await page.click("button#btnSearch")

            try:
                await page.wait_for_selector("div.search-item", timeout=8000)
            except:
                print("⚠️ 無搜尋結果")
                continue

            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            items = soup.select("div.search-item")

            for item in items:
                a_tag = item.select_one("a")
                if a_tag and "routeid=" in a_tag["href"]:
                    route_id = a_tag["href"].split("routeid=")[-1]
                    route_name = a_tag.get_text(strip=True)
                    routes[route_id] = route_name

        await browser.close()

    return routes

async def save_routes_json():
    routes = await fetch_routes_from_search()
    print(f"✅ 共抓到 {len(routes)} 條獨立路線")

    # 儲存成 JSON
    with open("routes_basic.json", "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    print("✅ 資料已儲存為 routes_basic.json")

# 主程式
if __name__ == "__main__":
    asyncio.run(save_routes_json())
