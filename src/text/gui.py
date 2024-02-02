import os
import sys
import logging
import pandas as pd
import bokeh
import googleapiclient
import networkx as nx
from bokeh.plotting import figure, show, from_networkx
from bokeh.models import (Select, HoverTool, TapTool, BoxSelectTool,
                          Legend, Range1d, Circle, MultiLine)
from ..google_trends import GT


class DrawTopics:
    def __init__(self, words: list, restrictions_geo: str, gt_instance):
        """
        Class for drawing network graphs of topics based on Google Trends data.

        Args:
            words (list): A list of topic keywords.
            restrictions_geo (str): Geographic restrictions for Google Trends queries.
            gt_instance (GT): An instance of the Google Trends API client.

        Attributes:
            words (list): A list of topic keywords.
            restrictions_geo (str): Geographic restrictions for Google Trends queries.
            gt_instance (GT): An instance of the Google Trends API client.
        """
        if not isinstance(gt_instance.service, googleapiclient.discovery.Resource):
            raise TypeError(
                f"{gt_instance} is not a googleapiclient.discovery.Resource instance.")
        self.words = words
        self.restrictions_geo = restrictions_geo
        self.gt_instance = gt_instance
        self.result = None
        self.idx_dict = None
        self.G = None
        self.node_attrs = None

    @staticmethod
    def get_query_results(words: list,
                          restrictions_geo: str,
                          gt_instance: GT):
        """
        Get a DataFrame containing query results based on getTopTopics.

        Args:
            words (list): A list of topic keywords.
            restrictions_geo (str): Geographic restrictions for Google Trends queries.
            gt_instance (GT): An instance of the Google Trends API client.

        Returns:
            pd.DataFrame: A DataFrame with columns 'source', 'target', and 'volume'.
        """
        terms = []
        for word in words:
            topic_dict = gt_instance.get_top_topics(term=word,
                                                    restrictions_geo=restrictions_geo)
            if len(topic_dict) != 0:
                for item in topic_dict["item"]:
                    if item["title"].isdigit() != True:
                        terms.append(
                            [word, item["title"].lower(), item["value"]])
            else:
                logging.info(f"Querying {word} return an empty result.")

        return pd.DataFrame(terms, columns=["source", "target", "volume"])

    @staticmethod
    def get_id_for_each_word(data: pd.DataFrame):
        """
        Get a dictionary mapping unique words to their corresponding IDs.

        Args:
            data (pd.DataFrame): A DataFrame with columns 'source' and 'target'.

        Returns:
            dict: A dictionary mapping unique words to their IDs.
        """
        source = data["source"].unique().tolist()
        target = data["target"].unique().tolist()
        source.extend(target)
        unique_word_set = set(source)
        idx_dict = {}
        for idx, i in enumerate(unique_word_set):
            idx_dict.update({i: idx + 1})
        return idx_dict

    def trends_to_nx_object(self) -> nx.Graph:
        """
        Convert Google Trends data into a NetworkX graph.

        Returns:
            nx.Graph: A NetworkX graph representing topic relationships.
        """
        self.result = self.get_query_results(
            self.words, self.restrictions_geo, self.gt_instance)
        self.idx_dict = self.get_id_for_each_word(self.result)
        for col in ["source", "target"]:
            self.result[col + "_idx"] = self.result[col].map(self.idx_dict)

        self.G = nx.from_pandas_edgelist(
            self.result, "source_idx", "target_idx")

        self.node_attrs = {}
        for k, v in self.idx_dict.items():
            if k in self.words:
                self.node_attrs.update(
                    {v: {"term": k, "color": "red", "edge_size": 15}})
            else:
                self.node_attrs.update(
                    {v: {"term": k, "color": "blue", "edge_size": 6}})
        nx.set_node_attributes(self.G, self.node_attrs)

        return self.G

    def make_graph(self):
        """
        Create and return a Bokeh figure representing the network graph of topics.

        Returns:
            figure: A Bokeh figure representing the network graph.
        """

        plot = figure(width=800,
                      height=500,
                      tools="pan,wheel_zoom,save,reset",
                      active_scroll='wheel_zoom',
                      x_range=Range1d(-10.1, 10.1),
                      y_range=Range1d(-10.1, 10.1))
        plot.add_tools(
            HoverTool(tooltips=[("Term", "@term")]),
            TapTool(),
            BoxSelectTool())

        network_graph = from_networkx(
            self.G, nx.spring_layout, scale=10, center=(0, 0))
        network_graph.node_renderer.glyph = Circle(size="edge_size",
                                                   fill_color='color')
        network_graph.edge_renderer.glyph = MultiLine(
            line_alpha=0.5, line_width=1)

        # Add network graph to the plot
        plot.renderers.append(network_graph)
        plot.xaxis.visible = False
        plot.yaxis.visible = False
        plot.xgrid.visible = False
        plot.ygrid.visible = False
        return plot
