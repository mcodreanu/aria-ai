# Aria AI Assistant

Aria is a powerful AI assistant that combines various AI capabilities including natural language processing, voice commands, and memory retention to provide a personalized assistant experience.

## Features

- 🧠 **Memory Retention**: Remembers past conversations for contextual responses
- 🗣️ **Voice Commands**: Supports voice activation and speech recognition
- 📱 **WhatsApp Integration**: Send messages through WhatsApp
- 📧 **Email Support**: Send emails through voice commands
- 🌤️ **Weather Updates**: Get real-time weather information
- 📰 **News Updates**: Fetch latest news headlines
- 🎵 **Media Control**: Play music and YouTube videos
- 🔊 **Volume Control**: Adjust system volume through voice commands
- 🌐 **Internet Tools**: Speed test, IP lookup, and web searches
- 📝 **Text Generation**: Powered by Google's Gemini AI
- 🖼️ **Image Generation**: Create images from text descriptions

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Required API keys (Gemini, OpenWeather, News API)
- Gmail account (for email features)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aria-ai.git
cd aria-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your actual values:
- API keys (Gemini, OpenWeather, News)
- Email credentials
- Database configuration

## Configuration

The following environment variables are required:

### User Configuration
- `USER`: Your name
- `ASSISTANT_NAME`: Name for the AI (default: "Aria")

### Email Configuration
- `EMAIL`: Your Gmail address
- `PASSWORD`: Gmail app password
- `SMTP_URL`: SMTP server (default: smtp.gmail.com)
- `SMTP_PORT`: SMTP port (default: 587)

### API Keys
- `GEMINI_API_KEY`: Google Gemini API key
- `NEWS_FETCH_API_KEY`: NewsAPI key
- `WEATHER_FETCH_API_KEY`: OpenWeather API key

### Database Configuration
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host (default: localhost)
- `DB_PORT`: Database port (default: 5432)

## Usage

1. Start the assistant:
```bash
python run.py
```

2. Voice Commands:
- Say "Hey Aria" to activate voice commands
- Wait for the activation sound
- Speak your command

3. Available Commands:
- Weather: "What's the weather in [city]?"
- News: "Tell me the latest news"
- Email: "Send email"
- WhatsApp: "Send WhatsApp message"
- Music: "Play [song name]"
- Volume: "Set volume to [level]"
- Time: "What's the time?"
- Internet: "Speed test"
- Search: "Search on Wikipedia [query]"
- General chat: Any other conversation

4. Memory Features:
- `/recall [topic]`: Recall previous conversations
- `/forget`: Remove last conversation
- `/memorize [information]`: Store specific information

## Database Setup

1. Create PostgreSQL database:
```sql
CREATE DATABASE memory_agent;
```

2. Tables will be automatically created on first run

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Security Notes

- Never commit your `.env` file
- Use app-specific passwords for Gmail
- Keep API keys secure
- Regularly update dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details
