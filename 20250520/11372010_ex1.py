import pandas as pd

# 讀取輸入檔案路徑
input_path = input("請輸入CSV檔案【讀取路徑】：").strip()

# 讀取CSV
df = pd.read_csv(input_path)

# 取分數部分（假設第1欄是學生姓名，其餘為分數）
score_only = df.iloc[:, 1:]

# 計算不及格（<60）的科目數
fail_counts = (score_only < 60).sum(axis=1)

# 找出不及格科目數 >= 4 的學生
fail_4_or_more = df[fail_counts >= 4]

# 顯示結果
print("\n=== 不及格科目數大於等於4的學生名單 ===")
print(fail_4_or_more)

# 輸出檔案路徑
output_path = input("\n請輸入CSV檔案【輸出儲存路徑與檔名】：").strip()

# 儲存成CSV
fail_4_or_more.to_csv(output_path, index=False, encoding='utf-8-sig')
print(f"\n✅ 名單已成功儲存至：{output_path}")
