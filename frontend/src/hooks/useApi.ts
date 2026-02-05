/**
 * SWR hooks for data fetching following Vercel React best practices.
 * 
 * Best practices applied:
 * - Use SWR for automatic request deduplication (client-swr-dedup)
 * - Proper error handling and loading states
 * - Revalidation on focus for fresh data
 * 
 * @see https://swr.vercel.app
 */

import useSWR from 'swr';
import useSWRMutation from 'swr/mutation';
import { 
  fetchHealth, 
  fetchStats, 
  askQuestion, 
  uploadDocument,
  type HealthResponse,
  type StatsResponse,
  type AnswerResponse,
  type DocumentUploadResponse
} from '../api/client';

// SWR keys
const KEYS = {
  health: '/api/v1/health',
  stats: '/api/v1/stats',
} as const;

/**
 * Hook for fetching health status
 * Uses SWR for caching and automatic revalidation
 */
export function useHealth() {
  return useSWR<HealthResponse>(
    KEYS.health,
    fetchHealth,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: false, // Health doesn't change often
    }
  );
}

/**
 * Hook for fetching system statistics
 * Uses SWR for caching with revalidation on focus
 */
export function useStats() {
  return useSWR<StatsResponse>(
    KEYS.stats,
    fetchStats,
    {
      refreshInterval: 5000, // Refresh every 5 seconds
      revalidateOnFocus: true,
    }
  );
}

/**
 * Hook for asking questions (mutation)
 * Uses SWR Mutation for POST requests
 */
export function useAskQuestion() {
  return useSWRMutation<AnswerResponse, Error, string, string>(
    'ask-question',
    async (_, { arg: question }) => askQuestion(question)
  );
}

/**
 * Hook for uploading documents (mutation)
 * Uses SWR Mutation for file uploads
 */
export function useUploadDocument() {
  return useSWRMutation<DocumentUploadResponse, Error, string, File>(
    'upload-document',
    async (_, { arg: file }) => uploadDocument(file)
  );
}

// Export keys for manual revalidation
export { KEYS };
