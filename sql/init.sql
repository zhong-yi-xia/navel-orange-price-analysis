-- 脐橙价格分析：建库建表脚本
-- 数据库: navel_price

CREATE DATABASE IF NOT EXISTS navel_price DEFAULT CHARSET utf8mb4;
USE navel_price;

-- 批发价日表（2022-2026，新发地市场）
DROP TABLE IF EXISTS wholesale_daily;
CREATE TABLE wholesale_daily (
    date          DATE         NOT NULL COMMENT '日期',
    year          INT          NOT NULL COMMENT '年',
    month         INT          NOT NULL COMMENT '月',
    is_season     TINYINT      NOT NULL COMMENT '是否上市季(11-2月) 1是 0否',
    price_yuan_jin DECIMAL(6,2) NOT NULL COMMENT '均价(元/斤)',
    price_yuan_kg DECIMAL(6,2) NOT NULL COMMENT '均价(元/公斤)',
    records       INT          NOT NULL DEFAULT 1 COMMENT '当日记录数',
    PRIMARY KEY (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='脐橙批发价日度数据';

-- 电商零售价表（2026-11-16 京东采集）
DROP TABLE IF EXISTS retail_price;
CREATE TABLE retail_price (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    prod_name      VARCHAR(200) NOT NULL COMMENT '商品名称',
    spec           VARCHAR(50)  DEFAULT NULL COMMENT '规格',
    jin            DECIMAL(6,2) DEFAULT NULL COMMENT '斤数',
    price          DECIMAL(10,2) NOT NULL COMMENT '售价(元)',
    price_yuan_jin DECIMAL(6,2) DEFAULT NULL COMMENT '单价(元/斤)',
    shop           VARCHAR(100) DEFAULT NULL COMMENT '店铺',
    collect_date   DATE         NOT NULL COMMENT '采集日期'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='脐橙电商零售价';
