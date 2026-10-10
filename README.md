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

- **Personalized Health Profile**: Maintain demographics (age, gender, height, weight, blood group), dietary preferences, allergies, chronic conditions, and current medications with real-time profile completeness tracking.
- **Personal Health AI Assistant**: Conversational AI powered by Google Gemini to explain health concepts, routines, and wellness topics with goal identification, progressive questioning, and deterministic macro calculations.
- **Guided Symptom Assessment**: Structured symptom intake questionnaire with a 1–10 severity slider, safe self-care advice, and immediate red-flag triage with Indian emergency contact (`112`) escalation.
- **Source-Grounded Nutrition & Diet Planner**:
  - **6 Fitness & Body Goals**: *Muscle Gain*, *Body Recomposition*, *Maintain*, *General Fitness*, *Performance*, and *Fat Loss*.
  - **Unselected-by-Default Food Selection**: 8 expandable categories with automatic allergen exclusion.
  - **Protein Powder Supplement Module**: Verified database items (Whey Isolate, Whey Concentrate, Plant Protein, Soy Isolate) and custom label inputs.
  - **Deterministic 7-Day Meal Plan**: 5 daily meals optimized to reach **>=90% of calorie and macronutrient targets** using verified data—zero AI calorie hallucinations.
  - **Interactive Food Substitutions & Meal Swaps**: Swap individual meals and recalculate daily macros dynamically.
- **Health Insights**: Data-grounded metrics including BMI, BMR (Mifflin-St Jeor), and TDEE.
- **Consultation & Health History**: Search and review previous chat sessions, symptom checks, and saved 7-day diet plans with one-click ReportLab PDF export.
- **Document Center & Scanner**: Upload or paste lab report excerpts to receive plain-English AI explanations.
- **Privacy & Account Controls**: Multi-user isolation via PostgreSQL Row Level Security (RLS), full JSON/CSV data backup exports, and a permanent account deletion Danger Zone.
- **Production-Safe Demo Mode**: One-click exploration without requiring registration or external API credentials.

---

## Technology Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/) (custom light healthcare CSS design system)
- **Backend & Database**: [Supabase](https://supabase.com/) (PostgreSQL with Row Level Security, Auth) — Official Python SDK (`supabase`)
- **AI & Language Models**: [Google GenAI SDK](https://ai.google.dev/) (`google-genai` / Gemini 2.5 Flash) with cached diagnostics, 429 rate-limit backoff protection, and evidence-based demo fallbacks
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
├── database/                   # Database layer (official Python Supabase SDK)
│   ├── client.py               # Supabase client manager, diagnostics & mock fallback
│   ├── repositories.py         # Isolated DAOs (Profile, Chat, Symptom, Diet)
│   └── schema.sql              # Supabase PostgreSQL schema with RLS policies
│
├── datasets/                   # Verified food composition datasets
│   └── icmr_nin_foods.json     # Verified ICMR-NIN & USDA nutritional records
│
├── services/                   # Business logic and external API clients
│   ├── ai_service.py           # Gemini AI client with goal identification & progressive questioning
│   ├── auth_service.py         # Authentication, demo sessions, and tokens
│   ├── demo_service.py         # Fictional demo data & context-aware fallback AI
│   ├── diet_planner_service.py # Deterministic 7-day meal optimization engine
│   ├── health_service.py       # BMI, BMR, TDEE, profile completeness math
│   ├── nutrition_service.py    # Database food lookup and substitution engine
│   ├── report_service.py       # ReportLab PDF report generation
│   └── safety_service.py       # Multi-layer emergency triage engine
│
├── utils/                      # Styling tokens and helpers
│   ├── icons.py                # SVG icon library (Lucide/Heroicon vectors)
│   ├── custom_css.py           # Healthcare light design system CSS
│   ├── formatting.py           # Text and numeric formatting helpers
│   └── validation.py           # Input sanitization and validators
│
└── tests/                      # Automated test suite
    ├── run_all_tests.py        # Master test runner (51 unit tests)
    ├── test_ai_diagnostics.py  # AI diagnostic & placeholder tests
    ├── test_ai_responses.py    # AI identity isolation & goal-identification tests
    ├── test_auth_isolation.py  # Supabase multi-user isolation tests
    ├── test_demo_mode.py       # Demo mode & deployment resilience tests
    ├── test_diet_planner.py    # Diet planner & nutrition target tests
    ├── test_emoji_audit.py     # Zero-emoji compliance audit
    ├── test_gemini_diagnostics.py # Live Gemini API integration tests
    ├── test_nutrition.py       # ICMR/USDA food lookup tests
    ├── test_profile_completeness.py # Profile completeness tests
    ├── test_safety.py          # Emergency triage tests
    └── test_supabase_config.py # Supabase config, diagnostics & publishable key tests
```

---

## Windows PowerShell Quickstart (Fresh Installation)

### 1. Clone the Repository
```powershell
git clone https://github.com/hirday-02/VitalBite-AI.git
cd VitalBite-AI
```

### 2. Create and Activate a Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure API Keys (Optional — Skip for Demo Mode)

Copy `.env.example` to `.env` and fill in your credentials:

```powershell
Copy-Item .env.example .env
notepad .env
```

**Edit `.env` with your real values:**
```ini
# Google Gemini API Key — get at https://aistudio.google.com/app/apikey
GEMINI_API_KEY=AIzaSy...

# Supabase Credentials — get at https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional: USDA FDC API Key for extended food lookups
# USDA_FDC_API_KEY=

# Optional: Strict local dev mock mode (must be false in production)
VITALBITE_ALLOW_MOCK_DB=false
```

Alternatively, copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and use the same key names.

> **Tip:** You can skip Step 4 entirely and click **Explore Demo** on the login page to run the application immediately without any credentials!

### 5. Apply Supabase Database Schema (Production Only)

If using a real Supabase project, apply the schema once via the Supabase SQL Editor:

1. Open your Supabase project dashboard.
2. Navigate to **SQL Editor**.
3. Paste the entire contents of [`database/schema.sql`](database/schema.sql) and click **Run**.

This creates all required tables, performance indexes, Row Level Security (RLS) policies, and the automatic profile creation trigger.

> **Important**: Never disable RLS on any of these tables. The RLS policies guarantee that User A can never read or write User B's data.

### 6. Launch the Application
```powershell
streamlit run app.py
```

Open your browser at **`http://localhost:8501`**.

---

## API Keys & Configuration Reference

| Variable | Purpose | Where to Obtain | Required? |
| :--- | :--- | :--- | :--- |
| `GEMINI_API_KEY` | Google Gemini AI — chat, lab scanner, symptom analysis | [Google AI Studio](https://aistudio.google.com/) | Optional (Demo fallback available) |
| `SUPABASE_URL` | Supabase PostgreSQL endpoint URL | [Supabase Dashboard](https://supabase.com/dashboard) → Settings → API | Optional (Demo mode bypasses DB) |
| `SUPABASE_ANON_KEY` | Supabase public anon key (also accepts `SUPABASE_PUBLISHABLE_KEY`) | [Supabase Dashboard](https://supabase.com/dashboard) → Settings → API | Optional (Demo mode bypasses DB) |
| `VITALBITE_ALLOW_MOCK_DB` | Enable in-memory mock DB for offline dev/testing | Set `true` locally only | Optional |

> **Security Note**: Only use the **Anon Key** (`SUPABASE_ANON_KEY` / `SUPABASE_PUBLISHABLE_KEY`). Never add the Supabase `service_role` secret key to application configuration or commit it to Git. The existing Row Level Security policies enforce user-level data isolation using the anon key.

---

## Supabase Python SDK (Correct Integration)

VitalBite AI uses the **official Python Supabase SDK** (`supabase` package — `supabase-py`). This is a Python project and does **not** use any JavaScript packages like `@supabase/server`.

**How credentials are read (in priority order):**
1. Environment variable (`SUPABASE_URL`, `SUPABASE_ANON_KEY` or `SUPABASE_PUBLISHABLE_KEY`)
2. `.env` file in the project root (loaded by `python-dotenv`)
3. `.streamlit/secrets.toml` (loaded by Streamlit)

**Connection diagnostics** are built in. If your Supabase connection fails, you'll see a clear message distinguishing:
- `CONFIG_MISSING` — URL or key not set at all
- `CONFIG_PLACEHOLDER` — Still using template values like `your-project-id`
- `AUTH_FAILED` — Key rejected by Supabase (wrong anon key)
- `TABLE_MISSING` — Connected but `schema.sql` not applied yet
- `READY` — Fully connected and operational

---

## AI Response Behavior

### Goal Identification & Progressive Questioning

When you ask a diet or fitness question (e.g., *"I want to start gym. What diet should I take?"*), VitalBite AI:

1. **Checks your saved profile** for already-provided details (age, height, weight, goal, dietary preference).
2. **If profile is complete**: Generates deterministic calorie and macro targets using Mifflin-St Jeor BMR + TDEE math. No AI-invented numbers.
3. **If profile is incomplete**: Provides helpful beginner principles immediately, then asks 2–3 progressive clarifying questions. Does not repeat questions about data already in your profile.
4. **Meal plan requests**: Directs you to the deterministic 7-Day Diet Planner tab instead of generating unverified free-form meal plans in chat.

### Identity Safety

- The AI assistant **never assumes your name is "Alex Rivera"**. Alex Rivera is strictly a fictional demo profile and is never presented as the current user's identity.
- In Demo Mode, responses clearly identify that the profile data is fictional demonstration data.
- In Production Mode, only your verified authenticated profile data is used.

---

## Automated Verification & Testing

```powershell
# Run all 51 unit and integration tests
c:\VitalBite\venv\Scripts\python.exe tests/run_all_tests.py

# Verify Python syntax and bytecode compilation
c:\VitalBite\venv\Scripts\python.exe -m compileall -f .
```

### Test Coverage
- **AI Response Identity Isolation**: Verifies Alex Rivera never appears in non-demo AI responses
- **Progressive Questioning**: Verifies missing profile leads to clarifying questions, not generic lectures
- **Deterministic Target Calculations**: Verifies complete profiles produce calculated (not fabricated) macro targets
- **Supabase Configuration Diagnostics**: Verifies placeholder detection, publishable key fallback, graceful failure handling
- **Zero Emoji Compliance**: Audits all source files for emoji characters in user-facing strings
- **Multi-user RLS Isolation**: Verifies User A cannot read User B's data
- **Demo Mode Containment**: Verifies zero writes to production Supabase tables during demo sessions
- **Emergency Triage**: Verifies Indian 112 emergency escalation logic

---

## Security & Privacy Architecture

- **PostgreSQL Row Level Security (RLS)**: In production mode, every database record is strictly partitioned by `user_id`. User A can never query or mutate User B's records.
- **Zero Database Writes in Demo Mode**: Demo mode operates strictly in local session memory, ensuring zero demo data leaks into the production database.
- **Zero Hardcoded Secrets**: All API credentials and service tokens are excluded from version control via `.gitignore`.
- **Rate-Limit & RPM Protection**: Gemini model diagnostics are cached in memory (10-minute TTL) with exponential backoff on 429 responses, ensuring 1 user action produces at most 1 API request.
- **Anon Key Only**: The app uses only the Supabase anon key. The service role key is never referenced or needed.

---

## Beta Disclaimer

> [!IMPORTANT]
> **VitalBite AI is currently in early beta.** All information, nutritional targets, and symptom evaluations are provided strictly for general educational and informational purposes. VitalBite AI is not a licensed physician, diagnostic device, or substitute for professional medical care. For acute medical emergencies in India, immediately call **112** or visit the nearest emergency room.
