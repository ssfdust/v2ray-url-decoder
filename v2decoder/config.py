#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pathlib import Path
from copy import deepcopy
from typing import Dict, Tuple, Union, Any, List
import json

rootpath = Path(__file__).parent.absolute()

with open(rootpath / "templates/config.json") as f:
    DEFAULT_CONFIG = json.load(f)
with open(rootpath / "templates/test_config.json") as f:
    TEST_CONFIG = json.load(f)


def _parse_parts(
    parts: Dict[str, Union[str, int]]
) -> Tuple[str, str, Dict]:
    name: str = str(parts["ps"])
    address = parts["add"]
    if "ss" in parts:
        outbound = {
            "protocol": "shadowsocks",
            "settings": {
                "servers": [
                    {
                        "address": parts["add"],
                        "port": int(parts["port"]),
                        "method": parts["method"],
                        "password": parts["password"],
                    }
                ]
            },
        }
    else:
        outbound = {
            "protocol": "vmess",
            "settings": {
                "vnext": [
                    {
                        "address": parts["add"],
                        "port": int(parts["port"]),
                        "users": [
                            {
                                "id": parts["id"],
                                "level": 1,
                                "alterId": parts["aid"],
                            }
                        ],
                    }
                ]
            },
            "streamSettings": {
                "network": parts["net"],
                "security": parts["tls"] if parts["tls"] else "none",
                "wsSettings": {"path": parts["path"]},
            },
        }
    return (name.strip(), address.strip(), outbound)


class Config:
    test_config: Dict[str, Any]
    speed: float
    config: Dict[str, Any]
    tls: bool

    def __init__(self, defaults: Dict[str, Union[str, int]]):
        self.name, self.address, self.parts = _parse_parts(defaults)
        self.tls = "tls" in defaults and defaults["tls"] == "tls"
        self.ping = -1
        self._get_config()

    def _get_config(self) -> None:
        self.__get_test_config()
        self.__get_config()

    def __get_test_config(self) -> None:
        self.test_config = deepcopy(TEST_CONFIG)
        self.test_config["outbounds"].insert(0, self.parts)

    def __get_config(self) -> None:
        self.config = deepcopy(DEFAULT_CONFIG)
        self.config["outbounds"].insert(0, self.parts)


def _if_create_subdir(path_str: str) -> None:
    path = Path(path_str)
    if not path.exists():
        path.mkdir()


def dump_json(config: Config, subdir: str = "configs") -> None:
    _if_create_subdir(subdir)
    with open(f"{subdir}/{config.name}.json", "w") as f:
        if "test" in subdir:
            json.dump(config.test_config, f)
        else:
            json.dump(config.config, f, indent=4)


def dump_config_lst(configs: List[Config], is_test: bool = False):
    for config in configs:
        if is_test:
            dump_json(config, "test_configs")
        else:
            dump_json(config)


def dump_bench_lst(configs: List[Config]):
    for config in configs:
        dump_json(config, "bench_configs")
