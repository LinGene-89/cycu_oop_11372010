# -*- coding: utf-8 -*-
import os
import re
import time
import pandas as pd
from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.orm import sessionmaker, declarative_base


class taipei_route_list:
    def __init__(self, working_directory: str = 'data'):
        self.working_directory = working_directory
        self.url = 'https://ebus.gov.taipei/ebus?ct=all'
        self.content = None

        os.makedirs(self.working_directory, exist_ok=True)
        self._fetch_content()

        Base = declarative_base()

        class bus_route_orm(Base):
            __tablename__ = 'data_route_list'
            route_id = Column(String, primary_key=True)
            route_name = Column(String)
            route_data_updated = Column(Integer, default=0)

        self.orm = bus_route_orm

        self.engine = create_engine(f'sqlite:///{self.working_directory}/hermes_ebus_taipei.sqlite3')
        self.engine.connect()
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _fetch_content(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            page.wait_for_timeout(3000)
            self.content = page.content()
            browser.close()

        html_file_path = f'{self.working_directory}/hermes_ebus_taipei_route_list.html'
        with open(html_file_path, "w", encoding="utf-8") as file:
            file.write(self.content)

    def parse_route_list(self) -> pd.DataFrame:
        pattern = r'<li><a href="javascript:go\(\'(.*?)\'\)">(.*?)</a></li>'
        matches = re.findall(pattern, self.content, re.DOTALL)

        if not matches:
            raise ValueError("No data found for route table")

        bus_routes = [(route_id, route_name.strip()) for route_id, route_name in matches]
        self.dataframe = pd.DataFrame(bus_routes, columns=["route_id", "route_name"])
        return self.dataframe

    def save_to_database(self):
        for _, row in self.dataframe.iterrows():
            self.session.merge(self.orm(route_id=row['route_id'], route_name=row['route_name']))
        self.session.commit()

    def set_route_data_updated(self, route_id: str, route_data_updated: int = 1):
        self.session.query(self.orm).filter_by(route_id=route_id).update({"route_data_updated": route_data_updated})
        self.session.commit()

    def set_route_data_unexcepted(self, route_id: str):
        self.session.query(self.orm).filter_by(route_id=route_id).update({"route_data_updated": 2})
        self.session.commit()

    def read_from_database(self) -> pd.DataFrame:
        query = self.session.query(self.orm)
        self.db_dataframe = pd.read_sql(query.statement, self.session.bind)
        return self.db_dataframe

    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
        if hasattr(self, 'engine'):
            self.engine.dispose()


class taipei_route_info:
    def __init__(self, route_id: str, direction: str = 'go', working_directory: str = 'data'):
        self.route_id = route_id
        self.direction = direction
        self.content = None
        self.url = f'https://ebus.gov.taipei/Route/StopsOfRoute?routeid={route_id}'
        self.working_directory = working_directory

        if self.direction not in ['go', 'come']:
            raise ValueError("Direction must be 'go' or 'come'")

        os.makedirs(self.working_directory, exist_ok=True)
        self._fetch_content()

    def _fetch_content(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(self.url)
            if self.direction == 'come':
                page.click('a.stationlist-come-go-gray.stationlist-come')
            page.wait_for_timeout(3000)
            self.content = page.content()
            browser.close()

    def parse_route_info(self) -> pd.DataFrame:
        pattern = re.compile(
            r'<li>.*?<span class="auto-list-stationlist-position.*?">(.*?)</span>\s*'
            r'<span class="auto-list-stationlist-number">\s*(\d+)</span>\s*'
            r'<span class="auto-list-stationlist-place">(.*?)</span>.*?'
            r'<input[^>]+name="item\.UniStopId"[^>]+value="(\d+)"[^>]*>.*?'
            r'<input[^>]+name="item\.Latitude"[^>]+value="([\d\.]+)"[^>]*>.*?'
            r'<input[^>]+name="item\.Longitude"[^>]+value="([\d\.]+)"[^>]*>',
            re.DOTALL
        )

        matches = pattern.findall(self.content)
        if not matches:
            raise ValueError(f"No data found for route ID {self.route_id} direction {self.direction}")

        self.dataframe = pd.DataFrame(
            matches,
            columns=["arrival_info", "stop_number", "stop_name", "stop_id", "latitude", "longitude"]
        )

        self.dataframe["direction"] = self.direction
        self.dataframe["route_id"] = self.route_id
        return self.dataframe

    def save_to_database(self):
        db_file = f"{self.working_directory}/hermes_ebus_taipei.sqlite3"
        engine = create_engine(f"sqlite:///{db_file}")
        Base = declarative_base()

        class bus_stop_orm(Base):
            __tablename__ = "data_route_info_busstop"
            stop_id = Column(Integer)
            arrival_info = Column(String)
            stop_number = Column(Integer, primary_key=True)
            stop_name = Column(String)
            latitude = Column(Float)
            longitude = Column(Float)
            direction = Column(String, primary_key=True)
            route_id = Column(String, primary_key=True)

        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for _, row in self.dataframe.iterrows():
            session.merge(bus_stop_orm(
                stop_id=row["stop_id"],
                arrival_info=row["arrival_info"],
                stop_number=row["stop_number"],
                stop_name=row["stop_name"],
                latitude=row["latitude"],
                longitude=row["longitude"],
                direction=row["direction"],
                route_id=row["route_id"]
            ))

        session.commit()
        session.close()


if __name__ == "__main__":
    route_list = taipei_route_list()
    route_list.parse_route_list()
    route_list.save_to_database()

    all_routes_df = route_list.read_from_database()
    print(f"Total routes found: {len(all_routes_df)}")

    all_routes_info = []  # 用於匯出Excel

    for idx, row in all_routes_df.iterrows():
        route_id = row['route_id']
        route_name = row['route_name']
        print(f"Processing route {route_name} ({route_id})")

        try:
            for direction in ['go', 'come']:
                route_info = taipei_route_info(route_id, direction=direction)
                route_info.parse_route_info()
                route_info.save_to_database()

                # 加入路線資訊與路線名稱、代碼合併
                df_tmp = route_info.dataframe.copy()
                df_tmp['route_name'] = route_name

                all_routes_info.append(df_tmp)

                print(f"Saved stops for route {route_name} ({route_id}) direction {direction}")

                time.sleep(3)  # 避免爬太快

            route_list.set_route_data_updated(route_id)

        except Exception as e:
            print(f"Error processing route {route_name}: {e}")
            route_list.set_route_data_unexcepted(route_id)

    # 匯出所有路線站牌資訊成 Excel
    if all_routes_info:
        all_routes_df = pd.concat(all_routes_info, ignore_index=True)
        excel_path = os.path.join(route_list.working_directory, 'all_bus_routes_info.xlsx')
        all_routes_df.to_excel(excel_path, index=False)
        print(f"✅ Exported all routes info to {excel_path}")
