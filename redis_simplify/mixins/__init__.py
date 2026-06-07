"""Mixins para Redis Simplify - Todos os componentes modulares"""

from redis_simplify.mixins.connection import ConnectionMixin
from redis_simplify.mixins.string import StringMixin
from redis_simplify.mixins.set import SetMixin
from redis_simplify.mixins.hash import HashMixin
from redis_simplify.mixins.list import ListMixin
from redis_simplify.mixins.json import JSONMixin
from redis_simplify.mixins.pipeline import PipelineMixin
from redis_simplify.mixins.admin import AdminMixin
# Lista de todos os mixins para fácil importação
__all__ = [
    'ConnectionMixin',
    'StringMixin',
    'SetMixin',
    'HashMixin',
    'ListMixin',
    'JSONMixin',
    'PipelineMixin',
    'AdminMixin',
    'AllMixins',
]

# Classe que agrega todos os mixins
class AllMixins(
    ConnectionMixin,
    SetMixin,
    HashMixin,
    StringMixin,
    ListMixin,
    JSONMixin,
    PipelineMixin,
    AdminMixin
):
    pass