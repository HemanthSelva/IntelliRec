-- IntelliRec — add `theme` column to user_preferences so the My Profile
-- "Save Preferences" button can persist the user's selected theme alongside
-- preferred_categories / preferred_engine / diversity_level.
--
-- Idempotent; safe to re-run.

alter table public.user_preferences
    add column if not exists theme text default 'light'
        check (theme in ('light', 'dark'));
