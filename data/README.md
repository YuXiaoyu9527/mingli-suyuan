# 数据层

本目录存放项目的所有数据资产。所有古籍文本来源于公开可追溯的学术数字化项目。

## 目录结构

```
data/
├── VERIFICATION_STANDARDS.md  # 数据核验标准（必读）
├── VERIFICATION_REPORT.md     # 核验报告（每批数据处理后生成）
├── raw/                       # 原始获取文本（不修改）
│   ├── santonghui/            # 三命通會
│   ├── ditianshui/            # 滴天髓闡微
│   ├── yuanhaiziping/         # 淵海子平
│   └── xiejibianfangshu/      # 協紀辨方書
├── cleaned/                   # 清洗后结构化JSON
├── scripts/                   # 数据获取/清洗/核验脚本
│   ├── fetch_*.py             # 获取脚本
│   ├── clean_*.py             # 清洗脚本
│   └── verify_terms.py       # 术语校验脚本
├── mingli_cases.jsonl         # 历史命例数据
├── quiz_cases.jsonl           # 断案录题库
└── zeji_rules.json            # 择吉规则
```

## 数据来源

所有古籍文本来自 [中国哲学书电子化计划 (CText.org)](https://ctext.org)。

## 注意事项

1. CText文本为OCR初稿，存在形近字识别错误
2. 每段文本保留原始OCR版本(`raw_text`)和清洗后版本(`original`)
3. 清洗脚本必须可复现
4. 任何缺失/存疑处必须标注，不可猜测填补
