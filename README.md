# Budget-Friendly Product Explain Bot

## 🎯 Project Overview

An AI-powered full-stack web application that helps users make smarter purchasing decisions using Artificial Intelligence and Large Language Models (LLMs).

**Key Features:**
- 🤖 AI-powered product analysis
- 🔄 Product comparison
- 💡 Budget-based recommendations
- 📊 Category-specific insights
- 🎨 Modern, responsive UI
- ⚡ Real-time LLM analysis

---

## 📋 Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Usage](#usage)
7. [API Endpoints](#api-endpoints)
8. [Category Detection](#category-detection)
9. [Deployment](#deployment)

---

## ✨ Features

### Core Features
- **Product Analysis**: AI generates comprehensive product insights
- **Budget Analysis**: Analyzes product fit within user's budget
- **Category Detection**: Auto-detects product category from name
- **Product Comparison**: Compares two products side-by-side
- **Alternative Suggestions**: Recommends similar products
- **Price Estimation**: LLM-based price estimation for Indian market
- **Dynamic Scoring**: Category-specific scoring system
- **Professional UI**: Modern dark-mode responsive design

### AI Capabilities
- Large Language Model (LLM) powered by Groq API
- Llama 3.1 8B Instant model
- Structured JSON generation
- Prompt engineering for product analysis
- Category-specific feature extraction
- Comparative reasoning

### Supported Categories
1. **Phone** - Smartphones, mobile devices
2. **Laptop** - Personal computers, notebooks
3. **Smartwatch** - Wearable watches
4. **Headphones** - Audio devices, earbuds
5. **General** - Other products

---

## 🛠️ Tech Stack

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling, animations, dark mode
- **JavaScript (Vanilla)**: No frameworks, pure DOM manipulation
- **Responsive Design**: Mobile-first, works on all devices

### Backend
- **Python 3.11+**: Core language
- **Flask**: Lightweight web framework
- **Flask-CORS**: Cross-origin resource sharing
- **Groq API**: LLM provider (Llama 3.1)
- **BeautifulSoup4**: Web scraping for images
- **Requests**: HTTP client library
- **python-dotenv**: Environment variable management

### External APIs
- **Groq API**: Llama 3.1 8B Instant LLM
- **Bing Images**: Product image fetching

---

## 📁 Project Structure

```
Budget-Friendly Product Explain Bot/
│
├── backend/
│   ├── app.py                 # Flask app, routes
│   ├── llm.py                 # LLM integration, category detection
│   ├── .env                   # Environment variables (Groq API key)
│   └── .gitignore             # Git ignore rules
│
├── frontend/
│   ├── index.html             # Main HTML page
│   ├── script.js              # DOM manipulation, API calls
│   ├── style.css              # Styling and animations
│   └── assets/
│       └── no-image.png       # Fallback image
│
├── CATEGORY_DETECTION.md      # Category detection documentation
├── TESTING_GUIDE.sh           # Testing instructions
└── README.md                  # This file
```

---

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)
- Groq API key (get from https://console.groq.com)
- Modern web browser

### Step 1: Clone/Download Project
```bash
cd "Budget-Friendly Product Explain Bot"
```

### Step 2: Install Backend Dependencies
```bash
pip install flask flask-cors groq requests beautifulsoup4 python-dotenv
```

### Step 3: Create `.env` File
Create `backend/.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### Step 4: Verify Installation
```bash
python -m py_compile backend/app.py backend/llm.py
```

---

## ⚙️ Configuration

### Groq API Setup
1. Visit https://console.groq.com
2. Sign up / Log in
3. Create API key
4. Add to `backend/.env`

### Category Keywords (backend/llm.py)
Customize keyword detection:
```python
CATEGORY_KEYWORDS = {
    "phone": ["iphone", "samsung galaxy", "oneplus", ...],
    "laptop": ["victus", "pavilion", "macbook", ...],
    "watch": ["apple watch", "galaxy watch", ...],
    "headphones": ["airpods", "sony wh", "bose", ...],
}
```

---

## 📖 Usage

### Starting the Application

#### Terminal 1: Start Backend Server
```bash
cd "Budget-Friendly Product Explain Bot"
python backend/app.py
```
Server runs on: `http://127.0.0.1:5000`

#### Terminal 2: Open Frontend
```bash
# Navigate to frontend/index.html in your browser
# Or use a simple HTTP server:
cd frontend
python -m http.server 8000
# Open: http://localhost:8000
```

### Using the Application

1. **Enter Product Name**: Type product name (e.g., "iPhone 15 Pro Max")
2. **Select Category**: Choose from Phone, Laptop, Watch, Headphones, General
3. **Enter Budget**: Enter your budget in INR (e.g., 100000)
4. **Optional - Compare**: Enter another product for comparison
5. **Click Analyze**: Wait for AI analysis
6. **Review Results**: See comprehensive product analysis

### Features Displayed

- **📦 Overview**: Professional product summary
- **✨ Key Features**: Name-value feature pairs
- **👍 Pros & 👎 Cons**: Advantages and disadvantages
- **💰 Price Info**: Price in INR, budget percentage
- **📊 Scores**: Category-specific rating (0-10)
- **⚔️ Comparison**: Side-by-side comparison (if provided)
- **🛍️ Buying Advice**: Professional recommendation
- **🎯 Final Verdict**: Overall assessment
- **🔄 Alternatives**: Suggested alternatives
- **⚠️ Category Warning**: If category was auto-detected

---

## 🔌 API Endpoints

### POST /explain
Analyzes a product and generates AI insights.

**Request:**
```json
{
  "product": "HP Victus 16",
  "budget": "150000",
  "category": "laptop",
  "compare_with": "ASUS ROG Strix"
}
```

**Response:**
```json
{
  "detected_category": "laptop",
  "user_selected_category": "laptop",
  "category_warning": null,
  
  "overview": "Professional product summary...",
  "features": [
    {"name": "Processor", "value": "Intel Core i9"},
    ...
  ],
  "pros": ["Fast processing", "Great display", ...],
  "cons": ["Heavy weight", "Limited battery", ...],
  
  "scores": {
    "performance": "9",
    "graphics": "8",
    "display": "9",
    "battery": "5",
    "build_quality": "8",
    "value": "7"
  },
  
  "comparison": {
    "better_in": ["Better performance", "Better cooling"],
    "weaker_in": ["Heavier", "More expensive"],
    "summary": "HP Victus has better gaming performance..."
  },
  
  "best_for": "Gaming, content creation",
  "budget_fit": "Above budget but worth premium",
  "buying_advice": "Great for professional gaming...",
  "final_verdict": "Excellent gaming laptop for heavy workloads",
  "alternatives": ["ASUS ROG", "MSI Raider", "Alienware"],
  "bullets": ["Top gaming performance", "Premium build", "Good cooling"],
  
  "price": 149999,
  "currency": "INR",
  "image": "https://...",
  "compare_price": 160000
}
```

---

## 🤖 Category Detection

### How It Works

1. **Keyword Matching**: Product name matched against category keywords
2. **Exact Match Priority**: First matching category is selected
3. **Auto-Override**: If detected differs from user selection, warning shown
4. **Category-Specific Analysis**: LLM uses category context for features/scores

### Example: Wrong Category

- **User Input**: Product = "HP Victus", Category = "Smartwatch"
- **Detection**: "laptop" (keyword "victus" found)
- **Warning**: "Product appears to belong to Laptop category..."
- **Analysis**: Generated using laptop-specific criteria

For detailed info, see [CATEGORY_DETECTION.md](CATEGORY_DETECTION.md)

---

## 📊 Category Features & Scores

### Phone
**Features**: Processor, RAM, Storage, Camera Quality, Battery Life, Display Quality, Charging Speed, Build Quality, Software Experience, 5G Connectivity
**Scores**: Performance, Camera, Battery, Display, Charging, Value

### Laptop
**Features**: Processor, RAM, SSD Storage, Graphics Card, Display Quality, Battery Backup, Build Quality, Cooling System, Keyboard Quality, Port Selection
**Scores**: Performance, Graphics, Display, Battery, Build Quality, Value

### Smartwatch
**Features**: Health Tracking, Heart Rate Accuracy, Sleep Tracking, Battery Life, Display Quality, Water Resistance, GPS Accuracy, Comfort, Calling Features, Smart Features
**Scores**: Health Tracking, Battery, Display, Accuracy, Comfort, Value

### Headphones
**Features**: Sound Quality, Bass, Noise Cancellation, Battery Life, Comfort, Microphone Quality, Build Quality, Connectivity, Latency, Portability
**Scores**: Sound, Bass, ANC, Battery, Comfort, Value

### General Products
**Features**: Quality, Durability, Safety, Ease Of Use, Design, Reliability, Material Quality, Maintenance, Brand Trust, Value For Money
**Scores**: Quality, Durability, Safety, Reliability, Usability, Value

---

## 🚀 Deployment

### Local Deployment (Development)
```bash
cd "Budget-Friendly Product Explain Bot"
python backend/app.py
# Access at http://127.0.0.1:5000
```

### Production Considerations

1. **Use WSGI Server** (not Flask dev server)
   ```bash
   pip install gunicorn
   gunicorn backend.app:app --bind 0.0.0.0:8000
   ```

2. **Environment Variables**: Use `.env` file (already set up)

3. **CORS Configuration**: Update allowed origins in `backend/app.py`
   ```python
   CORS(app, origins=["https://yourdomain.com"])
   ```

4. **Error Handling**: Implement proper error logging

5. **Rate Limiting**: Add rate limiting for LLM API calls

6. **Caching**: Cache LLM responses for common products

### Docker Deployment (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD ["gunicorn", "backend.app:app", "--bind", "0.0.0.0:8000"]
```

Build and run:
```bash
docker build -t product-analyzer .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key product-analyzer
```

---

## 🧪 Testing

Run comprehensive tests:
```bash
bash TESTING_GUIDE.sh
```

Quick test:
```bash
curl -X POST http://127.0.0.1:5000/explain \
  -H "Content-Type: application/json" \
  -d '{
    "product": "iPhone 15",
    "budget": "100000",
    "category": "phone"
  }'
```

---

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not found"
**Solution**: Create `backend/.env` with your API key

### Issue: "Port 5000 already in use"
**Solution**: Kill process or use different port:
```bash
python backend/app.py --port 5001
```

### Issue: Image not loading
**Solution**: System falls back to `assets/no-image.png`

### Issue: Slow LLM responses
**Solution**: Groq API might be under load, try again later

---

## 📈 Performance Metrics

- **Response Time**: 3-10 seconds (includes LLM inference)
- **Image Fetch**: <2 seconds
- **Price Estimation**: <3 seconds
- **Total**: ~5-15 seconds per analysis

---

## 📝 Future Enhancements

- [ ] Database for storing product analyses
- [ ] User accounts and history
- [ ] Advanced filters and sorting
- [ ] Mobile app (React Native)
- [ ] ML-based price prediction
- [ ] Sentiment analysis from reviews
- [ ] Real-time price tracking
- [ ] Browser extensions
- [ ] Voice search capability
- [ ] Multi-language support

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👨‍💻 Developer Notes

### Code Quality
- Clean, well-commented code
- Professional error handling
- Responsive UI/UX design
- Production-ready structure

### Performance Optimizations
- Parallel image/price fetching
- Efficient keyword matching
- JSON response caching ready
- Minimal DOM manipulation

### Security Best Practices
- Environment variables for secrets
- CORS configuration
- Input validation
- Error messages without sensitive info

---

## 📞 Support

For issues or questions:
1. Check [CATEGORY_DETECTION.md](CATEGORY_DETECTION.md) for feature details
2. Review [TESTING_GUIDE.sh](TESTING_GUIDE.sh) for test cases
3. Check console logs in browser/terminal
4. Verify Groq API key and internet connection

---

## 🎉 Acknowledgments

- Groq API for Llama 3.1 LLM access
- Bing Images for product images
- Flask framework
- Open source community

---

**Last Updated**: June 2026
**Version**: 2.0 (Category Detection)
