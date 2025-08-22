import React, { useEffect, useState } from 'react'
import { listQuestionsPaged, updateQuestion, QuestionOut } from '../services/api'

export default function QuestionList() {
const [items, setItems] = useState<QuestionOut[]>([])
const [loading, setLoading] = useState(true)
const [page, setPage] = useState(1)
const [pageSize, setPageSize] = useState(5)
const [pages, setPages] = useState(1)
const [total, setTotal] = useState(0)

async function refresh(p=page, ps=pageSize) {
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

useEffect(()=>{ refresh(1, pageSize) }, [])

  const setFlag = async (q: QuestionOut, v: boolean) => {
    await updateQuestion(q.id, { flagged: v })
    refresh()
  }

  const setDiff = async (q: QuestionOut, v: number) => {
    await updateQuestion(q.id, { difficulty: v })
    refresh()
  }

  return (
    <div className='card'>
      <h2>Saved Questions</h2>
      {loading ? <p>Loading...</p> : (
        items.length===0 ? <p>No questions yet.</p> : (
          <ul className='list'>
            {items.map(q => (
              <li key={q.id} style={{marginBottom:10}}>
                <b>#{q.id} {q.type}:</b> {q.text}
                <div style={{display:'flex', gap:8, alignItems:'center'}}>
                  <label>
                    Difficulty:
                    <select value={q.difficulty ?? ''} onChange={e=>setDiff(q, Number(e.target.value))}>
                      <option value="">--</option>
                      {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
                    </select>
                  </label>
                  <label>
                    <input type="checkbox" checked={q.flagged} onChange={e=>setFlag(q, e.target.checked)} />
                    Flag
                  </label>
                </div>
              </li>
            ))}
          </ul>
            )
  )}
  <div className='pagination' style={{marginTop:12}}>
    <button disabled={page<=1} onClick={()=>refresh(page-1, pageSize)}>Prev</button>
    <span>Page {page} / {pages} — {total} total</span>
    <button disabled={page>=pages} onClick={()=>refresh(page+1, pageSize)}>Next</button>
    <label>
      Page size:
      <select value={pageSize} onChange={e=>refresh(1, Number(e.target.value))}>
        {[5,10,20,50].map(n=> <option key={n} value={n}>{n}</option>)}
      </select>
    </label>
  </div>
</div>
  )
}
