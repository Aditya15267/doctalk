import { useRef, useState } from "react"
import { uploadPDF } from "../../api/client"
import styles from "./UploadZone.module.css"

export default function UploadZone({ onUploadComplete }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  function handleFileSelect(selected) {
    setError(null)
    setFile(selected)
  }

  function handleDragOver(e) {
    e.preventDefault()
    setDragging(true)
  }

  function handleDragLeave() {
    setDragging(false)
  }

  function handleDrop(e) {
    e.preventDefault()
    setDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) handleFileSelect(dropped)
  }

  async function handleUpload() {
    if (!file) return
    setLoading(true)
    setError(null)

    try {
      const result = await uploadPDF(file)
      localStorage.setItem("session_id", result.session_id)
      localStorage.setItem("filename", result.filename)
      onUploadComplete(result.session_id, result.filename)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  function formatSize(bytes) {
    return (bytes / (1024 * 1024)).toFixed(2) + " MB"
  }

  return (
    <div className={styles.wrapper}>
      <div
        className={`${styles.dropzone} ${dragging ? styles.dragging : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => inputRef.current.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className={styles.hidden}
          onChange={(e) => handleFileSelect(e.target.files[0])}
        />

        {file ? (
          <div className={styles.fileInfo}>
            <span className={styles.filename}>{file.name}</span>
            <span className={styles.filesize}>{formatSize(file.size)}</span>
          </div>
        ) : (
          <div className={styles.placeholder}>
            <p>Drag &amp; drop a PDF here</p>
            <p className={styles.or}>or click to browse</p>
          </div>
        )}
      </div>

      {error && <p className={styles.error}>{error}</p>}

      {loading && (
        <p className={styles.processing}>
          Processing your document — this may take a moment...
        </p>
      )}

      <button
        className={styles.uploadBtn}
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? "Uploading..." : "Upload PDF"}
      </button>
    </div>
  )
}
