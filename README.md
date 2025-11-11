# D.O.C - Digital Oversight Companion
___

![D.O.C Logo](./frontend/public/logo.png)

## Hackathon Project - AI-Powered Medication Management Platform

## What Is D.O.C?
D.O.C is an intelligent medication companion that helps patients manage their medications safely through AI-powered drug identification, age verification, dosage confirmation, and comprehensive health documentation.

---

##  Problem Statement

- **40%** of medication errors are age-related
- **7,000+** annual deaths from preventable medication mistakes
- Patients don't know if their medications are safe for their age
- No centralized system to track medications, documents, and doctor communications
- Terminal illness patients lack access to latest drug research

---

## Whats Our Solution?

D.O.C provides *7* intelligent features:

1. **Camera Drug Scanner** - Identify drugs via photo, get instant descriptions
2. **Side Effects Checker** - Comprehensive side effect database
3. **Age Verification** - AI validates drug safety for patient's age
4. **Dosage Confirmation** - Verify prescribed dosage accuracy
5. **Medical Triage** - Store documents, prescriptions, doctor contacts
6. **Research Updates** - Latest drug news for cancer/terminal illnesses
7. **Patient Logging** - Voice/text notes sent directly to doctors

**Unique Feature:** Handles multiple medications simultaneously

---

## Tech Stack

### Frontend
- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS
- **State Management:** Context API + React Query
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Camera:** react-webcam
- **Voice Recording:** react-media-recorder

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** JWT tokens
- **File Storage:** Supabase Storage
- **API Documentation:** Swagger/OpenAPI

### AI Services
- **OCR:** Tesseract, Google Cloud Vision API
- **NLP:** Claude API (Anthropic), OpenAI Whisper
- **Drug Data:** OpenFDA, RxNorm, DrugBank
- **Research:** PubMed API, ClinicalTrials.gov API

---

## 📦 Installation & Setup

### Prerequisites

Node.js 18+
Python 3.11+
Git
Tesseract OCR
___

Quick Start
1. # Clone Repository
git clone https://github.com/your-team/doc-medication-platform.git
cd doc-medication-platform

2. # Frontend Setup
cd frontend
npm install
cp .env.example .env

# Add your API keys to .env
npm run dev
3. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate 

# On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Add your API keys to .env
uvicorn app.main:app --reload

4. # AI Services Setup
cd ai-services
pip install -r requirements.txt
cp .env.example .env

# Add your API keys to .env
python -m ocr.drug_ocr  # Test OCR
## Environment Variables

# Frontend (.env)
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key

# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/doc
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
SECRET_KEY=your_jwt_secret_key
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_key
GOOGLE_CLOUD_VISION_KEY=your_google_vision_key

# AI Services (.env)
OPENFDA_API_KEY=not_required
RXNORM_API_KEY=not_required
PUBMED_API_KEY=your_pubmed_key
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_key

## API Endpoints
Authentication
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
GET    /api/v1/auth/me
Camera & Drug Identification
POST   /api/v1/camera/scan
GET    /api/v1/drugs/{drug_id}
POST   /api/v1/drugs/identify
POST   /api/v1/drugs/batch-scan
Side Effects
GET    /api/v1/side-effects/{drug_id}
GET    /api/v1/side-effects/interactions
POST   /api/v1/side-effects/report
Age Verification
POST   /api/v1/age-verification/check
GET    /api/v1/age-verification/beers-criteria
POST   /api/v1/age-verification/batch-check
Dosage Confirmation
POST   /api/v1/dosage/verify
POST   /api/v1/dosage/calculate
GET    /api/v1/dosage/guidelines/{drug_id}
Medical Triage
POST   /api/v1/triage/documents/upload
GET    /api/v1/triage/documents
DELETE /api/v1/triage/documents/{id}
POST   /api/v1/triage/doctors
GET    /api/v1/triage/doctors
PUT    /api/v1/triage/doctors/{id}
Research Updates
GET    /api/v1/research/latest
GET    /api/v1/research/by-illness/{illness}
POST   /api/v1/research/bookmark
GET    /api/v1/research/bookmarks
Patient Logging
POST   /api/v1/logs/text
POST   /api/v1/logs/voice
GET    /api/v1/logs
POST   /api/v1/logs/send-to-doctor
GET    /api/v1/logs/analytics
___


## UI/UX Flow
User Journey
Login → Dashboard → Camera Scanner → Results → Side Effects → 
Age Verification → Dosage Check → Save to Triage → Log Experience
Page Descriptions
1. Camera Scanner
Live camera feed
Capture multiple drugs at once
OCR processing indicator
Drug identification results
Brief description for each drug
2. Side Effects
List all identified drugs
Expandable side effect cards
Severity indicators (mild/moderate/severe)
Interaction warnings
Filter by severity
3. Age Verification
Input patient age
AI analyzes each drug for age-appropriateness
Risk score (0-10)
Recommendations
Alternative suggestions
4. Dosage Confirmation
Display prescribed dosage
Compare with recommended dosage
Show acceptable range
Flag over/under dosing
Doctor's prescription view
5. Medical Triage
Upload medical documents (PDF, images)
Document categorization (prescriptions, lab results, etc.)
Doctor contact management
Emergency contacts
Quick access to recent documents
6. Research Updates
Filter by illness type
Latest clinical trials
New drug approvals
Research summaries
Bookmark articles
Share with doctor
7. Patient Logging
Text entry for notes
Voice recording option
Categorize logs (side effects, mood, pain level)
Timeline view
Send specific logs to doctor
AI analysis of patterns

## AI Features & Models
1. OCR Drug Identification
Technology: Tesseract + Google Cloud Vision
Accuracy: 92%+
Process:
Image preprocessing (grayscale, denoise, contrast)
Text extraction
Drug name matching with fuzzy logic
NDC barcode detection
2. Age Risk Detection
Algorithm: Custom ML + Beers Criteria
Input: Drug name, dosage, patient age
Output: Risk score (0-10), recommendations
Rules:
40+ Beers Criteria drugs for elderly (65+)
Pediatric contraindications (<18)
Weight-based dosing for children
Renal function adjustments
3. Side Effect Prediction
Data Source: OpenFDA Adverse Events
Model: Classification + NLP
Features:
Common vs rare side effects
Severity classification
Drug-drug interactions
Food-drug interactions
4. Dosage Validation
Algorithm: Rule-based + ML
Checks:
Age-appropriate dosing
Weight-based calculations (mg/kg)
Renal dose adjustments
Maximum daily limits
Frequency validation
5. Voice Transcription
Technology: OpenAI Whisper API
Languages: 90+ supported
Features:
Real-time transcription
Medical terminology recognition
Speaker diarization
Sentiment analysis
6. Research Aggregation
Sources: PubMed, ClinicalTrials.gov, FDA
Algorithm: NLP + Content Ranking
Features:
Relevance scoring
Publication date weighting
Clinical trial phase filtering
Automatic summarization
7. AI Explanations
Technology: Claude API (Anthropic)
Purpose: Patient-friendly explanations
Reading Level: 8th grade
Languages: English, Spanish (expandable)

## Database Schema
Tables
users
id, email, password_hash, age, created_at
medications
id, user_id, drug_name, dosage, ndc_code, identified_at
side_effects
id, drug_id, effect_name, severity, frequency
age_checks
id, user_id, medication_id, age, risk_score, safe, checked_at
dosage_checks
id, medication_id, prescribed_dose, recommended_dose, within_range
documents
id, user_id, file_url, document_type, uploaded_at
doctor_contacts
id, user_id, doctor_name, specialty, phone, email
research_articles
id, title, summary, illness_type, publication_date, source_url
patient_logs
id, user_id, log_type, content, voice_url, sent_to_doctor, created_at

## Testing
Run Tests
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
pytest

# AI services tests
cd ai-services
pytest

# Deployment?
Frontend (Vercel)
cd frontend
vercel deploy --prod
Backend (Railway/Render)
cd backend

# Push to GitHub
# Connect repo to hosting platform.
# Auto-deploy on push
Environment
Frontend: https://doc-app.vercel.app
Backend API: https://doc-api.railway.app
Documentation: https://doc-api.railway.app/docs
___

## Team
*Frontend Developer* - React UI/UX Implementation

*Backend Developer* - FastAPI + Database Architecture

*AI Developer* - ML Models + NLP + OCR Services

## License
MIT License - See LICENSE file

## Acknowledgments
OpenFDA for drug data
Anthropic for Claude API
Beers Criteria for geriatric medication guidelines
___

## All open-source contributors
📞 Support
For issues: GitHub Issues
For questions: dada4ash@example.com
Built with 💲 for safer medication management
