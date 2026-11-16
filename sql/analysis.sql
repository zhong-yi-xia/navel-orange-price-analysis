-- 脐橙价格分析：五条核心分析 SQL

USE navel_price;

-- 1. 上市季 vs 淡季 批发均价对比
SELECT is_season AS 上市季,
       COUNT(*) AS 天数,
       ROUND(AVG(price_yuan_kg), 2) AS 均价_元每公斤
FROM wholesale_daily
GROUP BY is_season;

-- 2. 各年度批发均价走势
SELECT year AS 年份,
       ROUND(AVG(price_yuan_kg), 2) AS 年均价_元每公斤,
       ROUND(MIN(price_yuan_kg), 2) AS 年最低,
       ROUND(MAX(price_yuan_kg), 2) AS 年最高
FROM wholesale_daily
GROUP BY year
ORDER BY year;

-- 3. 各月平均价（季节性曲线）
SELECT month AS 月份,
       ROUND(AVG(price_yuan_kg), 2) AS 月均_元每公斤
FROM wholesale_daily
GROUP BY month
ORDER BY month;

-- 4. 近一年价格波动最大的10天
SELECT date AS 日期, price_yuan_kg AS 当日均价_元每公斤
FROM wholesale_daily
WHERE date >= DATE_SUB((SELECT MAX(date) FROM wholesale_daily), INTERVAL 365 DAY)
ORDER BY price_yuan_kg DESC
LIMIT 10;

-- 5. 批发-零售价差（同期对比）
SELECT '电商零售中位价(元/斤)' AS 指标,
       (SELECT ROUND(AVG(price_yuan_jin), 2) FROM
            (SELECT price_yuan_jin FROM retail_price
             WHERE price_yuan_jin IS NOT NULL
             ORDER BY price_yuan_jin
             LIMIT 4 OFFSET 2) t) AS 数值
UNION ALL
SELECT '同期批发均价(元/斤)',
       (SELECT ROUND(AVG(price_yuan_jin), 2) FROM wholesale_daily
        WHERE date >= DATE_SUB((SELECT MAX(date) FROM wholesale_daily), INTERVAL 7 DAY));
