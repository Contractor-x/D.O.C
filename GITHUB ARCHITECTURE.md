bash
```
D.O.C/
│
├── README.md
├── .gitignore
├── LICENSE
├── CONTRIBUTING.md
├── GITHUB ARCHITECTURE.md
│
├── frontend/                          # FRONTEND DEVELOPER'S WORKSPACE
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── .env.example
│   ├── .env
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.png
│   │   └── robots.txt
│   │
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── index.css
│   │   │
│   │   ├── assets/
│   │   │   ├── images/
│   │   │   │   ├── logo.svg
│   │   │   │   ├── placeholder-drug.png
│   │   │   │   └── doctor-icon.png
│   │   │   └── icons/
│   │   │       ├── camera.svg
│   │   │       ├── warning.svg
│   │   │       └── success.svg
│   │   │
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── Navbar.jsx
│   │   │   │   ├── LoadingSpinner.jsx
│   │   │   │   ├── ErrorBoundary.jsx
│   │   │   │   ├── Toast.jsx
│   │   │   │   └── Modal.jsx
│   │   │   │
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   ├── RegisterForm.jsx
│   │   │   │   ├── ForgotPassword.jsx
│   │   │   │   └── ProtectedRoute.jsx
│   │   │   │
│   │   │   ├── camera/
│   │   │   │   ├── CameraCapture.jsx
│   │   │   │   ├── DrugPreview.jsx
│   │   │   │   ├── IdentificationResult.jsx
│   │   │   │   └── MultipleDrugView.jsx
│   │   │   │
│   │   │   ├── sideEffects/
│   │   │   │   ├── SideEffectCard.jsx
│   │   │   │   ├── SideEffectList.jsx
│   │   │   │   ├── SeverityBadge.jsx
│   │   │   │   └── FilterOptions.jsx
│   │   │   │
│   │   │   ├── ageVerification/
│   │   │   │   ├── AgeInputForm.jsx
│   │   │   │   ├── SafetyResult.jsx
│   │   │   │   ├── RiskIndicator.jsx
│   │   │   │   └── RecommendationCard.jsx
│   │   │   │
│   │   │   ├── dosage/
│   │   │   │   ├── DosageComparisonCard.jsx
│   │   │   │   ├── PrescriptionUpload.jsx
│   │   │   │   ├── DosageCalculator.jsx
│   │   │   │   └── DoctorPrescriptionView.jsx
│   │   │   │
│   │   │   ├── triage/
│   │   │   │   ├── DocumentUploader.jsx
│   │   │   │   ├── DocumentList.jsx
│   │   │   │   ├── DocumentViewer.jsx
│   │   │   │   ├── DoctorContactCard.jsx
│   │   │   │   ├── AddDoctorForm.jsx
│   │   │   │   └── EmergencyContacts.jsx
│   │   │   │
│   │   │   ├── research/
│   │   │   │   ├── ResearchFeed.jsx
│   │   │   │   ├── ResearchCard.jsx
│   │   │   │   ├── IllnessFilter.jsx
│   │   │   │   ├── BookmarkButton.jsx
│   │   │   │   └── ShareButton.jsx
│   │   │   │
│   │   │   └── logging/
│   │   │       ├── TextLogInput.jsx
│   │   │       ├── VoiceRecorder.jsx
│   │   │       ├── LogList.jsx
│   │   │       ├── LogDetail.jsx
│   │   │       ├── SendToDoctor.jsx
│   │   │       └── LogAnalytics.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Register.jsx
│   │   │   │   └── ForgotPassword.jsx
│   │   │   │
│   │   │   ├── Dashboard.jsx
│   │   │   ├── CameraScanner.jsx
│   │   │   ├── SideEffects.jsx
│   │   │   ├── AgeVerification.jsx
│   │   │   ├── DosageConfirmation.jsx
│   │   │   ├── MedicalTriage.jsx
│   │   │   ├── ResearchUpdates.jsx
│   │   │   ├── PatientLogging.jsx
│   │   │   └── Profile.jsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   ├── useCamera.js
│   │   │   ├── useVoiceRecorder.js
│   │   │   ├── useGeolocation.js
│   │   │   ├── useLocalStorage.js
│   │   │   └── useDebounce.js
│   │   │
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   ├── ThemeContext.jsx
│   │   │   ├── MedicationContext.jsx
│   │   │   └── NotificationContext.jsx
│   │   │
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── auth.service.js
│   │   │   ├── drug.service.js
│   │   │   ├── ocr.service.js
│   │   │   ├── sideEffects.service.js
│   │   │   ├── dosage.service.js
│   │   │   ├── triage.service.js
│   │   │   ├── research.service.js
│   │   │   └── logging.service.js
│   │   │
│   │   ├── utils/
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   ├── validators.js
│   │   │   ├── formatters.js
│   │   │   └── imageProcessing.js
│   │   │
│   │   └── styles/
│   │       ├── global.css
│   │       ├── variables.css
│   │       └── animations.css
│   │
│   └── tests/
│       ├── components/
│       ├── pages/
│       └── utils/
│
├── backend/                           # BACKEND DEVELOPER'S WORKSPACE
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── setup.py
│   ├── pytest.ini
│   ├── .env.example
│   ├── .env
│   ├── Procfile                       # For deployment
│   ├── railway.json
│   ├── render.yaml
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── config.py                  # Configuration management
│   │   ├── dependencies.py
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   ├── camera.py
│   │   │   │   │   ├── drugs.py
│   │   │   │   │   ├── side_effects.py
│   │   │   │   │   ├── age_verification.py
│   │   │   │   │   ├── dosage.py
│   │   │   │   │   ├── triage.py
│   │   │   │   │   ├── research.py
│   │   │   │   │   └── logging.py
│   │   │   │   └── router.py
│   │   │   └── deps.py
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py
│   │   │   ├── security.py            # JWT, password hashing
│   │   │   ├── database.py            # Supabase connection
│   │   │   └── exceptions.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── medication.py
│   │   │   ├── side_effect.py
│   │   │   ├── document.py
│   │   │   ├── doctor_contact.py
│   │   │   ├── research.py
│   │   │   └── patient_log.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── medication.py
│   │   │   ├── side_effect.py
│   │   │   ├── age_check.py
│   │   │   ├── dosage.py
│   │   │   ├── document.py
│   │   │   ├── research.py
│   │   │   └── log.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   ├── drug_service.py
│   │   │   ├── side_effect_service.py
│   │   │   ├── age_service.py
│   │   │   ├── dosage_service.py
│   │   │   ├── document_service.py
│   │   │   ├── research_service.py
│   │   │   └── logging_service.py
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── helpers.py
│   │   │   ├── validators.py
│   │   │   ├── formatters.py
│   │   │   └── email.py
│   │   │
│   │   └── middleware/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── cors.py
│   │       ├── rate_limit.py
│   │       └── logging.py
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_drugs.py
│   │   ├── test_dosage.py
│   │   └── test_age_verification.py
│   │
│   └── scripts/
│       ├── init_db.py
│       ├── seed_data.py
│       └── migrate.py
│
├── ai-services/                       # AI DEVELOPER'S WORKSPACE
│   ├── requirements.txt
│   ├── .env.example
│   ├── .env
│   │
│   ├── ocr/
│   │   ├── __init__.py
│   │   ├── drug_ocr.py                # Tesseract OCR implementation
│   │   ├── prescription_ocr.py
│   │   ├── preprocessing.py           # Image enhancement
│   │   └── confidence_scorer.py
│   │
│   ├── drug_identification/
│   │   ├── __init__.py
│   │   ├── identifier.py              # Drug name matching
│   │   ├── fuzzy_matcher.py
│   │   └── ndc_lookup.py
│   │
│   ├── age_verification/
│   │   ├── __init__.py
│   │   ├── age_checker.py             # Beers Criteria implementation
│   │   ├── risk_scorer.py
│   │   ├── pediatric_rules.py
│   │   └── geriatric_rules.py
│   │
│   ├── dosage_validation/
│   │   ├── __init__.py
│   │   ├── dosage_calculator.py       # mg/kg calculations
│   │   ├── range_validator.py
│   │   └── renal_adjustment.py
│   │
│   ├── side_effects/
│   │   ├── __init__.py
│   │   ├── side_effect_extractor.py
│   │   ├── severity_classifier.py
│   │   └── interaction_checker.py
│   │
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── explanation_generator.py   # Claude/GPT integration
│   │   ├── voice_transcription.py     # Whisper API
│   │   ├── sentiment_analysis.py
│   │   └── medical_ner.py             # Named Entity Recognition
│   │
│   ├── research/
│   │   ├── __init__.py
│   │   ├── pubmed_scraper.py
│   │   ├── clinical_trials_api.py
│   │   ├── drug_news_aggregator.py
│   │   └── content_ranker.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── drug_classifier.pkl        # Pre-trained models
│   │   └── side_effect_predictor.pkl
│   │
│   ├── data/
│   │   ├── beers_criteria.json
│   │   ├── drug_database.json
│   │   ├── side_effects_db.json
│   │   ├── dosage_guidelines.json
│   │   └── drug_interactions.csv
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── api_client.py
│   │   ├── data_processor.py
│   │   └── cache_manager.py
│   │
│   └── tests/
│       ├── test_ocr.py
│       ├── test_age_verification.py
│       ├── test_dosage.py
│       └── test_nlp.py
│
├── shared/                            # SHARED RESOURCES (All Team)
│   ├── docs/
│   │   ├── API_DOCUMENTATION.md
│   │   ├── ARCHITECTURE.md
│   │   ├── DEPLOYMENT.md
│   │   ├── USER_GUIDE.md
│   │   └── CONTRIBUTING.md
│   │
│   ├── scripts/
│   │   ├── setup_dev_env.sh
│   │   ├── run_tests.sh
│   │   ├── deploy.sh
│   │   └── backup_db.sh
│   │
│   ├── database/
│   │   ├── schema.sql
│   │   ├── migrations/
│   │   │   ├── 001_initial_schema.sql
│   │   │   ├── 002_add_documents_table.sql
│   │   │   └── 003_add_research_table.sql
│   │   └── seeds/
│   │       ├── users.sql
│   │       └── sample_drugs.sql
│   │
│   └── postman/
│       └── DOC_API_Collection.json
│
```
