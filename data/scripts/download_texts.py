"""
从殆知阁（daizhigev20）GitHub仓库下载古籍文本

来源：https://github.com/garychowcmu/daizhigev20
分类：易藏/术数

用法：
  python download_texts.py
"""

import requests
import hashlib
from datetime import datetime
from pathlib import Path

# 目标文本：名称 → GitHub raw URL
TEXTS = {
    "santonghui": {
        "name": "三命通會",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/易藏/术数/三命通会.txt",
        "stage": "MVP",
    },
    "ditianshui": {
        "name": "滴天髓闡微",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/易藏/术数/滴天髓阐微.txt",
        "stage": "MVP",
    },
    "yuanhaiziping": {
        "name": "淵海子平",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/易藏/术数/渊海子平.txt",
        "stage": "MVP",
    },
    "xiejibianfangshu": {
        "name": "欽定協紀辨方書",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/易藏/术数/钦定协纪辨方书.txt",
        "stage": "MVP",
    },
    "qiongtongbaojian": {
        "name": "窮通寶鑑",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/易藏/术数/穷通宝鉴.txt",
        "stage": "V2",
    },
    "zipingzhenquan": {
        "name": "子平真詮評注",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/易藏/术数/子平真诠评注.txt",
        "stage": "V2",
    },
}

OUTPUT_DIR = Path(__file__).parent.parent / "raw"
HEADERS = {"User-Agent": "MingLiTracer/0.1 (Research project)"}


def download_text(key: str, info: dict) -> Path:
    """下载单个文本并保存"""
    print(f"下载: {info['name']} ({info['stage']})")
    print(f"  URL: {info['url']}")

    resp = requests.get(info["url"], headers=HEADERS, timeout=60)
    resp.raise_for_status()

    # 尝试检测编码
    resp.encoding = "utf-8"
    text = resp.text

    # 计算哈希
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

    # 保存原始文本
    out_dir = OUTPUT_DIR / key
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{key}_raw.txt"

    # 添加元数据头
    metadata = f"""# {info['name']}
# 来源: 殆知阁古代文献txt大全集 (daizhigev20)
# GitHub: https://github.com/garychowcmu/daizhigev20
# 下载日期: {datetime.now().strftime('%Y-%m-%d')}
# 文件SHA256: {sha}
# 原始大小: {len(text):,} 字符
# 注意: 此文本未经清洗，可能包含OCR错误、格式问题
#
"""
    out_path.write_text(metadata + text, encoding="utf-8")

    print(f"  → {out_path}")
    print(f"  → {len(text):,} 字符, SHA256: {sha[:16]}...")
    print()

    return out_path


def main():
    print("=== 下载古籍文本 ===\n")

    for key, info in TEXTS.items():
        try:
            download_text(key, info)
        except Exception as e:
            print(f"  ❌ 下载失败: {e}\n")

    # 生成下载摘要
    summary_path = OUTPUT_DIR / "download_summary.md"
    lines = [
        f"# 古籍文本下载摘要",
        f"下载日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"数据来源: 殆知阁古代文献txt大全集",
        f"GitHub: https://github.com/garychowcmu/daizhigev20",
        f"",
        f"| 古籍 | 文件名 | 阶段 | 大小 | 状态 |",
        f"|------|--------|------|------|------|",
    ]
    for key, info in TEXTS.items():
        raw_file = OUTPUT_DIR / key / f"{key}_raw.txt"
        if raw_file.exists():
            size = raw_file.stat().st_size
            lines.append(f"| {info['name']} | {key}_raw.txt | {info['stage']} | {size:,} B | ✅ |")
        else:
            lines.append(f"| {info['name']} | — | {info['stage']} | — | ❌ |")

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"摘要: {summary_path}")
    print("完成。")


if __name__ == "__main__":
    main()
