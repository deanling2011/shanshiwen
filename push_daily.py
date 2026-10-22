# -*- coding: utf-8 -*-
"""
PushDeer 推送脚本：推送「历史上的今天」卡片 + 图片直链。

用法：
  python push_daily.py <pushkey> [MM-DD]

推送内容为 markdown 格式：
  - 今日标题 + 条数摘要
  - 文字版链接（GitHub Pages / jsDelivr）
  - 图片版直链（jsDelivr CDN 加速，国内免翻墙直连）
"""
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

REPO = "deanling2011/shanwenji"
BRANCH = "main"
# 国内免翻墙加速通道：ghproxy 镜像 raw 文件
RAW = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
GH = f"https://ghproxy.net/{RAW}"


def pad(n):
    return f"{n:02d}"


def main():
    if len(sys.argv) < 2:
        print("用法: python push_daily.py <pushkey> [MM-DD]")
        sys.exit(1)
    pushkey = sys.argv[1]
    t = datetime.now()
    md = sys.argv[2] if len(sys.argv) > 2 else f"{pad(t.month)}-{pad(t.day)}"

    # 读取 index 获取条数
    count, years_n = 0, 0
    try:
        with open("data/index.json", encoding="utf-8") as f:
            idx = json.load(f)
        if md in idx:
            count = idx[md]["count"]
            years_n = len(idx[md]["years"])
    except Exception:
        pass

    m, d = md.split("-")
    desp = (
        f"> 🌟 **{int(m)}月{int(d)}日 · 历史上的今天**\n"
        f"---\n"
        f"历年今日共 **{count}** 条内容，覆盖 **{years_n}** 个年份。\n\n"
        f"👉 [文字版在线阅读（免翻墙）]({GH}/archive/{md}.md)\n\n"
        f"🖼️ [图片版（免翻墙直连）]({GH}/img/{md}.png)"
    )

    payload = urllib.parse.urlencode({
        "pushkey": pushkey,
        "text": f"{int(m)}月{int(d)}日 · 历史上的今天",
        "desp": desp,
        "type": "markdown",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api2.pushdeer.com/message/push",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    print("PushDeer 响应:", json.dumps(body, ensure_ascii=False))
    if body.get("code") == 0:
        print("✅ 推送成功")
    else:
        print("❌ 推送失败")
        sys.exit(2)


if __name__ == "__main__":
    main()
