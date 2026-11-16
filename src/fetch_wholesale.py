# -*- coding: utf-8 -*-
"""
采集新发地批发市场「脐橙」历史批发价格数据
数据来源: www.xinfadi.com.cn (全国最大农产品批发市场)
输出: data/raw_wholesale.csv
"""
import time
import pandas as pd
import requests

URL = "http://www.xinfadi.com.cn/getPriceData.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def fetch_page(page: int, page_size: int = 500) -> list:
    """抓取一页数据，返回记录列表"""
    payload = {
        "limit": page_size,
        "current": page,
        "pubDateStartTime": "",
        "pubDateEndTime": "",
        "prodPrid": "",
        "prodName": "脐橙",
        "purpose": "",
        "startCount": "",
        "limitCount": "",
    }
    resp = requests.post(URL, data=payload, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("list", [])

def main():
    # 第一页先探测总条数
    first = fetch_page(1)
    total = requests.post(URL, data={"limit": 500, "current": 1, "prodName": "脐橙",
                                     "pubDateStartTime": "", "pubDateEndTime": "",
                                     "prodPrid": "", "purpose": "", "startCount": "",
                                     "limitCount": ""},
                          headers=HEADERS, timeout=30).json().get("count", 0)
    print(f"共 {total} 条记录，每页 500 条，需 {((total - 1) // 500) + 1} 页")

    records = list(first)
    page = 2
    while len(records) < total:
        time.sleep(2)  # 限速，礼貌抓取
        batch = fetch_page(page)
        if not batch:
            break
        records.extend(batch)
        print(f"已采集 {len(records)}/{total}")
        page += 1

    df = pd.DataFrame(records)
    df = df[["pubDate", "prodName", "prodPcat", "lowPrice", "avgPrice",
             "highPrice", "place", "unitInfo"]]
    df.to_csv("data/raw_wholesale.csv", index=False, encoding="utf-8-sig")
    print(f"完成: {len(df)} 条已保存到 data/raw_wholesale.csv")
    print(df.head())

if __name__ == "__main__":
    main()
