# 数据层核验标准
# Data Verification Standards

## 一、来源追溯标准

每条数据记录必须包含以下字段，缺一不可入库：

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `source_name` | string | 古籍书名（繁体） | `三命通會` |
| `volume` | string | 卷数 | `卷一` |
| `section` | string | 篇名/章节 | `論五行生成` |
| `source_url` | string | CText公开可访问URL | `https://ctext.org/wiki.pl?if=gb&chapter=212352` |
| `retrieved_date` | string | 获取日期 ISO 8601 | `2026-06-01` |
| `source_type` | string | 来源类型 | `ctext_wiki` |
| `raw_text_hash` | string | 原始文本SHA256 | `a1b2c3...` |

**红线：无 source_url 的数据不入库。**

## 二、完整性标准

1. **卷覆盖率**：目标卷数 / 实际获取卷数 × 100%。MVP阶段目标：100%。
2. **段落完整性**：与CText源章节数对比。缺失处必须标注。
3. **缺失标注格式**：
   - 原文模糊不清：`[...闕文]`
   - 原文疑似错误：`[...存疑:XXX]`
   - 跳过非核心内容：`[...此處略去XXX]`

## 三、清洗标准

1. **必须可复现**：清洗脚本放在 `data/scripts/`，运行后输出结果应一致
2. **AI可辅助但不可替代人工判断**：
   - AI可以做：去HTML标签、分段、基础格式统一
   - AI不可以做：改写原文、猜测模糊文字、翻译成白话
3. **保留原始和清洗两个版本**：`data/raw/` 存原始，`data/cleaned/` 存清洗后

## 四、关键术语校验标准

八字命理有22个核心字符（10天干+12地支），任何清洗不得改变这些字符：

```
天干：甲乙丙丁戊己庚辛壬癸
地支：子丑寅卯辰巳午未申酉戌亥
```

**校验脚本**：`data/scripts/verify_terms.py`
- 检查原文和清洗版中干支字符是否一致
- 检查常见OCR错误模式：
  - 己 → 已 （天干"己"误为副词"已"）
  - 戌 → 戍 （地支"戌"误为"戍"）
  - 戊 → 戌 （天干"戊"与地支"戌"混淆）
  - 未 → 末 （地支"未"误为"末"）
  - 申 → 甲 （地支"申"误为天干"甲"）

## 五、结构化JSON规范

### 古籍段落格式
```json
{
  "id": "{source_abbr}-{volume}-{seq:03d}",
  "source_name": "三命通會",
  "source_abbr": "smtm",
  "volume": "卷一",
  "section": "論五行生成",
  "paragraph_seq": 1,
  "original": "五行者，往來乎天地之間而不窮者也……",
  "raw_text": "五行者，往來乎天地之間而不窮者也……",
  "tags": ["五行", "基礎理論"],
  "source_url": "https://ctext.org/wiki.pl?if=gb&chapter=212352",
  "retrieved_date": "2026-06-01",
  "raw_text_hash": "sha256:..."
}
```

### 命例格式（JSONL，一行一条）
```jsonl
{"id":"mingli-001","name":"李鴻章","birth_date":"1823-02-15","birth_time":"寅時","birth_place":"安徽合肥","gender":"男","year_pillar":"癸未","month_pillar":"甲寅","day_pillar":"乙亥","hour_pillar":"己卯","pattern":"正官格","rishu":"乙木","reliability":"正史記載","source_text":"《滴天髓闡微》","original_comment":"乙木春生，得癸水滋潤……","tags":["正官格","清代","政治人物"]}
```

## 六、批次核验清单

每批数据处理完毕后，必须逐条检查：

```
□ source_url 是否可访问？
□ original 与 raw_text 是否一致（除标点外）？
□ 干支字符是否与源文本一致？
□ tags 是否正确分类？
□ 缺失处是否已标注？
□ SHA256哈希是否匹配？
```

## 七、核验报告模板

见 `VERIFICATION_REPORT.md`
