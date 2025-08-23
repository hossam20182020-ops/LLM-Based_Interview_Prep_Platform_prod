import React, { useState } from 'react'
import { generate, saveSet, GeneratedQuestion } from '../services/api'

type Props = {
  onSaved: () => void
}

export default function GenerateForm({ onSaved }: Props) {
  const [job, setJob] = useState('Job title')
  const [name, setName] = useState('Dataset Name')
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

  const handleSave = async () => {
    if (qs.length === 0) return
    setLoading(true)
    try {
      await saveSet(job, qs, name)
      setQs([])
      onSaved?.()
      //alert('Saved!')
      // Full refresh so Saved Questions & Stats update immediately
      window.location.reload()
    } catch (err) {
      console.error('Save failed:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl border bg-white shadow-sm p-4">
      <h2 className="text-lg font-semibold">Generate Questions</h2>
      <div className="mt-3 grid gap-3 md:grid-cols-3">
        <input
          className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 
                     placeholder-gray-400 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500"
          value={job}
          onChange={e => setJob(e.target.value)}
          placeholder="Job title"
        />

        <input
          className="w-full rounded-xl border border-gray-300 bg-white px-3 py-2 text-gray-900 
                     placeholder-gray-400 outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500"
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Set name (optional)"
        />

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl bg-green-400 px-4 py-2 font-medium 
                     text-white hover:bg-green-500 transition disabled:opacity-50"
          onClick={onGenerate}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate'}
        </button>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl bg-green-400 px-4 py-2 font-medium 
                     text-white hover:bg-green-500 transition disabled:opacity-50"
          onClick={handleSave}
          disabled={loading || qs.length === 0}
        >
          Save as Set
        </button>
      </div>

      {qs.length > 0 && (
        <ol className="mt-4 space-y-2">
          {qs.map((q, i) => (
            <li key={i}>
              <b>{q.type}:</b> {q.text}
            </li>
          ))}
        </ol>
      )}
    </div>
  )
}
