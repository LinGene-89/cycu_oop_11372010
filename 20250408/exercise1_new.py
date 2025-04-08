import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm

def calculate_lognormal_cdf(mu, sigma, x_range):
    """
    計算對數常態累積分布函數 (CDF)
    :param mu: 對數常態分布的 mu
    :param sigma: 對數常態分布的 sigma
    :param x_range: x 軸的數據範圍
    :return: CDF 值
    """
    return lognorm.cdf(x_range, sigma, scale=np.exp(mu))

def plot_lognormal_cdf(x, cdf):
    """
    繪製對數常態累積分布函數 (CDF) 圖形
    :param x: x 軸數據
    :param cdf: CDF 值
    """
    plt.figure(figsize=(8, 6))
    plt.plot(x, cdf, label='Log-Normal CDF', color='b')
    plt.title('Log-Normal Cumulative Distribution Function')
    plt.xlabel('x')
    plt.ylabel('CDF')
    plt.grid(True)
    plt.legend()
    plt.savefig('lognormal_cdf.jpg', format='jpg')
    plt.show()

def main():
    # 讓使用者輸入 mu 和 sigma
    mu = float(input("請輸入 mu 的值: "))
    sigma = float(input("請輸入 sigma 的值: "))

    # 生成數據點
    x = np.linspace(0, 10, 1000)

    # 計算 CDF
    cdf = calculate_lognormal_cdf(mu, sigma, x)

    # 繪製圖形
    plot_lognormal_cdf(x, cdf)

if __name__ == "__main__":
    main()