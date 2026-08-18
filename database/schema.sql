-- =====================================================================
-- VitalBite AI — Supabase PostgreSQL Database Schema & Security DDL
-- Multi-User Row Level Security (RLS) Implementation
-- =====================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. PROFILES TABLE
-- Linked 1:1 with Supabase auth.users
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT DEFAULT '',
    age INT CHECK (age IS NULL OR (age >= 0 AND age <= 130)),
    gender TEXT DEFAULT 'Male',
    height_cm NUMERIC(5,2) CHECK (height_cm IS NULL OR (height_cm > 0 AND height_cm < 300)),
    weight_kg NUMERIC(5,2) CHECK (weight_kg IS NULL OR (weight_kg > 0 AND weight_kg < 500)),
    blood_type TEXT DEFAULT '',
    allergies TEXT DEFAULT '',
    conditions TEXT DEFAULT '',
    medications TEXT DEFAULT '',
    dietary_preference TEXT DEFAULT 'Vegetarian',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. CHAT SESSIONS TABLE
CREATE TABLE IF NOT EXISTS public.chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'New Health Conversation',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CHAT MESSAGES TABLE
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    sender TEXT NOT NULL CHECK (sender IN ('user', 'assistant')),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. SYMPTOM ASSESSMENTS TABLE
CREATE TABLE IF NOT EXISTS public.symptom_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    symptoms TEXT NOT NULL,
    duration TEXT DEFAULT '',
    severity TEXT DEFAULT '',
    analysis TEXT NOT NULL,
    is_emergency BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. DIET PLANS TABLE
CREATE TABLE IF NOT EXISTS public.diet_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    goal TEXT NOT NULL,
    diet_type TEXT NOT NULL,
    plan_text TEXT NOT NULL,
    structured_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. DOCUMENTS TABLE
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    storage_path TEXT DEFAULT '',
    analysis_summary TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. HEALTH METRICS TABLE
CREATE TABLE IF NOT EXISTS public.health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type TEXT NOT NULL, -- e.g. 'weight', 'bmi', 'blood_pressure'
    metric_value NUMERIC(7,2) NOT NULL,
    unit TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. REPORTS TABLE
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    report_type TEXT NOT NULL, -- 'consultation', 'symptoms', 'diet_plan'
    title TEXT NOT NULL,
    content_summary TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON public.chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON public.chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_symptom_assessments_user_id ON public.symptom_assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_diet_plans_user_id ON public.diet_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_health_metrics_user_id ON public.health_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON public.reports(user_id);

-- =====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES — MANDATORY ISOLATION
-- Rule: A user can ONLY access/modify records matching auth.uid()
-- =====================================================================

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.symptom_assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.diet_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- 1. PROFILES POLICIES
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can delete own profile"
    ON public.profiles FOR DELETE
    USING (auth.uid() = id);

-- 2. CHAT SESSIONS POLICIES
CREATE POLICY "Users can view own chat sessions"
    ON public.chat_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat sessions"
    ON public.chat_sessions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chat sessions"
    ON public.chat_sessions FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat sessions"
    ON public.chat_sessions FOR DELETE
    USING (auth.uid() = user_id);

-- 3. CHAT MESSAGES POLICIES
CREATE POLICY "Users can view own chat messages"
    ON public.chat_messages FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat messages"
    ON public.chat_messages FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat messages"
    ON public.chat_messages FOR DELETE
    USING (auth.uid() = user_id);

-- 4. SYMPTOM ASSESSMENTS POLICIES
CREATE POLICY "Users can view own symptom assessments"
    ON public.symptom_assessments FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own symptom assessments"
    ON public.symptom_assessments FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own symptom assessments"
    ON public.symptom_assessments FOR DELETE
    USING (auth.uid() = user_id);

-- 5. DIET PLANS POLICIES
CREATE POLICY "Users can view own diet plans"
    ON public.diet_plans FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own diet plans"
    ON public.diet_plans FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own diet plans"
    ON public.diet_plans FOR DELETE
    USING (auth.uid() = user_id);

-- 6. DOCUMENTS POLICIES
CREATE POLICY "Users can view own documents"
    ON public.documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents"
    ON public.documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents"
    ON public.documents FOR DELETE
    USING (auth.uid() = user_id);

-- 7. HEALTH METRICS POLICIES
CREATE POLICY "Users can view own health metrics"
    ON public.health_metrics FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own health metrics"
    ON public.health_metrics FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own health metrics"
    ON public.health_metrics FOR DELETE
    USING (auth.uid() = user_id);

-- 8. REPORTS POLICIES
CREATE POLICY "Users can view own reports"
    ON public.reports FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own reports"
    ON public.reports FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own reports"
    ON public.reports FOR DELETE
    USING (auth.uid() = user_id);

-- AUTOMATIC PROFILE CREATION TRIGGER ON SIGNUP
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
