"""Mixins para Redis Simplify - Todos os componentes modulares"""

from redis_simplify.mixins.connection import ConnectionMixin
from redis_simplify.mixins.string import StringMixin
from redis_simplify.mixins.key import KeyMixin
from redis_simplify.mixins.set import SetMixin
from redis_simplify.mixins.hash import HashMixin
from redis_simplify.mixins.list import ListMixin
from redis_simplify.mixins.json import JSONMixin
from redis_simplify.mixins.pipeline import PipelineMixin
from redis_simplify.mixins.admin import AdminMixin
from redis_simplify.mixins.sorted_set import SortedSetMixin
from redis_simplify.mixins.cache import CacheMixin
from redis_simplify.mixins.ratelimit import RateLimitMixin
from redis_simplify.mixins.lock import LockMixin
from redis_simplify.mixins.pubsub import PubSubMixin
from redis_simplify.mixins.metrics import MetricsMixin
from redis_simplify.mixins.decorators import DecoratorsMixin
from redis_simplify.mixins.utils import UtilsMixin
from redis_simplify.mixins.batch import BatchMixin
from redis_simplify.mixins.health import HealthMixin

__all__ = [
    'ConnectionMixin',
    'StringMixin',
    'KeyMixin',
    'SetMixin',
    'HashMixin',
    'ListMixin',
    'JSONMixin',
    'PipelineMixin',
    'AdminMixin',
    'SortedSetMixin',
    'CacheMixin',
    'RateLimitMixin',
    'LockMixin',
    'PubSubMixin',
    'MetricsMixin',
    'DecoratorsMixin',
    'UtilsMixin',
    'BatchMixin',
    'HealthMixin',
    'AllMixins',
]

class AllMixins(
    ConnectionMixin,
    StringMixin,
    KeyMixin,
    SetMixin,
    HashMixin,
    ListMixin,
    JSONMixin,
    PipelineMixin,
    AdminMixin,
    SortedSetMixin,
    CacheMixin,
    RateLimitMixin,
    LockMixin,
    PubSubMixin,
    MetricsMixin,
    DecoratorsMixin,
    UtilsMixin,
    BatchMixin,
    HealthMixin,
):
    """Classe que agrega todos os mixins do Redis Simplify."""
    pass