# Discord Productivity Agent

An autonomous AI productivity assistant that uses Discord as its interface to provide scheduled check-ins, productivity analysis, and intelligent interventions.

## Features

- **Scheduled Check-ins**: Automated daily check-ins at 9:00 AM, 1:00 PM, and 9:00 PM
- **Event-Driven Agent**: Responds dynamically to user interactions using LLM decision making
- **Productivity Analysis**: AI-powered analysis of daily productivity with scoring
- **Intelligent Interventions**: Automatic recommendations when productivity is low
- **SQLite Database**: Stores user interactions, check-ins, and productivity scores
- **FastAPI Server**: REST API for health checks and manual triggers

## Architecture

The system operates as an event-driven agent:

1. **Scheduler** triggers Discord check-ins at scheduled times
2. **Discord Bot** sends prompts and captures user responses
3. **Agent System** processes events and makes decisions using LLM
4. **LLM Layer** provides intelligent decision making and productivity analysis
5. **Database** stores all interactions and history

## Setup

### Prerequisites

- Python 3.11+
- Discord Bot Token
- OpenAI API Key

### Installation

1. Clone the repository and navigate to the project directory:
```bash
cd productivity-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_target_channel_id
OPENAI_API_KEY=your_openai_api_key
```

### Discord Bot Setup

1. Create a new Discord application at https://discord.com/developers/applications
2. Create a bot user and get the token
3. Enable Message Content Intent in the bot settings
4. Invite the bot to your server with necessary permissions
5. Get the channel ID where you want the bot to operate

### Running the Application

Start the productivity agent:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will:
- Initialize the SQLite database
- Start the Discord bot
- Begin the scheduler for daily check-ins
- Launch the FastAPI server

## API Endpoints

### Health Check
```
GET /health
```
Returns the current status of the application.

### Manual Check-in Trigger
```
POST /trigger-checkin
Content-Type: application/json

{
  "type": "morning" | "midday" | "night"
}
```
Manually triggers a check-in of the specified type.

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation.

## Check-in Types

### Morning (9:00 AM)
```
Good morning.

What are the 3 most important things you must complete today?
```

### Midday (1:00 PM)
```
Quick check-in.

Have you started your primary task yet?

1) Yes
2) No
3) Stuck
```

### Night (9:00 PM)
```
End of day reflection.

What did you complete today?
What blocked you?
What should be tomorrow's first action?
```

## Productivity Scoring

After the night check-in, the system analyzes all daily responses and generates:

- **Productivity Score** (1-10): Overall productivity rating
- **Recommended Action**: Personalized recommendations
- **Reason**: Explanation for the score

If the score is 5 or lower, the bot automatically sends an intervention message with recommendations.

## Database Schema

The system uses SQLite with the following tables:

- **users**: Stores Discord user information
- **checkins**: Records all check-in messages and responses
- **productivity_scores**: Stores daily productivity analysis results
- **memories**: Stores behavioral patterns and summaries

## Development

### Project Structure
```
productivity-agent/
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Configuration management
│   ├── database.py      # Database setup
│   ├── models.py        # SQLAlchemy models
│   ├── bot.py           # Discord bot implementation
│   ├── scheduler.py     # APScheduler setup
│   ├── agent.py         # Event-driven agent system
│   └── llm.py           # OpenAI integration
├── data/
│   └── agent.db         # SQLite database
├── requirements.txt
├── .env.example
└── README.md
```

### Code Quality

- Type hints throughout the codebase
- Comprehensive docstrings
- Modular design with clear separation of concerns
- Error handling and logging
- Clean, readable code following Python best practices

## MVP Scope

This is a minimum viable product focusing on the core agent loop. Future versions may include:

- Multi-user support
- Analytics dashboard
- Calendar integrations
- Advanced memory summarization
- Additional communication platforms

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**: Ensure the bot has message content intent enabled and proper channel permissions
2. **Scheduler not working**: Check timezone configuration and system time
3. **LLM errors**: Verify OpenAI API key is valid and has sufficient credits
4. **Database issues**: Ensure the `data/` directory exists and is writable

### Logs

The application prints status messages to stdout. For production deployment, consider implementing proper logging.

## License

This project is provided as-is for educational and development purposes.
