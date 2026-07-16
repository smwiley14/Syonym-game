import { Fragment } from "react";
import type { SynsetGroup } from "../api";

const RELATION_ORDER = [
  "synonym", "antonym", "hypernym", "hyponym",
  "mero_part", "mero_member", "mero_substance",
  "holo_part", "holo_member", "holo_substance",
  "derivation",
];

const RELATION_ABBR: Record<string, string> = {
  // ConceptNet relations
  UsedFor: "used for",
  CapableOf: "capable of",
  AtLocation: "at location",
  MadeOf: "made of",
  HasProperty: "has property",
  Causes: "causes",
  PartOf: "part of",
  SimilarTo: "similar to",
  IsA: "is a",
  Synonym: "syn.",
  synonym: "syn.",
  antonym: "ant.",
  hypernym: "hyper.",
  hyponym: "hypo.",
  derivation: "deriv.",
  pertainym: "pertain.",
  participle: "part.",
  similar: "sim.",
  also: "see also",
  attribute: "attrib.",
  entails: "entails",
  is_entailed_by: "entailed by",
  causes: "causes",
  is_caused_by: "caused by",
  exemplifies: "exemplifies",
  is_exemplified_by: "exemplified by",
  holo_part: "part of",
  mero_part: "has part",
  holo_member: "member of",
  mero_member: "has member",
  holo_substance: "substance of",
  mero_substance: "has substance",
  instance_hypernym: "instance of",
  instance_hyponym: "has instance",
  domain_topic: "topic",
  has_domain_topic: "in topic",
  domain_region: "region",
  has_domain_region: "in region",
};

function relationRank(rel: string) {
  const i = RELATION_ORDER.indexOf(rel);
  return i === -1 ? RELATION_ORDER.length : i;
}

function relationLabel(rel: string) {
  return RELATION_ABBR[rel] ?? rel.replace(/_/g, " ");
}

export default function SynsetBlock({
  synset,
  onWordClick,
}: {
  synset: SynsetGroup;
  onWordClick: (word: string) => void;
}) {
  const groups = Object.entries(synset.relations).sort(
    ([a], [b]) => relationRank(a) - relationRank(b) || a.localeCompare(b)
  );

  return (
    <div className="synset-block">
      <p className="synset-def">
        {synset.pos && <span className="sense-pos">{synset.pos} </span>}
        {synset.definition}
        {synset.examples.map((ex, i) => (
          <span key={i} className="sense-example"> "{ex}"</span>
        ))}
      </p>
      {groups.map(([rel, words]) => (
        <p key={rel} className="relation-entry">
          <span className="relation-label">{relationLabel(rel)}</span>
          {words.map((w, i) => (
            <Fragment key={w}>
              {i > 0 && <span className="entry-sep">, </span>}
              <button className="word-link" onClick={() => onWordClick(w)}>
                {w}
              </button>
            </Fragment>
          ))}
        </p>
      ))}
    </div>
  );
}
