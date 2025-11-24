from attr import dataclass


@dataclass
class WordleUser:
    name: str
    win_count: int = 0
    # play_count and score_sum used to compute rolling average
    play_count: int = 0
    score_sum: int = 0
