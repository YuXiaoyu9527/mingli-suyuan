# 台式机部署指南

> ⚠️ **笔记本用户必读**：如果在笔记本上运行，请先看 [笔记本低配运行指南](#笔记本低配运行指南防卡死防黑屏) 部分，避免电脑卡死/黑屏。

## 前提条件

台式机需要先装好：

```
□ Python 3.11+ （去 python.org 下载，安装时勾选 "Add Python to PATH"）
□ Node.js 18+  （去 nodejs.org 下载 LTS 版）
□ Git          （去 git-scm.com 下载）
```

**验证安装**（打开命令行 CMD，逐条输入）：
```
python --version    # 应显示 Python 3.11.x 或更高
node --version      # 应显示 v18.x 或更高
git --version       # 应显示 git version 2.x
```

---

## 第一步：拷贝项目

把笔记本上整个文件夹拷到台式机：

```
笔记本: c:\text\创业项目\
    ↓  （U盘 / 移动硬盘 / 网盘）
台式机: d:\projects\创业项目\
```

或者用 git（如果你有 GitHub 账号）：
```
git clone <你的仓库地址>
```

---

## 第二步：安装 Python 依赖

打开 CMD，逐条执行：

```bash
# 进入项目目录
cd d:\projects\创业项目

# 安装排盘引擎依赖
pip install lunar-python

# 安装 RAG 依赖
pip install chromadb

# 安装 ONNX 运行时（轻量，不需要 PyTorch）
pip install onnxruntime

# 验证所有包装好了
python -c "import lunar_python; print('lunar OK')"
python -c "import chromadb; print('chromadb OK')"
python -c "import onnxruntime; print('onnx OK')"
```

如果 `onnxruntime` 报 DLL 错误，说明缺少 Visual C++ 运行库：
```
# 去微软官网下载安装：
# https://aka.ms/vs/17/release/vc_redist.x64.exe
# 安装后重启电脑，再试
```

---

## 第三步：安装前端依赖

```bash
cd d:\projects\创业项目\web
npm install
```

这步大概需要 2-5 分钟，取决于网速。

---

## 第四步：构建向量索引（吃CPU，台式机适合干这个）

```bash
cd d:\projects\创业项目

# 先跑小样本测试（200条，约2分钟）
python -m api.rag.indexer --sample 200 --rebuild

# 确认没问题后，跑全量（4000+条，约10-30分钟）
python -m api.rag.indexer --rebuild
```

成功标志：看到 `索引完成! 索引总量: XXXX`

---

## 第五步：验证一切正常

```bash
# 1. 排盘测试
python api/tests/test_runner.py --verbose
# 应该看到 10/10 通过

# 2. 检索测试
python -c "from api.rag import RAGSearcher; s = RAGSearcher(); print(s.search('正官格', top_k=3))"
# 应该返回3条古籍原文

# 3. 启动后端
cd d:\projects\创业项目
python -m uvicorn api.server:app --reload --port 8000
# 打开浏览器 http://localhost:8000  看到 {"name":"命理溯源 API"...}

# 4. 测试排盘API
# 浏览器打开 http://localhost:8000/api/paipan  会提示 Method Not Allowed（正常，这是POST接口）

# 5. 启动前端
cd d:\projects\创业项目\web
npm run dev
# 打开浏览器 http://localhost:3000
```

---

## 常见问题

| 问题 | 解决办法 |
|------|---------|
| `pip install` 太慢 | 加国内镜像：`pip install xxx -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `onnxruntime` DLL报错 | 安装 VC++ 运行库（见第三步） |
| `npm install` 失败 | 删掉 `node_modules` 文件夹重试 |
| 端口被占用 | 换端口：`--port 3001` 或 `--port 8001` |
| `python` 命令找不到 | 安装 Python 时没勾选 "Add to PATH"，重装或手动添加 |

---

## 笔记本低配运行指南（防卡死/防黑屏）

如果你的笔记本只有 **4GB 或 8GB 内存**，之前运行时电脑卡死甚至黑屏，
**这不是电脑坏了，是代码之前的内存策略有问题**。

### 问题根因

旧版 `SimpleSearcher` 会在内存中建立 n-gram 索引（660万+ 个词条），
单进程吃掉 **~700MB-1GB 内存**。再加上：
- Next.js dev server: ~500-800MB
- FastAPI: ~200MB（含数据）
- Windows 系统: ~2GB
- 浏览器: ~300MB

4GB 笔记本直接爆内存 → 触发磁盘换页 → 卡死 → 黑屏。

### 现在的修复（v2 已应用）

`SimpleSearcher` 已重写为流式扫描模式：
- 内存占用从 ~700MB 降到 ~5-10MB
- 搜索速度 4800 条 <100ms，完全不影响体验

### 安全运行步骤

**方案一：只跑后端（推荐，最安全）**

```bash
# 1. 启动后端
cd d:\projects\创业项目
python -m uvicorn api.server:app --port 8000
# 不要加 --reload，reload 会额外开一个进程

# 2. 浏览器打开 http://localhost:8000
# API 直接能用，用 curl 或浏览器测试
```

**方案二：先后端再前端（8GB 以上）**

```bash
# 终端1：先启动后端（不加 --reload）
python -m uvicorn api.server:app --port 8000

# 等后端完全启动后，终端2：启动前端
cd web
# 用 --turbo=false 关掉实验性编译器，省 ~200MB
npx next dev --turbo=false
```

**方案三：只跑前端（仅看页面，不求数据）**

```bash
cd web
npx next dev --turbo=false
```

### 内存监控

打开任务管理器（Ctrl+Shift+Esc），看"内存"列：
- Python 进程应该 < 300MB
- Node.js 进程应该 < 600MB
- 两个加起来 > 80%（比如总共 8GB，用了 6.4GB+）→ 关掉一个

### 如果你在笔记本上构建向量索引

```bash
# 只用小样本，不要跑全量！
python -m api.rag.indexer --sample 200 --rebuild
# 千万不要在笔记本上跑 --rebuild（不加 --sample），
# ONNX 模型加载 + 向量化 会吃 2GB+ 内存
```

---

## 最小验证（5分钟）

如果时间紧，只跑这3条确认项目能跑：

```bash
# 1. 排盘
python -c "from api.paipan import paipan, to_dict; import json; print(json.dumps(to_dict(paipan(1990,5,20,12,0,'男')), ensure_ascii=False, indent=2)[:500])"

# 2. 检索（需要先跑 python -m api.rag.indexer --sample 100 --rebuild）
python -c "from api.rag import RAGSearcher; s = RAGSearcher(); r = s.search('五行相生相克', 3); print(len(r), 'results')"

# 3. 前端
cd web && npm run dev
```
