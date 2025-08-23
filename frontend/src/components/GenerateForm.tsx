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
  const [jobError, setJobError] = useState('')

  const onGenerate = async () => {
    // Validate job title length
    if (job.length > 50) {
      setJobError('Job title must be 50 characters or less')
      return
    }
    if (job.trim().length === 0) {
      setJobError('Job title cannot be empty')
      return
    }
    setJobError('')

    try {
      setLoading(true)
      const out = await generate(job)
      setQs(out)
    } catch (err) {
      console.error('Generate failed:', err)
      if (err instanceof Error) {
        setJobError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleJobChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setJob(value)
    
    if (value.length > 50) {
      setJobError('Job title must be 50 characters or less')
    } else if (value.trim().length === 0) {
      setJobError('Job title cannot be empty')
    } else {
      setJobError('')
    }
  }

  const handleSave = async () => {
    if (qs.length === 0) return
    
    // Validate again before saving
    if (job.length > 50) {
      setJobError('Job title must be 50 characters or less')
      return
    }
    if (job.trim().length === 0) {
      setJobError('Job title cannot be empty')
      return
    }

    setLoading(true)
    try {
      await saveSet(job, qs, name)
      setQs([])
      onSaved?.()
      // Full refresh so Saved Questions & Stats update immediately
      window.location.reload()
    } catch (err) {
      console.error('Save failed:', err)
      if (err instanceof Error) {
        setJobError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="rounded-2xl border bg-white shadow-sm p-4">
      <h2 className="text-lg font-semibold">Generate Questions</h2>
      <div className="mt-3 grid gap-3 md:grid-cols-3">
        <div className="relative">
          <input
            className={`w-full h-11 rounded-xl border 
              ${jobError ? "border-red-500" : "border-gray-300"} 
              bg-white px-3 text-gray-900 placeholder-gray-400 
              outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500`}
            value={job}
            onChange={handleJobChange}
            placeholder="Job title"
            maxLength={50}  // Allow slight overage for real-time feedback
          />
          <div className="mt-1 flex justify-between items-center">
            <span className="text-xs text-gray-400">Max 50 characters</span>
            <span className={`text-xs ${
              job.length > 50 
                ? 'text-red-500' 
                : job.length > 25 
                ? 'text-orange-500' 
                : 'text-gray-400'
            }`}>
              {job.length}/50
            </span>
          </div>
          {jobError && (
            <span className="text-xs text-red-500 mt-1 block">{jobError}</span>
          )}
        </div>

        <input
         className="w-full h-11 rounded-xl border border-gray-300 
            bg-white px-3 text-gray-900 placeholder-gray-400 
            outline-none focus:border-green-500 focus:ring-2 focus:ring-green-500"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Set name (optional)"
        />

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl bg-green-400 px-4 py-2 font-medium 
                     text-white hover:bg-green-500 transition disabled:opacity-50"
          onClick={onGenerate}
          disabled={loading || job.length > 50 || job.trim().length === 0}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Generating...
            </>
          ) : 'Generate'}
        </button>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl bg-green-400 px-4 py-2 font-medium 
                     text-white hover:bg-green-500 transition disabled:opacity-50"
          onClick={handleSave}
          disabled={loading || qs.length === 0 || job.length > 50 || job.trim().length === 0}
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