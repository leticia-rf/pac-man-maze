from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class MazeConfig:
    map_path: str | Path | None = None
    full_observability: bool = True
    known_goal: bool = True
    reveal_radius: int = 1
    step_cost: float = -1.0
    bump_cost: float = -1.0
    wait_cost: float = -0.25
    success_reward: float = 1000.0
    reveal_full_on_terminal: bool = True


@dataclass(slots=True)
class RenderConfig:
    window_width: int = 1280
    window_height: int = 860
    fps: int = 60
    board_margin: int = 6
    board_gap: int = 6
    hud_width: int = 172
    background_color: tuple[int, int, int] = (8, 10, 20)
    board_bg_color: tuple[int, int, int] = (14, 14, 28)
    known_floor_color: tuple[int, int, int] = (20, 20, 30)
    hidden_color: tuple[int, int, int] = (35, 35, 50)
    hidden_outline_color: tuple[int, int, int] = (54, 54, 78)
    wall_color: tuple[int, int, int] = (26, 63, 158)
    wall_inner_color: tuple[int, int, int] = (45, 98, 220)
    discovered_wall_color: tuple[int, int, int] = (104, 70, 188)
    discovered_wall_inner_color: tuple[int, int, int] = (155, 116, 244)
    grid_line_color: tuple[int, int, int] = (38, 40, 60)
    text_color: tuple[int, int, int] = (240, 240, 245)
    accent_color: tuple[int, int, int] = (255, 208, 76)
    panel_color: tuple[int, int, int, int] = (10, 12, 22, 215)
    success_color: tuple[int, int, int] = (90, 215, 110)
    warning_color: tuple[int, int, int] = (232, 116, 96)
    shortest_path_color: tuple[int, int, int] = (255, 214, 64)
    shortest_path_glow_color: tuple[int, int, int, int] = (255, 214, 64, 110)
    visited_off_path_color: tuple[int, int, int] = (92, 188, 255)
    visited_off_path_glow_color: tuple[int, int, int, int] = (92, 188, 255, 62)
    search_expanded_color: tuple[int, int, int, int] = (66, 165, 245, 92)
    search_frontier_color: tuple[int, int, int, int] = (255, 214, 64, 118)
    search_current_color: tuple[int, int, int, int] = (255, 72, 72, 168)
    search_path_color: tuple[int, int, int] = (76, 217, 100)
    search_path_glow_color: tuple[int, int, int, int] = (76, 217, 100, 92)
