"""Discord bot for productivity check-ins and user interactions."""

import discord
from discord.ext import commands
from typing import Optional, Callable, Any
from sqlalchemy.orm import Session
from .config import Config
from .database import get_db, SessionLocal
from .models import User, Checkin


class ProductivityBot(commands.Bot):
    """Discord bot for productivity management."""
    
    def __init__(self, agent_handler: Optional[Callable] = None):
        """Initialize the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        
        self.agent_handler = agent_handler
        self.pending_checkins = {}  # Store pending check-ins by user_id
    
    async def on_ready(self):
        """Called when bot is ready."""
        print(f"Bot logged in as {self.user}")
        print(f"Bot ID: {self.user.id}")
    
    async def on_message(self, message: discord.Message):
        """Handle incoming messages."""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Only process messages in the configured channel
        if message.channel.id != Config.DISCORD_CHANNEL_ID:
            return
        
        # Check if this is a response to a pending check-in
        user_id = str(message.author.id)
        if user_id in self.pending_checkins:
            await self._handle_checkin_response(message)
        else:
            # Process commands
            await self.process_commands(message)
    
    async def _handle_checkin_response(self, message: discord.Message):
        """Handle user response to a check-in."""
        user_id = str(message.author.id)
        checkin_data = self.pending_checkins.pop(user_id)
        
        # Store response in database
        db = SessionLocal()
        try:
            # Get or create user
            user = db.query(User).filter(User.discord_id == user_id).first()
            if not user:
                user = User(discord_id=user_id)
                db.add(user)
                db.commit()
                db.refresh(user)
            
            # Update check-in with response
            checkin = db.query(Checkin).filter(
                Checkin.id == checkin_data["checkin_id"]
            ).first()
            
            if checkin:
                checkin.response = message.content
                db.commit()
                
                # Send event to agent
                if self.agent_handler:
                    await self.agent_handler(
                        "user_response_received",
                        {
                            "user_id": user.id,
                            "discord_id": user_id,
                            "checkin_type": checkin.checkin_type,
                            "response": message.content,
                            "discord_message_id": str(message.id)
                        }
                    )
        
        finally:
            db.close()
    
    async def send_checkin(self, checkin_type: str, target_user_id: Optional[str] = None):
        """Send a check-in prompt to the configured channel."""
        channel = self.get_channel(Config.DISCORD_CHANNEL_ID)
        if not channel:
            print(f"Channel {Config.DISCORD_CHANNEL_ID} not found")
            return
        
        prompt = self._get_checkin_prompt(checkin_type)
        if not prompt:
            return
        
        try:
            # Store check-in in database
            db = SessionLocal()
            try:
                # Get or create user
                user = None
                if target_user_id:
                    user = db.query(User).filter(User.discord_id == target_user_id).first()
                    if not user:
                        user = User(discord_id=target_user_id)
                        db.add(user)
                        db.commit()
                        db.refresh(user)
                
                # Create check-in record
                checkin = Checkin(
                    user_id=user.id if user else None,
                    checkin_type=checkin_type,
                    message=prompt
                )
                db.add(checkin)
                db.commit()
                db.refresh(checkin)
                
                # Store pending check-in for response tracking
                if target_user_id:
                    self.pending_checkins[target_user_id] = {
                        "checkin_id": checkin.id,
                        "checkin_type": checkin_type
                    }
                
                # Send message
                message = await channel.send(prompt)
                
                # Send event to agent
                if self.agent_handler:
                    await self.agent_handler(
                        "checkin_sent",
                        {
                            "checkin_type": checkin_type,
                            "message": prompt,
                            "discord_message_id": str(message.id),
                            "user_id": user.id if user else None
                        }
                    )
            
            finally:
                db.close()
        
        except discord.Forbidden:
            print("Bot doesn't have permission to send messages in the channel")
        except Exception as e:
            print(f"Error sending check-in: {e}")
    
    async def send_message(self, content: str, target_user_id: Optional[str] = None):
        """Send a message to the configured channel."""
        channel = self.get_channel(Config.DISCORD_CHANNEL_ID)
        if not channel:
            print(f"Channel {Config.DISCORD_CHANNEL_ID} not found")
            return
        
        try:
            await channel.send(content)
        except discord.Forbidden:
            print("Bot doesn't have permission to send messages in the channel")
        except Exception as e:
            print(f"Error sending message: {e}")
    
    def _get_checkin_prompt(self, checkin_type: str) -> Optional[str]:
        """Get the prompt for a specific check-in type."""
        prompts = {
            "morning": "Good morning.\n\nWhat are the 3 most important things you must complete today?",
            "midday": "Quick check-in.\n\nHave you started your primary task yet?\n\n1) Yes\n2) No\n3) Stuck",
            "night": "End of day reflection.\n\nWhat did you complete today?\nWhat blocked you?\nWhat should be tomorrow's first action?"
        }
        return prompts.get(checkin_type)


# Global bot instance
bot_instance = None


def get_bot(agent_handler: Optional[Callable] = None) -> ProductivityBot:
    """Get or create bot instance."""
    global bot_instance
    if bot_instance is None:
        bot_instance = ProductivityBot(agent_handler)
    return bot_instance
