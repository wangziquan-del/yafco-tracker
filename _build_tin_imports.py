# -*- coding: utf-8 -*-
"""生成锡需求面板数据 data/tin_imports.json（美/韩/日/印精炼锡进口月度序列）。

来源与交叉验证（2026-08-04）：
- 美国/日本/韩国：Mysteel锡线下数据.xlsx（各国海关口径，最新至 2026-04/06）；
  与 zhiji SMM 序列在 2024-11~2025-07 逐月一致，2025-08 起 SMM 停更前数值分化，
  采用 Mysteel Excel 海关口径为准。
- 印度：zhiji mysteel 指标 ID02323384（印度海关，未锻轧非合金锡进口合计，千克折吨），
  与 SMM 在 2024-11~2025-05 一致、之后分化，采用印度海关口径；
  该序列 2025-07/08/11/12 及 2026 年除 3 月外缺数（原始源如此）。
用法：python _build_tin_imports.py  （build_site.py 会读取产出的 tin_imports.json 注入锡页）
"""
import json
import datetime
from pathlib import Path

import openpyxl

BASE = Path(__file__).parent
EXCEL = Path(r"D:\拷贝文件\E\永安\周报数据更新\Mysteel锡线下数据.xlsx")
ZHIJI = BASE / "data" / "_tin_import_zhiji.json"
OUT = BASE / "data" / "tin_imports.json"


def dump(ws, date_col, val_col, header_rows, scale=1.0):
    out = {}
    for r in ws.iter_rows(min_row=header_rows + 1, values_only=True):
        d, v = r[date_col], r[val_col]
        if d is None or v is None:
            continue
        if isinstance(d, str):
            try:
                d = datetime.datetime.fromisoformat(d[:19].replace(" 0", "T0"))
            except ValueError:
                continue
        if not isinstance(d, datetime.datetime):
            continue
        try:
            out[d.strftime("%Y-%m")] = round(float(v) * scale, 1)
        except (TypeError, ValueError):
            continue
    return out


def main():
    wb = openpyxl.load_workbook(EXCEL, read_only=True)
    us = dump(wb["美国精锡进口"], 0, 1, 1)                      # 吨
    kr = dump(wb["韩国精锡及锡制品进出口"], 0, 1, 5)            # 吨（未锻轧精炼锡进口合计）
    jp = dump(wb["日本精炼锡进口数量"], 0, 1, 5, scale=0.001)   # 千克→吨（未锻轧非合金锡，税则80011000）
    zh = json.loads(ZHIJI.read_text(encoding="utf-8"))
    india = {k: v for k, v in zh["IN"].items()}

    countries = [
        {"key": "US", "name": "美国", "monthly": us,
         "source": "Mysteel 线下数据（美国海关精锡进口）",
         "xval": "与 zhiji SMM 序列 2024-11~2025-07 逐月一致；2025-08 起 SMM 停更前数值低于海关口径，以 Mysteel 海关数据为准"},
        {"key": "KR", "name": "韩国", "monthly": kr,
         "source": "Mysteel 线下数据（韩国海关未锻轧精炼锡进口合计）",
         "xval": "zhiji SMM 韩国指标无数据返回，未能交叉验证；单源采用"},
        {"key": "JP", "name": "日本", "monthly": jp,
         "source": "Mysteel 线下数据（日本海关未锻轧非合金锡，税则 80011000，千克折吨）",
         "xval": "与 zhiji SMM 序列 2024-11~2025-07 逐月一致；2025-08 起分化，以 Mysteel 海关数据为准"},
        {"key": "IN", "name": "印度", "monthly": india,
         "source": "zhiji/Mysteel（印度海关未锻轧非合金锡进口合计，千克折吨，指标 ID02323384）",
         "xval": "与 SMM 2024-11~2025-05 一致、之后分化，以印度海关口径为准；2025-07/08/11/12 及 2026 年部分月份原始源缺数"},
    ]
    for c in countries:
        ks = sorted(c["monthly"])
        c["latest"] = ks[-1] if ks else None
        print(f"  {c['name']}: {len(ks)} 个月, {ks[0]} ~ {ks[-1]}")

    payload = {
        "updated": datetime.date.today().isoformat(),
        "unit": "吨/月",
        "title": "海外精炼锡进口季节性",
        "note": "美/韩/日为 Mysteel 线下数据（各国海关口径），印度为 zhiji/Mysteel 印度海关口径；均与 zhiji SMM 序列做过重叠期交叉验证（见各国备注）。印度 2025 年下半年起缺数较多，谨慎解读。",
        "countries": countries,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(f"写出 {OUT}")


if __name__ == "__main__":
    main()
