def gcd(a, b):
    # 使用遞進實現輾轉相除法
    while b != 0:
        a, b = b, a % b  # 交換a和b，並計算a除以b的餘數
    return a  # 當b為0時，a即為最大公因數

# 範例
x = 7
y = 49
print(f"gcd of: {gcd(x, y)}")

# 範例
x = 11
y = 121
print(f"gcd of: {gcd(x, y)}")