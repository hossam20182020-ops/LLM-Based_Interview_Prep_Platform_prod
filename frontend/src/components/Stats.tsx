import React, { useEffect, useState } from 'react'
import { getStats } from '../services/api'

export default function Stats() {
  const [stats, setStats] = useState<any>(null)
  useEffect(()=>{
    getStats().then(setStats).catch(()=>{})
  },[])

  if (!stats) return <div className="rounded-2xl border bg-white p-4 shadow-sm"><h2 className="text-lg font-semibold">Stats</h2><p>Loading...</p></div>

  return (
    <div className="rounded-2xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Stats</h2>
      <ul>
        <li>Total sets: {stats.total_sets}</li>
        <li>Total questions: {stats.total_questions}</li>
        <li>Flagged questions: {stats.flagged_questions}</li>
        <li>Average difficulty: {stats.avg_difficulty ?? '-'}</li>
      </ul>
    </div>
  )
}
