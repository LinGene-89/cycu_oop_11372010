import asyncio
import os
import Bus_info_11372012

async def find_bus(route_id: str):
    print(f"正在查詢公車路線：{route_id}")
    output_file = os.path.join(os.path.expanduser("~"), "Desktop", "bus_stops.csv")
    Bus_info_11372012.scrape_bus_stops(route_id, output_file)

# 執行主程式
if __name__ == "__main__":
    route_id = input("請告訴我公車代碼：").strip()  # 在主程式中取得 route_id
    asyncio.run(find_bus(route_id))