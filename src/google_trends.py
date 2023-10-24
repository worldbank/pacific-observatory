import os
import json
import pandas as pd
import requests
# !pip install google-api-python-client
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
# local import
import logging

SERVICE_NAME = 'trends'
SERVICE_VERSION = 'v1beta'
_DISCOVERY_SERVICE_URL = 'https://www.googleapis.com/discovery/v1/apis/trends/v1beta/rest'


class GT:
    def __init__(self, _GOOGLE_API_KEY):
        self.service = build(
            serviceName=SERVICE_NAME,
            version=SERVICE_VERSION,
            discoveryServiceUrl=_DISCOVERY_SERVICE_URL,
            developerKey=_GOOGLE_API_KEY,
            cache_discovery=False)
        self.block_until = None

    def get_health_trends(self, terms, timelineResolution="month"):
        graph = self.service.getTimelinesForHealth(
            terms=terms,
            timelineResolution=timelineResolution
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
                    date.today() + timedelta(days=1), dtime.min)
                raise RuntimeError('%s: blocked until %s' %
                                   (reason, self.block_until))
            logging.warning(http_error)
            return []

    def get_graph(self, terms,
                  restrictions_geo,
                  restrictions_startDate="2004-01"):
        graph = self.service.getGraph(
            terms=terms,
            restrictions_geo=restrictions_geo,
            restrictions_startDate=restrictions_startDate
        )

        try:
            response = graph.execute()
            return response

        except HttpError as http_error:
            logging.warning(http_error)
            return []

    def get_top_topics(self, term,
                       restrictions_geo,
                       restrictions_startDate="2004-01"):
        graph = self.service.getTopTopics(
            term=term,
            restrictions_geo=restrictions_geo,
            restrictions_startDate=restrictions_startDate
        )
        try:
            response = graph.execute()
            return response
        except Exception as e:
            logging.warning(e)
            return []

    @staticmethod
    def to_df(result: json) -> pd.DataFrame:
        df = pd.json_normalize(result["lines"], meta=[
                               "term"], record_path=["points"])
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

        return df
