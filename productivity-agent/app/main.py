"""Main FastAPI application for the productivity agent."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from .config import Config
from .database import init_db
from .agent import get_agent
from .scheduler import get_scheduler
from .bot import get_bot


class CheckinRequest(BaseModel):
    """Request model for manual check-in trigger."""
    type: str  # morning, midday, night


# Global variables for services
agent = None
scheduler = None
bot = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    print("Starting Productivity Agent...")
    
    # Validate configuration
    Config.validate()
    
    # Initialize database
    init_db()
    print("Database initialized")
    
    # Initialize services
    global agent, scheduler, bot
    agent = get_agent()
    scheduler = get_scheduler(agent.handle_event)
    bot = get_bot(agent.handle_event)
    
    # Start Discord bot
    bot_task = asyncio.create_task(bot.start(Config.DISCORD_TOKEN))
    
    # Start scheduler
    scheduler.start()
    
    print("Productivity Agent started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down Productivity Agent...")
    scheduler.stop()
    await bot.close()
    print("Productivity Agent shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Productivity Agent",
    description="Autonomous Discord Productivity Assistant",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "running"}


@app.post("/trigger-checkin")
async def trigger_checkin(request: CheckinRequest):
    """Manually trigger a check-in."""
    if request.type not in ["morning", "midday", "night"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid check-in type. Must be 'morning', 'midday', or 'night'"
        )
    
    success = scheduler.trigger_checkin(request.type)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to trigger check-in"
        )
    
    return {"message": f"{request.type.capitalize()} check-in triggered successfully"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Productivity Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "trigger_checkin": "/trigger-checkin",
            "docs": "/docs"
        }
    }
