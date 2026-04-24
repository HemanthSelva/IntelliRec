# IntelliRec - Complete Project Context

## Project Overview
IntelliRec is a startup-level AI-powered E-Commerce 
Recommendation Engine built as an internship project for 
Sourcesys Technologies.

## Team
- Hemanthselva A K (Team Lead & Full-Stack AI)
- Monish Kaarthi R K (ML Engineer)
- Vishal K S (Data Scientist)
- Vishal M (Backend Developer)

## Tech Stack
- Frontend: Streamlit
- Authentication & Database: Supabase (PostgreSQL)
- ML Models: scikit-surprise (SVD), scikit-learn (TF-IDF), 
  vaderSentiment
- Charts: Plotly
- Deployment: Streamlit Cloud

## Three ML Engines
1. Collaborative Filtering - SVD Matrix Factorization
2. Content-Based Filtering - TF-IDF + Cosine Similarity
3. Sentiment-Aware Hybrid - CF + CBF + VADER sentiment

## Datasets
- ratings_Electronics.csv (7.8M user ratings from Kaggle)
- amazon_products.csv (1.4M products from Kaggle)
- Located at: D:\Desktop\IntelliRec\data\

## Current Status
- Phase 1 COMPLETE: Full frontend with dummy data
- Phase 2 PENDING: Supabase auth + ML models + real data

## Supabase Database Schema
Tables needed:
- users (id, email, full_name, username, created_at, 
  preferred_categories, avatar_color)
- recommendations (id, user_id, product_id, score, 
  engine_used, explanation, created_at)
- wishlist (id, user_id, product_id, added_at)
- feedback (id, user_id, product_id, is_positive, created_at)
- user_preferences (user_id, categories, min_price, 
  max_price, min_rating, updated_at)

## File Structure
D:\Desktop\IntelliRec\
├── app.py
├── PROJECT_CONTEXT.md (this file)
├── assets/ (logo, CSS, sample data)
├── auth/ (login, signup, session)
├── pages/ (7 pages)
├── models/ (ML model stubs - Phase 2)
├── utils/ (helper functions - Phase 2)
├── data/ (datasets go here)
├── saved_models/ (trained .pkl files - Phase 2)
└── requirements.txt

## Phase Roadmap
Phase 1 - Frontend (DONE)
Phase 2A - Supabase auth integration (DONE)
Phase 2B - Load real datasets (DONE — utils/data_loader.py)
Phase 2C - Train ML models (DONE — models/ + scripts/train_models.py)
Phase 2D - Connect models to UI (DONE — pages/02_For_You.py + 05_Analytics.py)
Phase 2E - Deploy to Streamlit Cloud (PENDING)
Phase 3 - GitHub push + documentation (PENDING)

## Auth Configuration (Phase 2A — Complete)
- Supabase email confirmation is ON (users must verify before login)
- Google OAuth is configured in Supabase (provider: google)
- GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are in .env
- Redirect URL for local dev: http://localhost:8501
- After deployment: update Supabase Site URL to Streamlit Cloud URL
  (Auth → URL Configuration in Supabase dashboard)
- All 5 database tables are created and working:
  profiles, user_preferences, wishlist, feedback, recommendation_history
- Email confirmation link lands on app.py with ?token_hash=&type= params
  which are handled at the top of app.py before init_session()

## Important Notes
- Always read this file before starting any task
- Datasets are large - use 500K row sampling
- scikit-surprise needs C++ build tools on Windows
  (use pre-built wheel or conda install)
- Light theme is default, dark mode toggle exists
