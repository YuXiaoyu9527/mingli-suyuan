"""
通用古籍文本清洗脚本
处理滴天髓阐微、渊海子平、协纪辨方书

用法：
  python clean_all.py
  python clean_all.py --text ditianshui
"""

import re
import json
import hashlib
import sys
from datetime import datetime
from pathlib import Path

# ===== 配置 =====

RAW_DIR = Path(__file__).parent.parent / "raw"
CLEANED_DIR = Path(__file__).parent.parent / "cleaned"

TEXT_CONFIGS = {
    "ditianshui": {
        "source_name": "滴天髓闡微",
        "source_abbr": "dts",
        "author": "任鐵樵",
        "dynasty": "清",
        "input_file": RAW_DIR / "ditianshui" / "ditianshui_raw.txt",
        "output_file": CLEANED_DIR / "ditianshui.json",
        "source_url": "https://github.com/garychowcmu/daizhigev20/tree/master/易藏/术数/滴天髓阐微.txt",
        "section_tag_rules": [
            (r"天道|地道|人道|知命|理气|配合", ["基礎理論", "通神論"]),
            (r"天干|地支|干支|形象|方局|八格|体用|精神", ["干支", "格局"]),
            (r"月令|生时|衰旺|中和|源流|通关|官杀|伤官", ["格局", "旺衰"]),
            (r"清气|浊气|真神|假神|刚柔|顺逆|寒暖|燥湿", ["用神", "調候"]),
            (r"隐显|众寡|震兑|坎离", ["通神論"]),
            (r"夫妻|子女|父母|兄弟|女命|小儿", ["六親"]),
            (r"何知章|才德|奋郁|恩怨|闲神", ["六親論"]),
            (r"从象|化象|假从|假化|顺局|反局", ["格局", "六親論"]),
            (r"战局|合局|君象|臣象|母象|子象", ["格局"]),
            (r"性情|疾病|出身|地位|岁运|贞元", ["命理", "六親論"]),
        ],
    },
    "yuanhaiziping": {
        "source_name": "淵海子平",
        "source_abbr": "yhp",
        "author": "徐大升",
        "dynasty": "宋",
        "input_file": RAW_DIR / "yuanhaiziping" / "yuanhaiziping_raw.txt",
        "output_file": CLEANED_DIR / "yuanhaiziping.json",
        "source_url": "https://github.com/garychowcmu/daizhigev20/tree/master/易藏/术数/渊海子平.txt",
        "section_tag_rules": [
            (r"基础|五干|天干|地支|阴阳|五行", ["基礎理論", "干支"]),
            (r"十神|比肩|劫财|食神|伤官|正财|偏财|正官|偏官|正印|偏印", ["十神"]),
            (r"继善篇|看命|神趣|杂论|群兴|兴亡", ["賦文", "格局"]),
            (r"宝法|寸金|搜髓|论命|造化", ["格局", "基礎理論"]),
            (r"六亲|父母|兄弟|妻财|子女|女命", ["六親"]),
        ],
    },
    "xiejibianfangshu": {
        "source_name": "欽定協紀辨方書",
        "source_abbr": "xjbf",
        "author": "允祿 等奉敕編",
        "dynasty": "清",
        "input_file": RAW_DIR / "xiejibianfangshu" / "xiejibianfangshu_raw.txt",
        "output_file": CLEANED_DIR / "xiejibianfangshu.json",
        "source_url": "https://github.com/garychowcmu/daizhigev20/tree/master/易藏/术数/钦定协纪辨方书.txt",
        "section_tag_rules": [
            (r"建除|满平|定执|破危|成收|开闭", ["建除十二神"]),
            (r"黄道|黑道|天德|月德|天赦|母仓|月恩", ["黃道黑道", "神煞"]),
            (r"嫁娶|婚姻|周堂|合婚", ["嫁娶"]),
            (r"出行|动土|开业|开市|搬家|入宅|安葬|修造", ["用事宜忌"]),
            (r"神煞|吉神|凶煞|宜忌", ["神煞", "宜忌"]),
            (r"本原|河图|洛书|八卦|干支|五行", ["基礎理論"]),
            (r"义例|立成|用事|公规", ["擇吉規則"]),
            (r"年表|月表|日表", ["擇吉曆表"]),
        ],
    },
}

# ===== 干支白名单 =====
TIAN_GAN = set("甲乙丙丁戊己庚辛壬癸")
DI_ZHI = set("子丑寅卯辰巳午未申酉戌亥")
ALL_GZ = TIAN_GAN | DI_ZHI


def load_text(filepath: Path) -> str:
    """加载原始文本，跳过元数据头"""
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("#") and line.strip():
            body_start = i
            break
    return "\n".join(lines[body_start:])


def clean_text(raw: str) -> str:
    """清洗文本"""
    text = raw
    # 移除元数据行
    text = re.sub(r"^.*钦定四库全书.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^.*[明明清].*[撰著编].*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^<子部.*$", "", text, flags=re.MULTILINE)
    # 规范化空白
    text = re.sub(r"[　 ]+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return text


def split_sections(text: str) -> list[dict]:
    """分割为节"""
    lines = text.split("\n")
    candidates = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) < 2:
            continue
        if re.match(r"^[<【\(钦御总校]", stripped):
            continue

        is_header = False
        # 前缀型标题
        if re.match(r"^[原论释总裁说辨辩赋篇诀歌解问答通六何].{2,}", stripped):
            is_header = True
        # 独立短行
        elif (
            3 <= len(stripped) <= 30
            and not re.search(r"[。，、；：（）\(\)「」『』]", stripped)
            and not re.search(r"[年月日时]$\s*$", stripped)
        ):
            is_header = True

        if is_header:
            candidates.append((i, stripped))

    sections = []
    used = set()
    for idx, (line_no, title) in enumerate(candidates):
        if line_no in used:
            continue
        used.add(line_no)

        end = len(lines)
        for next_no, _ in candidates[idx + 1:]:
            if next_no > line_no:
                end = next_no
                break

        section_text = "\n".join(lines[line_no:end]).strip()
        if len(section_text) > 10:
            sections.append({"section": title, "raw_text": section_text})

    return sections


def assign_tags(section_title: str, rules: list) -> list[str]:
    """根据规则分配标签"""
    tags = set()
    for pattern, tag_list in rules:
        if re.search(pattern, section_title):
            tags.update(tag_list)
    if not tags:
        tags.add("其他")
    return sorted(tags)


def validate_ganzhi(text: str) -> dict:
    """校验干支"""
    chars = list(text)
    gz_chars = [c for c in chars if c in ALL_GZ]
    warnings = []
    if "已" in text and any(c in "己" for c in text):
        warnings.append("包含'已'字符，可能为'己'的OCR错误")
    if "戍" in text:
        warnings.append("包含'戍'字符，可能为'戌'的OCR错误")
    return {
        "ganzhi_count": len(gz_chars),
        "unique_ganzhi": sorted(set(gz_chars)),
        "warnings": warnings,
    }


def process_text(key: str) -> list[dict]:
    """处理单个文本"""
    config = TEXT_CONFIGS[key]
    print(f"\n=== 处理《{config['source_name']}》 ===")

    # 加载
    print("1. 加载文本...")
    text = load_text(config["input_file"])
    print(f"   长度: {len(text):,} 字符")

    # 清洗
    print("2. 清洗...")
    text = clean_text(text)

    # 分割
    print("3. 分割章节...")
    sections = split_sections(text)
    print(f"   找到 {len(sections)} 个节")

    # 结构化
    print("4. 生成结构化记录...")
    records = []
    for sec in sections:
        clean = clean_text(sec["raw_text"])
        tags = assign_tags(sec["section"], config["section_tag_rules"])
        gz_check = validate_ganzhi(clean)

        record = {
            "id": f"{config['source_abbr']}-{len(records):04d}",
            "source_name": config["source_name"],
            "source_abbr": config["source_abbr"],
            "author": config["author"],
            "dynasty": config["dynasty"],
            "section": sec["section"],
            "original": clean,
            "tags": tags,
            "ganzhi_stats": gz_check,
            "source_url": config["source_url"],
            "processed_date": datetime.now().strftime("%Y-%m-%d"),
            "raw_char_count": len(clean),
            "raw_sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest(),
        }
        records.append(record)

    # 输出
    print("5. 保存...")
    output = {
        "meta": {
            "source_name": config["source_name"],
            "author": config["author"],
            "dynasty": config["dynasty"],
            "source_url": config["source_url"],
            "processed_date": datetime.now().strftime("%Y-%m-%d"),
            "total_records": len(records),
        },
        "records": records,
    }
    config["output_file"].parent.mkdir(parents=True, exist_ok=True)
    with open(config["output_file"], "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"   → {config['output_file']} ({len(records)} 条记录)")

    return records


def main():
    # 确定处理哪些文本
    if "--text" in sys.argv:
        idx = sys.argv.index("--text")
        keys = [sys.argv[idx + 1]]
    else:
        keys = list(TEXT_CONFIGS.keys())

    all_stats = {}
    for key in keys:
        if key not in TEXT_CONFIGS:
            print(f"未知文本: {key}")
            continue
        try:
            records = process_text(key)
            all_stats[key] = len(records)
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n=== 处理完成 ===")
    for k, v in all_stats.items():
        print(f"  {TEXT_CONFIGS[k]['source_name']}: {v} 条记录")


if __name__ == "__main__":
    main()
