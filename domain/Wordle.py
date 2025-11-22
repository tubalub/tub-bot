from attr import dataclass


@dataclass
class WordleUser:
    name: str
    win_count: int
    # play_count and score_sum used to compute rolling average
    play_count: int
    score_sum: int
