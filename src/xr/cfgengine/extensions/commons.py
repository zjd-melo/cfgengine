# cfgengine/extensions/commons.py
import os

from xr.cfgengine import ConfigLoader
from xr.cfgengine.parser import DotDict


class CommonsProxy:
    """
    commons 配置代理：
    - 支持 commons.KEY / commons.a.b
    - 支持 commons("a.b", default)
    """

    def __init__(self):
        self._cache = None

    def _load(self):
        if self._cache is None:
            commons_conf = os.getenv("CFGENGINE_COMMONS")
            if not commons_conf:
                raise RuntimeError(
                    "CFGENGINE_COMMONS is not set. "
                    "Please set it to a commons config source, e.g.:\n"
                    "  export CFGENGINE_COMMONS=nacos://127.0.0.1:8848?"
                    "data_id=commons.json&group=DEFAULT_GROUP"
                )

            cfg = ConfigLoader.load_config(commons_conf)
            self._cache = DotDict(cfg)

        return self._cache

    def __call__(self, key, default=None):
        cfg = self._load()
        try:
            for part in key.split("."):
                cfg = cfg[part]
            return cfg
        except KeyError:
            if default is not None:
                return default
            raise KeyError(f"Common config '{key}' not found")

    def __getattr__(self, name):
        cfg = self._load()
        try:
            return cfg[name]
        except KeyError:
            raise AttributeError(f"Common config '{name}' not found")

    # 只读保护
    def __setattr__(self, name, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            raise RuntimeError("commons config is read-only")


from xr.cfgengine.parser import _default_env

_default_env.globals["commons"] = CommonsProxy()
