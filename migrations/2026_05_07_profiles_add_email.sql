-- IntelliRec — add missing `email` column to public.profiles
--
-- Five places in the app code (app.py:144, auth/session.py:123 / 432 / 454 / 464,
-- plus the duplicate-email check at session.py:98 and 220) read or write
-- profiles.email but the column is not in the actual schema.  Result:
--   PGRST204 "Could not find the 'email' column of 'profiles' in the schema cache"
-- which silently aborts the profile INSERT during sign-up.  The cascade is:
--   1. Google sign-in succeeds in auth.users.
--   2. INSERT into public.profiles fails (no email column).
--   3. INSERT into public.user_preferences fails with FK violation
--      ("Key is not present in table 'profiles'") because no profile exists.
--   4. Save Preferences in My Profile shows the FK error to the user.
--
-- Run this in the Supabase SQL Editor.  Idempotent (uses IF NOT EXISTS),
-- safe to re-run.

alter table public.profiles
    add column if not exists email text;

-- Backfill from auth.users so existing rows pick up their email.
-- Safe no-op for fresh installs (no rows to update).
update public.profiles p
   set email = u.email
  from auth.users u
 where p.id = u.id
   and p.email is null;
