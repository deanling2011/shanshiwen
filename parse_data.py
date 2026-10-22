# -*- coding: utf-8 -*-
"""
解析 shanshi_cleaned.xlsx，生成按「月-日」拆分的数据文件，供网页按需加载。

输出结构（全部放在 data/ 目录）：
  data/index.json        — 索引：每个 "MM-DD" -> { count, years: [...] }
  data/MM-DD.json        — 该月-日的内容，按年份分组：[{year, items:[...]}]
  data/meta.json         — 元信息

这样网页加载「历史上的今天」只需请求一个几十 KB 的小文件，秒开。
"""
import openpyxl
import json
import os
from datetime import datetime
from collections import defaultdict, OrderedDict

SRC = r"D:/ext.lingzicheng1/Downloads/shanshi_cleaned.xlsx"
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT_DIR, exist_ok=True)


def build():
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ws = wb["shanshi_cleaned"]
    rows = list(ws.iter_rows(values_only=True))[1:]

    clean = []
    bad = []
    for r in rows:
        d, c = r[0], r[1]
        if isinstance(d, datetime) and isinstance(c, str) and c.strip():
            clean.append((d.date(), c.strip()))
        else:
            bad.append((str(d), c))

    # 数据修正：'2028-13-34' 为日期笔误，实际发布于 2018-05-11 20:08
    # 将该条内容归入 2018-05-11
    for bd, c in bad:
        if str(bd) == "2028-13-34" and c:
            fixed_date = datetime(2018, 5, 11).date()
            fixed_content = "2018年5月11日 20:08 " + c.strip().strip("\u200b")
            clean.append((fixed_date, fixed_content))
            print(f"[修正] 2028-13-34 -> 2018-05-11: {fixed_content[:40]}...")
            bad.remove((bd, c))

    by_md = defaultdict(list)
    for d, c in clean:
        by_md[(d.month, d.day)].append((d, c))

    index = OrderedDict()
    for (m, day) in sorted(by_md.keys()):
        key = f"{m:02d}-{day:02d}"
        entries = sorted(by_md[(m, day)], key=lambda x: x[0])
        grouped = []
        for d, c in entries:
            if grouped and grouped[-1]["year"] == d.year:
                grouped[-1]["items"].append(c)
            else:
                grouped.append({"year": d.year, "items": [c]})
        # 写单个文件
        with open(os.path.join(OUT_DIR, f"{key}.json"), "w", encoding="utf-8") as f:
            json.dump(grouped, f, ensure_ascii=False)
        # 索引
        index[key] = {
            "count": sum(len(g["items"]) for g in grouped),
            "years": [g["year"] for g in grouped],
        }

    with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)

    dates = [d for d, _ in clean]
    meta = {
        "total": len(clean),
        "date_min": str(min(dates)),
        "date_max": str(max(dates)),
        "years": sorted({d.year for d in dates}),
        "covered_md": len(index),
        "bad_rows": len(bad),
    }
    with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f"有效: {meta['total']} | 丢弃: {meta['bad_rows']} | 覆盖月-日: {meta['covered_md']}/366")
    print(f"索引文件: {os.path.join(OUT_DIR, 'index.json')}")


if __name__ == "__main__":
    build()
