# homework 2

class BusInfo:
    def __init__(self, bus_id):
        self.bus_id = bus_id

    def get_route_info_go(self):
        """
        根據 bus_id 回傳該路線的所有去程站 id（模擬資料）
        """
        if self.bus_id == "M25305":
            return ['stop_id1', 'stop_id2']
        return []

    def get_route_info_come(self):
        """
        根據 bus_id 回傳該路線的所有回程站 id（模擬資料）
        """
        return ['stop_id3', 'stop_id4']

    def get_stop_name(self, stop_id):
        """
        根據 stop_id 查詢站名（模擬回傳）
        :param stop_id: 站牌 ID
        :return: 站名
        """
        stop_name = "台北火車站"
        return stop_name

    def get_arrival_time_info(self, stop_id):
        """
        根據 stop_id 查詢預估到站時間（分鐘）（模擬回傳）
        :param stop_id: 站牌 ID
        :return: 預估到站時間（分鐘）
        """
        arrival_time = 5
        return arrival_time


if __name__ == "__main__":
    bus = BusInfo("M25305")
    print(f"Bus ID: {bus.bus_id}")
    print(f"Route Info Go: {bus.get_route_info_go()}")
    print(f"Route Info Come: {bus.get_route_info_come()}")

    # get stop name of second stop of route_info_go
    route_info_go = bus.get_route_info_go()
    stop_id = route_info_go[1] if len(route_info_go) > 1 else None

    if stop_id:
        stop_name = bus.get_stop_name(stop_id)
        print(f"Stop Name: {stop_name}")

        arrival_time = bus.get_arrival_time_info(stop_id)
        print(f"Arrival Time: {arrival_time} minutes")
    else:
        print("No stop ID available.")