from datetime import datetime

def calculate_julian_date(input_time_str):
    # 將輸入的時間字串轉換為 datetime 物件
    input_time = datetime.strptime(input_time_str, "%Y-%m-%d %H:%M")
    
    # 計算該天是星期幾
    weekday = input_time.strftime("%A")  # 取得星期幾的英文名稱
    
    # 計算輸入時間的 Julian 日期
    julian_start = datetime(4713, 1, 1, 12)  # Julian 日期的起始點
    julian_days_input = (input_time - julian_start).total_seconds() / 86400  # 轉換為天數
    
    # 計算當前時間的 Julian 日期
    now = datetime.now()
    julian_days_now = (now - julian_start).total_seconds() / 86400  # 轉換為天數
    
    # 計算輸入時間至現在的間隔天數
    elapsed_days = julian_days_now - julian_days_input
    
    # 回傳結果
    return weekday, elapsed_days

# 測試函數
if __name__ == "__main__":
    input_time_str = input("請輸入時間 (格式為 YYYY-MM-DD HH:MM，例如 2020-04-15 20:30): ")
    weekday, elapsed_days = calculate_julian_date(input_time_str)
    print(f"該天是星期: {weekday}")
    print(f"該時刻至今經過的太陽日數: {elapsed_days:.6f}")