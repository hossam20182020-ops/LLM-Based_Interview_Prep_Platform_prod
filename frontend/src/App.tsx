import React from 'react'
import GenerateForm from './components/GenerateForm'
import QuestionList from './components/QuestionList'
import Stats from './components/Stats'

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b">
  <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
    <div className="flex items-center gap-2">
      <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-green-400 to-blue-500" />
      <h1 className="text-lg font-semibold">LLM Interview Prep</h1>
      <span className="ml-2 rounded-md border px-1.5 py-0.5 text-xs text-neutral-600">v1</span>
    </div>
    <div className="flex items-center gap-2">
      {/* optional: dark toggle later */}
      <a href="https://github.com/..." target="_blank" className="text-sm underline underline-offset-4 hover:opacity-80">Docs</a>
    </div>
  </div>
</header>


      <main className="container max-w-5xl py-6 grid gap-6 md:grid-cols-3">
        <section className="md:col-span-2 space-y-6">
          <GenerateForm onSaved={() => {}} />
          <QuestionList />
        </section>
        <aside className="space-y-6">
          <Stats />
        </aside>
      </main>

      <footer className="container max-w-5xl pb-10 pt-2 text-sm text-neutral-500">
        Built with FastAPI + React + PostgreSQL
      </footer>
    </div>
  )
}
