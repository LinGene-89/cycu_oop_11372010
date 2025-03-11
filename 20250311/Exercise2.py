import pandas as pd
import matplotlib.pyplot as plt

# 讀取 Excel 檔案
df = pd.read_excel('311.xlsx')

# 計算 x 和 y 的和
df['sum'] = df['x'] + df['y']

# 印出結果
print(df['sum'])

# 繪製散佈圖
plt.scatter(df['x'], df['y'])
plt.xlabel('x')
plt.ylabel('y')
plt.title('Scatter Plot of x and y')
plt.show()