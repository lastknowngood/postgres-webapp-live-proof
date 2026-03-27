from collections.abc import Sequence
from dataclasses import dataclass, field

from .models import EntryRecord


class EntryStore:
    def list_entries(self) -> Sequence[EntryRecord]:
        raise NotImplementedError

    def create_entry(self, value: str) -> EntryRecord:
        raise NotImplementedError


@dataclass
class InMemoryEntryStore(EntryStore):
    _values: list[EntryRecord] = field(default_factory=list)

    def list_entries(self) -> Sequence[EntryRecord]:
        return list(self._values)

    def create_entry(self, value: str) -> EntryRecord:
        entry = EntryRecord(id=len(self._values) + 1, value=value)
        self._values.append(entry)
        return entry
