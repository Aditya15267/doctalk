import { useState } from "react"
import styles from "./CitationCard.module.css"

export default function CitationCard({ citation }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className={styles.card}>
      <button
        className={styles.toggle}
        onClick={() => setExpanded(prev => !prev)}
      >
        Source: Page {citation.page_number + 1}
        <span className={styles.arrow}>{expanded ? "▲" : "▼"}</span>
      </button>

      {expanded && (
        <p className={styles.text}>{citation.chunk_text}</p>
      )}
    </div>
  )
}
