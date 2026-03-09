/**
 * Custom hook for submitting investigation queries
 */

import { useState } from "react";
import { api } from "@/lib/api";

interface QueryResult {
  query: string;
  response: string;
  evidence: Array<{
    id: string;
    content: string;
    similarity: number;
    category: string;
    severity: string;
    timestamp: string;
  }>;
  confidence: number;
  techniques: string[];
  response_time: number;
  evidence_count: number;
}

export function useQuery() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryResult[]>([]);

  const submit = async (query: string, topK: number = 5) => {
    try {
      setLoading(true);
      setError(null);

      const response = await api.query.submit(query, topK);
      setResult(response);
      setHistory((prev) => [response, ...prev]);

      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Query failed";
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearHistory = () => setHistory([]);
  const clearResult = () => setResult(null);

  return {
    loading,
    result,
    error,
    history,
    submit,
    clearHistory,
    clearResult,
  };
}
