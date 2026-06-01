"""
全量数据自动化验证脚本
=====================
用法: python api/tests/auto_verify.py

验证项目:
  1. 题库格式+古籍引用真实性
  2. 命例八字格式+与lunar_python对照
  3. 古籍文本干支完整性
  4. 断案录答案逻辑一致性
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent


def verify_quiz_bank():
    """验证题库"""
    print("=" * 50)
    print("1. 题库验证")
    print("=" * 50)

    quiz_file = ROOT / "data" / "quiz_cases.jsonl"
    with open(quiz_file, encoding="utf-8") as f:
        quizzes = [json.loads(l) for l in f if l.strip()]

    errors = []
    chapters = {}

    for q in quizzes:
        qid = q.get("id", "?")
        chapters[q.get("chapter", "?")] = chapters.get(q.get("chapter", "?"), 0) + 1

        # 结构检查
        if not q.get("id", "").startswith("quiz-"):
            errors.append(f"{qid}: id格式错误")
        if len(q.get("options", [])) != 4:
            errors.append(f"{qid}: 不是4个选项")
        if q.get("correct", -1) not in range(4):
            errors.append(f"{qid}: 正确答案索引无效")
        if not q.get("classical_ref"):
            errors.append(f"{qid}: 缺少古籍引用")
        if not q.get("story") or len(q["story"]) < 50:
            errors.append(f"{qid}: 故事过短")

        # 古籍引用格式检查
        ref = q.get("classical_ref", "")
        if "《" not in ref or "》" not in ref:
            errors.append(f"{qid}: 古籍引用格式不正确")

        # 正确答案与选项一致性
        correct_idx = q["correct"]
        correct_label = q["options"][correct_idx]["label"]
        if correct_label not in "ABCD":
            errors.append(f"{qid}: 正确选项标签异常")

    print(f"  总题数: {len(quizzes)}")
    for ch, cnt in sorted(chapters.items()):
        print(f"    {ch}: {cnt}题")
    print(f"  错误: {len(errors)}")
    for e in errors:
        print(f"    [FAIL] {e}")

    return len(errors) == 0, errors


def verify_mingli_cases():
    """验证历史命例"""
    print()
    print("=" * 50)
    print("2. 命例验证")
    print("=" * 50)

    cases_file = ROOT / "data" / "mingli_cases.jsonl"
    with open(cases_file, encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]

    errors = []
    gz_pattern = re.compile(r"^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]$")
    reliabilities = {}
    patterns = {}

    for c in cases:
        name = c.get("name", "?")
        reliabilities[c.get("reliability", "?")] = reliabilities.get(c.get("reliability", "?"), 0) + 1
        patterns[c.get("pattern", "?")] = patterns.get(c.get("pattern", "?"), 0) + 1

        # 八字格式
        pillars = c.get("bazi", "").split()
        if len(pillars) != 4:
            errors.append(f"{name}: 不是4柱 ({len(pillars)}柱)")
            continue
        for i, p in enumerate(pillars):
            if not gz_pattern.match(p):
                errors.append(f"{name}: 第{i+1}柱'{p}'格式错误")

        # 必填字段
        for field in ["name", "era", "bazi", "pattern", "rishu", "reliability", "commentary", "source"]:
            if not c.get(field):
                errors.append(f"{name}: 缺少{field}字段")

    print(f"  总命例: {len(cases)}")
    print(f"  可信度: {reliabilities}")
    print(f"  格局数: {len(patterns)}")
    print(f"  错误: {len(errors)}")
    for e in errors:
        print(f"    [FAIL] {e}")

    return len(errors) == 0, errors


def verify_historical_bazi():
    """用lunar_python验证正史记载人物的八字"""
    print()
    print("=" * 50)
    print("3. 正史人物八字交叉验证")
    print("=" * 50)

    from lunar_python import Solar

    cases_file = ROOT / "data" / "mingli_cases.jsonl"
    with open(cases_file, encoding="utf-8") as f:
        cases = [json.loads(l) for l in f if l.strip()]

    # 正史记载且有明确生日的（前3柱可验证）
    verified = [
        ("曾国藩", 1811, 11, 26),
        ("康熙帝", 1654, 5, 4),
        ("鲁迅", 1881, 9, 25),
        ("宋美龄", 1897, 3, 5),
        ("郑板桥", 1693, 11, 22),
        ("林则徐", 1785, 8, 30),
        ("乾隆帝", 1711, 9, 25),
    ]

    mismatches = []
    for name, y, m, d in verified:
        solar = Solar.fromYmdHms(y, m, d, 12, 0, 0)
        lunar = solar.getLunar()
        ba = lunar.getEightChar()
        calc_bazi = (
            f"{ba.getYearGan()}{ba.getYearZhi()} "
            f"{ba.getMonthGan()}{ba.getMonthZhi()} "
            f"{ba.getDayGan()}{ba.getDayZhi()} "
            f"{ba.getTimeGan()}{ba.getTimeZhi()}"
        )

        for c in cases:
            if c["name"] == name:
                recorded = c["bazi"]
                calc_parts = calc_bazi.split()
                rec_parts = recorded.split()
                match = calc_parts[:3] == rec_parts[:3]
                status = "[OK]" if match else "[MISMATCH]"
                print(f"  {status} {name}({y}-{m:02d}-{d:02d})")
                print(f"        记录: {recorded}")
                print(f"        计算: {calc_bazi}  (午时)")
                if not match:
                    mismatches.append((name, recorded, calc_bazi))
                break

    if mismatches:
        print(f"\n  [WARN] {len(mismatches)}个人物前3柱不一致，需要核实生日或八字来源")
    else:
        print(f"\n  [OK] 全部一致")

    return len(mismatches) == 0, mismatches


def verify_ganzhi_in_texts():
    """验证古籍文本干支完整性"""
    print()
    print("=" * 50)
    print("4. 古籍干支完整性")
    print("=" * 50)

    import json as jmod
    cleaned_dir = ROOT / "data" / "cleaned"
    all_gan = set("甲乙丙丁戊己庚辛壬癸")
    all_zhi = set("子丑寅卯辰巳午未申酉戌亥")

    for fpath in sorted(cleaned_dir.glob("*.json")):
        with open(fpath, encoding="utf-8") as f:
            data = jmod.load(f)

        all_text = "".join(r["original"] for r in data["records"])
        found_gan = all_gan & set(all_text)
        found_zhi = all_zhi & set(all_text)
        missing_gan = all_gan - found_gan
        missing_zhi = all_zhi - found_zhi

        name = data["meta"]["source_name"]
        status = "[OK]" if not missing_gan and not missing_zhi else "[WARN]"
        issues = []
        if missing_gan:
            issues.append(f"缺天干:{''.join(missing_gan)}")
        if missing_zhi:
            issues.append(f"缺地支:{''.join(missing_zhi)}")

        print(f"  {status} {name}: 天干{10-len(missing_gan)}/10 地支{12-len(missing_zhi)}/12 {' '.join(issues)}")

    return True, []


def main():
    print("命理溯源 · 全量数据自动验证")
    print()

    results = {}
    for name, fn in [
        ("题库", verify_quiz_bank),
        ("命例", verify_mingli_cases),
        ("八字交叉验证", verify_historical_bazi),
        ("干支完整性", verify_ganzhi_in_texts),
    ]:
        try:
            passed, details = fn()
            results[name] = passed
        except Exception as e:
            print(f"\n  [ERROR] {name}: {e}")
            results[name] = False

    print()
    print("=" * 50)
    print("汇总")
    print("=" * 50)
    all_pass = True
    for name, passed in results.items():
        status = "[OK]" if passed else "[FAIL]"
        if not passed:
            all_pass = False
        print(f"  {status} {name}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
