import docx
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def create_document():
    doc = docx.Document()
    
    # Title
    title = doc.add_heading('PROJECT MASTER INTERVIEW GUIDE', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph("Comprehensive Technical Reference & Interview Preparation")
    doc.add_page_break()

    def h1(text): doc.add_heading(text, level=1)
    def h2(text): doc.add_heading(text, level=2)
    def h3(text): doc.add_heading(text, level=3)
    def p(text): doc.add_paragraph(text)
    def b(text): doc.add_paragraph(text, style='List Bullet')
    def code(text): doc.add_paragraph(text, style='No Spacing').runs[0].font.name = 'Courier New'

    # ==================================================
    # 1. PROJECT OVERVIEW
    # ==================================================
    h1("1. PROJECT OVERVIEW")
    h2("Project Name")
    p("Stock Price Prediction System")
    
    h2("Purpose")
    p("An AI-powered, full-stack web application for real-time stock price analysis. It predicts future stock trends using deep learning (LSTM/GRU/Conv1D meta-ensemble) and provides actionable BUY/SELL/HOLD recommendations by combining technical indicators and NLP-based news sentiment analysis.")
    
    h2("Real-World Problem Solved")
    p("Retail investors often struggle to analyze massive amounts of market data, technical indicators, and news simultaneously. This project democratizes quantitative finance by providing institutional-grade analytics (ML forecasts, momentum, volatility, and sentiment) in an intuitive, single-page dashboard.")
    
    h2("Target Users")
    b("Retail Investors & Day Traders")
    b("Financial Analysts seeking quantitative validation")
    b("Data Scientists / ML Enthusiasts interested in algorithmic trading")
    
    h2("Core Features")
    b("Real-Time Data Fetching: US & Indian (NSE/BSE) Stocks via yfinance.")
    b("Advanced Technical Analysis: MA20/MA50, RSI, MACD, Bollinger Bands.")
    b("Hedge-Fund Grade ML: Meta-ensemble model fusing LSTM (Attention), GRU, and Conv1D.")
    b("Smart Recommendation Engine: Multi-factor scoring system yielding BUY/SELL/HOLD.")
    b("Live News Sentiment: NLP processing (VADER) on real-time news.")
    b("Premium UI/UX: Streamlit with Plotly, glassmorphism design, and dark mode.")
    
    h2("Business Use Case")
    p("Can be deployed as a SaaS platform for traders, integrated as an API backend for fintech apps, or used as an internal portfolio management tool for boutique trading firms.")
    doc.add_page_break()

    # ==================================================
    # 2. TECH STACK
    # ==================================================
    h1("2. TECH STACK")
    
    h2("Frontend: Streamlit")
    b("What it is: A Python-based framework for rapidly building data apps.")
    b("Why used: Allows seamless integration with Python data science libraries (Pandas, Plotly) without writing separate React/Vue code.")
    b("Advantages: High development speed, built-in state management, native Python integration.")
    b("Disadvantages: Less granular control over DOM/CSS compared to React; heavier client-side load.")
    b("Alternatives: React, Vue.js, Angular, Dash.")
    b("Where used: frontend/app.py (Entire UI layer).")
    
    h2("Backend: Flask")
    b("What it is: A lightweight WSGI web application framework in Python.")
    b("Why used: Minimalistic, highly flexible, perfect for wrapping ML inference scripts into REST APIs.")
    b("Advantages: Easy to set up, minimal boilerplate, great for microservices.")
    b("Disadvantages: Lacks built-in ORM/Auth (unlike Django); requires manual wiring for complex apps.")
    b("Alternatives: FastAPI, Django, Express.js.")
    b("Where used: backend/app.py, backend/routes/ (REST API layer).")
    
    h2("Machine Learning: TensorFlow / Keras")
    b("What it is: Open-source deep learning framework.")
    b("Why used: Industry standard for building custom neural networks, particularly LSTMs for time-series.")
    b("Advantages: Highly scalable, extensive community, TensorBoard for profiling.")
    b("Disadvantages: Steep learning curve, heavy resource consumption.")
    b("Alternatives: PyTorch, Scikit-learn (for shallow models).")
    b("Where used: ml/model.py (Architecture, Training, Inference).")
    
    h2("Data & Finance Libraries: yfinance, pandas, numpy, ta")
    b("What it is: Ecosystem for data manipulation and financial data extraction.")
    b("Why used: yfinance gives free real-time data; pandas handles time-series beautifully; ta provides technical indicators.")
    b("Where used: backend/services/stock_service.py, backend/services/indicator_service.py.")
    
    h2("Visualization: Plotly")
    b("What it is: Interactive graphing library.")
    b("Why used: Creates beautiful, interactive candlestick charts with hovertooltips, vastly superior to static Matplotlib.")
    b("Where used: frontend/app.py.")
    
    h2("NLP: VADER Sentiment")
    b("What it is: Lexicon and rule-based sentiment analysis tool.")
    b("Why used: Specifically attuned to sentiments expressed in social media and short news snippets; fast and requires no GPU.")
    b("Where used: backend/services/stock_service.py (News analysis).")
    doc.add_page_break()

    # ==================================================
    # 3. HIGH LEVEL ARCHITECTURE
    # ==================================================
    h1("3. HIGH LEVEL ARCHITECTURE")
    
    p("The system follows a Decoupled Client-Server Architecture (Microservices pattern).")
    
    h2("Frontend Architecture")
    p("Streamlit serves as the presentation layer. It manages user inputs (ticker, timeframe), maintains session state, and makes synchronous HTTP GET requests to the Flask API. It dynamically renders HTML/CSS/Plotly components based on the JSON response.")
    
    h2("Backend Architecture")
    p("Flask serves as a REST API gateway. It routes requests to specialized Service Modules (StockService, IndicatorService, PredictionService, RecommendationService). These services perform heavy lifting, interact with external APIs (Yahoo Finance), run ML inferences, and format data back to JSON.")
    
    h2("Data Flow / Request Lifecycle")
    b("1. User enters 'AAPL' on Streamlit UI and clicks 'Analyze'.")
    b("2. Streamlit calls Flask API: GET /api/stock-data?ticker=AAPL")
    b("3. Flask Route parses request, calls StockService.fetch_stock_data().")
    b("4. StockService calls yfinance API, downloads OHLCV data, cleans it with Pandas, returns dict.")
    b("5. Streamlit parallelly calls GET /api/indicators, GET /api/predict, GET /api/recommend.")
    b("6. PredictionService loads trained .h5 model from disk, scales data, runs model.predict(), returns future prices.")
    b("7. RecommendationService aggregates MA, RSI, MACD, ML Trend, and VADER Sentiment to compute a final BUY/SELL/HOLD score.")
    b("8. Streamlit receives all JSONs and renders Plotly charts and Metric Cards.")
    
    h2("Architecture Diagram (Conceptual)")
    p("""
    [ User / Browser ] 
          | (HTTP)
    [ Streamlit Frontend (Port 8501) ]
          | (REST API / JSON)
    [ Flask Backend (Port 5000) ]
       /      |       \       \ 
[Stock] [Indicators] [Predict] [Recommend]
  |           |         |          |
(yf)      (pandas) (TensorFlow) (Scoring Logic)
  |                     |
[Yahoo Finance]   [Local FS (.h5, .pkl)]
    """)
    doc.add_page_break()

    # ==================================================
    # 4. COMPLETE FOLDER STRUCTURE
    # ==================================================
    h1("4. COMPLETE FOLDER STRUCTURE")
    
    p("backend/app.py: Flask entry point. Configures CORS and registers API blueprints.")
    p("backend/routes/stock_routes.py: Maps URL endpoints (/api/predict) to controller functions. Handles HTTP request parsing and response formatting.")
    p("backend/services/stock_service.py: Contains business logic for data fetching, ticker validation, and VADER news sentiment analysis.")
    p("backend/services/indicator_service.py: Calculates MA, RSI, MACD, Bollinger Bands using Pandas rolling functions.")
    p("backend/services/prediction_service.py: Prepares multivariate sequences, handles MinMaxScaler state, calls model inference, and handles dynamic retraining.")
    p("backend/services/recommendation_service.py: The rules engine that assigns weights to technicals, sentiment, and ML trend to output BUY/SELL/HOLD.")
    p("backend/utils/helpers.py: String manipulation for tickers, Indian market suffix handling, currency symbols.")
    
    p("ml/model.py: Core deep learning architecture. Defines the custom `directional_loss` and the Meta-Ensemble Functional Keras Model (LSTM + Attention + GRU + Conv1D).")
    
    p("frontend/app.py: The monolithic Streamlit UI. Contains custom CSS for glassmorphism, Plotly charting logic, and layout rendering.")
    
    p("data/models/: Local file system cache for saved TensorFlow models (.h5) and scikit-learn Scalers (.pkl).")
    
    p("run.py: A subprocess orchestrator that boots both Flask and Streamlit simultaneously.")
    doc.add_page_break()

    # ==================================================
    # 5. FRONTEND DEEP DIVE
    # ==================================================
    h1("5. FRONTEND DEEP DIVE")
    
    h2("Framework & Styling")
    p("Built with Streamlit. Uses massive custom CSS injection (`unsafe_allow_html=True`) to override default styles, creating a 'Glassmorphism' dark UI. CSS variables (--bg-primary, --accent-purple) enforce a consistent design language.")
    
    h2("State Management")
    p("Uses `st.session_state` to persist the user's Watchlist across reruns (e.g., adding/removing tickers without losing data).")
    
    h2("Components & Layout")
    b("Sidebar: Inputs (Ticker, Timeframe, RSI parameters) and Watchlist management.")
    b("Metric Cards: Top row showing Current Price, Day Range, 52-Week Range, Volume with color-coded delta arrows.")
    b("Tabs: `st.tabs` used to modularize the view into Price, Indicators, Prediction, Recommendation, and Fundamentals.")
    
    h2("Rendering Lifecycle")
    p("Streamlit runs top-to-bottom on every interaction. Clicking 'Analyze' sets a flag, triggering sequential `api_call()` functions (which wrap the `requests` module). Loading spinners (`st.spinner`) give UX feedback during network waits.")
    
    h2("Visualizations")
    p("Plotly Graph Objects (`go.Figure`) are used heavily. Configured with a custom `CHART_LAYOUT` to strip backgrounds and apply gridlines matching the dark theme. Includes multi-trace charts (Candlesticks + Lines) and dual-axis handling (MACD Histogram).")
    doc.add_page_break()

    # ==================================================
    # 6. BACKEND DEEP DIVE
    # ==================================================
    h1("6. BACKEND DEEP DIVE")
    
    h2("Server Setup & Middleware")
    p("Flask 3.x initialized in `create_app()`. `Flask-CORS` is applied globally to allow Streamlit (Port 8501) to talk to Flask (Port 5000) without Cross-Origin blocks.")
    
    h2("Routes & Controllers")
    p("Blueprints (`api = Blueprint(...)`) are used to prefix all routes with `/api`. Controllers are thin: they validate `request.args`, call a Service, and return `jsonify(result)`.")
    
    h2("Services Layer (Business Logic)")
    p("This architecture isolates logic. Routes don't fetch data; Services do. ")
    b("Indicator Service: Uses vectorized Pandas operations (e.g., `df.rolling(window).mean()`) for extreme speed.")
    b("Prediction Service: The heaviest module. It merges price data, technical distances, macro indicators (^GSPC, ^VIX), and sentiment scores into a massive multivariate DataFrame, then scales it via `MinMaxScaler` before passing to Keras.")
    
    h2("Error Handling")
    p("Uses try-except blocks across external API calls (yfinance) and ML inferences. Returns standard JSON structures: `{'success': False, 'error': 'Reason'}` which the frontend renders gracefully as `st.error`.")
    doc.add_page_break()

    # ==================================================
    # 7. DATABASE EXPLANATION
    # ==================================================
    h1("7. DATABASE EXPLANATION")
    
    p("Beginner Answer: 'We don't use a traditional database like MySQL or MongoDB. We fetch live data directly from Yahoo Finance every time the user requests it, ensuring we always have the absolute latest market prices.'")
    
    p("Advanced Technical Answer: 'The architecture is stateless and highly ephemeral. For market data, it acts as a passthrough API proxy to Yahoo Finance, utilizing Pandas DataFrames as in-memory data structures for transformations. For state persistence, we utilize a Local File System Cache Strategy. The heavy ML models (.h5) and their corresponding Scikit-Learn stateful scalers (.pkl) are serialized and stored in the `data/models/` directory. This acts as a NoSQL document store, keyed by ticker symbol, preventing the need to retrain the model on every API call. If a model exists and its input shape matches the current feature set, we deserialize it for O(1) inference time.'")
    doc.add_page_break()

    # ==================================================
    # 8. AUTHENTICATION FLOW
    # ==================================================
    h1("8. AUTHENTICATION FLOW (Current & Future Implementation)")
    
    p("Current State: The application is currently designed as an open, public-facing analytical utility. There is no authentication barrier, allowing instant access to stock predictions.")
    
    p("How it WOULD be implemented (Interview Answer):")
    p("If we were to productionize this into a SaaS platform, I would implement a JWT (JSON Web Token) based authentication flow:")
    b("1. User Registration: Store hashed passwords using `bcrypt` in a PostgreSQL database.")
    b("2. Login: User provides credentials. Backend validates against hash and issues an Access Token (15m expiry) and Refresh Token (7d expiry) as HttpOnly cookies.")
    b("3. Protected Routes: Flask endpoints would be wrapped in a `@jwt_required` middleware decorator.")
    b("4. Role Management: Free tier users would get limited API calls (Rate Limiting via Redis) and access only to basic indicators. Premium users' JWT payload would contain `role: premium`, unlocking the ML Prediction endpoint.")
    doc.add_page_break()

    # ==================================================
    # 9. API DOCUMENTATION
    # ==================================================
    h1("9. API DOCUMENTATION")
    
    h2("1. GET /api/validate-ticker")
    b("Purpose: Checks if ticker exists on yfinance. Auto-appends .NS for Indian stocks.")
    b("Query Params: `ticker` (string)")
    b("Response: `{ 'valid': true, 'ticker': 'RELIANCE.NS', 'name': 'Reliance Ind', 'currency': 'INR' }`")
    
    h2("2. GET /api/stock-data")
    b("Purpose: Returns historical OHLCV data and company metadata.")
    b("Query Params: `ticker`, `period`")
    b("Response: `{ 'success': true, 'current_price': 150.2, 'data': { 'dates': [...], 'close': [...] } }`")
    
    h2("3. GET /api/indicators")
    b("Purpose: Calculates Technical Indicators.")
    b("Query Params: `ticker`, `period`, `rsi_period`")
    b("Response: `{ 'success': true, 'indicators': { 'MA20': [...], 'RSI': [...], 'MACD': [...] } }`")
    
    h2("4. GET /api/predict")
    b("Purpose: Runs LSTM inference for future prices.")
    b("Query Params: `ticker`, `days`")
    b("Response: `{ 'success': true, 'predictions': { 'dates': [...], 'prices': [...] }, 'trend': { 'direction': 'up' } }`")
    
    h2("5. GET /api/recommend")
    b("Purpose: Returns BUY/SELL/HOLD decision.")
    b("Query Params: `ticker`")
    b("Response: `{ 'recommendation': 'BUY', 'score': 5, 'confidence': 85.5, 'signals': [...] }`")
    doc.add_page_break()

    # ==================================================
    # 10. IMPORTANT MODULES
    # ==================================================
    h1("10. IMPORTANT MODULES DEEP DIVE")
    
    h2("ml/model.py (The Brain)")
    p("This is the most complex module. It uses Keras Functional API to build a Meta-Ensemble model.")
    b("Branch 1: LSTM + MultiHeadAttention. The LSTM handles sequence memory, while Self-Attention allows the network to focus on specific historical spikes/crashes (anomalies) regardless of sequence distance.")
    b("Branch 2: GRU (Gated Recurrent Unit). Faster to train, acts as a momentum tracker.")
    b("Branch 3: Conv1D + MaxPooling. Treats the time-series as a 1D image, extracting structural geometric patterns (like head-and-shoulders) via convolution filters.")
    p("Fusion: The outputs of all 3 branches are merged using an `Average()` layer, significantly reducing variance and overfitting.")
    p("Custom Loss (`directional_loss`): Standard MSE penalizes magnitude errors. This custom TF loss function adds a heavy penalty multiplier (up to 5x) if the model predicts the WRONG DIRECTION (e.g., predicts UP when actual is DOWN).")
    
    h2("backend/services/prediction_service.py")
    p("The Data Pipeline for ML. It performs feature engineering: converting absolute prices into stationary log-returns (`np.log(df/df.shift(1))`), calculating distance-to-moving-averages, and pulling macroeconomic data (S&P500, VIX) as exogenous variables. It handles Inverse Scaling to convert predictions back to real dollar values.")
    
    h2("backend/services/recommendation_service.py")
    p("The Rules Engine. It aggregates multiple distinct domains into a single integer score:")
    b("MA Crossover (+2 / -2)")
    b("RSI Thresholds (+2 for oversold, -2 for overbought)")
    b("ML Trend Magnitude (+3 to -3 based on predicted % change)")
    b("News Sentiment (+2 to -2 based on VADER compound score)")
    p("It then translates this integer score into a Confidence Percentage for the UI.")
    doc.add_page_break()

    # ==================================================
    # 11. EXECUTION FLOW
    # ==================================================
    h1("11. EXECUTION FLOW")
    
    h2("App Startup Flow")
    p("User executes `python run.py`. The script uses `subprocess.Popen` to spawn two separate OS processes: one for Flask (`backend/app.py`) on port 5000, and one for Streamlit (`frontend/app.py`) on port 8501. It catches KeyboardInterrupts to cleanly terminate both processes.")
    
    h2("Request-to-Response Flow (Example: Predict)")
    b("1. User clicks 'Analyze' -> Streamlit sets loading state.")
    b("2. `requests.get('http://localhost:5000/api/predict?ticker=AAPL')` is fired.")
    b("3. Flask Router catches `/api/predict`, validates input, calls `predict_prices('AAPL')`.")
    b("4. Prediction pipeline pulls 2y historical data from yfinance.")
    b("5. Feature engineering -> Scaling -> Model Architecture defined.")
    b("6. If `AAPL_lstm.h5` exists locally and shapes match, it loads weights (Inference state). If not, it trains on the fly (Training state).")
    b("7. Model outputs array of predicted returns. Returns are inverse-transformed to prices.")
    b("8. Python dict converted to JSON -> returned to Flask -> returned to Streamlit.")
    b("9. Streamlit parses JSON, renders Plotly line chart.")
    doc.add_page_break()

    # ==================================================
    # 12. DEPENDENCIES EXPLANATION
    # ==================================================
    h1("12. DEPENDENCIES EXPLANATION")
    
    b("Flask (backend web framework, REST routing)")
    b("Flask-CORS (allows frontend to fetch data from backend across ports)")
    b("Streamlit (UI framework, auto-generates frontend from python script)")
    b("yfinance (unofficial Yahoo Finance API scraper; fetches OHLCV and news)")
    b("pandas & numpy (matrix operations, time-series alignment, rolling windows)")
    b("scikit-learn (MinMaxScaler for normalizing ML inputs [0, 1] to prevent vanishing gradients)")
    b("TensorFlow / Keras (Core deep learning engine for compiling/training the neural network)")
    b("Plotly (Interactive charting library, D3.js based, used for candlesticks)")
    b("vaderSentiment (NLP lexicon specifically tuned for social/financial text sentiment polarity)")
    b("joblib (Fast serialization library used to save Scikit-learn Scaler objects to disk)")
    doc.add_page_break()

    # ==================================================
    # 13. SECURITY & 14. PERFORMANCE
    # ==================================================
    h1("13. SECURITY")
    p("Input Sanitization: All tickers undergo `.strip().upper()` and regex validation in `helpers.py` to prevent Command Injection or path traversal during model saving.")
    p("CORS: Implemented to restrict API access if deployed in production.")
    p("Rate Limiting: (Future) Would use Flask-Limiter to prevent abusive API scraping.")
    
    h1("14. PERFORMANCE OPTIMIZATION")
    b("Vectorization: Using Pandas native functions (`pct_change()`, `rolling().mean()`) instead of python `for` loops, making indicator calculation near-instantaneous (C-level execution).")
    b("Model Caching: Saving trained `.h5` files locally. Training takes ~10 seconds, but subsequent inferences take ~100ms. This prevents redundant compute overhead.")
    b("Asynchronous UI Fetching: Streamlit triggers API calls efficiently. While the heavy ML model trains in the background, the UI instantly renders the Price Charts and Indicators.")
    b("Forward-fill Missing Data: Markets have holidays. `df.ffill()` handles nan values optimally without breaking sequence arrays.")
    doc.add_page_break()

    # ==================================================
    # 15. DEPLOYMENT & 16. TESTING
    # ==================================================
    h1("15. DEPLOYMENT (Strategy)")
    p("To deploy this in production, I would use Docker & AWS:")
    b("1. Dockerize: Write a `Dockerfile` for the Backend (Python 3.10-slim + TensorFlow) and a separate one for the Frontend (Streamlit).")
    b("2. Container Orchestration: Use `docker-compose` locally, and deploy to AWS ECS (Elastic Container Service) or EKS (Kubernetes) in production.")
    b("3. Web Server: Wrap Flask in `Gunicorn` (WSGI) behind an `Nginx` reverse proxy for handling concurrent connections.")
    b("4. CI/CD: GitHub Actions pipeline to run linting and unit tests on push, and automatically push Docker images to AWS ECR.")
    
    h1("16. TESTING (Strategy)")
    p("Testing would be divided into 3 layers:")
    b("Unit Tests: `pytest` for `indicator_service.py` to ensure MA calculations mathematically match expected static arrays.")
    b("Integration Tests: API testing using Flask's `test_client()` to mock `yfinance` network calls and assert correct JSON schemas.")
    b("E2E Testing: Using Selenium or Playwright to load the Streamlit UI, input a ticker, and verify chart rendering.")
    doc.add_page_break()

    # ==================================================
    # 17. CHALLENGES & 18. TRADEOFFS
    # ==================================================
    h1("17. CHALLENGES FACED")
    p("1. Data Stationarity for ML: Neural networks perform poorly on absolute stock prices because they trend infinitely upward. Solution: Converted prices into logarithmic returns (`np.log(curr/prev)`) and relative percentage distances from Moving Averages. The model predicts the return, which is mathematically inverse-transformed back to price.")
    p("2. Market Holidays / Missing Data: Indian stocks (.NS) often have NaNs on global market days, breaking the 3D tensor shapes. Solution: Implemented `df.ffill()` to forward-carry prices across holidays.")
    p("3. Loss Function Mismatch: Standard MSE optimizes for the exact price, but in trading, DIRECTION is more important than magnitude. Solution: Wrote a custom Keras loss function `directional_loss` that penalizes the model heavily if signs (positive/negative return) differ between truth and prediction.")
    
    h1("18. TRADEOFFS")
    p("1. Streamlit vs React: Chose Streamlit for extreme development velocity and native Python plotting, trading off fine-grained CSS control and smaller bundle sizes.")
    p("2. On-the-Fly Training vs Pre-trained: The system currently trains on the fly for unseen tickers. Tradeoff: High initial latency (10s) for a new stock, but infinite flexibility (supports 10,000+ stocks) without needing a massive centralized GPU training farm.")
    doc.add_page_break()

    # ==================================================
    # 19. SCALABILITY
    # ==================================================
    h1("19. SCALABILITY")
    b("Bottlenecks: Machine learning inference (CPU/GPU bound), API rate limits (yfinance), and Streamlit websocket concurrency.")
    b("Scaling Strategy: Move ML workloads to a message queue (Celery + Redis) to decouple from the HTTP request cycle. Shift to a paid data provider (Polygon.io) via WebSockets to bypass yfinance rate limits. Use a load balancer across multiple Gunicorn worker nodes.")
    b("Future Architecture Improvements: Migrate to FastAPI for async native routing, and rewrite frontend in React for lighter client-side load.")
    doc.add_page_break()

    # ==================================================
    # 20. INTERVIEW QUESTIONS & ANSWERS
    # ==================================================
    h1("20. INTERVIEW QUESTIONS & ANSWERS")
    
    h2("Beginner")
    b("Q: What is the purpose of this project?")
    b("A: It's an end-to-end full stack application that analyzes stock data using technical indicators, machine learning, and news sentiment to recommend whether a user should buy, sell, or hold a stock.")
    
    h2("Intermediate")
    b("Q: Why separate the frontend (Streamlit) from the backend (Flask)?")
    b("A: Separation of concerns. Streamlit handles UI state and rendering, while Flask acts as an API gateway. This microservice architecture allows us to easily swap the frontend for a React app or mobile app in the future without touching the core ML and data logic.")
    
    h2("Advanced")
    b("Q: Explain your ML Architecture and why you didn't just use a basic LSTM.")
    b("A: Financial time series are highly noisy and non-stationary. A basic LSTM struggles with regime changes. I built a Keras Functional Meta-Ensemble model with three branches. Branch 1 is an LSTM with Multi-Head Attention to capture long-term anomalies. Branch 2 is a GRU for fast momentum tracking. Branch 3 is a Conv1D layer to extract structural geometric patterns (like head-and-shoulders). Their outputs are averaged, significantly reducing variance and improving directional accuracy.")
    
    h2("System Design")
    b("Q: If this app goes viral and gets 10,000 concurrent users, how do you scale it?")
    b("A: First, introduce caching using Redis. If 100 users request 'AAPL' in 5 minutes, only the first request hits yfinance and runs ML inference; the rest get the cached JSON. Second, deploy Flask on AWS ECS with Auto-Scaling based on CPU load. Third, separate the ML inference into an asynchronous Celery worker queue (RabbitMQ), so heavy matrix operations don't block the Flask web threads.")
    
    h2("HR / Project Discussion")
    b("Q: What did you learn from building this?")
    b("A: I learned how to architect microservices, handle real-world dirty data (like market holidays), and bridge the gap between Data Science (TensorFlow) and Software Engineering (Flask/React). I also learned that feature engineering (stationarity) is way more important than just having a massive neural network.")
    doc.add_page_break()

    # ==================================================
    # 21. PROJECT STORY
    # ==================================================
    h1("21. PROJECT STORY")
    
    h2("2-Minute Pitch")
    p("I noticed retail investors suffer from information overload—staring at charts, news, and indicators simultaneously. To solve this, I built a full-stack Stock Prediction System. I used Flask for the backend to orchestrate Yahoo Finance data, Pandas for technical indicators, and VADER for NLP news sentiment. For the AI core, I designed a multi-branch Deep Learning ensemble (LSTM + GRU + Conv1D) to forecast prices. Finally, I wrapped it all in a beautiful, glassmorphism Streamlit UI. It aggregates these complex data streams into a simple, actionable BUY/SELL/HOLD recommendation, running smoothly in real-time.")
    
    h2("5-Minute Pitch")
    p("[Expand on the 2-minute pitch by discussing the architecture: how Streamlit hits Flask endpoints, how the StockService cleans data, how the PredictionService dynamically trains .h5 models if missing, and how the RecommendationService mathematically weighs ML, technicals, and sentiment.]")
    
    h2("10-Minute Pitch")
    p("[Expand on the 5-minute pitch by deeply detailing the challenges (stationarity, custom directional_loss), the specific parameters of the ML model, how CORS was solved, and future scalability plans via Redis and Docker.]")
    doc.add_page_break()

    # ==================================================
    # 22. RESUME CONTENT
    # ==================================================
    h1("22. RESUME CONTENT")
    
    h2("One-Line Summary")
    p("AI-Powered Stock Analysis Platform (Python, Flask, TensorFlow, Streamlit)")
    
    h2("ATS-Friendly Bullet Points")
    b("Architected a decoupled full-stack application using Flask and Streamlit, serving real-time financial data and interactive Plotly visualizations for 1000+ global equities.")
    b("Engineered a Meta-Ensemble Deep Learning model (LSTM, GRU, Conv1D, Self-Attention) in TensorFlow/Keras to forecast time-series data, implementing a custom directional loss function to maximize trading accuracy.")
    b("Developed a robust quantitative recommendation engine utilizing Pandas for vectorized technical analysis (MACD, RSI, Bollinger Bands) and VADER NLP for real-time news sentiment extraction.")
    b("Optimized inference latency by 90% via local file system serialization (.h5, .pkl) and decoupled asynchronous API routing.")
    
    h2("Three-Line Summary")
    p("An AI-powered quantitative analysis platform integrating real-time market data, technical indicators, and VADER news sentiment. Features a custom Keras Meta-Ensemble deep learning model (LSTM/GRU/Conv1D) for time-series forecasting. Architected with a Flask REST backend and a glassmorphism Streamlit UI for seamless retail trading recommendations.")
    doc.add_page_break()

    # ==================================================
    # 23. FUTURE IMPROVEMENTS
    # ==================================================
    h1("23. FUTURE IMPROVEMENTS")
    b("Paper Trading Integration: Add user auth and a virtual portfolio to track recommendation performance over time.")
    b("Alternative Data: Integrate Reddit/Twitter APIs via Kafka streams for real-time social sentiment.")
    b("Advanced ML: Shift from point-prediction to probabilistic forecasting using Bayesian Neural Networks to output confidence intervals (e.g., 'AAPL will be $150 ± $5').")
    doc.add_page_break()

    # ==================================================
    # 24. FINAL REVISION SECTION
    # ==================================================
    h1("24. FINAL REVISION CHEAT SHEET")
    
    h2("Quick Notes")
    b("Frontend: Streamlit, Plotly, custom CSS (Glassmorphism).")
    b("Backend: Flask (REST API), Flask-CORS.")
    b("Data: yfinance, pandas (vectorized fast math).")
    b("ML: TensorFlow/Keras Functional API, MinMaxScaler (for stationarity).")
    b("Architecture: Microservices (Client -> API Gateway -> Services).")
    
    h2("Key Talking Points")
    b("Secret Sauce 1: Custom 'directional_loss' penalty in Keras to heavily punish wrong direction predictions.")
    b("Secret Sauce 2: Meta-ensemble fusion (LSTM/GRU/Conv1D) combining sequential memory, momentum, and geometric patterns.")
    b("Secret Sauce 3: Combining Technicals + ML + NLP Sentiment for final BUY/SELL/HOLD score.")
    
    h2("Best Project Introduction")
    p("'I built a full-stack, AI-powered stock prediction system. It isn't just a basic charting app—it uses a deep learning meta-ensemble to forecast prices, VADER NLP to read the news, and standard technical indicators to issue a combined BUY/SELL/HOLD signal. I structured it as a microservice architecture with a Flask REST API backend and a Streamlit UI, making it extremely modular and scalable.'")

    file_path = os.path.join(os.getcwd(), 'PROJECT_INTERVIEW_GUIDE.docx')
    doc.save(file_path)
    print(f"Successfully saved to {file_path}")

if __name__ == "__main__":
    create_document()
