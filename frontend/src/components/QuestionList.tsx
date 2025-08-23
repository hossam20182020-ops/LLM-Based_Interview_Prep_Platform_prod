import React, { useEffect, useState } from 'react'
import { listQuestionsPaged, updateQuestion, deleteQuestion, QuestionOut } from '../services/api'

export default function QuestionList() {
  const [items, setItems] = useState<QuestionOut[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(5)
  const [pages, setPages] = useState(1)
  const [total, setTotal] = useState(0)
  const [deleting, setDeleting] = useState<number | null>(null)

  async function refresh(p = page, ps = pageSize) {
    setLoading(true)
    try {
      const data = await listQuestionsPaged(p, ps)
      setItems(data.items)
      setPages(data.pages)
      setTotal(data.total)
      setPage(p)
      setPageSize(ps)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { 
    refresh(1, pageSize) 
  }, [])

  const setFlag = async (q: QuestionOut, v: boolean) => {
    try {
      await updateQuestion(q.id, { flagged: v })
      // Update the local state instead of refreshing
      setItems(prevItems => 
        prevItems.map(item => 
          item.id === q.id ? { ...item, flagged: v } : item
        )
      )
    } catch (error) {
      console.error('Failed to update flag:', error)
      alert('Failed to update flag. Please try again.')
    }
  }

  const setDiff = async (q: QuestionOut, v: number) => {
    try {
      await updateQuestion(q.id, { difficulty: v })
      // Update the local state instead of refreshing
      setItems(prevItems => 
        prevItems.map(item => 
          item.id === q.id ? { ...item, difficulty: v } : item
        )
      )
    } catch (error) {
      console.error('Failed to update difficulty:', error)
      alert('Failed to update difficulty. Please try again.')
    }
  }

  const handleDelete = async (q: QuestionOut) => {
    if (!window.confirm(`Delete this question?\n\n"${q.text}"`)) {
      return
    }

    setDeleting(q.id)
    try {
      await deleteQuestion(q.id)
      
      // If we're on the last page and delete the last item, go to previous page
      const newTotal = total - 1
      const newPages = Math.max(1, Math.ceil(newTotal / pageSize))
      const targetPage = page > newPages ? Math.max(1, page - 1) : page
      
      await refresh(targetPage, pageSize)
    } catch (error) {
      console.error('Failed to delete question:', error)
      alert('Failed to delete question. Please try again.')
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="rounded-2xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Saved Questions</h2>
      
      {loading ? <p>Loading...</p> : (
        items.length === 0 ? <p>No questions yet.</p> : (
          <ul className='list'>
            {items.map(q => (
              <li key={q.id} style={{ marginBottom: 16, padding: 12, border: '1px solid #eee', borderRadius: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <div style={{ flex: 1 }}>
                    <strong>#{q.id} {q.type}:</strong> {q.text}
                  </div>
                  <button className="inline-flex items-center justify-center rounded-lg border px-3 py-1.5 text-sm hover:bg-black hover:text-white transition disabled:opacity-50"
                    onClick={() => handleDelete(q)}
                    disabled={deleting === q.id}
                    style={{
                      backgroundColor: '#dc3545',
                      color: 'white',
                      border: 'none',
                      padding: '6px 12px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      cursor: deleting === q.id ? 'not-allowed' : 'pointer',
                      marginLeft: 12,
                      minWidth: '70px'
                    }}
                    title="Delete this question"
                  >
                    {deleting === q.id ? 'Deleting...' : '🗑️ Delete'}
                  </button>
                </div>
                
                <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                  <label>
                    Difficulty:
                    <select 
                      value={q.difficulty ?? ''} 
                      onChange={e => setDiff(q, Number(e.target.value))}
                      disabled={deleting === q.id}
                      style={{ marginLeft: 8 }}
                    >
                      <option value="">--</option>
                      {[1, 2, 3, 4, 5].map(n => <option key={n} value={n}>{n}</option>)}
                    </select>
                  </label>
                  <label>
                    <input 
                      type="checkbox" 
                      checked={q.flagged} 
                      onChange={e => setFlag(q, e.target.checked)}
                      disabled={deleting === q.id}
                      style={{ marginRight: 4 }}
                    />
                    Flag interesting
                  </label>
                </div>
              </li>
            ))}
          </ul>
        )
      )}
      
      <div className="mt-3 flex items-center justify-between gap-3 flex-wrap" style={{ marginTop: 16 }}>
        <button className="inline-flex items-center justify-center rounded-lg border px-3 py-1.5 text-sm hover:bg-black hover:text-white transition disabled:opacity-50" disabled={page <= 1 || loading} onClick={() => refresh(page - 1, pageSize)}>
          Previous
        </button>
        <span style={{ margin: '0 16px' }}>
          Page {page} of {pages} ({total} total questions)
        </span>
        <button className="inline-flex items-center justify-center rounded-lg border px-3 py-1.5 text-sm hover:bg-black hover:text-white transition disabled:opacity-50" disabled={page >= pages || loading} onClick={() => refresh(page + 1, pageSize)}>
          Next
        </button>
        <label style={{ marginLeft: 16 }}>
          Page size:
          <select 
            value={pageSize} 
            onChange={e => refresh(1, Number(e.target.value))} 
            disabled={loading}
            style={{ marginLeft: 8 }}
          >
            {[5, 10, 20, 50].map(n => <option key={n} value={n}>{n}</option>)}
          </select>
        </label>
      </div>
    </div>
  )
}