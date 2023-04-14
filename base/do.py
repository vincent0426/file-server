"""
data objects
"""

from dataclasses import dataclass
from uuid import UUID

from base import enums


@dataclass
class Account:
    id: UUID
    username: str
    password: str
    pub_key: str


@dataclass
class S3File:
    uuid: UUID
    key: str
    bucket: str

