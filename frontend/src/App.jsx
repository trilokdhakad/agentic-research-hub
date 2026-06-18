import { useState, useEffect } from 'react'
import axios from 'axios'
import {
  Upload,
  Send,
  Trash2
} from 'lucide-react'

export default function App() {
  const [file, setFile] = useState(null)
  const [query, setQuery] = useState('')
  const [chat, setChat] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState('idle') // 'idle', 'uploading', 'success', 'error'
  const [documents, setDocuments] = useState([])
  const [selectedMetadata, setSelectedMetadata] = useState(null)
  const [selectedDocName, setSelectedDocName] = useState(null) // track which doc is selected

  const fetchDocuments = async () => {
    try {
      const res = await axios.get(
        'http://localhost:8000/documents/'
      )

      setDocuments(res.data.documents)
    } catch (err) {
      console.error(err)
    }
  }

  const deleteDocument = async (filename) => {
    try {
      await axios.delete(
        `http://localhost:8000/documents/${filename}`
      )

      // If the deleted document was selected, clear metadata
      if (selectedDocName === filename) {
        setSelectedMetadata(null)
        setSelectedDocName(null)
      }

      fetchDocuments()
    } catch (err) {
      console.error(err)
    }
  }

  const fetchMetadata = async (filename) => {
    // Toggle: if the same document is clicked again, hide metadata
    if (selectedDocName === filename) {
      setSelectedMetadata(null)
      setSelectedDocName(null)
      return
    }

    try {
      const res = await axios.get(
        `http://localhost:8000/metadata/${filename}`
      )

      setSelectedMetadata(res.data)
      setSelectedDocName(filename)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetchDocuments()
  }, [])

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) return

    setUploadStatus('uploading')
    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post('http://localhost:8000/upload/', formData)
      fetchDocuments()
      setUploadStatus('success')
      setTimeout(() => setUploadStatus('idle'), 3000) // Reset after 3 seconds
    } catch (err) {
      console.error(err)
      setUploadStatus('error')
    }
  }

  const handleAsk = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    const newChat = [...chat, { type: 'user', text: query }]
    setChat(newChat)
    setQuery('')
    setLoading(true)

    try {
      const res = await axios.post('http://localhost:8000/ask/', { question: query })
      setChat([...newChat, {
        type: 'bot',
        text: res.data.answer,
        sources: res.data.sources,
        plan: res.data.plan
      }])
    } catch (err) {
      console.error(err)
      setChat([...newChat, { type: 'bot', text: 'Error connecting to the backend.' }])
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">

        <div className="text-center">
          <h1 className="text-4xl font-bold text-blue-400">Agentic Research Hub</h1>
          <p className="text-gray-400 mt-2">Local RAG Powered by LangGraph</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2"><Upload size={20} /> Knowledge Base</h2>
          <form onSubmit={handleUpload} className="flex gap-4 items-center">
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => setFile(e.target.files[0])}
              className="flex-1 bg-gray-700 p-2 rounded text-sm"
            />
            <button
              type="submit"
              disabled={uploadStatus === 'uploading'}
              className={`px-6 py-2 rounded font-semibold transition-colors ${uploadStatus === 'uploading' ? 'bg-gray-600 cursor-not-allowed' :
                  uploadStatus === 'success' ? 'bg-green-600 hover:bg-green-700' :
                    'bg-blue-600 hover:bg-blue-700'
                }`}
            >
              {uploadStatus === 'uploading' ? 'Processing...' :
                uploadStatus === 'success' ? 'Embedded!' :
                  'Process Document'}
            </button>
          </form>

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-gray-400 mb-2">
              Indexed Documents
            </h3>

            <div className="space-y-2">
              {documents.length === 0 ? (
                <p className="text-gray-500 text-sm">
                  No documents indexed.
                </p>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc.name}
                    onClick={() => fetchMetadata(doc.name)}
                    className={`flex justify-between items-center px-3 py-3 rounded cursor-pointer hover:bg-gray-600 ${
                      selectedDocName === doc.name ? 'bg-gray-600' : 'bg-gray-700'
                    }`}
                  >
                    <div>
                      <div className="font-medium">
                        {doc.name}
                      </div>

                      <div className="text-xs text-gray-400 mt-1">
                        {doc.type.toUpperCase()} • {doc.chunks} chunks
                      </div>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteDocument(doc.name)
                      }}
                      className="text-red-400 hover:text-red-300"
                    >
                      <Trash2 size={18} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>

          {selectedMetadata && (
            <div className="mt-6 bg-gray-700 p-4 rounded">
              
              <h3 className="text-lg font-semibold text-blue-400 mb-3">
                Document Intelligence
              </h3>

              <div className="space-y-3">

                <div>
                  <div className="text-sm text-gray-400">
                    Title
                  </div>
                  <div>
                    {selectedMetadata.title}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400">
                    Summary
                  </div>
                  <div>
                    {selectedMetadata.summary}
                  </div>
                </div>

                <div>
                  <div className="text-sm text-gray-400">
                    Keywords
                  </div>

                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedMetadata.keywords?.map(
                      (keyword, idx) => (
                        <span
                          key={idx}
                          className="bg-blue-600 px-2 py-1 rounded text-sm"
                        >
                          {keyword}
                        </span>
                      )
                    )}
                  </div>
                </div>

              </div>

            </div>
          )}
        </div>

        <div className="bg-gray-800 rounded-lg border border-gray-700 h-[500px] flex flex-col">
          <div className="flex-1 p-6 overflow-y-auto space-y-4">
            {chat.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-lg p-4 ${msg.type === 'user' ? 'bg-blue-600' : 'bg-gray-700'}`}>

                  {msg.plan && (
                    <div className="mb-4 p-3 bg-gray-900 rounded border border-gray-600 text-sm text-gray-400 font-mono">
                      <span className="text-blue-400 font-bold block mb-1">🤖 Planner Agent Strategy:</span>
                      {msg.plan}
                    </div>
                  )}

                  <p className="whitespace-pre-wrap">{msg.text}</p>

                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-600 text-xs text-gray-300 font-mono">
                      Sources: {msg.sources.join(', ')}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && <div className="text-gray-400 animate-pulse">Consulting Vector DB...</div>}
          </div>

          <form onSubmit={handleAsk} className="p-4 border-t border-gray-700 flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about your research..."
              className="flex-1 bg-gray-700 p-3 rounded text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button type="submit" className="bg-blue-600 hover:bg-blue-700 p-3 rounded transition-colors flex items-center justify-center">
              <Send size={20} />
            </button>
          </form>
        </div>

      </div>
    </div>
  )
}