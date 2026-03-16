"""Agent system for handling events and making decisions."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .database import SessionLocal
from .models import User, Checkin, ProductivityScore, Memory
from .llm import LLMService
from .bot import get_bot


class ProductivityAgent:
    """Agent that handles events and makes productivity decisions."""
    
    def __init__(self):
        """Initialize the agent."""
        self.llm = LLMService()
        self.bot = get_bot(self.handle_event)
    
    async def handle_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Handle incoming events and decide on actions.
        
        Args:
            event_type: Type of event (e.g., 'user_response_received')
            payload: Event data
        """
        try:
            # Get recent memory
            memory = self._get_recent_memory(payload.get("user_id"))
            
            # Get LLM decision
            decision = self.llm.agent_decision(event_type, payload, memory)
            
            # Execute action based on decision
            await self._execute_action(decision, payload)
            
            # Handle specific event types
            if event_type == "user_response_received" and payload.get("checkin_type") == "night":
                await self._handle_night_checkin_complete(payload)
        
        except Exception as e:
            print(f"Error handling event {event_type}: {e}")
    
    async def _execute_action(self, decision: Dict[str, Any], payload: Dict[str, Any]):
        """Execute the action decided by the LLM."""
        action = decision.get("action", "do_nothing")
        
        if action == "send_message":
            message = decision.get("message", "")
            if message:
                await self.bot.send_message(message)
        
        elif action == "trigger_analysis":
            await self._trigger_productivity_analysis(payload)
        
        elif action == "schedule_followup":
            message = decision.get("message", "Follow-up check-in scheduled.")
            if message:
                await self.bot.send_message(message)
        
        # do_nothing requires no action
    
    async def _handle_night_checkin_complete(self, payload: Dict[str, Any]):
        """Handle completion of night check-in by triggering productivity analysis."""
        user_id = payload.get("user_id")
        if not user_id:
            return
        
        # Get today's check-ins
        today = datetime.utcnow().date()
        db = SessionLocal()
        try:
            checkins = db.query(Checkin).filter(
                Checkin.user_id == user_id,
                Checkin.created_at >= today
            ).order_by(Checkin.created_at).all()
            
            # Extract responses by type
            morning_response = ""
            midday_response = ""
            night_response = payload.get("response", "")
            
            for checkin in checkins:
                if checkin.checkin_type == "morning" and checkin.response:
                    morning_response = checkin.response
                elif checkin.checkin_type == "midday" and checkin.response:
                    midday_response = checkin.response
            
            # Analyze productivity
            analysis = self.llm.analyze_productivity(
                morning_response, midday_response, night_response
            )
            
            # Store productivity score
            score = ProductivityScore(
                user_id=user_id,
                score=analysis["score"],
                recommended_action=analysis["recommended_action"],
                reason=analysis["reason"]
            )
            db.add(score)
            db.commit()
            
            # Send intervention if score is low
            if analysis["score"] <= 5:
                message = (
                    f"Today's productivity score: {analysis['score']}\n\n"
                    f"Recommendation:\n{analysis['recommended_action']}"
                )
                await self.bot.send_message(message)
            
            # Store memory
            memory_content = f"Productivity analysis: Score {analysis['score']}, {analysis['reason']}"
            memory = Memory(
                type="productive_day" if analysis["score"] > 7 else "blocker",
                content=memory_content
            )
            db.add(memory)
            db.commit()
        
        finally:
            db.close()
    
    async def _trigger_productivity_analysis(self, payload: Dict[str, Any]):
        """Trigger manual productivity analysis."""
        user_id = payload.get("user_id")
        if not user_id:
            return
        
        # Similar logic to night check-in analysis
        await self._handle_night_checkin_complete(payload)
    
    def _get_recent_memory(self, user_id: Optional[int]) -> str:
        """Get recent memory for context."""
        if not user_id:
            return "No recent memory available."
        
        db = SessionLocal()
        try:
            # Get recent memories from last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            memories = db.query(Memory).filter(
                Memory.created_at >= week_ago
            ).order_by(desc(Memory.created_at)).limit(5).all()
            
            if not memories:
                return "No recent memory available."
            
            memory_texts = []
            for memory in memories:
                memory_texts.append(f"{memory.type}: {memory.content}")
            
            return "\n".join(memory_texts)
        
        finally:
            db.close()


# Global agent instance
agent_instance = None


def get_agent() -> ProductivityAgent:
    """Get or create agent instance."""
    global agent_instance
    if agent_instance is None:
        agent_instance = ProductivityAgent()
    return agent_instance
