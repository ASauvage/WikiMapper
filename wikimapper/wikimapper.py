import csv
from re import finditer
from time import sleep
from urllib.parse import unquote
from pyvis.network import Network
from requests import get, RequestException

from .settings import *


class WikiMapper(Network):
    def __init__(self, url: str, levels: int = 10, delay: int = 0, verbose: bool = False):
        super().__init__(
            notebook=True,
            directed=False,
            layout=False,
            cdn_resources="remote",
            bgcolor="#222222",
            font_color="#ffffff",
            width="100%",
            height="99.5vh",
            heading="WikiMapper",
            select_menu=True,
            filter_menu=True
        )

        # self.show_buttons(filter_='physics')
        self.barnes_hut()

        self.add_node(url[24:], label=url[24:], color="#9a31a8", title=f'<a href="{url}">{url[24:]}</a>')

        self.url = url
        self.levels = levels
        self.delay = delay
        self.verbose = verbose

    def create_html(self) -> None:
        with open('output/output.html', 'w', encoding="utf-8") as file:
            file.write(self.generate_html())

        print(f'-- output/output.html has been generated ---')

    def get_related_pages(self, url) -> list[str]:
        nodes = {
            'nodes': list(),
            'label': list(),
            'title': list()
        }
        edges = list()

        try:
            response = get(WIKIPEDIA_SRV_FR + url, headers={'Content-Type': 'text/html', 'charset': 'utf-8'})
            response.encoding = 'utf-8'

        except RequestException as e:
            raise e

        matches = finditer('<a href="(/wiki/[^"]+)" title="([^"]+)">', response.content.decode('utf-8'))

        for match in matches:
            href = unquote(match.group(1))
            title = unquote((match.group(2)))

            # check irrelevant pages
            if any(substring in href for substring in EXCLUDED_PAGES):
                continue

            if href not in nodes['nodes']:
                nodes['nodes'].append(href)
                nodes['label'].append(title)
                nodes['title'].append(f'<a href="{WIKIPEDIA_SRV_FR + href}" target="_blank">{title}</a>')

            edges.append((url, href))

        edges = list(dict.fromkeys(edges))

        self.add_nodes(**nodes)
        self.add_edges(edges)

        # debug options
        if self.verbose:
            print(f"[done] '{url}': {len(edges)} nodes")

        return nodes['nodes']

    def complete_graph(self, ids: list[str], level: int = 0) -> None:
        clevel = level
        for id in ids:
            related_ids = self.get_related_pages(id)

            if clevel < self.levels:
                sleep(self.delay)

                self.complete_graph(related_ids, clevel + 1)
