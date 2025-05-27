import asyncio
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

URL = "https://ebus.gov.taipei/Route/CityRoutes"

async def fetch_all_buses():
    routes = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # headless 模式避免跳出視窗
        page = await browser.new_page()
        await page.goto(URL)
        await page.wait_for_selector("a[href*='routeid=']")  # 等待有 routeid 的連結

        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")

        for a in soup.select("a[href*='routeid=']"):
            href = a.get("href")
            name = a.get_text(strip=True)
            routeid = href.split("routeid=")[-1].split("&")[0]
            routes[routeid] = name

        await browser.close()

    return routes

async def save_bus_route_list():
    routes = await fetch_all_buses()
    print(f"✅ 共抓到 {len(routes)} 條公車路線")

    with open("taipei_bus_routes.json", "w", encoding="utf-8") as f:
        json.dump(routes, f, ensure_ascii=False, indent=2)

    print("✅ 已儲存為 taipei_bus_routes.json")

if __name__ == "__main__":
    asyncio.run(save_bus_route_list())
