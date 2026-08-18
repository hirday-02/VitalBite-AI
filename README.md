# VitalBite AI

> **Personalized Digital Health & Nutrition AI Platform**  
> An intelligent healthcare SaaS companion built with Python, Streamlit, PostgreSQL (Supabase), and Google Gemini AI.

---

## Overview

**VitalBite AI** is a production-quality, multi-user health and nutrition web application designed to help individuals track their wellness, analyze symptoms safely, explore verified dietary data, and generate goal-aligned 7-day meal plans.

The platform operates in two seamless modes:
1. **Production Mode**: Full Supabase authentication, PostgreSQL Row Level Security (RLS) data isolation, and live Google Gemini AI reasoning.
2. **Demo Mode**: Instant zero-credential exploration with realistic fictional sample data (*Alex Rivera*), session-contained in-memory storage, deterministic 7-day meal planning, and evidence-based fallback AI guidance without requiring database or API keys.

---

## Key Features

- 👤 **Personalized Health Profile**: Maintain core demographics (age, gender, height, weight, blood group), dietary preferences, allergies, chronic conditions, and current medications with real-time profile completeness tracking.
- 💬 **Personal Health AI Assistant**: Conversational AI powered by Google Gemini to explain health concepts, routines, and wellness topics in plain English with multi-layer emergency guardrails.
- ⚡ **Guided Symptom Assessment**: Structured symptom intake questionnaire with a 1–10 severity slider, safe self-care advice, and immediate red-flag triage with Indian emergency contact (`112`) escalation.
- 🥗 **Source-Grounded Nutrition & Diet Planner**:
  - **6 Fitness & Body Goals**: *Muscle Gain*, *Body Recomposition*, *Maintain*, *General Fitness*, *Performance*, and *Fat Loss*.
  - **Unselected-by-Default Food Selection**: 8 expandable categories (*Fruits*, *Vegetables*, *Protein*, *Grains & Cereals*, *Dairy*, *Nuts & Seeds*, *Legumes & Dals*, *Indian Dishes*) with automatic allergen exclusion.
  - **Protein Powder Supplement Module**: Verified database items (Whey Isolate, Whey Concentrate, Plant Protein, Soy Isolate) and custom label inputs with serving selectors (0.5 to 2.0 scoops).
  - **Deterministic 7-Day Meal Plan**: 5 daily meals (*Breakfast*, *Mid-Morning*, *Lunch*, *Evening*, *Dinner*) optimized to reach **≥90% of calorie and macronutrient targets** using verified data—zero AI calorie hallucinations.
  - **Interactive Food Substitutions & Meal Swaps**: Swap individual meals and recalculate daily macros dynamically.
- 📈 **Health Insights**: Data-grounded metrics including Body Mass Index (BMI), Basal Metabolic Rate (BMR via Mifflin-St Jeor), and Total Daily Energy Expenditure (TDEE).
- 🕒 **Consultation & Health History**: Search and review previous chat sessions, symptom checks, and saved 7-day diet plans with one-click ReportLab PDF export.
- 📄 **Document Center & Scanner**: Upload or paste lab report excerpts to receive plain-English AI explanations.
- ⚙️ **Privacy & Account Controls**: Multi-user isolation via PostgreSQL Row Level Security (RLS), full JSON/CSV data backup exports, and a permanent account deletion Danger Zone.
- ✨ **Production-Safe Demo Mode**: One-click exploration without requiring registration or external API credentials.

---

## Technology Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/) (with custom light frosted glassmorphism CSS)
- **Backend & Database**: [Supabase](https://supabase.com/) (PostgreSQL with Row Level Security, Auth, and Storage)
- **AI & Language Models**: [Google GenAI SDK](https://ai.google.dev/) (`google-genai` / Gemini 3.6 Flash) with cached diagnostics, 429 rate-limit backoff protection, and evidence-based demo fallbacks
- **PDF Report Generation**: [ReportLab](https://www.reportlab.com/)
- **Nutritional Datasets**: ICMR-NIN Indian Food Composition Tables (IFCT 2017) & USDA FoodData Central (FDC)
- **Validation & Utilities**: Pydantic, Pandas, Python-Dotenv

---

## Project Structure

```
VitalBite-AI/
├── app.py                      # Main application router and brand shell
├── requirements.txt            # Production dependencies
├── README.md                   # Project documentation
├── .gitignore                  # Git secret and cache exclusion rules
├── .env.example                # Environment variable configuration template
│
├── .streamlit/
│   ├── config.toml             # Streamlit Light theme configuration
│   └── secrets.toml.example    # Streamlit secrets template
│
├── components/                 # Reusable UI component modules
│   ├── auth_ui.py              # Login, registration, password reset, demo entry
│   ├── dashboard_ui.py         # Personal health command center
│   ├── profile_ui.py           # Demographics and profile management
│   ├── chat_ui.py              # Health AI conversation tab
│   ├── symptom_ui.py           # Symptom checker and triage
│   ├── diet_ui.py              # Interactive 7-day diet planner & food lookup
│   ├── insights_ui.py          # BMI, BMR, TDEE health analytics
│   ├── history_ui.py           # Consultation history & PDF export
│   ├── documents_ui.py         # Document center & lab scanner
│   ├── settings_ui.py          # Account, data backup, danger zone, exit demo
│   └── emergency_modal.py      # Indian 112 emergency overlay banner
│
├── database/                   # Database layer
│   ├── client.py               # Supabase client manager & mock fallback
│   ├── repositories.py         # Isolated DAOs (Profile, Chat, Symptom, Diet)
│   └── schema.sql              # Supabase PostgreSQL schema with RLS policies
│
├── datasets/                   # Verified food composition datasets
│   └── icmr_nin_foods.json     # Verified ICMR-NIN & USDA nutritional records
│
├── services/                   # Business logic and external API clients
│   ├── ai_service.py           # Gemini AI client with 429 backoff & caching
│   ├── auth_service.py         # Authentication, demo sessions, and tokens
│   ├── demo_service.py         # Fictional demo data & fallback intelligence
│   ├── diet_planner_service.py # Deterministic 7-day meal optimization engine
│   ├── health_service.py       # BMI, BMR, TDEE, profile completeness math
│   ├── nutrition_service.py    # Database food lookup and substitution engine
│   ├── report_service.py       # ReportLab PDF report generation
│   └── safety_service.py       # Multi-layer emergency triage engine
│
├── utils/                      # Styling tokens and helpers
│   ├── custom_css.py           # Light frosted glassmorphism CSS & SVG gauges
│   ├── formatting.py           # Text and numeric formatting helpers
│   └── validation.py           # Input sanitization and validators
│
└── tests/                      # Automated test suite
    ├── run_all_tests.py        # Master test runner (40 unit tests)
    ├── test_ai_diagnostics.py  # AI diagnostic & placeholder tests
    ├── test_auth_isolation.py  # Supabase multi-user isolation tests
    ├── test_demo_mode.py       # Demo mode & deployment resilience tests
    ├── test_diet_planner.py    # Diet planner & nutrition target tests
    ├── test_gemini_diagnostics.py # Live Gemini API integration tests
    ├── test_nutrition.py       # ICMR/USDA food lookup tests
    ├── test_profile_completeness.py # Profile completeness tests
    └── test_safety.py          # Emergency triage tests
```

---

## Quickstart & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/hirday-02/VitalBite-AI.git
cd VitalBite-AI
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional for Demo Mode)
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` (or `.env.example` to `.env`):
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your_supabase_anon_key_here"
```
*(Note: You can skip this step and click **✨ Explore Demo** on the login page to run the application immediately without credentials!)*

### 5. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## Automated Verification & Testing

To run the complete automated test suite:
```bash
# Run all unit and integration tests (40 tests)
python tests/run_all_tests.py

# Verify Python syntax and bytecode compilation
python -m compileall -f .
```

---

## Security & Privacy Architecture

- **PostgreSQL Row Level Security (RLS)**: In production mode, every database record is strictly partitioned by `user_id`. User A can never query or mutate User B's records.
- **Zero Database Writes in Demo Mode**: Demo mode operates strictly in local session memory, ensuring zero demo data leaks into the production database.
- **Zero Hardcoded Secrets**: All API credentials and service tokens are excluded from version control via `.gitignore`.
- **Rate-Limit & RPM Protection**: Gemini model diagnostics are cached in memory (10-minute TTL) with exponential backoff on 429 responses, ensuring 1 user action produces at most 1 API request.

---

## Beta Disclaimer

> [!IMPORTANT]
> **VitalBite AI is currently in early beta.** All information, nutritional targets, and symptom evaluations are provided strictly for general educational and informational purposes. VitalBite AI is not a licensed physician, diagnostic device, or substitute for professional medical care. For acute medical emergencies in India, immediately call **112** or visit the nearest emergency room.
