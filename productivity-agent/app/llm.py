"""LLM integration for agent decision making and productivity analysis."""

import json
import openai
from typing import Dict, Any, Optional
from .config import Config


class LLMService:
    """Service for interacting with OpenAI API."""
    
    def __init__(self):
        """Initialize LLM service with OpenAI client."""
        openai.api_key = Config.OPENAI_API_KEY
    
    def agent_decision(self, event_type: str, payload: Dict[str, Any], memory: str) -> Dict[str, Any]:
        """
        Get agent decision based on event and memory.
        
        Args:
            event_type: Type of event (e.g., 'user_response_received')
            payload: Event data
            memory: Recent memory context
            
        Returns:
            Dictionary containing action and optional message
        """
        prompt = self._build_agent_decision_prompt(event_type, payload, memory)
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an autonomous productivity assistant. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            
            # Validate response structure
            if "action" not in result:
                result["action"] = "do_nothing"
            
            return result
            
        except Exception as e:
            print(f"LLM error in agent_decision: {e}")
            return {"action": "do_nothing"}
    
    def analyze_productivity(self, morning: str, midday: str, night: str) -> Dict[str, Any]:
        """
        Analyze productivity based on daily check-ins.
        
        Args:
            morning: Morning check-in response
            midday: Midday check-in response
            night: Night check-in response
            
        Returns:
            Dictionary containing score, recommended_action, and reason
        """
        prompt = self._build_productivity_analysis_prompt(morning, midday, night)
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a productivity analyst. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            
            # Validate response structure
            if "score" not in result:
                result["score"] = 5
            if "recommended_action" not in result:
                result["recommended_action"] = "Continue with your current approach."
            if "reason" not in result:
                result["reason"] = "Unable to analyze due to insufficient data."
            
            # Ensure score is within bounds
            result["score"] = max(1, min(10, int(result["score"])))
            
            return result
            
        except Exception as e:
            print(f"LLM error in analyze_productivity: {e}")
            return {
                "score": 5,
                "recommended_action": "Continue with your current approach.",
                "reason": "Analysis unavailable due to technical issues."
            }
    
    def _build_agent_decision_prompt(self, event_type: str, payload: Dict[str, Any], memory: str) -> str:
        """Build prompt for agent decision making."""
        return f"""You are an autonomous productivity assistant.

Event: {event_type}

Context:
{json.dumps(payload, indent=2)}

Recent memory:
{memory}

Choose an action.

Available actions:
- send_message
- trigger_analysis
- schedule_followup
- do_nothing

Return JSON:
{{
  "action": "string",
  "message": "optional string"
}}"""
    
    def _build_productivity_analysis_prompt(self, morning: str, midday: str, night: str) -> str:
        """Build prompt for productivity analysis."""
        return f"""You are a productivity analyst.

Morning intent:
{morning}

Midday status:
{midday}

Night reflection:
{night}

Evaluate productivity.

Return JSON:
{{
  "score": number from 1–10,
  "recommended_action": "string",
  "reason": "string"
}}"""
