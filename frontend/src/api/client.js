const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000"

/**
 * Upload a PDF file and start a new session.
 *
 * @param {File} file - The PDF file object from the file input or drop event.
 * @returns {Promise<{session_id, filename, pages, chunks, status}>}
 */
export async function uploadPDF(file) {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Upload failed.")
  }

  return response.json()
}

/**
 * Stream a chat response token by token using SSE.
 *
 * Opens a POST /chat request and reads the streaming response manually.
 * Calls onToken for each text token, onDone with citations when complete,
 * and onError if the request or stream fails.
 *
 * @param {string} session_id
 * @param {string} question
 * @param {(token: string) => void} onToken - Called for each streamed token.
 * @param {(citations: Array) => void} onDone - Called once with final citations.
 * @param {(error: Error) => void} onError - Called on any failure.
 */
export async function streamChat(session_id, question, onToken, onDone, onError) {
  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id, question }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || "Chat request failed.")
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ""

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split("\n")
      buffer = lines.pop()

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue
        const event = JSON.parse(line.slice(6))

        if (event.type === "token") {
          onToken(event.value)
        } else if (event.type === "done") {
          onDone(event.citations)
        }
      }
    }
  } catch (error) {
    onError(error)
  }
}

/**
 * Fetch the full chat history for a session.
 *
 * @param {string} session_id
 * @returns {Promise<{session_id, messages}>}
 */
export async function getHistory(session_id) {
  const response = await fetch(`${API_BASE}/history/${session_id}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || "Failed to load history.")
  }

  return response.json()
}
