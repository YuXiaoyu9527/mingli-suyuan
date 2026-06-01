"""
获取《三命通会》文本从 CText.org
来源：https://ctext.org/wiki.pl?if=gb&res=758991

用法：
  python fetch_santonghui.py            # 获取全部12卷
  python fetch_santonghui.py --vol 1-5  # 只获取卷1-5

输出：
  data/raw/santonghui/vol_01.txt
  data/raw/santonghui/vol_01.html
  ...
"""

import requests
import time
import sys
import os
import hashlib
import re
from datetime import datetime
from pathlib import Path

# CText 章节ID映射（从wiki页面获取）
# 格式：卷X → chapter_id
CHAPTER_MAP = {
    1: "212352",
    2: "974603",
    3: "626505",
    4: "493343",
    5: "535907",
    6: "537147",
    7: "297439",
    8: "100067",
    9: "547989",
    10: "965856",
    11: "812377",
    12: "960747",
}

BASE_URL = "https://ctext.org/wiki.pl?if=gb&chapter={chapter_id}"
OUTPUT_DIR = Path(__file__).parent.parent / "raw" / "santonghui"
HEADERS = {
    "User-Agent": "MingLiTracer/0.1 (Research project; contact@example.com)"
}
DELAY = 2  # 请求间隔，尊重服务器


def fetch_chapter(chapter_id: str) -> str:
    """获取章节HTML"""
    url = BASE_URL.format(chapter_id=chapter_id)
    print(f"  请求: {url}")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return resp.text


def extract_text(html: str) -> str:
    """从CText HTML中提取纯文本"""
    # CText 页面正文在 <div class="ctext"> 或 <div id="content3"> 中
    # 移除HTML标签和导航元素
    from html import unescape

    # 提取正文区域
    patterns = [
        r'<div[^>]*id="content3"[^>]*>(.*?)</div>\s*<div[^>]*id="comments"',
        r'<div[^>]*class="ctext"[^>]*>(.*?)</div>',
        r'<table[^>]*class="wikitable"[^>]*>(.*?)</table>',
    ]

    text = html
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1)
            break

    # 移除HTML标签
    text = re.sub(r"<[^>]+>", "", text)
    # 处理HTML实体
    text = unescape(text)
    # 移除CText标记
    text = re.sub(r"\{[\d]+\}", "", text)
    # 规范化空白
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    # 移除首尾空白
    text = text.strip()

    return text


def save_raw(vol: int, html: str, text: str):
    """保存原始数据"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 保存HTML
    html_path = OUTPUT_DIR / f"vol_{vol:02d}.html"
    html_path.write_text(html, encoding="utf-8")

    # 保存提取的文本
    txt_path = OUTPUT_DIR / f"vol_{vol:02d}.txt"
    # 添加元数据头
    metadata = f"""# 《三命通会》卷{vol}
# 来源: {BASE_URL.format(chapter_id=CHAPTER_MAP[vol])}
# 获取日期: {datetime.now().strftime('%Y-%m-%d')}
# SHA256: {hashlib.sha256(text.encode('utf-8')).hexdigest()}
# 注意: 此为OCR初稿，可能存在形近字识别错误
#
"""
    txt_path.write_text(metadata + text, encoding="utf-8")

    return txt_path


def main():
    # 解析参数
    vol_range = range(1, 13)  # 默认全部
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if "--vol" in sys.argv:
            idx = sys.argv.index("--vol")
            parts = sys.argv[idx + 1].split("-")
            vol_range = range(int(parts[0]), int(parts[-1]) + 1)

    print(f"=== 获取《三命通会》卷{min(vol_range)}-{max(vol_range)} ===")
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    for vol_num in vol_range:
        chapter_id = CHAPTER_MAP.get(vol_num)
        if not chapter_id:
            print(f"⚠ 卷{vol_num}: 未找到章节ID，跳过")
            continue

        print(f"📖 卷{vol_num} (章节ID: {chapter_id})")

        try:
            html = fetch_chapter(chapter_id)
            text = extract_text(html)

            if len(text) < 100:
                print(f"⚠ 卷{vol_num}: 提取文本过短 ({len(text)}字符)，可能解析失败")
                print(f"   前100字符: {text[:100]}")

            txt_path = save_raw(vol_num, html, text)
            print(f"✅ 卷{vol_num}: 已保存 → {txt_path.name} ({len(text)}字符)")

        except Exception as e:
            print(f"❌ 卷{vol_num}: 获取失败 - {e}")

        time.sleep(DELAY)

    print()
    print("完成。下一步: python clean_santonghui.py")


if __name__ == "__main__":
    main()
