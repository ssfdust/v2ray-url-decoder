#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argparse import ArgumentParser

from v2decoder.config import dump_config_lst
from v2decoder.decoder import decode_url_to_configs
from v2decoder.tester import print_test_results, speedtest_config_lst


def dump_configs(url):
    """ """
    configs = decode_url_to_configs(url)
    dump_config_lst(configs, is_test=False)


def test_url(url):
    """ """
    configs = decode_url_to_configs(url)
    dump_config_lst(configs, is_test=True)
    speedtest_config_lst(configs)
    print_test_results(configs)


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "-t", "--test", help="test all configs from subscribe URL",
        action="store_true", dest="is_test", default=False
    )
    parser.add_argument("url", help="The v2ray subscribe url")

    args = parser.parse_args()
    if args.is_test:
        test_url(args.url)
    else:
        dump_configs(args.url)


if __name__ == '__main__':
    main()
