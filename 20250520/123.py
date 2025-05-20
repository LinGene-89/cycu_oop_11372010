from playwright.async_api import async_playwright
import asyncio

async def check_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("https://ebus.gov.taipei/EBus2/Map/RouteMap?rid=0161000900&sec=0")
        await page.wait_for_timeout(10000)  # 等你人工看一下
        await browser.close()

asyncio.run(check_page())
