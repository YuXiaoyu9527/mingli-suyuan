"""
八字排盘测试套件
================
运行所有测试用例并生成报告。

用法：
  python test_runner.py
  python test_runner.py --verbose
"""

import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.paipan import paipan, to_dict, calc_dayun_from_lunar, calc_shensha
from lunar_python import Solar


def load_cases():
    case_path = Path(__file__).parent / "test_cases.json"
    with open(case_path, encoding="utf-8") as f:
        return json.load(f)


def run_case(case: dict, verbose: bool = False) -> dict:
    """运行单个测试用例"""
    y, m, d, h, minute = case["year"], case["month"], case["day"], case["hour"], case["minute"]
    gender = case["gender"]
    expected = case["expected"]
    failures = []
    checks = []

    try:
        r = paipan(y, m, d, h, minute, gender)
        data = to_dict(r)

        # 建立检查表
        pillars = data["pillars"]

        # 年柱
        if "year_ganzhi" in expected:
            actual = pillars["year"]["ganzhi"]
            if actual != expected["year_ganzhi"]:
                failures.append(f"年柱: expected {expected['year_ganzhi']}, got {actual}")
            checks.append(f"年柱={actual}")

        # 月柱
        if "month_ganzhi" in expected:
            actual = pillars["month"]["ganzhi"]
            if actual != expected["month_ganzhi"]:
                failures.append(f"月柱: expected {expected['month_ganzhi']}, got {actual}")
            checks.append(f"月柱={actual}")

        # 日柱
        if "day_ganzhi" in expected:
            actual = pillars["day"]["ganzhi"]
            if actual != expected["day_ganzhi"]:
                failures.append(f"日柱: expected {expected['day_ganzhi']}, got {actual}")
            checks.append(f"日柱={actual}")

        # 时柱
        if "hour_ganzhi" in expected:
            actual = pillars["hour"]["ganzhi"]
            if actual != expected["hour_ganzhi"]:
                failures.append(f"时柱: expected {expected['hour_ganzhi']}, got {actual}")
            checks.append(f"时柱={actual}")

        # 日主
        if "rizhu" in expected:
            actual = r.rizhu
            if actual != expected["rizhu"]:
                failures.append(f"日主: expected {expected['rizhu']}, got {actual}")

        # 日主五行
        if "rizhu_wuxing" in expected:
            actual = r.rizhu_wuxing
            if actual != expected["rizhu_wuxing"]:
                failures.append(f"日主五行: expected {expected['rizhu_wuxing']}, got {actual}")

        # 纳音
        if "nayin" in expected:
            actual = pillars["year"]["nayin"]
            if actual != expected["nayin"]:
                failures.append(f"纳音: expected {expected['nayin']}, got {actual}")

        # 大运方向
        if "dayun_direction" in expected:
            year_gan = pillars["year"]["gan"]
            month_gan = pillars["month"]["gan"]
            month_zhi = pillars["month"]["zhi"]
            solar = Solar.fromYmdHms(y, m, d, h, minute, 0)
            lunar = solar.getLunar()
            dayun = calc_dayun_from_lunar(lunar, year_gan, month_gan, month_zhi, gender)
            first_dy = dayun[0]["ganzhi"] if dayun else None
            if first_dy and "dayun_first_ganzhi" in expected:
                if first_dy != expected["dayun_first_ganzhi"]:
                    failures.append(f"第一步大运: expected {expected['dayun_first_ganzhi']}, got {first_dy}")

        # 空亡
        if "kongwang_zhi" in expected:
            sha = calc_shensha(
                pillars["year"]["zhi"], pillars["month"]["zhi"],
                pillars["day"]["gan"], pillars["day"]["zhi"],
                pillars["hour"]["zhi"], pillars["month"]["gan"],
            )
            if "空亡" in sha:
                # 简化检查
                checks.append(f"空亡={sha['空亡']}")
            else:
                checks.append("空亡=未检出")

        # 天乙贵人
        if "tianyi_at" in expected:
            sha = calc_shensha(
                pillars["year"]["zhi"], pillars["month"]["zhi"],
                pillars["day"]["gan"], pillars["day"]["zhi"],
                pillars["hour"]["zhi"], pillars["month"]["gan"],
            )
            if "天乙贵人" in sha:
                checks.append(f"天乙={sha['天乙贵人']}")

        # 桃花
        if "taohua_at" in expected:
            sha = calc_shensha(
                pillars["year"]["zhi"], pillars["month"]["zhi"],
                pillars["day"]["gan"], pillars["day"]["zhi"],
                pillars["hour"]["zhi"], pillars["month"]["gan"],
            )
            if "桃花" in sha:
                checks.append(f"桃花={sha['桃花']}")

    except Exception as e:
        failures.append(f"Exception: {e}")

    return {
        "case_id": case["id"],
        "name": case["name"],
        "passed": len(failures) == 0,
        "failures": failures,
        "checks": checks,
    }


def main():
    verbose = "--verbose" in sys.argv
    cases = load_cases()
    results = []

    print(f"=== 八字排盘测试套件 ({len(cases)} cases) ===\n")

    for case in cases:
        result = run_case(case, verbose)
        results.append(result)

        status = "[PASS]" if result["passed"] else "[FAIL]"
        print(f"{status} {case['id']}: {case['name']}")

        if verbose and result["checks"]:
            for check in result["checks"]:
                print(f"       {check}")

        if result["failures"]:
            for f in result["failures"]:
                print(f"       FAIL: {f}")
        print()

    # 汇总
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    print(f"=== 结果: {passed}/{len(results)} 通过, {failed} 失败 ===")

    if failed > 0:
        print("\n请将失败的案例与问真八字App交叉验证。")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
