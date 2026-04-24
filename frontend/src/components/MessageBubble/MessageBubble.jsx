import CitationCard from "../CitationCard/CitationCard"
import styles from "./MessageBubble.module.css"

export default function MessageBubble({ message }) {
  const isUser = message.role === "user"

  return (
    <div className={`${styles.wrapper} ${isUser ? styles.userWrapper : styles.assistantWrapper}`}>
      <div className={`${styles.bubble} ${isUser ? styles.userBubble : styles.assistantBubble}`}>
        {message.content}
        {message.streaming && <span className={styles.cursor}>|</span>}
      </div>

      {!isUser && message.citations?.length > 0 && (
        <div className={styles.citations}>
          {message.citations.map((citation, i) => (
            <CitationCard key={i} citation={citation} />
          ))}
        </div>
      )}
    </div>
  )
}
