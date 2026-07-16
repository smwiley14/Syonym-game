import { useState } from "react";
import { fetchExplore, type SynsetGroup } from "../../api";
import SynsetBlock from "../../components/SynsetBlock";
import "./Explorer.css";

export default function Explorer() {
  const [input, setInput] = useState("");
  const [word, setWord] = useState<string | null>(null);
  const [synsets, setSynsets] = useState<SynsetGroup[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function explore(w: string) {
    if (!w) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetchExplore(w);
      setWord(res.word);
      setSynsets(res.synsets);
    } catch (err) {
      setWord(null);
      setSynsets([]);
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  function search(e: React.FormEvent) {
    e.preventDefault();
    explore(input.trim().toLowerCase());
  }

  function followWord(w: string) {
    setInput(w);
    explore(w.toLowerCase());
  }

  return (
    <div className="explorer">
      <form className="search-form" onSubmit={search}>
        <input
          className="search-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Look up a word…"
          autoFocus
        />
        <button className="sketch-btn" type="submit" disabled={loading}>
          {loading ? "…" : "Look up"}
        </button>
      </form>

      {error && <p className="explore-error">{error}</p>}

      {word && synsets.length > 0 && (
        <div className="dictionary-entry">
          <p className="entry-headword">{word}</p>
          {synsets.map((s, i) => (
            <SynsetBlock key={i} synset={s} onWordClick={followWord} />
          ))}
        </div>
      )}
    </div>
  );
}
