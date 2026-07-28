# 财报跟踪平台

全球锡 / 锌 / 铝 / 镍 / 铜企业财报产量数据跟踪网站。本地静态页面，**双击 `index.html` 即可使用**（file:// 协议直接运行，无需任何服务器）。

- 访问密码：`yafco888`（前端 SHA-256 校验，sessionStorage 记住；仅为本地防窥门槛，非安全加密）
- 数据来源：公司官方财报 / 业绩公告，汇总于三个 Excel 数据源

## 目录结构

```
财报跟踪平台/
  build_site.py      # 数据管道：读 Excel → 生成 data/data.js
  index.html         # 唯一入口（含密码门）
  assets/style.css   # 深色金融终端风样式
  assets/app.js      # 前端逻辑（纯 JS，无框架）
  data/data.js       # build 生成：window.SITE_DATA = {...}（script src 引入，避开 file:// 的 fetch/CORS 限制）
  README.md
```

## 日常使用

1. 更新 Excel 数据源（锡 / 锌产量表）；
2. 运行数据管道重建网站数据：

   ```
   python "D:\拷贝文件\E\永安\财报跟踪平台\build_site.py"
   ```

   运行后会打印各品种抽取到的公司数 / 数据点数摘要，并自动抽查关键数值（PASS/FAIL）。
   Windows 终端如显示乱码，可先执行 `set PYTHONIOENCODING=utf-8`（不影响生成文件，文件本身为 UTF-8）。
3. 刷新浏览器页面即可看到最新数据。

## 数据源

| 品种 | Excel | 说明 |
|---|---|---|
| 锡 | `D:\拷贝文件\E\永安\周报数据更新\进出口库存\海外主要公司产量.xlsx` | Sheet1 矿表/锭表 + Alphamin / Metals X / Timah / MSC 各公司 sheet +「季度补充」sheet |
| 锌 | `D:\拷贝文件\E\永安\锌\全球锌企季度产量梳理.xlsx` | 锌矿季度产量、锌锭冶炼季度产量、资本开支、更新日志 |
| 铝 | `D:\拷贝文件\E\永安\铝\全球铝企季度产量梳理.xlsx` | 铝土矿 / 氧化铝 / 电解铝季度产量（三个板块）、更新日志 |
| 镍 | `D:\拷贝文件\E\永安\镍\全球镍企季度产量梳理.xlsx` | 印尼中间品（重点板块，排第一位）/ 一级镍 / 镍铁NPI 季度产量、更新日志；单位=吨 |
| 铜 | `D:\拷贝文件\E\永安\铜\全球铜企季度产量梳理.xlsx` | 铜矿（海外，单位 kt）/ 国内铜企（单位万吨）季度产量、更新日志；两板块单位不同 |

注意：锡 Excel 部分单元格为公式且无缓存值，脚本一律以 `data_only=False` 读原始值，同比/累计由 Python 自行计算；铝/镍 Excel 同比列与总计行也是公式，同样跳过自算。镍表 26Q1/26Q2 列中的「待发布/未披露」等文本按无数据处理，但会记录在公司卡片上展示（⏳ 标记）。

## 功能

- **总览**：品种卡片（最新季度披露进度、首个板块合计及同比、最近更新）、财报披露倒计时（跨品种按日期升序）、最近更新日志；
- **品种页**：按品种配置的板块列表渲染（锡=矿山/精炼、锌=锌矿/锌锭冶炼、铝=铝土矿/氧化铝/电解铝、镍=印尼中间品/一级镍/镍铁NPI、铜=铜矿(kt)/国内铜企(万吨)），每板块季度 / 年度视图切换（铝默认年度视图，其余默认季度视图，品种级配置 `default_view`），ECharts 堆叠柱状图 + 合计同比双轴折线，表格悬停显示变化原因，含估算/推算的系列带 † 标记；
- **公司卡片**：按板块逐组渲染；最新季度产量、同比（红涨绿跌）、FY 指引进度条、变化原因、下次披露日、口径备注；最新数据为年度值的公司标注「年度披露」；
- **披露日历**：日期 + 公司 + 事件 + 状态（已披露待核 / 待披露，按构建日期自动判定）；
- **成本与资本开支**：锌资本开支总表（币种未折算，见口径说明）；锡 Alphamin AISC、Metals X C1/AISC 季度折线；铝暂无；
- **更新日志**：锌/铝读自 Excel「更新日志」sheet；锡日志为 `build_site.py` 中的 `TIN_CHANGELOG` 常量；
- **口径说明**：各品种页底部折叠区。

图表依赖 jsDelivr CDN 的 ECharts；CDN 不可用时图表区显示降级提示，数据表不受影响。

## 扩展新品种

1. 在 `build_site.py` 顶部的 `COMMODITIES` 注册表中新增一个条目：
   `{key, name, excel 路径, extract(抽取函数名), calendar(披露日历常量), caliber_notes(口径说明), default_view("quarter"/"year")}`；
2. 仿照 `extract_tin` / `extract_zinc` / `extract_aluminum` 编写抽取函数，返回统一结构：
   `sections`（板块列表，每板块含 `key`、`title`、`unit`、`quarters`、`years`、
   `companies[{name,country,project,data,yoy,guide,reason,note,est,est_note}]`、`total`，数量任意），
   以及 `costs` / `capex` / `changelog` / `overview` / `last_update`；
3. 运行 `build_site.py`，前端按 `sections` 列表自动渲染对应数量的板块（表格+图表+公司卡片），无需改动前端代码。

披露日历、锡更新日志等集中在 `build_site.py` 文件头的常量区，方便手工维护；云锡/华锡/兴业/明苏尔的季度序列（含明苏尔矿产锡 SR+B2、Pisco 精炼锡）统一从 Excel「季度补充」sheet 读取，是该数据的唯一来源。
