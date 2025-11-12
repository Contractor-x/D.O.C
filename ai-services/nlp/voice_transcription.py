"""
Voice transcription service using OpenAI Whisper API.
"""

import os
import tempfile
from typing import Dict, Any, Optional, BinaryIO
import openai
from pathlib import Path


class VoiceTranscription:
    """Handles voice transcription for patient logs and medical notes."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")

        openai.api_key = self.api_key

    def transcribe_audio_file(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to audio file
            language: Language code (default: 'en')

        Returns:
            Dict containing transcription and metadata
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="json"
                )

            return {
                "transcription": transcript["text"].strip(),
                "language": language,
                "confidence": transcript.get("confidence", 0.0),
                "duration": transcript.get("duration", 0.0),
                "model": "whisper-1",
                "success": True
            }

        except Exception as e:
            return {
                "transcription": "",
                "error": str(e),
                "language": language,
                "success": False
            }

    def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "audio.wav", language: str = "en") -> Dict[str, Any]:
        """
        Transcribe audio from bytes.

        Args:
            audio_bytes: Audio data as bytes
            filename: Filename for temporary file
            language: Language code

        Returns:
            Dict containing transcription and metadata
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            # Transcribe the temporary file
            result = self.transcribe_audio_file(temp_file_path, language)

            # Clean up temporary file
            Path(temp_file_path).unlink(missing_ok=True)

            return result

        except Exception as e:
            return {
                "transcription": "",
                "error": str(e),
                "language": language,
                "success": False
            }

    def transcribe_medical_note(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe medical note with medical terminology optimization.

        Args:
            audio_file_path: Path to audio file

        Returns:
            Dict with medical note transcription
        """
        # Use English medical context
        result = self.transcribe_audio_file(audio_file_path, language="en")

        if result["success"]:
            # Add medical context metadata
            result.update({
                "note_type": "medical_note",
                "contains_medical_terms": self._detect_medical_terms(result["transcription"]),
                "estimated_word_count": len(result["transcription"].split())
            })

        return result

    def _detect_medical_terms(self, text: str) -> bool:
        """
        Simple detection of medical terminology in text.

        Args:
            text: Transcribed text

        Returns:
            Boolean indicating presence of medical terms
        """
        medical_terms = [
            "mg", "ml", "dose", "medication", "prescription", "symptoms",
            "diagnosis", "treatment", "patient", "doctor", "nurse",
            "hospital", "clinic", "pain", "fever", "blood", "heart"
        ]

        text_lower = text.lower()
        return any(term in text_lower for term in medical_terms)

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for transcription.

        Returns:
            List of language codes
        """
        return [
            "en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh",
            "ar", "hi", "bn", "pa", "te", "mr", "ur", "gu", "ta", "kn"
        ]
