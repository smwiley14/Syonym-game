from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from wordnet_service import (
    get_game_neighbors_batch,
    get_game_synset_neighbors,
    random_puzzle,
    shortest_path,
)
from .puzzles import get_daily_puzzle, add_optimal_steps

router = APIRouter(prefix="/synonym-chain", tags=["synonym-chain"])


class PathRequest(BaseModel):
    start: str
    end: str
    chain: list[str]
    conceptual: bool = False


@router.get("/puzzle")
def daily_puzzle():
    puzzle = get_daily_puzzle()
    return add_optimal_steps(puzzle)


@router.get("/random")
def random_game(min_steps: int = 3, max_steps: int = 4):
    if not 1 <= min_steps <= max_steps <= 6:
        raise HTTPException(status_code=400, detail="Steps must satisfy 1 <= min <= max <= 6")
    puzzle = random_puzzle(min_steps, max_steps)
    if puzzle is None:
        raise HTTPException(status_code=503, detail="Could not generate a puzzle, try again")
    return puzzle


@router.get("/neighbors/{word}")
def neighbors(word: str, conceptual: bool = False):
    synsets = get_game_synset_neighbors(word, conceptual=conceptual)
    if not synsets:
        raise HTTPException(status_code=404, detail=f"No related words found for '{word}'")
    return {"word": word, "synsets": synsets}


@router.post("/validate")
def validate(req: PathRequest):
    chain = req.chain
    endpoints_match = (
        len(chain) >= 2
        and chain[0].lower() == req.start.lower()
        and chain[-1].lower() == req.end.lower()
    )

    links_valid = False
    if endpoints_match:
        neighbors_by_word = get_game_neighbors_batch(chain[:-1], conceptual=req.conceptual)
        links_valid = all(
            nxt.lower() in {n.lower() for n in neighbors_by_word.get(cur, {})}
            for cur, nxt in zip(chain, chain[1:])
        )

    optimal = shortest_path(req.start, req.end)

    return {
        "valid": endpoints_match and links_valid,
        "player_steps": len(chain) - 1,
        "optimal_steps": len(optimal) - 1 if optimal else None,
    }
