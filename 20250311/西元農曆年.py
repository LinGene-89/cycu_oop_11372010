from lunarcalendar import Converter, Solar

# 建立一個包含十二生肖的列表
zodiacs = ['鼠', '牛', '虎', '兔', '龍', '蛇', '馬', '羊', '猴', '雞', '狗', '豬']

# 獲取使用者輸入的西元年月日
year = int(input('請輸入西元年: '))
month = int(input('請輸入西元月: '))
day = int(input('請輸入西元日: '))

# 將西元日期轉換為農曆日期
solar = Solar(year, month, day)
lunar = Converter.Solar2Lunar(solar)

# 獲取農曆年份的生肖
zodiac = zodiacs[(lunar.year - 4) % 12]

# 輸出農曆日期和生肖
print(f"農曆日期: {lunar.year}年{lunar.month}月{lunar.day}日")
print(f"該年生肖: {zodiac}")
