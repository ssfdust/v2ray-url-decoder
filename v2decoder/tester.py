#!/usr/bin/env python
# -*- coding: utf-8 -*-

from contextlib import contextmanager
import subprocess
import os
import time
from shutil import rmtree
from operator import attrgetter
import speedtest
import psutil
from typing import TYPE_CHECKING, Iterator, List
from .config import Config
import ping3


def callback(completed, total, end=False, **kwargs) -> None:
    if end is True:
        rate = round(completed / total * 100, 4)
        print(f".......... {rate} %")


def _create_v2ray_subporcess(config_name: str) -> subprocess.Popen:
    print("启动v2ray进程...")
    process = subprocess.Popen(["v2ray", "-config", f"test_configs/{config_name}.json"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    time.sleep(1.3)
    return process


def create_v2ray_subporcess(config_name):
    process = _create_v2ray_subporcess(config_name)
    if not check_process(process):
        print("重建v2ray进程...")
        return _create_v2ray_subporcess(config_name)
    return process


def check_process(process: subprocess.Popen) -> bool:
    if process.poll():
        print("v2ray执行失败，尝试杀死所有v2ray进程")
        for proc in psutil.process_iter(['name', 'username']):
            if proc.name() == 'v2ray' and proc.username() != 'root':
                proc.kill()
        return False
    return True


def _get_download_speed(tester: speedtest.Speedtest) -> float:
    print('获取服务中...')
    tester.get_servers([])
    print('开始下载...')
    tester.download(threads=1, callback=callback)
    return tester.results.download / 1024 / 1024


def get_download_speed(config: Config) -> float:
    speed = 0.0
    try:
        print(f"开始测试 {config.name} 服务...")
        tester = speedtest.Speedtest(timeout=3)
        speed = round(_get_download_speed(tester), 3)
    except speedtest.ConfigRetrievalError:
        print(f"测试 {config.name} 服务超时...")
        speed = -1.0

    return speed


@contextmanager
def system_proxy():
    os.environ["HTTP_PROXY"] = "127.0.0.1:10086"
    os.environ["HTTPS_PROXY"] = "127.0.0.1:10086"
    yield
    os.environ["HTTP_PROXY"] = ""
    os.environ["HTTPS_PROXY"] = ""


class ConfigTester:
    def __init__(self, config: Config):
        self._config = config
        self.run_cnt = 1

    def start_test(self) -> None:
        with system_proxy():
            self._config.speed = self._start_test_loop()
            print(self._config.name, self._config.speed, "MB/s")

    def _start_test_loop(self) -> float:
        for speed in self.__test_loop():
            if speed > 0:
                break

        return speed

    def __test_loop(self) -> Iterator[float]:
        for _ in range(3):
            self.run_cnt += 1
            yield self.__start_single_loop()
            print(f"重试第{self.run_cnt}次...")
            time.sleep(2.5)

    def __start_single_loop(self) -> float:
        process = create_v2ray_subporcess(self._config.name)
        speed = get_download_speed(self._config)
        process.terminate()

        return speed

def pingtest_configlst(configs: List[Config]):
    print("正在进行ping测试...")
    for config in configs:
        config.ping = ping3.ping(config.address, timeout=1) or -1

    configs = list(filter(lambda x: x.ping > 0, configs))
    configs.sort(key=attrgetter("ping"))
    return configs[0:8]


def speedtest_config_lst(configs: List[Config]):
    configs = pingtest_configlst(configs)
    items_num = len(configs)
    for idx, config in enumerate(configs, 1):
        print(f"正在测试第{idx}个，共计{items_num}个")
        tester = ConfigTester(config)
        tester.start_test()
    return configs

def print_test_results(configs: List[Config]) -> None:
    result_lst = sorted(configs, key=attrgetter("tls", "speed"), reverse=True)
    for idx, i in enumerate(result_lst, 1):
        print(i.name, "tls" if i.tls else "", i.speed)
        i.name = f"rank{idx}_{i.name}_{i.speed}"
    return configs
