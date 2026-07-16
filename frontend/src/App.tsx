import { useState } from "react";
import SynonymChain from "./games/SynonymChain";
import Explorer from "./games/Explorer";

const TABS = ["Word Chain", "Explorer"] as const;
type Tab = (typeof TABS)[number];

export default function App() {
  const [tab, setTab] = useState<Tab>("Word Chain");

  return (
    <main>
      <header className="masthead">
        <h1 className="headword-title">
          Syn<span className="syllable-dot">·</span>on<span className="syllable-dot">·</span>y<span className="syllable-dot">·</span>non<span className="syllable-dot">·</span>ism
        </h1>
        <p className="pronunciation">
          /sɪˈnɒn.ɪ.nɒn.ɪz.əm/ <span className="pos">n.</span>
        </p>
        <p className="tagline">a game of words and their relations</p>
        <hr className="masthead-rule" />
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`tab-btn${tab === t ? " active" : ""}`}
          >
            {t}
          </button>
        ))}
      </nav>

      {tab === "Word Chain" && <SynonymChain />}
      {tab === "Explorer" && <Explorer />}

      <footer className="powered-by">
        <span className="powered-by-label">Powered by</span>
        <a
          href="https://github.com/globalwordnet/english-wordnet"
          target="_blank"
          rel="noopener noreferrer"
          className="powered-by-link"
        >
          <img src="/wordnet.png" alt="Global WordNet Association" className="powered-by-logo" />
        </a>
      </footer>
    </main>
  );
}
