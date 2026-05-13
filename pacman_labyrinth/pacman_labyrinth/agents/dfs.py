from __future__ import annotations

from .search_agent_base import SearchAgentBase
from ..search.algorithms import SearchResult, reconstruct_path


class DFSAgent(SearchAgentBase):
    algorithm_name = "dfs"

    def search(self, problem) -> SearchResult:
        raise NotImplementedError