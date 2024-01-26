import json
import logging
from typing import List, Union
from datetime import datetime, timedelta, date
import pandas as pd
# !pip install google-api-python-client
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SERVICE_NAME = 'trends'
SERVICE_VERSION = 'v1beta'
_DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/trends/v1beta/rest'


class GT:
    """
    A class to interact with Google Trends API to fetch health trends, search interest over time,
    and top related topics for given terms.

    Attributes:
        service (Resource): The Google Trends API service object for making requests.
        block
    """
    def __init__(self, google_api_key: str):
        self.service = build(
            serviceName=SERVICE_NAME,
            version=SERVICE_VERSION,
            discoveryServiceUrl=_DISCOVERY_SERVICE_URL,
            developerKey=google_api_key,
            cache_discovery=False)
        self.block_until = None

    def get_health_trends(self,
                          terms: Union[str, List[str]],
                          time_line_resolution: str ="month"):
        """
        Fetches trends for specified terms.

        Args:
            terms (List[str]): A list of terms to search for.
            time_line_resolution (str, optional): The time resolution for the trend data. 
                Defaults to "month".

        Raises:
            RuntimeError: If the daily limit is exceeded and the service is blocked until a 
                certain datetime.
        """
        graph = self.service.getTimelinesForHealth(
            terms=terms,
            timelineResolution=time_line_resolution
        )

        try:
            response = graph.execute()
            return response

        except HttpError as http_error:
            data = json.loads(http_error.content.decode('utf-8'))
            code = data['error']['code']
            reason = data['error']['errors'][0]['reason']
            if code == 403 and reason == 'dailyLimitExceeded':
                self.block_until = datetime.combine(
                    date.today() + timedelta(days=1), datetime.now().time())
                raise RuntimeError(f"{reason}: {self.block_until}")
            logging.warning(http_error)
            return []

    def get_graph(self,
                  terms: Union[str, List[str]],
                  restrictions_geo: str,
                  restrictions_start_date: str ="2004-01"):
        """
        Fetches search interest over time and location for specified terms.

        Args:
            terms (List[str]): A list of terms to search for.
            restrictions_geo (str): The geographic area to restrict the search to.
            restrictions_startDate (str, optional): The start date for the search interest data. 
                Defaults to "2004-01".
        """
        graph = self.service.getGraph(
            terms=terms,
            restrictions_geo=restrictions_geo,
            restrictions_startDate=restrictions_start_date
        )

        try:
            response = graph.execute()
            return response

        except HttpError as http_error:
            logging.warning(http_error)
            return []

    def get_top_topics(self,
                       term: Union[str, List[str]],
                       restrictions_geo: str,
                       restrictions_start_date="2004-01"):
        graph = self.service.getTopTopics(
            term=term,
            restrictions_geo=restrictions_geo,
            restrictions_startDate=restrictions_start_date
        )
        try:
            response = graph.execute()
            return response
        except Exception as e:
            logging.warning(e)
            return []

    @staticmethod
    def to_df(result: dict) -> pd.DataFrame:
        """
        Converts the result from the Google Trends API to a pandas DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing the normalized trend data.
        """
        df = pd.json_normalize(result["lines"], meta=[
                               "term"], record_path=["points"])
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        return df
