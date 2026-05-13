from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class UCSAgent(SearchAgentBase):
    algorithm_name = "ucs"

    def search(self, problem) -> SearchResult:
        raise NotImplementedError()