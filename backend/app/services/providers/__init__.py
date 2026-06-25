from importlib import import_module


Alibaba1688Provider = import_module("app.services.providers.1688_provider").Alibaba1688Provider
PddProvider = import_module("app.services.providers.pdd_provider").PddProvider
YiwuProvider = import_module("app.services.providers.yiwu_provider").YiwuProvider
FactoryProvider = import_module("app.services.providers.factory_provider").FactoryProvider

__all__ = [
    "Alibaba1688Provider",
    "PddProvider",
    "YiwuProvider",
    "FactoryProvider",
]
