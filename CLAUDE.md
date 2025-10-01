# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered novel generation tool that creates cohesive, long-form stories using large language models. The application features a comprehensive GUI for managing the entire novel creation workflow.

## Key Commands

### Running the Application
```bash
python main.py
```

### Building Executable
```bash
pip install pyinstaller
pyinstaller main.spec
```
The executable will be created in the `dist/` directory with version `AI_NovelGenerator_V1.4.4`.

### Installing Dependencies
```bash
pip install -r requirements.txt
python check_dependencies.py  # Verify installations
```

### Testing & Debugging
```bash
python test_fixes.py  # Test recent bug fixes
```

## Core Architecture

### Entry Point
- `main.py` - Comprehensive entry point with enhanced error handling and logging

### GUI Framework
- Uses `customtkinter` for modern dark/light theme GUI
- Main GUI class: `NovelGeneratorGUI` in `ui/main_window.py` with enhanced error handling
- Tab-based interface with separate modules for different functions

### Novel Generation Pipeline
The novel generation follows a structured 4-step process:

1. **Architecture Generation** (`novel_generator/architecture.py`)
   - Creates world-building, character definitions, plot foundations
   - Uses chunked generation for large content
   - Outputs: `Novel_setting.txt`

2. **Chapter Blueprint** (`novel_generator/blueprint.py`)
   - Generates chapter titles and summaries for the entire novel
   - Supports chunked processing for large chapter counts
   - Outputs: `Novel_directory.txt`

3. **Chapter Draft Generation** (`novel_generator/chapter.py`)
   - Creates individual chapter drafts with context awareness
   - Uses vector retrieval for long-term context consistency
   - Outputs: `chapter_X.txt` and `outline_X.txt`

4. **Chapter Finalization** (`novel_generator/finalization.py`)
   - Updates global state, character development, plot arcs
   - Updates vector database for future chapters

### Key Components

#### LLM Adapters (`llm_adapters.py`)
- Unified interface for multiple LLM providers (OpenAI, DeepSeek, Gemini, Azure)
- Base class `BaseLLMAdapter` with provider-specific implementations
- Supports retry mechanisms with exponential backoff
- Intelligent error classification (retryable vs non-retryable)

#### Embedding & Vector Store (`embedding_adapters.py`, `novel_generator/vectorstore_utils.py`)
- ChromaDB for vector storage and retrieval
- Supports OpenAI, Azure embeddings
- Configurable retrieval parameters (retrieval_k)
- Graceful fallback when ChromaDB unavailable

#### Configuration Management (`config_manager.py`)
- JSON-based configuration with thread-safe operations
- Multiple LLM configurations for different generation tasks
- Auto-creates default config from `config.example.json`
- Recent improvements: thread safety, atomic writes, backup mechanism

#### UI Structure (`ui/` directory)
- `main_window.py` - Main GUI controller with enhanced error handling
- `main_tab.py` - Primary generation workflow interface
- `config_tab.py` - LLM and embedding configuration with help tooltips
- `novel_params_tab.py` - Novel parameters (topic, genre, chapter count, etc.)
- `setting_tab.py` - Novel architecture editing
- `directory_tab.py` - Chapter directory management
- `character_tab.py` - Character state tracking
- `summary_tab.py` - Global summary management
- `chapters_tab.py` - Chapter content editing
- `other_settings.py` - Additional configuration options

#### Supporting Components
- `consistency_checker.py` - Detects plot contradictions and character inconsistencies
- `prompt_definitions.py` - Centralized AI prompt management
- `utils.py` - Common utilities with enhanced error handling
- `chapter_directory_parser.py` - Chapter blueprint parsing

### File Organization
Generated files are organized in user-specified output directory:
- `Novel_setting.txt` - World/character/plot settings
- `Novel_directory.txt` - Chapter titles and summaries
- `chapter_X.txt` - Individual chapter content
- `outline_X.txt` - Chapter outlines
- `global_summary.txt` - Overall story summary
- `character_state.txt` - Character development tracking
- `plot_arcs.txt` - Plot arc management
- `vectorstore/` - ChromaDB vector database

## Configuration Structure

The application uses a sophisticated configuration system supporting:
- **Multiple LLM configurations** for different generation tasks
- **Task-specific model selection** (draft, outline, final, consistency check)
- **Separate embedding model configuration**
- **Proxy settings** with validation
- **WebDAV sync capabilities** for configuration backup
- **Thread-safe configuration operations**

Key sections:
- `llm_configs` - Multiple LLM provider configurations
- `embedding_configs` - Embedding model settings
- `choose_configs` - Task-specific model assignments
- `other_params` - Novel parameters and generation settings
- `proxy_setting` - Network proxy configuration
- `webdav_config` - Remote sync settings

## Dependencies & Frameworks

**Core Dependencies:**
- `customtkinter` - Modern GUI framework
- `langchain-*` - LLM integration framework
- `chromadb` - Vector database for context retrieval
- `openai`, `google-generativeai` - LLM provider SDKs
- `pydantic` - Data validation
- `requests`, `httpx` - HTTP clients

**Python Requirements:**
- Python 3.8+ (recommended 3.9-3.12)

## Recent Improvements

Major fixes implemented:
- **Thread-safe configuration management** with atomic writes and backup
- **Enhanced GUI error handling** with safe configuration loading
- **Improved LLM adapters** with retry mechanisms and error classification
- **Better parameter validation** and type checking throughout the application

## Development Notes

- No formal test suite exists, but has `test_fixes.py` for validation
- Uses Chinese comments and variable names extensively
- PyInstaller configuration for Windows builds includes custom paths
- Supports both local (Ollama) and cloud-based LLM services
- Vector database can be cleared when switching embedding models
- Logging configured for both file and console output
- Global exception handling with user-friendly error dialogs
- Icon support (`icon.ico`) for packaged executable