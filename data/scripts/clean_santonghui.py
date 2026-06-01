"""
清洗《三命通会》文本并结构化为JSON

输入：data/raw/santonghui/santonghui_raw.txt
输出：data/cleaned/santonghui.json

处理步骤：
1. 去除元数据头
2. 按卷分割
3. 按节（section）分割
4. 标注Tag（五行/十神/格局/神煞/干支/基础）
5. 校验干支字符
6. 输出结构化JSON

用法：
  python clean_santonghui.py
  python clean_santonghui.py --validate-only  # 只校验不输出
"""

import re
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path

# ===== 配置 =====

INPUT_FILE = Path(__file__).parent.parent / "raw" / "santonghui" / "santonghui_raw.txt"
OUTPUT_FILE = Path(__file__).parent.parent / "cleaned" / "santonghui.json"
SOURCE_NAME = "三命通會"
SOURCE_ABBR = "smtm"
AUTHOR = "萬民英"
DYNASTY = "明"
SOURCE_URL = "https://github.com/garychowcmu/daizhigev20/tree/master/易藏/术数/三命通会.txt"

# ===== 干支白名单 =====
TIAN_GAN = set("甲乙丙丁戊己庚辛壬癸")
DI_ZHI = set("子丑寅卯辰巳午未申酉戌亥")
ALL_GZ = TIAN_GAN | DI_ZHI

# ===== 常见OCR错误映射 =====
OCR_FIXES = {
    # 这些是在命理文本中致命的OCR错误
    "己": None,  # 不做自动替换，但标记为需检查
    "已": None,
    "戌": None,
    "戍": None,
    "戊": None,
}

# ===== 章节标签规则 =====
# 根据章节标题自动分配Tag
SECTION_TAG_RULES = [
    # (正则, Tag列表)
    (r"造化|五行生成|五行生尅|支干源流|十干名字|十二支名字|纳音", ["五行", "基礎理論"]),
    (r"天干|地支|十干|十二支|人元|四时|节气|日刻|时刻|遁月|年月日时", ["干支", "基礎理論"]),
    (r"胎元|命宫|大运|小运|太[嵗歲]|嵗运|进交退伏", ["大運", "基礎理論"]),
    (r"十干合|化气|支元|三合|将星|华[蓋葢]|六害|三刑|冲击|禄马", ["干支", "神煞"]),
    (r"贵人|三奇|天月[徳德]|太极|学堂|词馆|正印|[徳德]秀", ["神煞"]),
    (r"刼煞|亡神|羊刃|元辰|六厄|勾绞|孤辰|寡宿|天罗地网|十恶大败", ["神煞"]),
    (r"坐支|十二月支|时地分野", ["干支", "格局"]),
    (r"^论甲乙|^论丙丁|^论戊[巳己]|^论庚辛|^论壬癸", ["日主", "格局"]),
    (r"正官|偏官|正财|偏财|印绶|食神|伤官|阳刃|建禄|倒食|杂气|官财", ["十神", "格局"]),
    (r"性情|疾病|贫贱|夀夭|女命|小儿|六亲", ["命理", "應驗"]),
    (r"井栏|壬骑龙背|六乙鼠贵|子遥巳|丑遥巳|曲直|炎上|从革|润下|稼穑|飞天禄马", ["格局"]),
    (r"消息赋|明通赋|玉井|金声玉振|宝法|气象|形全|神峰", ["格局", "賦文"]),
]


def load_text() -> str:
    """加载原始文本"""
    text = INPUT_FILE.read_text(encoding="utf-8")
    # 去掉元数据头（以#开头的行）
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("#") and line.strip():
            body_start = i
            break
    return "\n".join(lines[body_start:])


def split_volumes(text: str) -> list[dict]:
    """按卷分割"""
    # 卷名模式（含OCR常见错误：会/會 → 防）
    vol_pattern = re.compile(r"三命通[会會防]卷([一二三四五六七八九十]+)")

    volumes = []
    lines = text.split("\n")
    current_vol = None
    current_start = 0

    for i, line in enumerate(lines):
        m = vol_pattern.search(line)
        if m:
            stripped = line.strip()
            # 只接受独立的卷标题行（短行，以书名开头）
            # 跳过嵌入在长文本中的引用（如 "三命通会,卷四" 在正文中间）
            is_title = (
                len(stripped) < 40 and
                (stripped.startswith("三命通会") or stripped.startswith("三命通防"))
            )
            if not is_title:
                continue

            # 保存上一卷
            if current_vol is not None:
                vol_text = "\n".join(lines[current_start:i])
                if len(vol_text.strip()) > 50:
                    volumes.append(current_vol)

            # 开始新卷（防→会的OCR修正）
            vol_num_str = m.group(1)
            current_vol = {
                "volume": f"卷{vol_num_str}",
                "start_line": i,
                "raw_text": "",
            }
            current_start = i

    # 保存最后一卷
    if current_vol is not None:
        vol_text = "\n".join(lines[current_start:])
        if len(vol_text.strip()) > 50:
            volumes.append(current_vol)

    # 填充每卷的文本
    for i, vol in enumerate(volumes):
        start = vol["start_line"]
        end = volumes[i + 1]["start_line"] if i + 1 < len(volumes) else len(lines)
        vol["raw_text"] = "\n".join(lines[start:end])

    return volumes


def split_sections(vol_text: str) -> list[dict]:
    """按节分割一卷内的文本。

    支持两种标题模式：
    1. 前缀型：论XXX / 原XXX / 释XXX / 总论XXX / XXX赋 / XXX篇 / XXX诀
    2. 独立短行型：格局名等（如"井栏斜义""壬骑龙背"），
       特征为3-20字符、无标点、位于段落之间的短行
    """
    lines = vol_text.split("\n")

    # 识别候选节标题
    candidates = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) < 2:
            continue

        # 跳过明显不是标题的行
        if re.match(r"^[<【\(]", stripped):
            continue
        if re.match(r"^[明钦御总].*$", stripped) and len(stripped) > 10:
            continue  # 钦定四库全书等元数据行

        is_header = False

        # 模式1: 前缀型标题
        if re.match(r"^[原论释总裁说辨辩赋篇诀歌解问答]+.{2,}", stripped):
            is_header = True

        # 模式2: 独立的格局名/短标题（3-20字符，无句读标点）
        elif (
            3 <= len(stripped) <= 25
            and not re.search(r"[。，、；：（）\(\)「」『』]", stripped)
            and not re.search(r"[年月日时]$", stripped)
        ):
            is_header = True

        if is_header:
            candidates.append((i, stripped))

    # 去重和合并（跳过连续标题中的子标题）
    sections = []
    used = set()
    for idx, (line_no, title) in enumerate(candidates):
        if line_no in used:
            continue
        used.add(line_no)

        start = line_no
        # 找到下一节的起始行
        end = len(lines)
        for next_no, _ in candidates[idx + 1:]:
            if next_no > line_no:
                end = next_no
                break

        section_text = "\n".join(lines[start:end]).strip()
        if len(section_text) > 10:  # 至少有点内容
            sections.append({
                "section": title,
                "raw_text": section_text,
            })

    return sections


def assign_tags(section_title: str) -> list[str]:
    """根据节标题分配标签"""
    tags = set()
    for pattern, tag_list in SECTION_TAG_RULES:
        if re.search(pattern, section_title):
            tags.update(tag_list)
    if not tags:
        tags.add("其他")
    return sorted(tags)


def clean_text(raw: str) -> str:
    """清洗文本"""
    text = raw

    # 移除卷标题行（第一行通常是"三命通会卷X"）
    text = re.sub(r"^.*三命通[会會]卷[一二三四五六七八九十]+.*$", "", text, flags=re.MULTILINE)
    # 移除四库全书标记行
    text = re.sub(r"^.*钦定四库全书.*$", "", text, flags=re.MULTILINE)
    # 移除作者行
    text = re.sub(r"^.*[明明清].*[撰著].*$", "", text, flags=re.MULTILINE)

    # 规范化空白
    text = re.sub(r"[　 ]+", "", text)  # 移除全角/半角空格
    text = re.sub(r"\n{3,}", "\n\n", text)  # 多个空行合并
    text = text.strip()

    return text


def validate_ganzhi(text: str) -> dict:
    """校验干支字符"""
    # 统计干支字符
    chars = list(text)
    gz_chars = [c for c in chars if c in ALL_GZ]

    # 检查常见错误
    warnings = []
    # 己/已混淆
    if "已" in text and any(c in text for c in "己"):
        warnings.append("包含'已'字符，可能为'己'的OCR错误")
    # 戌/戍混淆
    if "戍" in text:
        warnings.append("包含'戍'字符，可能为'戌'的OCR错误")

    return {
        "ganzhi_count": len(gz_chars),
        "unique_ganzhi": sorted(set(gz_chars)),
        "warnings": warnings,
    }


def process_all() -> list[dict]:
    """主处理流程"""
    print("=== 清洗《三命通会》 ===\n")

    # 1. 加载
    print("1. 加载原始文本...")
    text = load_text()
    print(f"   文本长度: {len(text):,} 字符")

    # 2. 按卷分割
    print("2. 按卷分割...")
    volumes = split_volumes(text)
    print(f"   找到 {len(volumes)} 卷")

    # 3. 逐卷处理
    all_records = []
    for vol in volumes:
        vol_name = vol["volume"]
        print(f"\n   处理 {vol_name}...")

        # 每卷内的节
        sections = split_sections(vol["raw_text"])
        print(f"   {len(sections)} 个节")

        for sec in sections:
            section_title = sec["section"]
            clean = clean_text(sec["raw_text"])
            tags = assign_tags(section_title)
            gz_check = validate_ganzhi(clean)

            record = {
                "id": f"{SOURCE_ABBR}-{vol_name.replace('卷', '')}-{len(all_records):04d}",
                "source_name": SOURCE_NAME,
                "source_abbr": SOURCE_ABBR,
                "author": AUTHOR,
                "dynasty": DYNASTY,
                "volume": vol_name,
                "section": section_title,
                "original": clean,
                "tags": tags,
                "ganzhi_stats": gz_check,
                "source_url": SOURCE_URL,
                "processed_date": datetime.now().strftime("%Y-%m-%d"),
                "raw_char_count": len(clean),
                "raw_sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest(),
            }

            all_records.append(record)

    return all_records


def generate_report(records: list[dict]) -> str:
    """生成处理报告"""
    total_chars = sum(r["raw_char_count"] for r in records)
    total_gz = sum(r["ganzhi_stats"]["ganzhi_count"] for r in records)
    tag_counts = {}
    vol_counts = {}

    for r in records:
        vol = r["volume"]
        vol_counts[vol] = vol_counts.get(vol, 0) + 1
        for tag in r["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    # 收集警告
    warnings = []
    for r in records:
        for w in r["ganzhi_stats"]["warnings"]:
            warnings.append(f"{r['id']}: {w}")

    report = f"""# 《三命通会》数据清洗报告
生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}
数据来源: {SOURCE_URL}

## 整体统计
- 总记录数: {len(records)}
- 总字符数: {total_chars:,}
- 干支字符数: {total_gz:,}
- 卷数: {len(vol_counts)}

## 各卷记录数
"""
    for vol in sorted(vol_counts.keys()):
        report += f"- {vol}: {vol_counts[vol]} 节\n"

    report += f"\n## 标签分布\n"
    for tag in sorted(tag_counts.keys(), key=lambda t: tag_counts[t], reverse=True):
        report += f"- {tag}: {tag_counts[tag]} 节\n"

    report += f"\n## 干支校验\n"
    if warnings:
        report += f"共 {len(warnings)} 条警告:\n"
        for w in warnings[:20]:
            report += f"- {w}\n"
        if len(warnings) > 20:
            report += f"- ... 还有 {len(warnings) - 20} 条\n"
    else:
        report += "无警告。\n"

    return report


def main():
    validate_only = "--validate-only" in sys.argv

    if not INPUT_FILE.exists():
        print(f"错误: 找不到输入文件 {INPUT_FILE}")
        sys.exit(1)

    # 处理
    records = process_all()

    # 生成报告
    report = generate_report(records)
    report_path = Path(__file__).parent.parent / "VERIFICATION_REPORT.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n核验报告: {report_path}")

    if not validate_only:
        # 输出JSON
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        output = {
            "meta": {
                "source_name": SOURCE_NAME,
                "author": AUTHOR,
                "dynasty": DYNASTY,
                "source_url": SOURCE_URL,
                "processed_date": datetime.now().strftime("%Y-%m-%d"),
                "total_records": len(records),
            },
            "records": records,
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"结构化数据: {OUTPUT_FILE}")
        print(f"共 {len(records)} 条记录")

    print("\n完成。")


if __name__ == "__main__":
    main()
