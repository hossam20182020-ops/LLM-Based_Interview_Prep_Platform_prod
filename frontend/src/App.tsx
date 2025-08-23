import React from "react";
import GenerateForm from "./components/GenerateForm";
import QuestionList from "./components/QuestionList";
import Stats from "./components/Stats";
import Card from "./components/ui/Card";

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b">
        <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          {/* Left: title + tagline */}
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-green-400 to-blue-500" />
              <h1 className="text-lg font-semibold">AI-Powered Interview Preparation</h1>
              <span className="ml-2 rounded-md border px-1.5 py-0.5 text-xs text-neutral-600">v1</span>
            </div>
            <p className="text-sm font-semibold text-black max-w-2xl">
              Generate realistic interview questions with AI, save datasets, and track your progress ✨.
            </p>
          </div>

          {/* Right: actions (placeholder) */}
          <div className="flex items-center gap-2">{/* actions */}</div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-6">
          <Card title="Generate Questions">
            <GenerateForm />
          </Card>
          <Card title="Saved Questions">
            <QuestionList />
          </Card>
        </div>
        <aside className="space-y-6 md:sticky md:top-20 h-fit">
          <Card title="Stats">
            <Stats />
          </Card>
        </aside>
      </main>
    </div>
  );
}
