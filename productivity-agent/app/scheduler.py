"""Scheduler for daily productivity check-ins."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Optional, Callable
from .config import Config
from .bot import get_bot


class CheckinScheduler:
    """Scheduler for managing daily check-ins."""
    
    def __init__(self, agent_handler: Optional[Callable] = None):
        """Initialize the scheduler."""
        self.scheduler = AsyncIOScheduler(timezone=Config.SCHEDULER_TIMEZONE)
        self.agent_handler = agent_handler
        self.bot = get_bot(agent_handler)
    
    def start(self):
        """Start the scheduler."""
        # Schedule morning check-in at 9:00 AM
        self.scheduler.add_job(
            func=self._morning_checkin,
            trigger=CronTrigger(hour=9, minute=0),
            id="morning_checkin",
            name="Morning Productivity Check-in",
            replace_existing=True
        )
        
        # Schedule midday check-in at 1:00 PM
        self.scheduler.add_job(
            func=self._midday_checkin,
            trigger=CronTrigger(hour=13, minute=0),
            id="midday_checkin",
            name="Midday Productivity Check-in",
            replace_existing=True
        )
        
        # Schedule night check-in at 9:00 PM
        self.scheduler.add_job(
            func=self._night_checkin,
            trigger=CronTrigger(hour=21, minute=0),
            id="night_checkin",
            name="Night Productivity Check-in",
            replace_existing=True
        )
        
        self.scheduler.start()
        print("Scheduler started with daily check-ins at 9:00 AM, 1:00 PM, and 9:00 PM")
    
    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        print("Scheduler stopped")
    
    async def _morning_checkin(self):
        """Send morning check-in."""
        await self.bot.send_checkin("morning")
    
    async def _midday_checkin(self):
        """Send midday check-in."""
        await self.bot.send_checkin("midday")
    
    async def _night_checkin(self):
        """Send night check-in."""
        await self.bot.send_checkin("night")
    
    def trigger_checkin(self, checkin_type: str):
        """Manually trigger a check-in for testing."""
        if checkin_type in ["morning", "midday", "night"]:
            job_func = getattr(self, f"_{checkin_type}_checkin")
            self.scheduler.add_job(
                func=job_func,
                trigger="date",
                id=f"manual_{checkin_type}",
                name=f"Manual {checkin_type} Check-in"
            )
            return True
        return False


# Global scheduler instance
scheduler_instance = None


def get_scheduler(agent_handler: Optional[Callable] = None) -> CheckinScheduler:
    """Get or create scheduler instance."""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = CheckinScheduler(agent_handler)
    return scheduler_instance
