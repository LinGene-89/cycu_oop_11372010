import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 讀取CSV檔案
file_path = input("請輸入CSV檔案完整路徑：").strip()
df = pd.read_csv(file_path)

# 假設第一欄是學生姓名，取出所有科目分數
subject_scores = df.iloc[:, 1:]

# 分數區間設定：0~10, 10~20, ..., 90~100
bins = list(range(0, 110, 10))  # [0,10,20,...,100]
bin_labels = [f'{bins[i]}–{bins[i+1]}' for i in range(len(bins)-1)]

# 計算每個科目在各區間的人數
hist_data = {}
for subject in subject_scores.columns:
    counts, _ = np.histogram(subject_scores[subject], bins=bins)
    hist_data[subject] = counts

# 將資料轉成 DataFrame，index 是分數區間
hist_df = pd.DataFrame(hist_data, index=bin_labels)

# 繪圖參數
x = np.arange(len(bin_labels))  # 每個區間的位置
bar_width = 0.8 / len(subject_scores.columns)  # 每個科目的條寬

# 繪圖開始
plt.figure(figsize=(12, 6))

for i, subject in enumerate(hist_df.columns):
    plt.bar(x + i * bar_width, hist_df[subject], width=bar_width, label=subject)

# === ✅ 修改區塊開始 ===
plt.title('Score Rande', fontsize=16)       # 主標題
plt.xlabel('score', fontsize=12)            # 橫軸：分數
plt.ylabel('number', fontsize=12)            # 縱軸：人數
# === ✅ 修改區塊結束 ===

plt.xticks(x + bar_width * (len(subject_scores.columns)-1)/2, bin_labels)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()
