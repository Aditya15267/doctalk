import { useEffect, useRef, useState } from "react"
import { streamChat } from "../../api/client"
import MessageBubble from "../MessageBubble/MessageBubble"
import styles from "./ChatWindow.module.css"

export default function ChatWindow({ sessionId, filename, initialMessages, onNewSession }) {
  const [messages, setMessages] = useState(initialMessages || [])
  const [input, setInput] = useState("")
  const [streaming, setStreaming] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  async function handleSend() {
    const question = input.trim()
    if (!question || streaming) return

    setInput("")
    setStreaming(true)

    setMessages(prev => [
      ...prev,
      { role: "user", content: question, citations: [], streaming: false },
      { role: "assistant", content: "", citations: [], streaming: true },
    ])

    await streamChat(
      sessionId,
      question,
      (token) => {
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: updated[updated.length - 1].content + token,
          }
          return updated
        })
      },
      (citations) => {
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            citations,
            streaming: false,
          }
          return updated
        })
        setStreaming(false)
      },
      (err) => {
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: "Something went wrong. Please try again.",
            streaming: false,
          }
          return updated
        })
        setStreaming(false)
        console.error(err)
      },
    )
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <span className={styles.filename}>{filename}</span>
        <button className={styles.newBtn} onClick={onNewSession}>
          New document
        </button>
      </header>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <p className={styles.empty}>Your document is ready. Ask anything.</p>
        )}
        {messages.map((message, i) => (
          <MessageBubble key={i} message={message} />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <textarea
          className={styles.input}
          rows={1}
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={streaming}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={!input.trim() || streaming}
        >
          Send
        </button>
      </div>
    </div>
  )
}
