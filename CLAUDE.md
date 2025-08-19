# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TradingAgents-CN is a multi-agent LLM-based Chinese financial trading decision framework. It's a Chinese-enhanced version of the original TradingAgents project, optimized for Chinese users with complete A-share/Hong Kong stock/US stock analysis capabilities.

## Development Commands

### Installation and Setup
```bash
# Install dependencies (recommended)
pip install -e .

# Alternative: Install from requirements.txt (deprecated)
pip install -r requirements.txt

# Upgrade pip first (important to avoid installation errors)
python -m pip install --upgrade pip
```

### Running the Application
```bash
# Start web interface (recommended)
python start_web.py

# Alternative web startup methods
python web/run_web.py
streamlit run web/app.py

# CLI interface
python -m cli.main

# Run main analysis script
python main.py
```

### Docker Commands
```bash
# Start all services (first time or with code changes)
docker-compose up -d --build

# Daily startup (no code changes)
docker-compose up -d

# Smart startup scripts
# Windows
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1
# Linux/Mac
chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh

# Stop services
docker-compose down

# View logs
docker-compose logs -f web
```

### Testing
```bash
# Run specific test files
python scripts/test_[specific_functionality].py

# Example test commands
python tests/test_akshare_api.py
python tests/test_dashscope_integration.py
python scripts/simple_async_test.py

# Syntax checking
python scripts/syntax_checker.py
python scripts/quick_syntax_check.py
```

### Database and Cache Management
```bash
# Initialize database
python scripts/setup/init_database.py

# Check system status
python scripts/validation/check_system_status.py

# Clean cache
python scripts/maintenance/cleanup_cache.py --days 7
```

## Architecture Overview

### Core Components

1. **TradingAgentsGraph** (`tradingagents/graph/trading_graph.py`)
   - Main orchestration class that coordinates all agents
   - Handles LLM provider switching (OpenAI, DashScope, DeepSeek, Google AI)
   - Manages the analysis workflow through LangGraph

2. **Multi-Agent System** (`tradingagents/agents/`)
   - **Analysts**: market, fundamentals, news, social_media analysts
   - **Researchers**: bull_researcher, bear_researcher (debate mechanism)
   - **Managers**: research_manager, risk_manager
   - **Trader**: final decision maker

3. **Data Flow System** (`tradingagents/dataflows/`)
   - Multiple data sources: Tushare, AkShare, FinnHub, Yahoo Finance
   - Intelligent caching with Redis and MongoDB
   - Fallback mechanism: Redis → MongoDB → API → Local cache

4. **LLM Adapters** (`tradingagents/llm_adapters/`)
   - OpenAI compatible adapters for different providers
   - DashScope (Alibaba), DeepSeek, Google AI support
   - Unified interface for model switching

### Key Configuration

- **Default Config**: `tradingagents/default_config.py`
- **Environment Variables**: `.env` file (copy from `.env.example`)
- **Database Config**: `tradingagents/config/database_config.py`

### Multi-LLM Provider Support

The system supports 4 major LLM providers:
- **DashScope** (Alibaba): qwen-turbo, qwen-plus, qwen-max
- **DeepSeek**: deepseek-chat (cost-effective)
- **Google AI**: 9 verified models including gemini-2.5-pro, gemini-2.0-flash
- **OpenRouter**: 60+ models aggregation platform

### Data Sources

- **A-shares**: Tushare (professional), AkShare, TDX (deprecated)
- **Hong Kong stocks**: AkShare, Yahoo Finance
- **US stocks**: FinnHub, Yahoo Finance
- **News**: Google News, unified news tool with AI filtering

## Important File Locations

### Entry Points
- `main.py` - Main analysis script entry point
- `start_web.py` - Web application launcher
- `web/app.py` - Streamlit web interface

### Core Libraries
- `tradingagents/graph/trading_graph.py` - Main orchestration
- `tradingagents/agents/` - All agent implementations
- `tradingagents/dataflows/` - Data processing and caching
- `tradingagents/config/` - Configuration management

### Web Interface
- `web/app.py` - Main Streamlit application
- `web/components/` - UI components
- `web/utils/` - Web utilities and session management

### Configuration Files
- `pyproject.toml` - Main project configuration and dependencies
- `docker-compose.yml` - Docker services configuration
- `.env` - Environment variables (create from `.env.example`)

## Development Guidelines

### Code Structure
- Follow the existing agent-based architecture
- Use the unified logging system: `tradingagents.utils.logging_manager`
- Implement proper error handling and fallback mechanisms
- Use type hints and proper documentation

### Testing
- Test files are in `tests/` and `scripts/test_*.py`
- Use existing test patterns for new functionality
- Test both individual components and integration scenarios

### Database Integration
- MongoDB for persistent data storage
- Redis for high-speed caching
- Automatic fallback to API calls if databases unavailable
- Check `tradingagents/config/database_manager.py` for database utilities

### LLM Integration
- Use the adapter pattern in `tradingagents/llm_adapters/`
- Support multiple providers through unified interface
- Handle rate limiting and error responses gracefully
- Cost optimization through model selection

## Special Notes

### Windows 10 Compatibility
- ChromaDB compatibility issues exist on Windows 10
- Use `MEMORY_ENABLED=false` in .env to disable memory features
- Run PowerShell as Administrator if needed

### Environment Configuration
- Copy `.env.example` to `.env` and configure API keys
- Different configurations for Docker vs local deployment
- Database hosts: `localhost` (local) vs `mongodb`/`redis` (Docker)

### Data Directory Configuration
```bash
# Configure custom data directory
python -m cli.main data-config --set /path/to/your/data

# View current configuration
python -m cli.main data-config --show
```

### Report Export
The system supports exporting analysis reports in multiple formats:
- Markdown (.md)
- Word (.docx) 
- PDF (.pdf)

Dependencies: `markdown`, `pypandoc`, `wkhtmltopdf`

## Common Development Workflows

1. **Adding New Agent**: Follow patterns in `tradingagents/agents/`
2. **Adding Data Source**: Implement in `tradingagents/dataflows/`
3. **Adding LLM Provider**: Create adapter in `tradingagents/llm_adapters/`
4. **Web UI Changes**: Modify components in `web/components/`
5. **Configuration Updates**: Update `default_config.py` and environment handling

This is a sophisticated multi-agent system with comprehensive Chinese market support, extensive documentation, and robust error handling mechanisms.