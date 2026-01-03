# 🎙️ AI Podcast Generator

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.52-red)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

An AI-powered application that automatically converts blog posts into podcast episodes. Simply provide a blog URL, and the system will scrape the content, generate a concise summary, and create an audio podcast using text-to-speech technology.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Usage](#usage)
- [API Keys](#api-keys)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ Features

- 🌐 **Web Scraping**: Extracts clean content from any blog URL using Firecrawl
- 🤖 **AI Summarization**: Generates concise 100-200 word summaries optimized for podcasts
- 🎵 **Text-to-Speech**: Converts summaries into high-quality audio using ElevenLabs
- 🔒 **Secure**: Uses Streamlit secrets for API key management
- 🚀 **Fast**: Generates podcasts in 5-10 seconds
- 🐳 **Containerized**: Runs in Docker for consistent deployment
- 🎨 **User-Friendly**: Simple Gradio interface with authentication

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                     (Gradio Web Interface)                      │
│                   Port: 7777 (Auth Protected)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Blog URL Input
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Application Layer                          │
│                         (app.py)                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Process Orchestration                        │ │
│  │  • Validate Input                                         │ │
│  │  • Coordinate Services                                    │ │
│  │  • Handle Errors                                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ├──────────────┬──────────────┐
                             ▼              ▼              ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   Scraping       │  │  Summarization   │  │  Audio Gen       │
│   Service        │  │  Service         │  │  Service         │
│                  │  │                  │  │                  │
│  Firecrawl API   │  │  Groq LLM        │  │  ElevenLabs      │
│  • Extract HTML  │  │  • llama-3.1-8b  │  │  • Flash v2.5    │
│  • Parse Content │  │  • 300 tokens    │  │  • Voice: George │
│  • Clean Text    │  │  • Temp: 0.7     │  │  • MP3 Output    │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                     │                      │
         │ Markdown            │ Summary              │ Audio File
         ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Output Layer                            │
│                                                                 │
│  • Blog Summary (Text)                                          │
│  • Podcast Audio (MP3)                                          │
│  • Status Messages                                              │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User Input
   └─> Blog URL entered in Gradio interface

2. Web Scraping (Firecrawl)
   └─> URL → Firecrawl API → Markdown content (clean text)

3. Content Processing
   └─> Truncate to 3000 chars (~750 tokens) to fit free tier limits

4. AI Summarization (Groq)
   └─> Content → Llama 3.1 8B → 100-200 word summary

5. Audio Generation (ElevenLabs)
   └─> Summary (first 350 chars) → TTS → MP3 file

6. Response
   └─> Display summary + audio player in UI
```

---

## 🛠️ Tech Stack

### Core Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.11 | Main programming language |
| **Framework** | Gradio 6.2.0 | Web UI framework |
| **Deployment** | Docker | Containerization |
| **Platform** | Streamlit Cloud | Hosting platform |

### AI/ML Services

| Service | Model/API | Function |
|---------|-----------|----------|
| **Firecrawl** | Web Scraper | Extracts clean content from blogs |
| **Groq** | Llama 3.1 8B Instant | Generates summaries (6000 TPM free tier) |
| **ElevenLabs** | Flash v2.5 | Converts text to speech |

### Key Libraries

```
gradio==6.2.0           # Web interface
groq==1.0.0             # LLM API client
firecrawl-py==4.12.0    # Web scraping
elevenlabs==2.27.0      # Text-to-speech
streamlit               # Secret management
python-dotenv==1.1.1    # Environment variables
```

---

## 🔄 How It Works

### Step-by-Step Process

#### 1. **Content Extraction** (Firecrawl)
```python
scraper = FirecrawlApp(api_key=firecrawl_key)
scraped_result = scraper.scrape_url(url)
content = scraped_result.get('markdown', '')
```
- Scrapes blog URL
- Removes navigation, ads, footers
- Returns clean markdown content

#### 2. **Content Optimization**
```python
max_chars = 3000
if len(content) > max_chars:
    content = content[:max_chars] + "..."
```
- Truncates to 3000 characters
- Ensures we stay within Groq's 6000 TPM free tier limit
- Maintains content quality while fitting constraints

#### 3. **AI Summarization** (Groq)
```python
client = Groq(api_key=groq_key)
chat_completion = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a content analyst..."},
        {"role": "user", "content": f"Summarize: {content}"}
    ],
    model="llama-3.1-8b-instant",
    temperature=0.7,
    max_tokens=300
)
```
- Uses Llama 3.1 8B model
- Optimized for podcast-style summaries
- Temperature 0.7 for balanced creativity

#### 4. **Audio Generation** (ElevenLabs)
```python
client = ElevenLabs(api_key=elevenlabs_key)
response = client.text_to_speech.convert(
    text=summary[:350],
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George voice
    model_id="eleven_flash_v2_5"
)
```
- Converts first 350 characters to audio
- Uses Flash v2.5 model (fast generation)
- Outputs MP3 format at 44.1kHz

---

## 📦 Installation

### Prerequisites

- Python 3.11+
- Docker (for containerized deployment)
- API Keys (Groq, Firecrawl, ElevenLabs)

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/podcast-generator.git
cd podcast-generator
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create `.env` file**
```bash
GROQ_API_KEY=your_groq_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

4. **Run the application**
```bash
python app.py
```

5. **Access the app**
- Open browser: `http://localhost:7777`
- Login: `aipodcast` / `Welcome@2026`

---

## 🐳 Docker Deployment

### Build and Run

```bash
# Build Docker image
docker build -t podcast-generator .

# Run container
docker run -it -p 7777:7777 --env-file .env podcast-generator
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  podcast-generator:
    build: .
    ports:
      - "7777:7777"
    env_file:
      - .env
    restart: unless-stopped
```

Run with:
```bash
docker-compose up -d
```

---

## ☁️ Streamlit Cloud Deployment

### 1. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Connect to Streamlit

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository
4. Set main file: `app.py`

### 3. Configure Secrets

In Streamlit Cloud dashboard:
- Go to **Settings** → **Secrets**
- Add:

```toml
GROQ_API_KEY = "gsk_your_groq_key_here"
FIRECRAWL_API_KEY = "fc-your_firecrawl_key_here"
ELEVENLABS_API_KEY = "your_elevenlabs_key_here"
```

### 4. Deploy

- Click "Deploy"
- App will be live at `https://your-app-name.streamlit.app`

---

## 🔑 API Keys

### Groq (Free Tier)
- **Website**: [console.groq.com](https://console.groq.com)
- **Sign up**: Free account
- **Limits**: 6,000 tokens/minute
- **Model**: `llama-3.1-8b-instant`

### Firecrawl
- **Website**: [firecrawl.dev](https://firecrawl.dev)
- **Sign up**: Free tier available
- **Limits**: Check current pricing
- **Purpose**: Web scraping

### ElevenLabs
- **Website**: [elevenlabs.io](https://elevenlabs.io)
- **Sign up**: Free tier available
- **Limits**: 10,000 characters/month (free)
- **Voice**: George (JBFqnCBsd6RMkjVDRZzb)

---

## 📁 Project Structure

```
podcast-generator/
├── app.py                  # Main application (Gradio interface)
├── blog_summarizer.py      # Core logic (scraping + summarization)
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container configuration
├── README.md              # This file
├── .env.example           # Environment variables template
└── .gitignore            # Git ignore rules

Generated Files:
├── podcast_episode.mp3    # Generated audio file
└── .streamlit/
    └── secrets.toml       # Streamlit secrets (local)
```

---

## 🎯 Usage

### Web Interface

1. **Access the app**
   - Local: `http://localhost:7777`
   - Cloud: Your Streamlit URL

2. **Login**
   - Username: `aipodcast`
   - Password: `Welcome@2026`

3. **Generate Podcast**
   - Enter blog URL
   - Click "Generate Podcast"
   - Wait 5-10 seconds
   - View summary + play audio

### API Usage (Optional)

```python
from blog_summarizer import summarize_blog

# Generate summary
url = "https://example.com/blog-post"
summary = summarize_blog(url)
print(summary)
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM | Yes |
| `FIRECRAWL_API_KEY` | Firecrawl API key for scraping | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key for TTS | Yes |

### Customization

#### Change Voice
Edit `app.py`:
```python
voice_id="JBFqnCBsd6RMkjVDRZzb"  # Change to your preferred voice ID
```

#### Adjust Summary Length
Edit `blog_summarizer.py`:
```python
max_tokens=300  # Increase/decrease for longer/shorter summaries
```

#### Change Model
Edit `blog_summarizer.py`:
```python
model="llama-3.1-8b-instant"  # Try other Groq models
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Errors
```
Error: API keys not configured
```
**Solution**: Add API keys to Streamlit secrets or `.env` file

#### 2. Token Limit Exceeded
```
Error: Request too large... Limit 6000, Requested 12864
```
**Solution**: Already handled by content truncation (3000 chars)

#### 3. Firecrawl Scraping Fails
```
Error scraping blog with Firecrawl
```
**Solution**: 
- Check if URL is accessible
- Verify Firecrawl API key
- Try a different blog URL

#### 4. Audio Generation Fails
```
Summary generated but audio failed
```
**Solution**: 
- Check ElevenLabs API key
- Verify you haven't exceeded free tier limits
- Check summary length (should be ≤350 chars for audio)

### Debug Mode

Enable detailed logging:
```python
# In blog_summarizer.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Average Processing Time** | 5-10 seconds |
| **Scraping Time** | 1-2 seconds |
| **Summary Generation** | 2-3 seconds |
| **Audio Generation** | 2-5 seconds |
| **Memory Usage** | ~200 MB |
| **Docker Image Size** | ~1.2 GB |

---

## 🚀 Future Enhancements

- [ ] Support for multiple languages
- [ ] Batch processing of URLs
- [ ] Custom voice selection
- [ ] Summary length customization
- [ ] Export to various audio formats
- [ ] Integration with podcast platforms
- [ ] Scheduled podcast generation
- [ ] RSS feed generation

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Your Name** - *Initial work*

---

## 🙏 Acknowledgments

- [Groq](https://groq.com) - Fast LLM inference
- [Firecrawl](https://firecrawl.dev) - Web scraping API
- [ElevenLabs](https://elevenlabs.io) - Text-to-speech technology
- [Gradio](https://gradio.app) - ML web interfaces
- [Streamlit](https://streamlit.io) - Deployment platform

---

## 📧 Contact

- **Project Link**: [https://github.com/yourusername/podcast-generator](https://github.com/yourusername/podcast-generator)
- **Email**: your.email@example.com

---

## 🔗 Links

- [Live Demo](https://your-app-name.streamlit.app)
- [Documentation](https://github.com/yourusername/podcast-generator/wiki)
- [Report Bug](https://github.com/yourusername/podcast-generator/issues)
- [Request Feature](https://github.com/yourusername/podcast-generator/issues)

---

**Made with ❤️ and AI**
