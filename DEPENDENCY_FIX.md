# 依赖问题修复说明

## 问题解决

我已经修复了导入依赖的问题，现在程序可以在缺少可选依赖的情况下正常启动：

### 🔧 **已修复的导入问题**

1. **Azure AI依赖** - 现在只在需要时才导入，缺少时会给出友好的安装提示
2. **Chroma向量数据库** - 如果未安装，程序会以降级模式运行，跳过向量存储功能
3. **scikit-learn** - 作为可选依赖，不影响核心功能

### 🚀 **启动程序**

现在可以直接运行：

```bash
python main.py
```

### 📦 **依赖检查**

运行依赖检查脚本了解缺失的包：

```bash
python check_dependencies.py
```

### 🎯 **功能降级说明**

如果缺少以下依赖，对应功能会降级：

- **langchain-chroma/chromadb**: 向量存储功能不可用，但可以正常生成小说
- **azure-ai-inference**: Azure AI适配器不可用，但可以使用其他LLM
- **scikit-learn**: 某些高级文本处理功能不可用

### 💡 **建议安装的依赖**

如果要获得完整功能，请安装：

```bash
# 安装所有依赖（推荐）
pip install -r requirements.txt

# 或者只安装核心依赖
pip install customtkinter langchain langchain-openai openai requests nltk numpy tiktoken

# 可选：向量存储功能
pip install langchain-chroma chromadb

# 可选：Azure AI支持
pip install azure-ai-inference
```

### 🔍 **故障排除**

如果仍有问题，请运行：

```bash
# 检查依赖
python check_dependencies.py

# 运行测试
python test_fixes.py
```

### 📝 **日志记录**

程序现在会记录详细的日志信息到 `novel_generator.log` 文件中，包括：

- 缺失依赖的警告
- 功能降级提示
- 正常运行日志

---

**状态**: ✅ 导入问题已修复，程序可以正常启动