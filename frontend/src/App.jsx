import { useEffect, useState } from "react"
import { getHistory } from "./api/client"
import ChatWindow from "./components/ChatWindow/ChatWindow"
import UploadZone from "./components/UploadZone/UploadZone"
import styles from "./App.module.css"

export default function App() {
  const [session, setSession] = useState(null)
  const [initialMessages, setInitialMessages] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const session_id = localStorage.getItem("session_id")
    const filename = localStorage.getItem("filename")

    if (!session_id) {
      setLoading(false)
      return
    }

    getHistory(session_id)
      .then((data) => {
        setInitialMessages(data.messages.map((m) => ({
          role: m.role,
          content: m.content,
          citations: m.citations || [],
          streaming: false,
        })))
        setSession({ session_id, filename })
      })
      .catch(() => {
        localStorage.removeItem("session_id")
        localStorage.removeItem("filename")
      })
      .finally(() => setLoading(false))
  }, [])

  function handleUploadComplete(session_id, filename) {
    setInitialMessages([])
    setSession({ session_id, filename })
  }

  function handleNewSession() {
    localStorage.removeItem("session_id")
    localStorage.removeItem("filename")
    setSession(null)
    setInitialMessages([])
  }

  if (loading) {
    return (
      <div className={styles.center}>
        <p className={styles.loading}>Loading...</p>
      </div>
    )
  }

  return (
    <div className={styles.app}>
      {session ? (
        <ChatWindow
          sessionId={session.session_id}
          filename={session.filename}
          initialMessages={initialMessages}
          onNewSession={handleNewSession}
        />
      ) : (
        <div className={styles.center}>
          <h1 className={styles.title}>DocTalk</h1>
          <p className={styles.subtitle}>Chat with your documents</p>
          <UploadZone onUploadComplete={handleUploadComplete} />
        </div>
      )}
    </div>
  )
}
