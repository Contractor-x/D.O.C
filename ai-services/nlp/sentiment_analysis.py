"""
Sentiment analysis for patient feedback and medical communications.
"""

import re
from typing import Dict, Any, List
from transformers import pipeline


class SentimentAnalysis:
    """Analyzes sentiment in patient communications and feedback."""

    def __init__(self):
        """Initialize sentiment analysis pipeline."""
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
        except Exception:
            # Fallback to basic sentiment analysis
            self.sentiment_pipeline = None

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment scores and classification
        """
        if not text or not text.strip():
            return {
                "text": text,
                "sentiment": "neutral",
                "confidence": 0.0,
                "scores": {"positive": 0.0, "neutral": 1.0, "negative": 0.0},
                "error": "Empty text provided"
            }

        try:
            if self.sentiment_pipeline:
                # Use transformer model
                results = self.sentiment_pipeline(text)
                if results and len(results[0]) > 0:
                    scores = {item['label'].lower(): item['score'] for item in results[0]}

                    # Determine dominant sentiment
                    dominant = max(scores.items(), key=lambda x: x[1])

                    return {
                        "text": text,
                        "sentiment": dominant[0],
                        "confidence": dominant[1],
                        "scores": scores,
                        "model": "roberta-sentiment"
                    }
            else:
                # Fallback to rule-based analysis
                return self._rule_based_sentiment(text)

        except Exception as e:
            return self._rule_based_sentiment(text, error=str(e))

    def _rule_based_sentiment(self, text: str, error: str = None) -> Dict[str, Any]:
        """
        Rule-based sentiment analysis as fallback.

        Args:
            text: Text to analyze
            error: Optional error message

        Returns:
            Dict with sentiment analysis
        """
        text_lower = text.lower()

        # Positive indicators
        positive_words = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "helpful", "thank", "appreciate", "better", "improved", "satisfied",
            "happy", "pleased", "relieved", "comfortable", "effective"
        ]

        # Negative indicators
        negative_words = [
            "bad", "terrible", "awful", "horrible", "worst", "pain", "hurt",
            "worry", "concerned", "scared", "anxious", "uncomfortable",
            "difficult", "problem", "issue", "worse", "disappointed"
        ]

        # Medical context modifiers
        medical_positive = ["recovery", "healing", "improvement", "stable", "managing"]
        medical_negative = ["decline", "worsening", "complication", "emergency", "critical"]

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        # Medical context
        med_positive_count = sum(1 for word in medical_positive if word in text_lower)
        med_negative_count = sum(1 for word in medical_negative if word in text_lower)

        total_positive = positive_count + med_positive_count
        total_negative = negative_count + med_negative_count

        # Determine sentiment
        if total_positive > total_negative:
            sentiment = "positive"
            confidence = min(0.9, total_positive / max(1, total_positive + total_negative))
        elif total_negative > total_positive:
            sentiment = "negative"
            confidence = min(0.9, total_negative / max(1, total_positive + total_negative))
        else:
            sentiment = "neutral"
            confidence = 0.5

        scores = {
            "positive": total_positive / max(1, total_positive + total_negative + 1),
            "negative": total_negative / max(1, total_positive + total_negative + 1),
            "neutral": 1.0 - confidence
        }

        result = {
            "text": text,
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": scores,
            "model": "rule-based"
        }

        if error:
            result["error"] = error

        return result

    def analyze_patient_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """
        Analyze patient feedback with medical context.

        Args:
            feedback_text: Patient feedback text

        Returns:
            Dict with detailed feedback analysis
        """
        base_sentiment = self.analyze_sentiment(feedback_text)

        # Extract key themes from feedback
        themes = self._extract_feedback_themes(feedback_text)

        # Assess urgency level
        urgency = self._assess_urgency(feedback_text)

        base_sentiment.update({
            "feedback_themes": themes,
            "urgency_level": urgency,
            "analysis_type": "patient_feedback"
        })

        return base_sentiment

    def _extract_feedback_themes(self, text: str) -> List[str]:
        """
        Extract key themes from feedback text.

        Args:
            text: Feedback text

        Returns:
            List of identified themes
        """
        text_lower = text.lower()
        themes = []

        theme_keywords = {
            "medication_effectiveness": ["effective", "works", "helps", "better", "improved"],
            "side_effects": ["side effect", "nausea", "dizzy", "headache", "pain"],
            "ease_of_use": ["easy", "simple", "convenient", "difficult", "complicated"],
            "customer_service": ["support", "help", "staff", "doctor", "nurse"],
            "cost": ["expensive", "cheap", "affordable", "cost", "price"],
            "wait_time": ["wait", "delay", "quick", "fast", "slow"]
        }

        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)

        return themes

    def _assess_urgency(self, text: str) -> str:
        """
        Assess urgency level from text.

        Args:
            text: Text to analyze

        Returns:
            Urgency level string
        """
        text_lower = text.lower()

        urgent_keywords = [
            "emergency", "urgent", "immediately", "asap", "critical",
            "severe pain", "can't breathe", "chest pain", "unconscious"
        ]

        high_priority_keywords = [
            "worse", "declining", "deteriorating", "serious", "concerning"
        ]

        if any(keyword in text_lower for keyword in urgent_keywords):
            return "urgent"
        elif any(keyword in text_lower for keyword in high_priority_keywords):
            return "high"
        else:
            return "normal"
