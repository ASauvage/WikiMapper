from argparse import ArgumentParser
from wikimapper.main import WikiMapper


def main(url: str, level: int = None, road: str = None) -> None:
    pass


if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('-u', '--url', action='store', type=str, dest='url', required=True, help="")
    ap.add_argument('-r', '--road', action='store', type=str,  dest='road', required=False, help="")
    ap.add_argument('-l', '--levels', action='store', type=int, dest='levels', required=False, help="")
    args = ap.parse_args()

    main(url=args.url, level=args.levels, road=args.road)
