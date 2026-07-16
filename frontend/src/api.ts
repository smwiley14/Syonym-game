const BASE = "/api";

export interface RandomPuzzle {
  start: string;
  end: string;
  optimal_steps: number;
  date?: string;
}

export interface SynsetGroup {
  definition: string;
  examples: string[];
  pos: string;
  relations: Record<string, string[]>;
}

export interface NeighborsResult {
  synsets: SynsetGroup[];
}

export async function fetchRandomPuzzle(): Promise<RandomPuzzle> {
  const res = await fetch(`${BASE}/synonym-chain/random`);
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? "Failed to generate a puzzle");
  }
  return res.json();
}

export async function fetchDailyPuzzle(): Promise<RandomPuzzle> {
  const res = await fetch(`${BASE}/synonym-chain/puzzle`);
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? "Failed to load daily puzzle");
  }
  return res.json();
}

export async function fetchNeighbors(word: string, conceptual = false): Promise<NeighborsResult> {
  const url = `${BASE}/synonym-chain/neighbors/${encodeURIComponent(word)}${conceptual ? "?conceptual=true" : ""}`;
  const res = await fetch(url);
  if (!res.ok) return { synsets: [] };
  const data = await res.json();
  return { synsets: data.synsets ?? [] };
}

export async function fetchExplore(word: string): Promise<NeighborsResult & { word: string }> {
  const res = await fetch(`${BASE}/explorer/${encodeURIComponent(word)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => null);
    throw new Error(err?.detail ?? "Request failed");
  }
  return res.json();
}

export async function validateChain(
  start: string,
  end: string,
  chain: string[],
  conceptual = false
): Promise<{ valid: boolean; player_steps: number; optimal_steps: number | null }> {
  const res = await fetch(`${BASE}/synonym-chain/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start, end, chain, conceptual }),
  });
  return res.json();
}
