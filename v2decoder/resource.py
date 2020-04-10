#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests


class Resource:
    def __init__(self, url: str):
        self.url = url
        self.cutted_str: str
        self._get_resource()

    def _get_resource(self) -> None:
        request = requests.get(self.url)
        self.cutted_str = request.text

    def get_encoded_data(self) -> str:
        return self.cutted_str + ((4 - len(self.cutted_str) % 4) * "=")
