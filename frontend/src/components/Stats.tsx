import React, { useEffect, useState } from "react";
import { getStats } from "../services/api";

type RawStats =
  | {
      total_sets?: number;
      total_questions?: number;
      flagged_questions?: number;
      avg_difficulty?: number | null;
      totalSets?: number;
      totalQuestions?: number;
      flaggedQuestions?: number;
      avgDifficulty?: number | null;
    }
  | null;

type UiStats = {
  totalSets: number;
  totalQuestions: number;
  flaggedQuestions: number;
  avgDifficulty: number | null;
};

function normalizeStats(s: RawStats): UiStats | null {
  if (!s) return null;
  const totalSets = (s.totalSets ?? s.total_sets) as number | undefined;
  const totalQuestions = (s.totalQuestions ?? s.total_questions) as number | undefined;
  const flaggedQuestions = (s.flaggedQuestions ?? s.flagged_questions) as number | undefined;
  const avgDifficulty = (s.avgDifficulty ?? s.avg_difficulty ?? null) as number | null;

  if (
    totalSets === undefined ||
    totalQuestions === undefined ||
    flaggedQuestions === undefined
  ) {
    return null; // shape not usable
  }
  return { totalSets, totalQuestions, flaggedQuestions, avgDifficulty };
}

export default function Stats() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<UiStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const ac = new AbortController();
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const raw = await getStats(ac.signal); // api returns Stats | null
        const norm = normalizeStats(raw as RawStats);
        if (!norm) {
          setStats(null);
          // not an error—just nothing to show yet
        } else {
          setStats(norm);
        }
      } catch (e: any) {
        setError(e?.message || "Failed to load stats");
      } finally {
        setLoading(false);
      }
    })();
    return () => ac.abort();
  }, []);

  return (
    <div className="rounded-2xl border bg-white p-4 shadow-sm">
      <h2 className="text-lg font-semibold">Stats</h2>

      {loading && <p className="text-sm text-muted-foreground">Loading…</p>}

      {!loading && error && (
        <p className="text-sm text-red-600">Couldn’t load stats. {error}</p>
      )}

      {!loading && !error && !stats && (
        <p className="text-sm text-muted-foreground">No stats yet.</p>
      )}

      {!loading && !error && stats && (
        <ul className="mt-1 space-y-1">
          <li>Total sets: {stats.totalSets}</li>
          <li>Total questions: {stats.totalQuestions}</li>
          <li>Flagged questions: {stats.flaggedQuestions}</li>
          <li>Average difficulty: {stats.avgDifficulty ?? "-"}</li>
        </ul>
      )}
    </div>
  );
}
