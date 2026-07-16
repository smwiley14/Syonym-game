import { useEffect, useState } from "react";
import {
  fetchRandomPuzzle,
  fetchDailyPuzzle,
  fetchNeighbors,
  type RandomPuzzle,
  type SynsetGroup,
} from "../../api";
import SynsetBlock from "../../components/SynsetBlock";

type Mode = "daily" | "random";

const HOW_TO_PLAY = [
  "You're given two words. Connect them by clicking through related words one step at a time.",
  "Each step must be a valid relation — a synonym, hypernym, antonym, derivation, and so on.",
  "Try to reach the target in as few steps as possible. The optimal path length is shown as a guide.",
  'Enable "Conceptual mode" to also hop via ConceptNet associations (used for, capable of, is a…).',
  "Click any word in your chain to backtrack to that point.",
];

export default function SynonymChain() {
  const [mode, setMode] = useState<Mode>("daily");
  const [puzzle, setPuzzle] = useState<RandomPuzzle | null>(null);
  const [chain, setChain] = useState<string[]>([]);
  const [synsets, setSynsets] = useState<SynsetGroup[]>([]);
  const [solved, setSolved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [conceptual, setConceptual] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

  async function loadPuzzle(m: Mode) {
    setLoading(true);
    setError(null);
    setSolved(false);
    setSynsets([]);
    try {
      const p = m === "daily" ? await fetchDailyPuzzle() : await fetchRandomPuzzle();
      setPuzzle(p);
      setChain([p.start]);
    } catch (err) {
      setPuzzle(null);
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadPuzzle(mode); }, []);

  function switchMode(m: Mode) {
    setMode(m);
    loadPuzzle(m);
  }

  useEffect(() => {
    if (!chain.length || solved) return;
    fetchNeighbors(chain[chain.length - 1], conceptual).then((res) =>
      setSynsets(res.synsets)
    );
  }, [chain, solved, conceptual]);

  function pick(word: string) {
    if (!puzzle || solved) return;
    const next = [...chain, word];
    setChain(next);
    if (word.toLowerCase() === puzzle.end.toLowerCase()) setSolved(true);
  }

  function backtrackTo(index: number) {
    if (solved || index >= chain.length - 1) return;
    setChain(chain.slice(0, index + 1));
    setSolved(false);
  }

  if (loading) return <p className="puzzle-hint">Leafing through the dictionary…</p>;
  if (error || !puzzle) {
    return (
      <div className="game">
        <p>{error ?? "Failed to load puzzle."}</p>
        <button className="sketch-btn" onClick={() => loadPuzzle(mode)}>Try again</button>
      </div>
    );
  }

  const playerSteps = chain.length - 1;

  return (
    <div className="game">
      {/* Mode switcher */}
      <div className="mode-switcher">
        <button
          className={`mode-btn${mode === "daily" ? " active" : ""}`}
          onClick={() => switchMode("daily")}
        >
          Daily
        </button>
        <button
          className={`mode-btn${mode === "random" ? " active" : ""}`}
          onClick={() => switchMode("random")}
        >
          Random
        </button>
        <button
          className="help-btn"
          onClick={() => setShowHelp((v) => !v)}
          aria-label="How to play"
        >
          ?
        </button>
      </div>

      {/* How to play */}
      {showHelp && (
        <ol className="how-to-play">
          {HOW_TO_PLAY.map((tip, i) => <li key={i}>{tip}</li>)}
        </ol>
      )}

      {/* Puzzle header */}
      <div className="targets">
        <span className="word">{puzzle.start}</span>
        <span className="arrow">⟶</span>
        <span className="word">{puzzle.end}</span>
      </div>

      <p className="puzzle-hint">
        {mode === "daily" && puzzle.date && (
          <span className="daily-date">{puzzle.date} · </span>
        )}
        Optimal: {puzzle.optimal_steps ?? "?"} step{puzzle.optimal_steps !== 1 ? "s" : ""}
        {playerSteps > 0 && !solved && (
          <span className="step-counter"> · Your steps: {playerSteps}</span>
        )}
      </p>

      {/* Conceptual toggle */}
      <label className="conceptual-toggle">
        <input
          type="checkbox"
          checked={conceptual}
          onChange={(e) => setConceptual(e.target.checked)}
        />
        {" "}Conceptual mode
      </label>

      {/* Chain — each word is clickable to backtrack */}
      <div className="chain">
        {chain.map((w, i) => (
          <span key={i}>
            {i > 0 && <span className="chain-arrow"> → </span>}
            <button
              className={`chain-word${i === chain.length - 1 ? " chain-word--current" : " chain-word--past"}`}
              onClick={() => backtrackTo(i)}
              disabled={i === chain.length - 1 || solved}
              title={i < chain.length - 1 ? "Backtrack to here" : undefined}
            >
              {w}
            </button>
          </span>
        ))}
      </div>

      {solved ? (
        <div className="result">
          <p>
            Solved in <strong>{playerSteps}</strong> step{playerSteps !== 1 ? "s" : ""}
            {" "}<span className="note">(optimal: {puzzle.optimal_steps})</span>
            {playerSteps === puzzle.optimal_steps ? " — perfect! 🎉" : ""}
          </p>
          {mode === "random" && (
            <button className="sketch-btn new-puzzle-btn" onClick={() => loadPuzzle("random")}>
              New puzzle
            </button>
          )}
          {mode === "daily" && (
            <button className="sketch-btn new-puzzle-btn" onClick={() => switchMode("random")}>
              Try a random puzzle
            </button>
          )}
        </div>
      ) : (
        <>
          <div className="game-actions">
            {mode === "random" && (
              <button className="sketch-btn" onClick={() => loadPuzzle("random")}>New puzzle</button>
            )}
          </div>
          {synsets.map((s, i) => (
            <SynsetBlock key={i} synset={s} onWordClick={pick} />
          ))}
        </>
      )}
    </div>
  );
}
