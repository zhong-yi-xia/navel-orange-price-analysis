# -*- coding: utf-8 -*-
"""
数据清洗与分析
- 批发价: 元/斤 -> 元/kg, 异常值剔除, 增加年/月/上市季字段
- 零售价: 解析规格 -> 计算 元/斤, 与批发价对比得出加价倍率
输入: data/raw_wholesale.csv, data/raw_retail.csv
输出: data/clean_wholesale.csv, data/clean_retail.csv
"""
import re
import pandas as pd

pd.set_option("display.unicode.east_asian_width", True)


def clean_wholesale() -> pd.DataFrame:
    df = pd.read_csv("data/raw_wholesale.csv")
    raw_len = len(df)

    # 1) 日期解析
    df["date"] = pd.to_datetime(df["pubDate"]).dt.date
    df["date"] = pd.to_datetime(df["date"])

    # 2) 数值化 + 单位换算（原数据单位: 元/斤 -> 元/kg）
    for col in ["lowPrice", "avgPrice", "highPrice"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    missing = df["avgPrice"].isna().sum()
    df = df.dropna(subset=["avgPrice"])

    # 3) 同日多条记录（不同等级/规格）按日均值聚合，保留信息而非直接去重
    multi = (df.groupby("date").size() > 1).sum()
    df = (df.groupby("date", as_index=False)
            .agg(avgPrice=("avgPrice", "mean"),
                 lowPrice=("lowPrice", "mean"),
                 highPrice=("highPrice", "mean"),
                 records=("avgPrice", "size"))
            .sort_values("date"))
    dup = multi

    # 4) 异常值：IQR 法
    q1, q3 = df["avgPrice"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
    outlier = ((df["avgPrice"] < lower) | (df["avgPrice"] > upper)).sum()
    df = df[(df["avgPrice"] >= lower) & (df["avgPrice"] <= upper)]

    # 5) 派生字段
    df["price_yuan_jin"] = df["avgPrice"].round(2)
    df["price_yuan_kg"] = (df["avgPrice"] * 2).round(2)
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    # 赣南脐橙上市季: 11月-次年2月
    df["is_season"] = df["month"].isin([11, 12, 1, 2]).astype(int)

    out = df[["date", "year", "month", "is_season", "price_yuan_jin", "price_yuan_kg"]]
    out.to_csv("data/clean_wholesale.csv", index=False, encoding="utf-8-sig")

    print(f"[批发价] 原始 {raw_len} 条 -> 清洗后 {len(out)} 条"
          f"（缺失 {missing}，同日多条聚合 {dup} 天，异常 {outlier}）")
    print(f"[批发价] 时间范围: {out['date'].min():%Y-%m-%d} ~ {out['date'].max():%Y-%m-%d}")
    return out


def clean_retail() -> pd.DataFrame:
    df = pd.read_csv("data/raw_retail.csv")
    raw_len = len(df)

    # 解析规格中的斤数，如 "10斤" -> 10
    def parse_jin(spec):
        m = re.search(r"(\d+(?:\.\d+)?)\s*斤", str(spec))
        return float(m.group(1)) if m else None

    df["jin"] = df["规格"].apply(parse_jin)
    df["price"] = pd.to_numeric(df["价格(元)"], errors="coerce")
    known = df.dropna(subset=["jin", "price"]).copy()
    known["price_yuan_jin"] = (known["price"] / known["jin"]).round(2)

    # 剔除明显不是鲜果单价的异常（如单价低于 1 元/斤或高于 20 元/斤）
    known = known[(known["price_yuan_jin"] >= 1) & (known["price_yuan_jin"] <= 20)]

    out = known[["商品名称", "规格", "jin", "price", "price_yuan_jin", "店铺", "采集日期"]]
    out.to_csv("data/clean_retail.csv", index=False, encoding="utf-8-sig")
    print(f"[零售价] 原始 {raw_len} 条 -> 规格可解析 {len(out)} 条"
          f"（{raw_len - len(out)} 条规格标注为未知，未参与单价计算）")
    return out


def analyze(wh: pd.DataFrame, rt: pd.DataFrame):
    print("\n===== 分析结论 =====")
    # 结论1: 上市季 vs 淡季
    season = wh[wh["is_season"] == 1]["price_yuan_kg"].mean()
    off = wh[wh["is_season"] == 0]["price_yuan_kg"].mean()
    print(f"1) 上市季(11-2月)批发均价 {season:.2f} 元/kg，淡季 {off:.2f} 元/kg，"
          f"淡季高出 {(off / season - 1) * 100:.1f}%")

    # 结论2: 年度走势
    year_avg = wh.groupby("year")["price_yuan_kg"].mean().round(2)
    print("2) 各年度批发均价(元/kg):",
          "，".join(f"{y}年 {v}" for y, v in year_avg.items()))

    # 结论3: 批发-零售价差
    if len(rt):
        rt_med = rt["price_yuan_jin"].median()
        wh_now = wh[wh["date"] >= wh["date"].max() - pd.Timedelta(days=7)]["price_yuan_jin"].mean()
        print(f"3) 电商零售中位价 {rt_med:.2f} 元/斤，同期批发价 {wh_now:.2f} 元/斤，"
              f"零售约为批发的 {rt_med / wh_now:.1f} 倍（流通加价率约 {(rt_med / wh_now - 1) * 100:.0f}%）")
        print(f"   零售单价区间: {rt['price_yuan_jin'].min():.2f} ~ {rt['price_yuan_jin'].max():.2f} 元/斤")


if __name__ == "__main__":
    wh = clean_wholesale()
    rt = clean_retail()
    analyze(wh, rt)
