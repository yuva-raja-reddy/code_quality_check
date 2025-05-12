"""
Core analyzer module for code quality assessment.
"""
from typing import Dict, List, Any
import os
from app.parsers.python_parser import PythonParser
from app.parsers.sql_parser import SQLParser
from app.rag.gemini_client import GeminiClient
from app.core.chunking import chunk_code
from app.utils.file_handlers import read_file
import asyncio

class CodeAnalyzer:
    """
    Analyzes code files for quality issues and warnings.
    """
    
    def __init__(self):
        """Initialize the code analyzer with parsers and LLM client."""
        self.python_parser = PythonParser()
        self.sql_parser = SQLParser()
        self.gemini_client = GeminiClient()
    
    async def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single file for code quality issues.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dict containing analysis results
        """
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        
        # Determine file type
        file_type = None
        if file_extension == '.py':
            file_type = 'python'
        elif file_extension == '.sql':
            file_type = 'sql'
        else:
            return {
                "error": f"Unsupported file type: {file_extension}",
                "file_name": file_name,
                "issues": []
            }
        
        # Read file content
        try:
            content = read_file(file_path)
        except Exception as e:
            return {
                "error": f"Error reading file: {str(e)}",
                "file_name": file_name,
                "issues": []
            }
        
        # Chunk large files if necessary
        chunks = chunk_code(content, file_type)
        
        if len(chunks) == 1:
            # If only one chunk, analyze directly
            result = await self.gemini_client.analyze_code(content, file_type, file_name)
            result["file_name"] = file_name
            return result
        else:
            # For multiple chunks, analyze each and combine
            chunk_results = []
            for i, chunk in enumerate(chunks):
                chunk_result = await self.gemini_client.analyze_code(
                    chunk["code"], 
                    file_type,
                    f"{file_name} (chunk {i+1}/{len(chunks)})"
                )
                # Adjust line numbers to match original file
                for issue in chunk_result.get("issues", []):
                    issue["line_start"] = chunk["start_line"] + issue.get("line_start", 0)
                    issue["line_end"] = chunk["start_line"] + issue.get("line_end", 0)
                
                chunk_results.append(chunk_result)
            
            # Combine results
            combined_result = {
                "file_name": file_name,
                "issues": [],
                "summary": "",
                "production_ready": True,
                "warnings_count": 0
            }
            
            for result in chunk_results:
                combined_result["issues"].extend(result.get("issues", []))
                combined_result["summary"] += result.get("summary", "") + "\n"
                if not result.get("production_ready", True):
                    combined_result["production_ready"] = False
                combined_result["warnings_count"] += result.get("warnings_count", 0)
            
            return combined_result
    
    async def analyze_multiple_files(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze multiple files concurrently.
        
        Args:
            file_paths: List of paths to files to analyze
            
        Returns:
            List of analysis results for each file
        """
        tasks = [self.analyze_file(path) for path in file_paths]
        return await asyncio.gather(*tasks)