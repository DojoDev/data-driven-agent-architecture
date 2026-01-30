---
description: Initialize the Data-Driven Agent Architecture project
---

# Project Initialization Workflow

This workflow sets up the complete development environment for the Data-Driven Agent Architecture POC.

## Prerequisites
- Python 3.8+ installed
- OpenAI API key

## Steps

### 1. Check Python Version
```bash
python3 --version
```
Ensure Python 3.8 or higher is installed.

### 2. Create Virtual Environment
```bash
python3 -m venv venv_estech
```
Creates an isolated Python environment for the project.

// turbo
### 3. Activate Virtual Environment (Linux/WSL)
```bash
source venv_estech/bin/activate
```

### 4. Upgrade pip
```bash
pip install --upgrade pip
```

// turbo
### 5. Install Dependencies
```bash
pip install -r requirements.txt
```
Installs all required packages: FastAPI, OpenAI, Pydantic, etc.

### 6. Verify Environment Configuration
Check that `.env` file exists and contains:
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATA_DRIVEN_API_URL` - API endpoint (default: http://localhost:8000/api)
- `DATA_DRIVEN_API_TOKEN` - API authentication token

### 7. Test Installation
```bash
python -c "import openai, fastapi, pydantic; print('✅ All dependencies installed successfully!')"
```

## Running the System

### Terminal 1 - Start API Server
```bash
source venv_estech/bin/activate
python -m app.presentation.api.server
```
The API will be available at http://localhost:8000

### Terminal 2 - Start Agent
```bash
source venv_estech/bin/activate
python main.py
```

## Verification

1. **API Health Check**: Visit http://localhost:8000/health
2. **API Documentation**: Visit http://localhost:8000/docs
3. **Agent Chat**: Interact with Lume in Terminal 2

## Example Queries
- "Olá!"
- "Qual o consumo do sensor SENSOR_001 na última hora?"
- "Mostre o consumo mensal do SENSOR_002"
- "Liste todos os sensores disponíveis"

## Troubleshooting

### OpenAI API Key Error
If you see "OPENAI_API_KEY não configurada", edit `.env` and add your key.

### Port Already in Use
If port 8000 is busy, modify `DATA_DRIVEN_API_URL` in `.env` or stop the conflicting service.

### Import Errors
Ensure virtual environment is activated and dependencies are installed.

## Next Steps
- Explore the SOLID architecture in `/app` directory
- Add new tools by extending the `Tool` abstract class
- Implement additional LLM providers (Gemini, DeepSeek)
- Review tests in `/tests` directory
