/**
 * Main entry point for the React application.
 * 
 * Best practices applied:
 * - SWR Provider for global cache configuration (client-swr-dedup)
 * - StrictMode for development-time checks
 * - Proper error handling setup
 */

import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { SWRConfig } from 'swr';
import './index.css';
import App from './App';

// SWR global configuration following best practices
const swrConfig = {
  // Revalidate on focus for fresh data
  revalidateOnFocus: true,
  // Revalidate on reconnect
  revalidateOnReconnect: true,
  // Deduping interval - deduplicate requests within 2 seconds
  dedupingInterval: 2000,
  // Error retry count
  errorRetryCount: 3,
  // Keep previous data while fetching new data
  keepPreviousData: true,
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SWRConfig value={swrConfig}>
      <App />
    </SWRConfig>
  </StrictMode>
);
