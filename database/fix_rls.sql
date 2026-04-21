-- ============================================================
-- IntelliRec — RLS Policy Fix
-- Run this in: Supabase Dashboard → SQL Editor → New query
-- ============================================================

-- ── profiles table ───────────────────────────────────────────

DROP POLICY IF EXISTS "Users can view own profile"   ON public.profiles;
DROP POLICY IF EXISTS "Users manage own profile"     ON public.profiles;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;

CREATE POLICY "Users can insert own profile" ON public.profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- ── user_preferences table ───────────────────────────────────

DROP POLICY IF EXISTS "Users manage own preferences"        ON public.user_preferences;
DROP POLICY IF EXISTS "Users can insert own preferences"    ON public.user_preferences;
DROP POLICY IF EXISTS "Users can view own preferences"      ON public.user_preferences;
DROP POLICY IF EXISTS "Users can update own preferences"    ON public.user_preferences;

CREATE POLICY "Users can insert own preferences" ON public.user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own preferences" ON public.user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON public.user_preferences
    FOR UPDATE USING (auth.uid() = user_id);
