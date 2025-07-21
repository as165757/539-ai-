from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# 根路徑測試用
@app.route('/')
def home():
    return '🎉 539 AI API 部署成功！'

# 範例 API：回傳兩數相加
@app.route('/add', methods=['GET'])
def add():
    try:
        a = int(request.args.get('a', 0))
        b = int(request.args.get('b', 0))
        return jsonify({
            'a': a,
            'b': b,
            'result': a + b
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 這是你未來可以擴充放 539 分析的地方
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        # 模擬結果
        result = {
            'input': data,
            'message': '預測邏輯未實作，請在這裡擴充你的 539 AI 分析'
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 本地開發時才會啟動
if __name__ == '__main__':
    app.run(debug=True)


# === 替代農曆月份分析（以陽曆月近似）===
def 分析_陽曆近似農曆(df_recent):
    df_recent = df_recent.copy()
    df_recent['陽曆月'] = df_recent['開獎日期'].dt.month
    top_month = df_recent['陽曆月'].mode()[0]
    df_filtered = df_recent[df_recent['陽曆月'] == top_month]
    number_columns = ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5']
    all_numbers = df_filtered[number_columns].values.flatten().astype(int)
    counter = Counter(all_numbers)
    return [n for n, _ in counter.most_common(3)]

# === 連號分析法 ===
def 分析_連號規律(df_recent):
    number_columns = ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5']
    consecutive = Counter()
    for row in df_recent[number_columns].astype(int).values:
        row = sorted(row)
        for i in range(len(row) - 1):
            if row[i+1] - row[i] == 1:
                consecutive[row[i]] += 1
                consecutive[row[i+1]] += 1
    return [num for num, _ in consecutive.most_common(3)]

# === 冷熱區過濾 ===
def 過濾_冷熱區號碼(all_numbers, df_recent):
    all_numbers = list(set(all_numbers))
    number_columns = ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5']
    all_drawn = df_recent[number_columns].values.flatten().astype(int)
    counter = Counter(all_drawn)
    counts = counter.most_common()
    threshold = len(df_recent) * 5 / 39
    hot = [n for n, c in counts if c > threshold * 1.2]
    cold = [n for n, c in counts if c < threshold * 0.6]
    result = [n for n in all_numbers if n not in hot and n not in cold]
    return result

# === 共現組合分析 ===
def 找出共現最多的兩顆(top_numbers, df_recent):
    number_columns = ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5']
    pair_counter = Counter()
    for _, row in df_recent[number_columns].iterrows():
        nums = set(map(int, row.values))
        common = nums.intersection(top_numbers)
        for pair in combinations(sorted(common), 2):
            pair_counter[pair] += 1
    if pair_counter:
        return pair_counter.most_common(1)[0]
    return (None, 0)

# === 其他分析法 ===
def 分析_五區分佈法(df_recent):
    分區 = {
        1: list(range(1, 9)),
        2: list(range(9, 17)),
        3: list(range(17, 25)),
        4: list(range(25, 33)),
        5: list(range(33, 40))
    }
    all_numbers = df_recent[['獎號1','獎號2','獎號3','獎號4','獎號5']].values.flatten().astype(int)
    counter = Counter(all_numbers)
    zone_score = {z: sum(counter[n] for n in nums) for z, nums in 分區.items()}
    熱門區 = sorted(zone_score.items(), key=lambda x: x[1], reverse=True)[:2]
    推薦號 = []
    for 區, _ in 熱門區:
        區內熱門 = sorted(分區[區], key=lambda n: counter[n], reverse=True)[:2]
        推薦號.extend(區內熱門)
    return 推薦號

def 分析_尾數版路(df_recent):
    all_numbers = df_recent[['獎號1','獎號2','獎號3','獎號4','獎號5']].values.flatten().astype(int)
    counter = Counter(n % 10 for n in all_numbers)
    熱門尾 = [尾 for 尾, _ in counter.most_common(2)]
    return [n for n in set(all_numbers) if n % 10 in 熱門尾][:3]

def 分析_直欄重複法(df_recent):
    結果 = []
    for col in ['獎號1','獎號2','獎號3','獎號4','獎號5']:
        counter = Counter(df_recent[col].astype(int))
        if counter:
            結果.append(counter.most_common(1)[0][0])
    return 結果[:2]

def 分析_跳點補缺法(df_recent):
    all_rows = df_recent[['獎號1','獎號2','獎號3','獎號4','獎號5']].astype(int).values.tolist()
    最近出現 = {}
    結果 = set()
    for idx, row in enumerate(reversed(all_rows)):
        for num in row:
            if num not in 最近出現:
                最近出現[num] = idx
            elif idx - 最近出現[num] >= 2:
                結果.add(num)
    return list(結果)[:2]

def 分析_對角連線圖(df_recent):
    matrix = df_recent[['獎號1','獎號2','獎號3','獎號4','獎號5']].astype(int).values[-30:]
    結果 = set()
    for offset in range(-3, 4):
        for i in range(len(matrix) - abs(offset)):
            if offset >= 0:
                nums = [matrix[i + j][j] for j in range(min(5, len(matrix) - i))]
            else:
                nums = [matrix[i + j][-j - 1] for j in range(min(5, len(matrix) - i))]
            結果.update(nums)
    return list(結果)[:3]

# === 讀取所有上傳資料 ===
base_path = "C:/Users/USER/Desktop/539"
years = range(2018, 2026)
files = [f"{base_path}/今彩539_{y}.csv" for y in years]
dfs = [pd.read_csv(file) for file in files if os.path.exists(file)]

uploaded_files = [
    "今彩539_2018.csv", "今彩539_2019.csv", "今彩539_2020.csv", "今彩539_2021.csv",
    "今彩539_2022.csv", "今彩539_2023.csv", "今彩539_2024.csv", "今彩539_2025.csv"
]
dfs = [pd.read_csv(os.path.join(base_path, f)) for f in uploaded_files]
df_all = pd.concat(dfs, ignore_index=True)

df_all["開獎日期"] = pd.to_datetime(df_all["開獎日期"], errors="coerce")
df_all.dropna(subset=["開獎日期"], inplace=True)
df_all["週期"] = df_all["開獎日期"].dt.weekday

weekday_map = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
today = datetime.today()
today_weekday = today.weekday()
weekday_name = weekday_map[today_weekday]
same_day_df = df_all[df_all["週期"] == today_weekday]
recent_df = same_day_df.sort_values(by="開獎日期", ascending=False).head(800)

# === 整合分析 ===
方法匯總 = (
    分析_五區分佈法(recent_df) +
    分析_尾數版路(recent_df) +
    分析_直欄重複法(recent_df) +
    分析_跳點補缺法(recent_df) +
    分析_對角連線圖(recent_df) +
    分析_陽曆近似農曆(recent_df) +
    分析_連號規律(recent_df)
)

# 過濾冷熱區並轉成 int 型別
過濾後 = 過濾_冷熱區號碼(方法匯總, recent_df)
freq = Counter(過濾後)
主牌 = [int(num) for num, _ in freq.most_common(6)]

# 找出強烈共現兩顆專車牌
專車, 共現次 = 找出共現最多的兩顆(主牌, recent_df)

# === 顯示分析結果 ===
print("━"*30)
print(f"🗕️ 今天是週期 {weekday_name} (代碼 {today_weekday})")
print("📌 使用分析法：五區 + 尾數 + 直欄 + 跳號 + 對角 + 陽曆月 + 連號 → 過濾冷熱區")
print(f"🌟 綜合推薦主牌（最多5顆）：", "、".join(map(str, 主牌)))
if 專車:
    print(f"🚀 強烈推薦專車牌：{專車[0]}、{專車[1]}（共出現 {共現次} 次）")
else:
    print("⚠️ 無法找出共現號碼")
print("━"*30)
