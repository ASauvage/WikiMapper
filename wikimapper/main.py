from networkx import Graph
from requests import get


class WikiMapper:
    def __init__(self, url: str, level: int = None, road: str = None):
        self.graph = Graph()
