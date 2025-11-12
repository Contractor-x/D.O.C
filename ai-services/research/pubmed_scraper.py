"""
PubMed research scraper for medical literature.
"""

import requests
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET


class PubMedScraper:
    """Scrapes PubMed for medical research articles."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    SEARCH_URL = BASE_URL + "esearch.fcgi"
    FETCH_URL = BASE_URL + "efetch.fcgi"

    def __init__(self, api_key: Optional[str] = None, email: str = "doc-platform@example.com"):
        """
        Initialize PubMed scraper.

        Args:
            api_key: NCBI API key for higher rate limits
            email: Email for NCBI identification
        """
        self.api_key = api_key
        self.email = email
        self.session = requests.Session()

    def search_articles(self, query: str, max_results: int = 10, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Search for recent medical articles.

        Args:
            query: Search query (e.g., "cancer immunotherapy")
            max_results: Maximum number of results
            days_back: Search within last N days

        Returns:
            List of article dictionaries
        """
        try:
            # Build date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)

            date_query = f'("{start_date.strftime("%Y/%m/%d")}"[Date - Publication] : "{end_date.strftime("%Y/%m/%d")}"[Date - Publication])'

            full_query = f"{query} AND {date_query}"

            # Search for article IDs
            search_params = {
                'db': 'pubmed',
                'term': full_query,
                'retmax': max_results,
                'retmode': 'json',
                'email': self.email
            }

            if self.api_key:
                search_params['api_key'] = self.api_key

            search_response = self.session.get(self.SEARCH_URL, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            article_ids = search_data.get('esearchresult', {}).get('idlist', [])

            if not article_ids:
                return []

            # Fetch article details
            articles = self._fetch_articles(article_ids)

            return articles

        except Exception as e:
            return [{
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }]

    def _fetch_articles(self, article_ids: List[str]) -> List[Dict[str, Any]]:
        """Fetch detailed article information."""
        articles = []

        # Process in batches of 10 to avoid API limits
        for i in range(0, len(article_ids), 10):
            batch_ids = article_ids[i:i+10]

            try:
                fetch_params = {
                    'db': 'pubmed',
                    'id': ','.join(batch_ids),
                    'retmode': 'xml',
                    'email': self.email
                }

                if self.api_key:
                    fetch_params['api_key'] = self.api_key

                fetch_response = self.session.get(self.FETCH_URL, params=fetch_params)
                fetch_response.raise_for_status()

                # Parse XML response
                batch_articles = self._parse_pubmed_xml(fetch_response.text)
                articles.extend(batch_articles)

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                articles.append({
                    "error": f"Failed to fetch batch {i//10}: {str(e)}",
                    "article_ids": batch_ids
                })

        return articles

    def _parse_pubmed_xml(self, xml_content: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response."""
        articles = []

        try:
            root = ET.fromstring(xml_content)

            for article in root.findall('.//PubmedArticle'):
                article_data = {}

                # Extract PMID
                pmid_elem = article.find('.//PMID')
                article_data['pmid'] = pmid_elem.text if pmid_elem is not None else None

                # Extract title
                title_elem = article.find('.//ArticleTitle')
                article_data['title'] = title_elem.text if title_elem is not None else "No title"

                # Extract abstract
                abstract_elem = article.find('.//AbstractText')
                article_data['abstract'] = abstract_elem.text if abstract_elem is not None else "No abstract"

                # Extract authors
                authors = []
                for author in article.findall('.//Author'):
                    last_name = author.find('LastName')
                    fore_name = author.find('ForeName')
                    if last_name is not None:
                        author_name = last_name.text
                        if fore_name is not None:
                            author_name += f" {fore_name.text}"
                        authors.append(author_name)

                article_data['authors'] = authors

                # Extract journal
                journal_elem = article.find('.//Journal/Title')
                article_data['journal'] = journal_elem.text if journal_elem is not None else "Unknown journal"

                # Extract publication date
                pub_date = article.find('.//PubDate')
                if pub_date is not None:
                    year = pub_date.find('Year')
                    month = pub_date.find('Month')
                    day = pub_date.find('Day')

                    date_str = ""
                    if year is not None:
                        date_str += year.text
                    if month is not None:
                        date_str += f"-{month.text.zfill(2)}"
                    if day is not None:
                        date_str += f"-{day.text.zfill(2)}"

                    article_data['publication_date'] = date_str

                # Extract DOI
                doi_elem = article.find('.//ELocationID[@EIdType="doi"]')
                article_data['doi'] = doi_elem.text if doi_elem is not None else None

                # Add metadata
                article_data['source'] = 'PubMed'
                article_data['fetched_at'] = datetime.now().isoformat()

                articles.append(article_data)

        except Exception as e:
            articles.append({
                "error": f"XML parsing failed: {str(e)}",
                "xml_length": len(xml_content)
            })

        return articles

    def search_disease_research(self, disease: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for research on a specific disease.

        Args:
            disease: Disease name
            max_results: Maximum results

        Returns:
            List of research articles
        """
        query = f'"{disease}"[MeSH Terms] OR "{disease}"[Title/Abstract]'
        return self.search_articles(query, max_results, days_back=90)

    def search_drug_research(self, drug_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for research on a specific drug.

        Args:
            drug_name: Drug name
            max_results: Maximum results

        Returns:
            List of research articles
        """
        query = f'"{drug_name}"[MeSH Terms] OR "{drug_name}"[Title/Abstract]'
        return self.search_articles(query, max_results, days_back=180)
