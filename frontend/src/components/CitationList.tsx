import { Citation } from "../api";

type Props = {
  citations: Citation[];
};

export function CitationList({ citations }: Props) {
  if (citations.length === 0) {
    return null;
  }

  return (
    <div className="citations">
      <strong>Sources</strong>
      <ul>
        {citations.map((citation) => (
          <li key={citation.chunk_id}>
            {citation.source}, p.{citation.page}, {citation.section}
          </li>
        ))}
      </ul>
    </div>
  );
}
