"""
Integration with Google's Gemini API for code analysis.
"""
import os
import google.generativeai as genai
from typing import List, Dict, Any

class GeminiClient:
    """Client for interacting with Google's Gemini models."""
    
    def __init__(self, model_name=None, temperature=0.1, max_output_tokens=2000):
        """Initialize the Gemini client with API key and parameters."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name or os.getenv("GEMINI_MODEL", "gemini-1.5-pro-latest")
        self.temperature = float(os.getenv("TEMPERATURE", temperature))
        self.max_output_tokens = int(os.getenv("MAX_TOKENS", max_output_tokens))
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }
        )
    
    async def analyze_code(self, code: str, file_type: str, file_name: str) -> Dict[str, Any]:
        """
        Analyze code for issues and generate warnings.
        
        Args:
            code (str): The code to analyze
            file_type (str): The type of file ('python' or 'sql')
            file_name (str): The name of the file
            
        Returns:
            Dict containing analysis results with issues and warnings
        """
        prompt = self._build_analysis_prompt(code, file_type, file_name)
        response = await self.model.generate_content_async(prompt)
        
        return self._parse_response(response)
    
    def _build_analysis_prompt(self, code: str, file_type: str, file_name: str) -> str:
        """Build a prompt for code analysis."""
        
        base_prompt = f"""
        You are a code quality assurance expert. Analyze this {file_type.upper()} code from the file "{file_name}" 
        and identify any issues related to:
        
        1. Syntax errors or potential bugs
        2. Coding standards violations (PEP8 for Python, ANSI SQL best practices for SQL)
        3. Security concerns or unsafe patterns
        4. Production readiness issues
        
        For SQL files, specifically flag:
        - DELETE statements without WHERE clauses
        - TRUNCATE TABLE statements
        - DROP TABLE/DATABASE statements
        - Queries that might cause performance issues
        
        For Python files, specifically check for:
        - PEP8 violations
        - Error handling issues
        - Resource management problems (unclosed files, connections)
        - Unreachable code or unused variables
        
        Return your analysis in the following JSON format:
        {{
            "issues": [
                {{
                    "line_start": <line_number>,
                    "line_end": <line_number>,
                    "issue_type": "<syntax|standard|security|performance>",
                    "severity": "<high|medium|low>",
                    "description": "<detailed description>",
                    "suggested_fix": "<code suggestion>"
                }}
            ],
            "summary": "<overall code quality assessment>",
            "production_ready": <true|false>,
            "warnings_count": <number>
        }}
        
        HERE IS THE CODE TO ANALYZE:
        ```{file_type}
        {code}
        ```
        """
        
        return base_prompt
    
    def _parse_response(self, response) -> Dict[str, Any]:
        """Parse the Gemini response into a structured format."""
        try:
            # Extract JSON from response text
            text = response.text
            # Basic validation and fallback logic if JSON parsing fails
            if not text or "issues" not in text:
                return {
                    "issues": [],
                    "summary": "Analysis could not be completed.",
                    "production_ready": False,
                    "warnings_count": 0,
                    "error": "Failed to parse response"
                }
            
            # Try to extract and parse the JSON content
            import json
            import re
            
            # Look for JSON structure in the response
            json_match = re.search(r'({[\s\S]*})', text)
            if json_match:
                try:
                    result = json.loads(json_match.group(1))
                    # Ensure required fields exist
                    result.setdefault("issues", [])
                    result.setdefault("summary", "Analysis completed.")
                    result.setdefault("production_ready", False)
                    result.setdefault("warnings_count", len(result.get("issues", [])))
                    return result
                except json.JSONDecodeError:
                    pass  # Fall back to the default return
            
            return {
                "issues": [],
                "summary": "Analysis completed but response format was unexpected.",
                "production_ready": False,
                "warnings_count": 0,
                "raw_response": text
            }
        
        except Exception as e:
            return {
                "issues": [],
                "summary": f"Error processing response: {str(e)}",
                "production_ready": False,
                "warnings_count": 0,
                "error": str(e)
            }