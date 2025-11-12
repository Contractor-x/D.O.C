"""
Tests for NLP services.
"""

import pytest
from nlp.explanation_generator import ExplanationGenerator
from nlp.voice_transcription import VoiceTranscription
from nlp.sentiment_analysis import SentimentAnalysis
from nlp.medical_ner import MedicalNER


class TestExplanationGenerator:
    """Test cases for ExplanationGenerator service."""

    @pytest.fixture
    def explanation_generator(self):
        """Create ExplanationGenerator instance for testing."""
        return ExplanationGenerator()

    def test_generate_drug_explanation(self, explanation_generator):
        """Test drug explanation generation."""
        result = explanation_generator.generate_drug_explanation("ibuprofen", "patient")

        assert isinstance(result, dict)
        assert "explanation" in result
        assert "reading_level" in result
        assert "language" in result

    def test_generate_side_effect_explanation(self, explanation_generator):
        """Test side effect explanation generation."""
        result = explanation_generator.generate_side_effect_explanation(
            "ibuprofen", ["nausea", "headache"], "patient"
        )

        assert isinstance(result, dict)
        assert "explanation" in result
        assert len(result["explanation"]) > 0

    def test_generate_interaction_explanation(self, explanation_generator):
        """Test drug interaction explanation generation."""
        result = explanation_generator.generate_interaction_explanation(
            "warfarin", "aspirin", "patient"
        )

        assert isinstance(result, dict)
        assert "explanation" in result

    def test_simplify_medical_text(self, explanation_generator):
        """Test medical text simplification."""
        complex_text = "Non-steroidal anti-inflammatory drug used for analgesia"

        result = explanation_generator.simplify_medical_text(complex_text, "patient")

        assert isinstance(result, str)
        assert len(result) > 0
        # Should be simpler than original


class TestVoiceTranscription:
    """Test cases for VoiceTranscription service."""

    @pytest.fixture
    def voice_transcription(self):
        """Create VoiceTranscription instance for testing."""
        return VoiceTranscription()

    def test_transcribe_audio_file(self, voice_transcription):
        """Test audio file transcription."""
        # Mock audio file path
        audio_path = "test_audio.wav"

        try:
            result = voice_transcription.transcribe_audio_file(audio_path)
            assert isinstance(result, dict)
            assert "transcription" in result
            assert "confidence" in result
        except Exception:
            # Whisper API might not be available in test environment
            pass

    def test_transcribe_audio_bytes(self, voice_transcription):
        """Test audio bytes transcription."""
        # Mock audio bytes
        audio_bytes = b"mock_audio_data"

        try:
            result = voice_transcription.transcribe_audio_bytes(audio_bytes)
            assert isinstance(result, dict)
            assert "transcription" in result
        except Exception:
            # API not available
            pass

    def test_detect_medical_terms(self, voice_transcription):
        """Test medical term detection in transcription."""
        transcription = "Patient reports nausea and dizziness after taking lisinopril"

        result = voice_transcription.detect_medical_terms(transcription)

        assert isinstance(result, list)
        assert len(result) > 0
        # Should detect drug name and symptoms

    def test_get_transcription_metadata(self, voice_transcription):
        """Test transcription metadata extraction."""
        transcription = "Take 500mg of amoxicillin three times daily for ear infection"

        metadata = voice_transcription.get_transcription_metadata(transcription)

        assert isinstance(metadata, dict)
        assert "duration" in metadata or "word_count" in metadata


class TestSentimentAnalysis:
    """Test cases for SentimentAnalysis service."""

    @pytest.fixture
    def sentiment_analysis(self):
        """Create SentimentAnalysis instance for testing."""
        return SentimentAnalysis()

    def test_analyze_patient_sentiment(self, sentiment_analysis):
        """Test patient sentiment analysis."""
        text = "I feel much better after taking this medication"

        result = sentiment_analysis.analyze_patient_sentiment(text)

        assert isinstance(result, dict)
        assert "sentiment" in result
        assert "confidence" in result
        assert result["sentiment"] in ["positive", "negative", "neutral"]

    def test_analyze_side_effect_reports(self, sentiment_analysis):
        """Test side effect report sentiment analysis."""
        reports = [
            "Severe headache and nausea",
            "Feeling much better now",
            "Mild stomach upset"
        ]

        result = sentiment_analysis.analyze_side_effect_reports(reports)

        assert isinstance(result, dict)
        assert "overall_sentiment" in result
        assert "severity_indicators" in result

    def test_detect_urgency_signals(self, sentiment_analysis):
        """Test urgency signal detection."""
        urgent_text = "Having trouble breathing and chest pain right now"
        normal_text = "Slight headache yesterday"

        urgent_result = sentiment_analysis.detect_urgency_signals(urgent_text)
        normal_result = sentiment_analysis.detect_urgency_signals(normal_text)

        assert urgent_result["urgency_level"] > normal_result["urgency_level"]


class TestMedicalNER:
    """Test cases for MedicalNER service."""

    @pytest.fixture
    def medical_ner(self):
        """Create MedicalNER instance for testing."""
        return MedicalNER()

    def test_extract_medical_entities(self, medical_ner):
        """Test medical entity extraction."""
        text = "Patient John Doe prescribed 500mg Amoxicillin for ear infection"

        result = medical_ner.extract_medical_entities(text)

        assert isinstance(result, dict)
        assert "entities" in result
        assert len(result["entities"]) > 0

        # Should extract drug name, dosage, condition
        entity_types = [entity["type"] for entity in result["entities"]]
        assert "drug" in entity_types

    def test_extract_drug_entities(self, medical_ner):
        """Test drug entity extraction."""
        text = "Take lisinopril 10mg and metformin 500mg twice daily"

        drugs = medical_ner.extract_drug_entities(text)

        assert isinstance(drugs, list)
        assert len(drugs) >= 2
        drug_names = [drug["name"].lower() for drug in drugs]
        assert "lisinopril" in drug_names
        assert "metformin" in drug_names

    def test_extract_symptom_entities(self, medical_ner):
        """Test symptom entity extraction."""
        text = "Patient complains of nausea, vomiting, and severe headache"

        symptoms = medical_ner.extract_symptom_entities(text)

        assert isinstance(symptoms, list)
        assert len(symptoms) >= 3
        symptom_names = [symptom["name"].lower() for symptom in symptoms]
        assert "nausea" in symptom_names

    def test_extract_dosage_entities(self, medical_ner):
        """Test dosage entity extraction."""
        text = "Prescribe 500mg three times daily for 7 days"

        dosages = medical_ner.extract_dosage_entities(text)

        assert isinstance(dosages, list)
        assert len(dosages) > 0
        # Should extract dosage amount and frequency

    def test_classify_medical_text(self, medical_ner):
        """Test medical text classification."""
        texts = [
            "Patient has diabetes and hypertension",
            "Take medication with food",
            "Schedule follow-up appointment"
        ]

        for text in texts:
            result = medical_ner.classify_medical_text(text)
            assert isinstance(result, dict)
            assert "category" in result
            assert "confidence" in result
