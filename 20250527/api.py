import requests
import json
import time

# 正確的 TDX API URL
ROUTE_API = "https://tdx.transportdata.tw/api/basic/v2/Bus/Route/City/Taipei"
STOP_API_TEMPLATE = "https://tdx.transportdata.tw/api/basic/v2/Bus/StopOfRoute/City/Taipei/{}"

HEADERS = {
    "accept": "application/json"
}

def get_all_routes():
    response = requests.get(ROUTE_API, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"無法取得路線資料，HTTP 狀態碼：{response.status_code}")
        return []

def get_stops_of_route(route_name):
    url = STOP_API_TEMPLATE.format(route_name)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"無法取得路線 {route_name} 的站牌資料，HTTP 狀態碼：{response.status_code}")
        return []

def build_routes_json():
    routes_data = {}
    all_routes = get_all_routes()
    for route in all_routes:
        route_name = route.get("RouteName", {}).get("Zh_tw")
        if not route_name:
            continue
        stops_info = get_stops_of_route(route_name)
        for direction_info in stops_info:
            direction = direction_info.get("Direction")
            stops = direction_info.get("Stops", [])
            stop_names = [stop.get("StopName", {}).get("Zh_tw") for stop in stops]
            if stop_names:
                key = f"{route_name}_{direction}"
                routes_data[key] = stop_names
        time.sleep(0.5)  # 防止過度請求
    return routes_data

def save_routes_to_json(file_path="routes.json"):
    routes_data = build_routes_json()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(routes_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已儲存至 {file_path}")

if __name__ == "__main__":
    save_routes_to_json()
