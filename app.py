from flask import Flask, request, jsonify
import pandas as pd
import os
from collections import Counter
from itertools import combinations
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return '🎉 539 AI API 部署成功！'

@app.route('/add', methods=['GET'])
def add():
    try:
        a = int(request.args.get('a', 0))
        b = int(request.args.get('b', 0))
        return jsonify({'a': a, 'b': b, 'result': a + b})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # === 讀取所有上傳資料 ===
        base_path = 'data'  # Railway 可用的相對資料夾
        years = range(2018, 2026)
        files = [f"{base_path}/今彩539_{y}.csv" for y in years]
        dfs = [pd.read_csv(file) for file in files if os.path.exists(file)]
        if not dfs:
            return jsonify({'error': '沒有找到任何 539 開獎資料'}), 400
        df_all = pd.concat(dfs, ignore_index=True)
        df_all["開獎日期"] = pd.to_datetime(df_all["開獎日期"], errors="coerce")
        df_all.dropna(subset=["開獎日期"], inplace=True)
        df_all["週期"] = df_all["開獎日期"].dt.weekday

        weekday_map = {0: "一", 1: "二", 2: "三", 3: "四", 4: "五", 5: "六", 6: "日"}
        today = datetime.today()
        today_weekday = today.weekday()
        same_day_df = df_all[df_all["週期"] == today_weekday]
        recent_df = same_day_df.sort_values(by="開獎日期", ascending=False).head(800)

        # 分析方法
        def 分析_五區分佈法(df):
            分區 = {
                1: list(range(1, 9)),
                2: list(range(9, 17)),
                3: list(range(17, 25)),
                4: list(range(25, 33)),
                5: list(range(33, 40))
            }
            all_numbers = df[['獎號1','獎號2','獎號3','獎號4','獎號5']].values.flatten().astype(int)
            counter = Counter(all_numbers)
            zone_score = {z: sum(counter[n] for n in nums) for z, nums in 分區.items()}
            熱門區 = sorted(zone_score.items(), key=lambda x: x[1], reverse=True)[:2]
            推薦號 = []
            for 區, _ in 熱門區:
                區內熱門 = sorted(分區[區], key=lambda n: counter[n], reverse=True)[:2]
                推薦號.extend(區內熱門)
            return 推薦號

        def 分析_尾數版路(df):
            all_numbers = df[['獎號1','獎號2','獎號3','獎號4','獎號5']].values.flatten().astype(int)
            counter = Counter(n % 10 for n in all_numbers)
            熱門尾 = [尾 for 尾, _ in counter.most_common(2)]
            return [n for n in set(all_numbers) if n % 10 in 熱門尾][:3]

        def 分析_直欄重複法(df):
            結果 = []
            for col in ['獎號1','獎號2','獎號3','獎號4','獎號5']:
                counter = Counter(df[col].astype(int))
                if counter:
                    結果.append(counter.most_common(1)[0][0])
            return 結果[:2]

        def 過濾_冷熱區號碼(all_numbers, df):
            all_numbers = list(set(all_numbers))
            number_columns = ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5']
            all_drawn = df[number_columns].values.flatten().astype(int)
            counter = Counter(all_drawn)
            threshold = len(df) * 5 / 39
            hot = [n for n, c in counter.items() if c > threshold * 1.2]
            cold = [n for n, c in counter.items() if c < threshold * 0.6]
            return [n for n in all_numbers if n not in hot and n not in cold]

        def 找出共現最多的兩顆(top_numbers, df):
            number_columns = ['獎號1', '獎號2', '獎號3', '獎號4', '獎號5']
            pair_counter = Counter()
            for _, row in df[number_columns].iterrows():
                nums = set(map(int, row.values))
                common = nums.intersection(top_numbers)
                for pair in combinations(sorted(common), 2):
                    pair_counter[pair] += 1
            return pair_counter.most_common(1)[0] if pair_counter else (None, 0)

        # 分析整合
        方法匯總 = (
            分析_五區分佈法(recent_df) +
            分析_尾數版路(recent_df) +
            分析_直欄重複法(recent_df)
        )
        過濾後 = 過濾_冷熱區號碼(方法匯總, recent_df)
        freq = Counter(過濾後)
        主牌 = [int(num) for num, _ in freq.most_common(5)]
        專車, 共現次 = 找出共現最多的兩顆(主牌, recent_df)

        return jsonify({
            "weekday": weekday_map[today_weekday],
            "主牌": 主牌,
            "專車牌": list(專車) if 專車 else [],
            "共現次數": 共現次 if 專車 else 0
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
