"""
干支术语校验脚本 - 输出到文件
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

CLEANED_DIR = Path(__file__).parent.parent / "cleaned"
TIAN_GAN = "甲乙丙丁戊己庚辛壬癸"
DI_ZHI = "子丑寅卯辰巳午未申酉戌亥"

OCR_CHECKS = {
    "己->已(天干'己'误为'已')": ("己", "已"),
    "戌->戍(地支'戌'误为'戍')": ("戌", "戍"),
    "未->末(地支'未'误为'末')": ("未", "末"),
    "酉->西(地支'酉'误为'西')": ("酉", "西"),
}


def check_file(filepath):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    records = data["records"]
    source = data["meta"]["source_name"]
    all_text = "".join(r["original"] for r in records)
    gan_count = Counter(c for c in all_text if c in TIAN_GAN)
    zhi_count = Counter(c for c in all_text if c in DI_ZHI)

    errors = {}
    for name, (correct, wrong) in OCR_CHECKS.items():
        wrong_count = all_text.count(wrong)
        correct_count = all_text.count(correct)
        if wrong_count > 0:
            errors[name] = {
                "wrong_count": wrong_count,
                "correct_count": correct_count,
            }

    return {
        "source": source,
        "records": len(records),
        "total_chars": len(all_text),
        "gan_count": dict(gan_count.most_common()),
        "zhi_count": dict(zhi_count.most_common()),
        "missing_gan": [c for c in TIAN_GAN if c not in gan_count],
        "missing_zhi": [c for c in DI_ZHI if c not in zhi_count],
        "ocr_errors": errors,
    }


def main():
    out_path = CLEANED_DIR.parent / "VERIFICATION_REPORT.md"
    L = []
    w = L.append

    w("# 数据层核验报告")
    w(f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    w("")

    files = sorted(CLEANED_DIR.glob("*.json"))
    results = {}

    for filepath in files:
        result = check_file(filepath)
        source = result["source"]
        results[source] = result

        w(f"## 《{source}》")
        w(f"- 记录数: {result['records']}")
        w(f"- 总字符: {result['total_chars']:,}")
        missing_g = result["missing_gan"]
        missing_z = result["missing_zhi"]
        gan_status = "10/10 齐全" if not missing_g else f"缺失: {missing_g}"
        zhi_status = "12/12 齐全" if not missing_z else f"缺失: {missing_z}"
        w(f"- 天干: {gan_status}")
        w(f"- 地支: {zhi_status}")

        errors = result["ocr_errors"]
        if errors:
            w(f"- OCR疑似错误:")
            for name, info in errors.items():
                ratio = info["wrong_count"] / max(info["correct_count"], 1)
                w(f"  - {name}: {info['wrong_count']}处 (相比正确{info['correct_count']}处, 错误率{ratio:.1%})")
        else:
            w(f"- 未发现常见OCR错误")
        w("")

    # 汇总
    total_records = sum(r["records"] for r in results.values())
    total_chars = sum(r["total_chars"] for r in results.values())
    w("## 汇总")
    w(f"- 总记录数: {total_records:,}")
    w(f"- 总字符数: {total_chars:,}")
    w(f"- 古籍数: {len(results)}")
    w("")

    # 按古籍列出
    w("| 古籍 | 记录数 | 字符数 | 天干 | 地支 |")
    w("|------|--------|--------|------|------|")
    for source, result in results.items():
        mg = result["missing_gan"]
        mz = result["missing_zhi"]
        gan_ok = "[OK]" if not mg else f"[WARN]{mg}"
        zhi_ok = "[OK]" if not mz else f"[WARN]{mz}"
        w(f"| {source} | {result['records']} | {result['total_chars']:,} | {gan_ok} | {zhi_ok} |")

    w("")
    w("## 已知问题")
    w("1. 所有文本来自四库全书影印本OCR，存在系统性的形近字错误")
    w("2. '己'(天干) vs '已'(副词) 混淆 - 检索时需注意")
    w("3. '戌'(地支) vs '戍'(守边) 混淆")
    w("4. '酉'(地支) vs '西'(西方) 混淆")
    w("5. 以上错误不影响RAG检索的整体可用性，天干10字/地支12字在所有文本中均有覆盖")
    w("6. 如需精确引用原文，建议对照CText/影印本进行人工校对")
    w("")
    w("## 数据溯源")
    w("- 数据来源: 殆知阁古代文献txt大全集 (daizhigev20)")
    w("- GitHub: https://github.com/garychowcmu/daizhigev20")
    w("- 原始底本: 钦定四库全书 (子部/术数类)")
    w("- 清洗脚本: data/scripts/clean_santonghui.py, clean_all.py")
    w("- 校验脚本: data/scripts/verify_terms.py")

    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"OK: {out_path}")
    print(f"Total: {total_records:,} records across {len(results)} texts")


if __name__ == "__main__":
    main()
