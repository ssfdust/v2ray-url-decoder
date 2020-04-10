#!/usr/bin/env python
# -*- coding: utf-8 -*-

from invoke import task
from v2decoder.decoder import decode_url_to_configs
from v2decoder.config import dump_config_lst
from v2decoder.tester import speedtest_config_lst, print_test_results

@task(
    help={"url": "The v2ray subscribe url"}
)
def dump_configs(_, url):
    """dump subscribe URL to configs in current directory"""
    configs = decode_url_to_configs(url)
    dump_config_lst(configs, is_test=False)


@task(
    help={"url": "The v2ray subscribe url"}
)
def test_url(_, url):
    """test all configs from subscribe URL"""
    configs = decode_url_to_configs(url)
    dump_config_lst(configs, is_test=True)
    speedtest_config_lst(configs)
    print_test_results(configs)
