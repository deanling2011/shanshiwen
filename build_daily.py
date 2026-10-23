# -*- coding: utf-8 -*-
"""
「历史上的今天」裁剪 + 图片生成脚本。

功能：
  1. 给定日期（默认今天，也可传 MM-DD 参数），从 data/MM-DD.json 读取历年内容
  2. 生成 markdown 归档到 archive/MM-DD.md
  3. 生成分年文字图到 img/MM-DD.png（年度合一）及 img/MM-DD-YYYY.png（单年图）

图片策略：
  - 单年一图：每个年份一张，高度可控、手机预览清晰（QQ 内直接可读）
  - 另合成一张全量图 MM-DD.png（总览，可能很长，仅作备用）

用法：
  python build_daily.py            # 今天
  python build_daily.py 10-22      # 指定月-日
"""
import json
import os
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE, "data")
ARCHIVE_DIR = os.path.join(BASE, "archive")
IMG_DIR = os.path.join(BASE, "img")

FONT_BOLD = os.environ.get("FONT_BOLD", "C:/Windows/Fonts/msyhbd.ttc")
FONT_REG = os.environ.get("FONT_REG", "C:/Windows/Fonts/msyh.ttc")
# 若本地 fonts/ 目录存在则优先使用（适配 GitHub Actions Linux 环境）
if os.path.exists(os.path.join(BASE, "fonts", "msyh.ttc")):
    FONT_REG = os.path.join(BASE, "fonts", "msyh.ttc")
    FONT_BOLD = os.path.join(BASE, "fonts", "msyhbd.ttc")

W = 1080
MARGIN = 60
LINE_H = 52

BG = (15, 17, 21)
TEXT = (232, 234, 240)
DIM = (154, 163, 178)
ACCENT = (212, 162, 90)


def pad(n):
    return f"{n:02d}"


def today_md():
    t = datetime.now()
    return f"{pad(t.month)}-{pad(t.day)}"


def load_data(md):
    p = os.path.join(DATA_DIR, f"{md}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build_markdown(md, data):
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    m, d = md.split("-")
    title = f"{int(m)}月{int(d)}日"
    lines = [f"# 山师文集 · {title} · 历史上的今天", ""]
    total = 0
    for g in data:
        lines.append(f"## {g['year']} 年")
        lines.append("")
        for txt in g["items"]:
            total += 1
            lines.append(txt)
            lines.append("")
    out = os.path.join(ARCHIVE_DIR, f"{md}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out, total


def wrap_text(text, font, max_w):
    """中文按字符换行，返回行数组"""
    lines = []
    cur = ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        t = cur + ch
        if font.getlength(t) <= max_w:
            cur = t
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def render_card(title, subtitle, blocks, out_path, foot=None):
    """
    渲染一张卡片图。
    blocks: [(year_or_None, [wrapped_lines])]
    采用两遍法：先精确计算内容总高，再创建画布绘制，避免内容被截断。
    """
    font_title = ImageFont.truetype(FONT_BOLD, 52)
    font_sub = ImageFont.truetype(FONT_REG, 30)
    font_year = ImageFont.truetype(FONT_BOLD, 38)
    font_body = ImageFont.truetype(FONT_REG, 34)

    def measure(y=0):
        y += MARGIN
        y += 84                                        # 标题
        if subtitle:
            y += 46
        y += 24
        for year, yl in blocks:
            if year is not None:
                y += 62
            y += len(yl) * LINE_H
            y += 20
        if foot:
            y += 56
        return y

    end_y = measure()
    H = end_y + MARGIN // 2
    img = Image.new("RGB", (W, max(H, 500)), BG)
    draw = ImageDraw.Draw(img)

    y = MARGIN
    draw.text((MARGIN, y), title, font=font_title, fill=ACCENT)
    y += 84
    if subtitle:
        draw.text((MARGIN, y), subtitle, font=font_sub, fill=DIM)
        y += 46
    y += 24

    for year, yl in blocks:
        if year is not None:
            draw.text((MARGIN, y), f"{year} 年", font=font_year, fill=ACCENT)
            y += 62
        for ln in yl:
            draw.text((MARGIN, y), ln, font=font_body, fill=TEXT)
            y += LINE_H
        y += 20

    if foot:
        draw.text((MARGIN, y + 6), foot, font=font_sub, fill=DIM)
        y += 56

    img = img.crop((0, 0, W, min(y + MARGIN // 2, img.height)))
    img.save(out_path, "PNG")
    return out_path


def build_images(md, data):
    """单年一图 + 合并总览图"""
    os.makedirs(IMG_DIR, exist_ok=True)
    m, d = md.split("-")
    md_title = f"山师文集 · {int(m)}月{int(d)}日 · 历史上的今天"

    outputs = []

    # 单年一图：MM-DD-YYYY.png
    for g in data:
        year = g["year"]
        blocks = []
        idx = 0
        for txt in g["items"]:
            idx += 1
            wrapped = wrap_text(txt, ImageFont.truetype(FONT_REG, 34), W - MARGIN * 2)
            # 条目编号放首行前缀
            wrapped[0] = f"#{idx}  {wrapped[0]}" if len(wrapped) else f"#{idx}"
            blocks.append((None, wrapped))
        sub = f"{year} 年 · 共 {len(g['items'])} 条"
        out = os.path.join(IMG_DIR, f"{md}-{year}.png")
        render_card(md_title, sub, blocks, out, foot=None)
        outputs.append(out)

    # 合并总览图 MM-DD.png（备用）
    blocks = []
    for g in data:
        wrapped_items = []
        idx = 0
        for txt in g["items"]:
            idx += 1
            ws = wrap_text(txt, ImageFont.truetype(FONT_REG, 34), W - MARGIN * 2)
            if ws:
                ws[0] = f"#{idx}  {ws[0]}"
            wrapped_items.extend(ws)
        blocks.append((g["year"], wrapped_items))
    total_n = sum(len(g["items"]) for g in data)
    out = os.path.join(IMG_DIR, f"{md}.png")
    render_card(md_title, f"共 {total_n} 条 · 覆盖 {len(data)} 个年份", blocks, out,
                foot=None)
    outputs.append(out)

    return outputs


def main():
    md = sys.argv[1] if len(sys.argv) > 1 else today_md()
    data = load_data(md)
    if data is None:
        print(f"[跳过] {md} 无数据文件")
        return
    md_path, total = build_markdown(md, data)
    imgs = build_images(md, data)
    years = [g["year"] for g in data]
    print(f"[{md}] 条数={total} 年份={years}")
    print(f"  markdown -> {md_path}")
    for p in imgs:
        from PIL import Image as I
        w, h = I.open(p).size
        print(f"  image    -> {p}  ({w}x{h})")


if __name__ == "__main__":
    main()
