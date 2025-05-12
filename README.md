# Code Quality Assurance RAG Pipeline

A RAG-based application that analyzes SQL and Python files for code quality, safety issues, and production readiness using Google's Gemini AI models.

## Features

- Automatic detection of unsafe SQL patterns (e.g., deletions without WHERE clauses)
- Python code quality checking based on PEP8 standards
- Syntax validation for both Python and SQL
- Production readiness analysis with detailed warnings
- Interactive UI for exploring and addressing issues

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+ (for UI)
- Docker and Docker Compose (optional)
- Google Gemini API Key

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yuva-raja-reddy/code_quality_check.git
   cd code_quality_check
   ```

2. Create and activate a virtual environment
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables
   ```
   cp .env
   # Edit .env with your Google API key and configuration
   ```

5. Install UI dependencies (optional)
   ```
   cd ui
   npm install
   cd ..
   ```

### Running the Application

#### Using Python directly

```
uvicorn app.api.main:app --reload --port 8000
```

#### Using Docker

```
docker-compose up --build
```

## Usage

1. Upload SQL or Python files through the web interface or API
2. The system will analyze the files for potential issues
3. Review the detailed report with warnings and suggestions
4. Use the chat interface for more specific questions about the findings

## Architecture

This application uses a Retrieval Augmented Generation (RAG) pipeline to:
1. Parse and chunk code files
2. Create embeddings of code chunks
3. Store embeddings in a vector database
4. Retrieve relevant context for analysis
5. Use Google's Gemini models to identify issues and generate warnings
6. Present findings in a structured report

## Google Gemini Integration

The application leverages Google's Gemini models for:
- Code analysis and quality assessment
- Detecting potential issues in SQL and Python files
- Generating detailed explanations and recommendations
- Supporting interactive chat for clarification on findings

## License

This project is licensed under the MIT License - see the LICENSE file for details.