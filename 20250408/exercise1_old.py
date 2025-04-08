import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm

# 讓使用者輸入 mu 和 sigma
mu = float(input("請輸入 mu 的值: "))
sigma = float(input("請輸入 sigma 的值: "))

# 生成數據點
x = np.linspace(0, 10, 1000)

# 計算對數常態累積分布函數 (CDF)
cdf = lognorm.cdf(x, sigma, scale=np.exp(mu))

# 繪製圖形
plt.figure(figsize=(8, 6))
plt.plot(x, cdf, label='Log-Normal CDF', color='b')
plt.title('Log-Normal Cumulative Distribution Function')
plt.xlabel('x')
plt.ylabel('CDF')
plt.grid(True)
plt.legend()

# 保存為 jpg 文件
plt.savefig('lognormal_cdf.jpg', format='jpg')

# 顯示圖形
plt.show()