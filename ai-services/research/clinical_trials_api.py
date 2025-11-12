"""
ClinicalTrials.gov API client for clinical trial information.
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class ClinicalTrialsAPI:
    """Interface to ClinicalTrials.gov API."""

    BASE_URL = "https://clinicaltrials.gov/api/v2/studies"

    def __init__(self):
        """Initialize ClinicalTrials API client."""
        self.session = requests.Session()

    def search_trials(self, condition: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for clinical trials by condition.

        Args:
            condition: Medical condition (e.g., "breast cancer")
            max_results: Maximum number of results

        Returns:
            List of clinical trial dictionaries
        """
        try:
            params = {
                'query.cond': condition,
                'countTotal': 'true',
                'pageSize': max_results,
                'format': 'json'
            }

            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            trials = []
            for study in data.get('studies', []):
                trial_data = self._parse_trial_data(study)
                trials.append(trial_data)

            return trials

        except Exception as e:
            return [{
                "error": str(e),
                "condition": condition,
                "timestamp": datetime.now().isoformat()
            }]

    def _parse_trial_data(self, study: Dict[str, Any]) -> Dict[str, Any]:
        """Parse clinical trial data from API response."""
        protocol = study.get('protocolSection', {})

        # Basic info
        identification = protocol.get('identificationModule', {})
        nct_id = identification.get('nctId', 'Unknown')

        # Title
        title = "No title available"
        if 'officialTitle' in identification:
            title = identification['officialTitle']
        elif 'briefTitle' in identification:
            title = identification['briefTitle']

        # Status
        status_module = protocol.get('statusModule', {})
        status = status_module.get('overallStatus', 'Unknown')

        # Phase
        design = protocol.get('designModule', {})
        phases = design.get('phases', [])
        phase = ', '.join(phases) if phases else 'Not specified'

        # Conditions
        conditions_module = protocol.get('conditionsModule', {})
        conditions = conditions_module.get('conditions', [])

        # Interventions
        interventions_module = protocol.get('armsInterventionsModule', {})
        interventions = interventions_module.get('interventions', [])

        # Locations
        locations_module = protocol.get('locationsModule', {})
        locations = locations_module.get('locations', [])

        # Eligibility
        eligibility = protocol.get('eligibilityModule', {})
        criteria = eligibility.get('eligibilityCriteria', 'Not specified')
        min_age = eligibility.get('minimumAge', 'Not specified')
        max_age = eligibility.get('maximumAge', 'Not specified')

        # Sponsor
        sponsor_module = protocol.get('sponsorCollaboratorsModule', {})
        sponsors = sponsor_module.get('responsibleParty', {})

        return {
            'nct_id': nct_id,
            'title': title,
            'status': status,
            'phase': phase,
            'conditions': conditions,
            'interventions': interventions,
            'locations': locations,
            'eligibility_criteria': criteria,
            'age_range': f"{min_age} - {max_age}",
            'sponsor': sponsors.get('organization', 'Not specified'),
            'source': 'ClinicalTrials.gov',
            'fetched_at': datetime.now().isoformat()
        }

    def search_drug_trials(self, drug_name: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for clinical trials involving a specific drug.

        Args:
            drug_name: Drug name
            max_results: Maximum results

        Returns:
            List of clinical trials
        """
        try:
            params = {
                'query.intr': drug_name,
                'countTotal': 'true',
                'pageSize': max_results,
                'format': 'json'
            }

            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            trials = []
            for study in data.get('studies', []):
                trial_data = self._parse_trial_data(study)
                trials.append(trial_data)

            return trials

        except Exception as e:
            return [{
                "error": str(e),
                "drug": drug_name,
                "timestamp": datetime.now().isoformat()
            }]

    def get_trial_details(self, nct_id: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific clinical trial.

        Args:
            nct_id: Clinical trial NCT ID

        Returns:
            Detailed trial information
        """
        try:
            url = f"{self.BASE_URL}/{nct_id}"
            params = {'format': 'json'}

            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            study = data.get('study', {})
            return self._parse_trial_data(study)

        except Exception as e:
            return {
                "error": str(e),
                "nct_id": nct_id,
                "timestamp": datetime.now().isoformat()
            }

    def search_recruiting_trials(self, condition: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for actively recruiting clinical trials.

        Args:
            condition: Medical condition
            max_results: Maximum results

        Returns:
            List of recruiting trials
        """
        try:
            params = {
                'query.cond': condition,
                'filter.overallStatus': 'RECRUITING',
                'countTotal': 'true',
                'pageSize': max_results,
                'format': 'json'
            }

            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()

            trials = []
            for study in data.get('studies', []):
                trial_data = self._parse_trial_data(study)
                trials.append(trial_data)

            return trials

        except Exception as e:
            return [{
                "error": str(e),
                "condition": condition,
                "status_filter": "RECRUITING",
                "timestamp": datetime.now().isoformat()
            }]
