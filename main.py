import os
from argparse import ArgumentParser
from wikimapper.wikimapper import WikiMapper


def main(url: str, output: str, levels: int = None, road: str = None, delay: int = 0, verbose: bool = False) -> None:
    map = WikiMapper(url=url, levels=levels, delay=delay, verbose=verbose)
    # map.get_related_pages(url[24:])

    map.complete_graph([url[24:]])

    os.makedirs('./output', exist_ok=True)

    match output:
        case 'html':
            map.create_html()

        case output if output in ('svg', 'png'):
            map.create_image(format=output)

        case 'json':
            map.create_json()

        case 'csv':
            pass


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-u', '--url', action='store', type=str, dest='url', required=True, help="Url of the first wikipedia page that will be scanned")
    ap.add_argument('-r', '--road', action='store', type=str,  dest='road', required=False, help="not implemented yet")
    ap.add_argument('-l', '--levels', action='store', type=int, dest='levels', default=5, required=False, help="number of children page that will be scanned")

    ap.add_argument('-o', '--output', action='store', type=str, dest='output', default='html', choices=('html', 'svg','png', 'json', 'csv'), help="Specify the output format")
    ap.add_argument('-D', '--delay', action='store', type=int, dest='delay', default=0, help="Delay between requests")

    ap.add_argument('-v', '--verbose', action='store_true', dest='verbose', required=False, help="Shows details durring execution")
    args = ap.parse_args()

    main(url=args.url, output=args.output, levels=args.levels, road=args.road, delay=args.delay, verbose=args.verbose)
