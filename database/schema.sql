-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    avatar_color TEXT DEFAULT '#6C63FF',
    preferred_categories TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Wishlist table
CREATE TABLE IF NOT EXISTS public.wishlist (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL,
    product_title TEXT,
    product_price DECIMAL,
    product_category TEXT,
    added_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- Recommendations history table
CREATE TABLE IF NOT EXISTS public.recommendation_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL,
    product_title TEXT,
    match_score DECIMAL,
    engine_used TEXT,
    explanation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- User feedback table
CREATE TABLE IF NOT EXISTS public.feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL,
    is_positive BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

-- User preferences table
CREATE TABLE IF NOT EXISTS public.user_preferences (
    user_id UUID REFERENCES public.profiles(id) PRIMARY KEY,
    preferred_categories TEXT[] DEFAULT '{}',
    min_price DECIMAL DEFAULT 0,
    max_price DECIMAL DEFAULT 10000,
    min_rating DECIMAL DEFAULT 1.0,
    diversity_level INTEGER DEFAULT 50,
    preferred_engine TEXT DEFAULT 'hybrid',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.wishlist ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recommendation_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policies (users can only see their own data)
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR ALL USING (auth.uid() = id);

CREATE POLICY "Users can manage own wishlist" ON public.wishlist
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can view own recommendations" 
    ON public.recommendation_history
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own feedback" ON public.feedback
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own preferences" 
    ON public.user_preferences
    FOR ALL USING (auth.uid() = user_id);
