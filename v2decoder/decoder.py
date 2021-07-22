#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import json
from base64 import b64decode
from typing import Dict, Iterator, List, Union
from .resource import Resource
from .config import Config

class BaseDecoder:
    def __init__(self, encode_str: str):
        self.encode_str = encode_str
        self.decode_str: str

    @staticmethod
    def _bytesto_str(iobytes: bytes) -> str:
        return iobytes.decode("utf8")

    def decode(self) -> None:
        self.decode_str = self._bytesto_str(b64decode(self.encode_str))


class ListDecoder(BaseDecoder):
    def iter_encode_config(self) -> Iterator[str]:
        for config_str in self.decode_str.splitlines():
            if config_str.startswith("vmess://"):
                _config_str = re.sub(r"vmess://", "", config_str)
                _econded_config_str = _config_str + ((4 - len(_config_str) % 4) * "=")
                yield _econded_config_str


class ConfigDecoder(BaseDecoder):
    def get_json(self) -> Dict:
        return json.loads(self.decode_str)

def _get_resource_from_url(url: str) -> str:
    resource = Resource(url)
    return resource.get_encoded_data()

def _get_listencoded_str_from_encoded_str(encoded_str: str) -> List[str]:
    decoder = ListDecoder(encoded_str)
    decoder.decode()
    return [item for item in decoder.iter_encode_config()]

def _decode_from_listencoded_str(lst_encoded_str: List[str]) -> List[Dict[str, Union[str, int]]]:
    results = []
    for encoded_str in lst_encoded_str:
        decoder = ConfigDecoder(encoded_str)
        decoder.decode()
        results.append(decoder.get_json())
    return results

def decode_url_to_configs(url: str) -> List[Config]:
    encoded_str = _get_resource_from_url(url)
    lst_encoded_str = _get_listencoded_str_from_encoded_str(encoded_str)
    json_lst = _decode_from_listencoded_str(lst_encoded_str)
    return [Config(json) for json in json_lst]
