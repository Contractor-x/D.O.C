# TODO: Fix All Failing Tests

## Age Verification Module
- [x] Fix age categorization in `age_checker.py` - elderly patients (75+) should be categorized as "geriatric" not "adult"
- [x] Fix pediatric criteria checking - ensure "pediatric" is included in checked_criteria for children

## Dosage Validation Module
- [ ] Fix safety status classification in `range_validator.py` - excessive doses should return "unsafe" not "high_risk"

## NLP Module
- [ ] Fix API key issues for ExplanationGenerator and VoiceTranscription (mock or provide test keys)
- [ ] Implement missing methods in SentimentAnalysis:
  - [ ] `analyze_patient_sentiment`
  - [ ] `analyze_side_effect_reports`
  - [ ] `detect_urgency_signals`
- [ ] Implement missing methods in MedicalNER:
  - [ ] `extract_medical_entities`
  - [ ] `extract_drug_entities`
  - [ ] `extract_symptom_entities`
  - [ ] `extract_dosage_entities`
  - [ ] `classify_medical_text`

## Testing
- [ ] Run full test suite after fixes
- [ ] Ensure all modules pass their tests
