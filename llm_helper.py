"""
LLM Helper - AI-Powered Question Analysis using PIPE_TOKEN

This module provides intelligent question understanding and code generation
using OpenAI API via the college-provided PIPE_TOKEN.

Fallback: If LLM fails or PIPE_TOKEN not configured, falls back to rule-based logic.
"""

import os
import json
import logging
from typing import Any, Dict, Optional, List
import pandas as pd

logger = logging.getLogger(__name__)

# Check if openai is available
try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai package not installed - using fallback mode only")


class LLMQuestionAnalyzer:
    """
    Analyzes quiz questions using LLM for intelligent understanding.
    Falls back to rule-based logic if LLM unavailable or fails.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize LLM analyzer
        
        Args:
            api_token: PIPE_TOKEN for OpenAI API (optional)
        """
        self.api_token = api_token or os.getenv("PIPE_TOKEN")
        self.enabled = bool(self.api_token and OPENAI_AVAILABLE)
        self.client = None
        
        if self.enabled:
            # Configure OpenAI client
            self.client = AsyncOpenAI(
                api_key=self.api_token,
                base_url="https://api.openai.com/v1" # Default, can be overridden if needed
            )
            logger.info("✅ LLM integration enabled with PIPE_TOKEN")
        else:
            if not self.api_token:
                logger.info("ℹ️  PIPE_TOKEN not set - using rule-based fallback only")
            elif not OPENAI_AVAILABLE:
                logger.warning("⚠️  openai package not available - using rule-based fallback")
    
    async def analyze_question(
        self,
        question_text: str,
        available_data: Dict[str, Any],
        html_content: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze question using LLM to understand intent and generate solution approach
        """
        if not self.enabled or not self.client:
            return {"fallback_used": True, "confidence": 0.5}
        
        try:
            # Prepare context for LLM
            context = self._prepare_context(question_text, available_data, html_content)
            
            # Call LLM
            response = await self._call_llm(context)
            
            # Parse LLM response
            analysis = self._parse_llm_response(response)
            analysis["fallback_used"] = False
            analysis["confidence"] = analysis.get("confidence", 0.8)
            
            logger.info(f"✅ LLM analysis: {analysis.get('operation', 'unknown')} on column '{analysis.get('column', 'N/A')}'")
            return analysis
            
        except Exception as e:
            logger.warning(f"⚠️  LLM analysis failed: {e} - using fallback")
            return {"fallback_used": True, "confidence": 0.3, "error": str(e)}
    
    def _prepare_context(
        self,
        question: str,
        data_info: Dict[str, Any],
        html: Optional[str] = None
    ) -> str:
        """
        Prepare context prompt for LLM
        """
        df = data_info.get("dataframe")
        
        context = f"""You are a data analysis expert helping solve quiz questions.

QUESTION: {question}

AVAILABLE DATA:
"""
        
        if df is not None and isinstance(df, pd.DataFrame):
            context += f"""
- Data shape: {df.shape[0]} rows, {df.shape[1]} columns
- Columns: {list(df.columns)}
- Column types: {df.dtypes.to_dict()}
- First few rows:
{df.head(3).to_string()}

- Data statistics:
{df.describe(include='all').to_string()}
"""
        else:
            context += f"""
- Data source: {data_info.get('data_source', 'Unknown')}
- Columns: {data_info.get('columns', [])}
"""
        
        if html:
            context += f"\n- HTML content available: {len(html)} characters"
        
        context += """

TASK:
Analyze the question and provide a JSON response with:
{
  "operation": "sum|count|mean|median|max|min|filter|chart|boolean|text",
  "column": "target_column_name",
  "filter_column": "column_to_filter_on (if filtering needed)",
  "filter_value": "value_to_filter_by",
  "aggregation": "function to apply after filtering",
  "chart_type": "bar|line|scatter|histogram (if visualization)",
  "confidence": 0.0-1.0,
  "explanation": "brief explanation of analysis approach"
}

Respond ONLY with valid JSON, no other text.
"""
        
        return context
    
    async def _call_llm(self, context: str) -> str:
        """
        Call OpenAI API with PIPE_TOKEN
        """
        try:
            # Use chat completions API (GPT-3.5/GPT-4)
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",  # Use a cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data analysis expert. Respond only with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.3,  # Lower temperature for more deterministic output
                max_tokens=500,
                timeout=10  # 10 second timeout
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
        """
        try:
            # Try to find JSON in response (in case LLM added extra text)
            start = response.find("{")
            end = response.rfind("}") + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                # Try parsing entire response
                return json.loads(response)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return {"error": "Invalid JSON from LLM"}
    
    async def generate_pandas_code(
        self,
        question: str,
        df_info: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate executable pandas code for complex questions
        
        Args:
            question: Original question
            df_info: DataFrame information
            analysis: LLM analysis result
            
        Returns:
            Python code string or None if fallback needed
        """
        if not self.enabled or analysis.get("fallback_used"):
            return None
        
        try:
            prompt = f"""Given this data analysis question, generate executable Python code using pandas.

QUESTION: {question}

DATAFRAME INFO:
- Columns: {df_info.get('columns', [])}
- Shape: {df_info.get('shape', 'unknown')}

ANALYSIS: {json.dumps(analysis, indent=2)}

Generate Python code that:
1. Assumes dataframe is available as 'df'
2. Performs the required operation
3. Returns the final result as 'answer'

Example:
```python
# Filter and calculate
filtered = df[df['Status'] == 'Active']
answer = filtered['Sales'].sum()
```

Respond with ONLY the Python code, no explanations or markdown.
"""
            
            response = await self._call_llm(prompt)
            
            # Extract code (remove markdown if present)
            code = response.strip()
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()
            
            logger.info(f"Generated pandas code: {len(code)} chars")
            return code
            
        except Exception as e:
            logger.warning(f"Code generation failed: {e}")
            return None


# Global instance (initialized on first use)
_llm_analyzer: Optional[LLMQuestionAnalyzer] = None


def get_llm_analyzer() -> LLMQuestionAnalyzer:
    """
    Get or create global LLM analyzer instance
    """
    global _llm_analyzer
    if _llm_analyzer is None:
        _llm_analyzer = LLMQuestionAnalyzer()
    return _llm_analyzer