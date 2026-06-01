# 台式机部署指南

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
