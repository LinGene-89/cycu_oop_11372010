# 修正 absolute_value_wrong，確保對所有輸入都有 return
def absolute_value_fixed(x):
    """計算絕對值"""
    if x < 0:
        return -x
    return x  # 直接返回 x，無需額外條件

# 改進 absolute_value_extra_return，去除死碼
def absolute_value_clean(x):
    """計算絕對值（無死碼）"""
    return -x if x < 0 else x

# 改進 is_divisible，簡化邏輯
def is_divisible(x, y):
    """檢查 x 是否能被 y 整除"""
    return x % y == 0  # 直接返回布林表達式

# 計算兩點之間的距離
import math

def distance(x1, y1, x2, y2):
    """計算兩點 (x1, y1) 和 (x2, y2) 之間的距離"""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# 測試函數
print(absolute_value_fixed(-5))  # 5
print(absolute_value_clean(3))   # 3
print(is_divisible(10, 2))       # True
print(distance(1, 2, 4, 6))      # 5.0