"""
Drug news aggregator for latest pharmaceutical information.
"""

import requests
import feedparser
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re


class DrugNewsAggregator:
    """Aggregates drug-related news from various sources."""

    NEWS_SOURCES = [
        {
            'name': 'FDA News',
            'url': 'https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/drug-safety-communications/rss.xml',
            'type': 'rss'
        },
        {
            'name': 'NIH News',
            'url': 'https://www.nih.gov/news-events/news-releases/feed',
            'type': 'rss'
        },
        {
            'name': 'MedlinePlus Drug News',
            'url': 'https://medlineplus.gov/feeds/drugnews.xml',
            'type': 'rss'
        }
    ]

    def __init__(self):
        """Initialize news aggregator."""
        self.session = requests.Session()

    def get_latest_news(self, drug_name: Optional[str] = None, days_back: int = 7, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get latest drug-related news.

        Args:
            drug_name: Specific drug to search for (optional)
            days_back: Number of days to look back
            max_results: Maximum number of results

        Returns:
            List of news articles
        """
        all_news = []

        for source in self.NEWS_SOURCES:
            try:
                news_items = self._fetch_source_news(source, days_back)
                all_news.extend(news_items)
            except Exception as e:
                all_news.append({
                    "error": f"Failed to fetch from {source['name']}: {str(e)}",
                    "source": source['name']
                })

        # Filter by drug name if specified
        if drug_name:
            all_news = [item for item in all_news if self._contains_drug_reference(item, drug_name)]

        # Sort by date (newest first) and limit results
        all_news = sorted(all_news, key=lambda x: x.get('published_date', datetime.min), reverse=True)
        return all_news[:max_results]

    def _fetch_source_news(self, source: Dict[str, Any], days_back: int) -> List[Dict[str, Any]]:
        """Fetch news from a specific source."""
        news_items = []

        try:
            if source['type'] == 'rss':
                feed = feedparser.parse(source['url'])

                cutoff_date = datetime.now() - timedelta(days=days_back)

                for entry in feed.entries:
                    published_date = self._parse_date(entry.get('published_parsed'))

                    if published_date and published_date >= cutoff_date:
                        news_item = {
                            'title': entry.get('title', 'No title'),
                            'summary': self._clean_html(entry.get('summary', '')),
                            'url': entry.get('link', ''),
                            'published_date': published_date.isoformat(),
                            'source': source['name'],
                            'drug_mentions': self._extract_drug_mentions(entry.get('title', '') + ' ' + entry.get('summary', ''))
                        }
                        news_items.append(news_item)

        except Exception as e:
            news_items.append({
                "error": str(e),
                "source": source['name']
            })

        return news_items

    def _parse_date(self, date_tuple) -> Optional[datetime]:
        """Parse date from RSS feed."""
        if not date_tuple:
            return None

        try:
            return datetime(*date_tuple[:6])
        except (ValueError, TypeError):
            return None

    def _clean_html(self, html_text: str) -> str:
        """Clean HTML tags from text."""
        # Simple HTML tag removal
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        # Decode common HTML entities
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('<', '<')
        clean_text = clean_text.replace('>', '>')
        clean_text = clean_text.replace('"', '"')
        return clean_text.strip()

    def _extract_drug_mentions(self, text: str) -> List[str]:
        """Extract drug names mentioned in text."""
        # Common drug name patterns
        drug_patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Proper nouns that might be drug names
            r'\b\d+\s*mg\b',  # Dosages
            r'\b\d+\s*mcg\b'
        ]

        mentions = []
        for pattern in drug_patterns:
            matches = re.findall(pattern, text)
            mentions.extend(matches)

        return list(set(mentions))  # Remove duplicates

    def _contains_drug_reference(self, news_item: Dict[str, Any], drug_name: str) -> bool:
        """Check if news item contains reference to specific drug."""
        text_to_check = (news_item.get('title', '') + ' ' + news_item.get('summary', '')).lower()
        drug_lower = drug_name.lower()

        # Check for exact match or common variations
        if drug_lower in text_to_check:
            return True

        # Check drug mentions
        mentions = news_item.get('drug_mentions', [])
        for mention in mentions:
            if drug_lower in mention.lower():
                return True

        return False

    def get_fda_alerts(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Get FDA drug safety alerts.

        Args:
            max_results: Maximum number of alerts

        Returns:
            List of FDA alerts
        """
        try:
            # FDA drug safety communications RSS
            fda_url = "https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/drug-safety-communications/rss.xml"
            feed = feedparser.parse(fda_url)

            alerts = []
            for entry in feed.entries[:max_results]:
                alert = {
                    'title': entry.get('title', 'No title'),
                    'summary': self._clean_html(entry.get('summary', '')),
                    'url': entry.get('link', ''),
                    'published_date': self._parse_date(entry.get('published_parsed')).isoformat() if entry.get('published_parsed') else None,
                    'source': 'FDA Drug Safety',
                    'alert_type': 'safety_communication',
                    'drug_mentions': self._extract_drug_mentions(entry.get('title', '') + ' ' + entry.get('summary', ''))
                }
                alerts.append(alert)

            return alerts

        except Exception as e:
            return [{
                "error": str(e),
                "source": "FDA Drug Safety"
            }]

    def search_drug_news(self, drug_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for news specifically about a drug.

        Args:
            drug_name: Name of the drug
            max_results: Maximum results

        Returns:
            List of drug-specific news
        """
        return self.get_latest_news(drug_name=drug_name, max_results=max_results)
