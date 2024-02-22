import csv
import json
import networkx
from re import finditer
from time import sleep
from urllib.parse import unquote
from pyvis.network import Network
from matplotlib import pyplot
from requests import get, RequestException

from .settings import *


class WikiMapper(networkx.Graph):
    def __init__(self, url: str, levels: int = 10, delay: int = 0, verbose: bool = False):
        super().__init__()

        self.add_node(url[24:], label=url[24:], color="#9a31a8", title=f'<a href="{url}">{url[24:]}</a>')

        self.url = url
        self.levels = levels
        self.delay = delay
        self.verbose = verbose

    def graph_stats(self) -> str:
        return f'{len(self)} nodes / {len(self.edges)} edges'

    def create_html(self) -> None:
        ntw = Network(
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

        # ntw.show_buttons(filter_='physics')
        ntw.barnes_hut()
        ntw.from_nx(self)

        with open('output/output.html', 'w', encoding="utf-8") as file:
            file.write(ntw.generate_html())

        print(f'-- output/output.html has been generated - [{self.graph_stats()}] --')

    def create_json(self) -> None:
        network_data = networkx.node_link_data(self)

        with open('output/output.json', 'w', encoding='utf-8') as file:
            file.write(json.dumps(network_data, ensure_ascii=False, indent=4))

        print(f'-- output/output.json has been generated - [{self.graph_stats()}] --')

    def create_svg(self) -> None:
        options = {
            'with_labels': False,
            'font_size': 9,
            'node_size': 100,
            'node_color': [COLORS[x % len(COLORS)] for x in range(len(self))],
            'width': 1,
        }

        pyplot.figure(1, figsize=(200, 80), dpi=60)
        networkx.draw(self, pos=networkx.random_layout(self), **options)
        pyplot.savefig('output/output.svg')
        # pyplot.show()

        print(f'-- output/output.svg has been generated - [{self.graph_stats()}] --')

    def get_related_pages(self, url) -> list[str]:
        nodes = list()
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

            if href not in self:
                nodes.append(href)
                self.add_node(href, label=title, title=f'<a href="{WIKIPEDIA_SRV_FR + href}" target="_blank">{title}</a>', color=COLORS[len(nodes) % len(COLORS)])

            edges.append((url, href))

        edges = list(dict.fromkeys(edges))

        self.add_edges_from(edges)

        # debug options
        if self.verbose:
            print(f"[done] '{url}': {len(edges)} nodes")

        return nodes

    def complete_graph(self, ids: list[str], level: int = 0) -> None:
        clevel = level
        for id in ids:
            related_ids = self.get_related_pages(id)

            if clevel < self.levels:
                sleep(self.delay)

                self.complete_graph(related_ids, clevel + 1)
