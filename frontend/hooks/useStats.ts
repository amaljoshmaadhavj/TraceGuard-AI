/**
 * Custom hook for fetching statistics
 */

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

interface Statistics {
  total_events: number;
  total_files: number;
  total_techniques: number;
  events_by_category: Record<string, number>;
  severity_distribution: Record<string, number>;
  techniques_list: string[];
}

export function useStats() {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.stats.get();
      setStats(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch stats";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return {
    stats,
    loading,
    error,
    refetch: fetchStats,
  };
}
