import React, { useState } from 'react'
import { generate, saveSet, GeneratedQuestion } from '../services/api'

type Props = {
  onSaved: () => void
}

export default function GenerateForm({ onSaved }: Props) {
  const [job, setJob] = useState('Data Scientist')
  const [name, setName] = useState('My DS Set')
  const [loading, setLoading] = useState(false)
  const [qs, setQs] = useState<GeneratedQuestion[]>([])

  const onGenerate = async () => {
    try {
      setLoading(true)
      const out = await generate(job)
      setQs(out)
    } finally {
      setLoading(false)
    }
  }

  const onSave = async () => {
    if (qs.length === 0) return
    setLoading(true)
    try {
      await saveSet(job, qs, name)
      setQs([])
      onSaved()
      alert('Saved!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className='card' style={{marginBottom:16}}>
      <h2>Generate Questions</h2>
      <div className='controls'>
        <input value={job} onChange={e=>setJob(e.target.value)} placeholder="Job title" />
        <input value={name} onChange={e=>setName(e.target.value)} placeholder="Set name (optional)" />
        <button onClick={onGenerate} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</button>
        <button onClick={onSave} disabled={loading || qs.length===0}>Save as Set</button>
      </div>
      {qs.length>0 && (
        <ol>
          {qs.map((q,i)=>(<li key={i}><b>{q.type}:</b> {q.text}</li>))}
        </ol>
      )}
    </div>
  )
}
