from fastapi import APIRouter, HTTPException

from wordnet_service import get_synset_neighbors

router = APIRouter(prefix="/explorer", tags=["explorer"])


@router.get("/{word}")
def explore(word: str):
    word = word.strip().lower()
    synsets = get_synset_neighbors(word)
    if not synsets:
        raise HTTPException(status_code=404, detail=f"No entries found for '{word}'")
    return {"word": word, "synsets": synsets}
