# -*- coding: utf-8 -*-
"""
将清洗后的 CSV 数据导入 MySQL 并执行分析 SQL
- 库: navel_price  表: wholesale_daily / retail_price
"""
import pandas as pd
import pymysql

MYSQL = dict(host="127.0.0.1", user="root", password="",
             database="navel_price", charset="utf8mb4")

def load_wholesale(conn):
    df = pd.read_csv("data/clean_wholesale.csv", parse_dates=["date"])
    rows = [(r["date"].date(), int(r["year"]), int(r["month"]), int(r["is_season"]),
             float(r["price_yuan_jin"]), float(r["price_yuan_kg"]), int(r["records"]))
            for _, r in df.iterrows()]
    sql = ("REPLACE INTO wholesale_daily "
           "(date, year, month, is_season, price_yuan_jin, price_yuan_kg, records) "
           "VALUES (%s,%s,%s,%s,%s,%s,%s)")
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()
    print(f"wholesale_daily 导入 {cur.rowcount if False else len(rows)} 行")

def load_retail(conn):
    df = pd.read_csv("data/clean_retail.csv")
    rows = [(r["商品名称"], r["规格"],
             None if pd.isna(r["jin"]) else float(r["jin"]),
             float(r["price"]),
             None if pd.isna(r["price_yuan_jin"]) else float(r["price_yuan_jin"]),
             r["店铺"], r["采集日期"])
            for _, r in df.iterrows()]
    sql = ("INSERT INTO retail_price "
           "(prod_name, spec, jin, price, price_yuan_jin, shop, collect_date) "
           "VALUES (%s,%s,%s,%s,%s,%s,%s)")
    with conn.cursor() as cur:
        cur.executemany(sql, rows)
    conn.commit()
    print(f"retail_price 导入 {len(rows)} 行")

def run_analysis(conn):
    with open("sql/analysis.sql", encoding="utf-8") as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip() and not all(
            line.strip().startswith("--") or not line.strip()
            for line in s.splitlines())]
    titles = ["①上市季 vs 淡季", "②年度走势", "③月度季节性", "④近一年价格TOP10", "⑤批发-零售价差"]
    with conn.cursor() as cur:
        i = 0
        for stmt in statements:
            body = "\n".join(l for l in stmt.splitlines() if not l.strip().startswith("--")).strip()
            if not body or body.upper().startswith("USE"):
                continue
            cur.execute(body)
            print(f"\n=== {titles[i] if i < len(titles) else i} ===")
            for row in cur.fetchall():
                print(row)
            i += 1

if __name__ == "__main__":
    conn = pymysql.connect(**MYSQL)
    try:
        load_wholesale(conn)
        load_retail(conn)
        run_analysis(conn)
    finally:
        conn.close()
    print("\n全部完成")
