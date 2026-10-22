# 山人拾遗 · shanwenji

每日自动归档「历史上的今天」文集：同一天（月-日）历年内容聚合展示，支持文字版网页浏览与图片版推送。

## 功能

- **每日自动裁剪**：GitHub Actions 每天北京时间 08:10 运行，裁剪当日（月-日）历年内容
- **文字版归档**：`archive/MM-DD.md`，jsDelivr CDN 国内直连
- **图片版长图**：`img/MM-DD.png`（总览）+ `img/MM-DD-YYYY.png`（单年分图）
- **网页浏览**：GitHub Pages 静态网页，支持按月/日导航，查看任意日期的历年文集
- **推送**：PushDeer 推送卡片 + 图片/文字直链

## 目录结构

```
├── index.html          # 前端网页（GitHub Pages 入口）
├── data/               # 静态数据（366 个 MM-DD.json + index.json + meta.json）
├── archive/            # 每日 markdown 归档
├── img/                # 每日生成的图片
├── scripts/            # 辅助脚本
├── build_daily.py      # 每日裁剪 + 图片生成
├── push_daily.py       # PushDeer 推送
├── parse_data.py       # Excel 数据源解析（一次性）
└── .github/workflows/daily.yml
```

## CDN 直连（国内免翻墙）

- 文字版：`https://cdn.jsdelivr.net/gh/deanling2011/shanwenji@main/archive/10-22.md`
- 图片版：`https://cdn.jsdelivr.net/gh/deanling2011/shanwenji@main/img/10-22.png`

## 手动触发

GitHub 仓库 → Actions → Daily Archive → Run workflow
