# -*- coding: utf-8 -*-
"""
脐橙价格可视化大屏
输入: data/clean_wholesale.csv
输出: output/index.html
"""
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Bar, Line, Page
from pyecharts.globals import CurrentConfig

# 关键：使用本地 echarts 资源，避免依赖国外 CDN（离线也能打开）
CurrentConfig.ONLINE_HOST = "./assets/"

df = pd.read_csv("data/clean_wholesale.csv", parse_dates=["date"])
df = df.sort_values("date")

# ---------- 图1: 价格走势（30日移动平均，去掉日常抖动）----------
daily = df.set_index("date")["price_yuan_kg"].resample("D").mean().ffill()
ma30 = daily.rolling(30, min_periods=1).mean().round(2)

line = (
    Line(init_opts=opts.InitOpts(width="100%", height="400px", theme="light"))
    .add_xaxis([d.strftime("%Y-%m") for d in ma30.index])
    .add_yaxis("30日均价", ma30.tolist(), is_smooth=True,
               label_opts=opts.LabelOpts(is_show=False),
               linestyle_opts=opts.LineStyleOpts(width=2, color="#C8102E"),
               areastyle_opts=opts.AreaStyleOpts(opacity=0.15, color="#C8102E"))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2022-2026 脐橙批发价走势（元/公斤）", pos_left="center"),
        xaxis_opts=opts.AxisOpts(type_="category", axislabel_opts=opts.LabelOpts(interval=59)),
        yaxis_opts=opts.AxisOpts(name="元/公斤", min_=0),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        legend_opts=opts.LegendOpts(is_show=False),
    )
)

# ---------- 图2: 月度均价（季节性）----------
month_avg = df.groupby("month")["price_yuan_kg"].mean().round(2)
colors = ["#C8102E" if m in (11, 12, 1, 2) else "#8FA8BF" for m in month_avg.index]

bar = (
    Bar(init_opts=opts.InitOpts(width="100%", height="350px", theme="light"))
    .add_xaxis([f"{m}月" for m in month_avg.index])
    .add_yaxis("月均批发价", month_avg.tolist(),
               itemstyle_opts=opts.ItemStyleOpts(color=None),
               label_opts=opts.LabelOpts(is_show=True, position="top", font_size=10))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="各月平均批发价（红色=上市季 11-2月）", pos_left="center"),
        xaxis_opts=opts.AxisOpts(name="月份"),
        yaxis_opts=opts.AxisOpts(name="元/公斤", min_=0),
        legend_opts=opts.LegendOpts(is_show=False),
    )
)
# 逐柱设置颜色
bar.options["series"][0]["data"] = [
    {"value": v, "itemStyle": {"color": c}} for v, c in zip(month_avg.tolist(), colors)
]

# ---------- 图3: 年度均价 ----------
year_avg = df.groupby("year")["price_yuan_kg"].mean().round(2)
bar2 = (
    Bar(init_opts=opts.InitOpts(width="100%", height="350px", theme="light"))
    .add_xaxis([f"{y}年" for y in year_avg.index])
    .add_yaxis("年度均价", year_avg.tolist(),
               label_opts=opts.LabelOpts(is_show=True, position="top"))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="各年度平均批发价", pos_left="center"),
        yaxis_opts=opts.AxisOpts(name="元/公斤", min_=0),
        legend_opts=opts.LegendOpts(is_show=False),
    )
)

page = Page(layout=Page.SimplePageLayout, page_title="赣南脐橙价格数据监控")
page.add(line, bar, bar2)
page.render("output/index.html")
print("已生成 output/index.html")
