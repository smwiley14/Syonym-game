from datetime import date


PUZZLES = [
    {"start": "happy", "end": "bright"},
    {"start": "cold", "end": "cruel"},
    {"start": "fast", "end": "sharp"},
    {"start": "big", "end": "loud"},
    {"start": "cold", "end": "sharp"},
]


def get_daily_puzzle() -> dict:
    index = (date.today() - date(2026, 1, 1)).days % len(PUZZLES)
    puzzle = PUZZLES[index]
    return {"start": puzzle["start"], "end": puzzle["end"], "date": str(date.today())}


def add_optimal_steps(puzzle: dict) -> dict:
    from wordnet_service import shortest_path
    path = shortest_path(puzzle["start"], puzzle["end"])
    return {**puzzle, "optimal_steps": len(path) - 1 if path else None}
