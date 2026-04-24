# IntelliRec — AI-Powered E-Commerce Recommendation Engine

> Internship Project — Sourcesys Technologies 2026

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://intellirec.streamlit.app)

## Team
| Name | Role |
|---|---|
| Hemanthselva AK | Team Lead & ML Engineer |
| Monish Kaarthi RK | Backend Developer |
| Vishal KS | Data Engineer |
| Vishal M | Frontend Developer |

## Overview
IntelliRec is a triple-engine AI recommendation system
that combines three powerful algorithms to deliver
personalized e-commerce product recommendations.

### Three AI Engines
| Engine | Algorithm | Best For |
|---|---|---|
| Collaborative Filtering | SVD Matrix Factorization | User behavior patterns |
| Content-Based | TF-IDF + Cosine Similarity | Product similarity |
| Hybrid Sentiment-Aware | CF + CBF + VADER | Best overall accuracy |

### Performance Metrics
| Model | RMSE | Precision@10 | F1 Score |
|---|---|---|---|
| Collaborative (SVD) | 1.14 | 21% | 0.34 |
| Content-Based (TF-IDF) | 0.95 | 60% | 0.55 |
| Hybrid Sentiment-Aware | 1.04 | 23.5% | 0.38 |

## Tech Stack
- **Frontend:** Streamlit (Python)
- **Auth & Database:** Supabase (PostgreSQL)
- **ML Models:** scikit-surprise, scikit-learn, VADER
- **Charts:** Plotly
- **Model Storage:** HuggingFace Hub
- **Dataset:** Amazon Reviews 2023 — McAuley Lab UCSD

## Features
- Triple AI engine recommendations
- Real-time sentiment analysis on 1.4M+ products
- Email authentication with confirmation
- Google OAuth sign-in
- Wishlist, cart, notifications system
- Light/Dark/System theme
- AI chatbot assistant
- Analytics dashboard with model comparison

## Dataset
- 998,751 Amazon reviews (Electronics + Home & Kitchen)
- 400,000 product metadata records
- Source: https://amazon-reviews-2023.github.io/

## Local Setup
1. Clone repo: `git clone https://github.com/HemanthSelva/IntelliRec`
2. Install: `pip install -r requirements.txt`
3. Create `.env` file with your API keys
4. Train models: `python scripts/train_models.py`
5. Run: `streamlit run app.py`

## Environment Variables
Create `.env` file with:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GROK_API_KEY=your_grok_api_key
```

## Project Structure
```
IntelliRec/
├── app.py              Main application
├── pages/              7 Streamlit pages
├── auth/               Authentication system
├── models/             ML model classes
├── utils/              Helper utilities
├── database/           Supabase operations
├── scripts/            Training scripts
├── assets/             CSS and static files
└── notebooks/          Jupyter notebook
```

## Acknowledgements
Dataset: He, R., & McAuley, J. (2023).
Amazon Reviews 2023. UCSD.
