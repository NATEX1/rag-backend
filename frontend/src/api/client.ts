/**
 * API client configuration following Vercel React best practices.
 * Uses axios for HTTP requests with proper typing.
 * 
 * Best practices applied:
 * - Separate raw API functions from React hooks (SWR)
 * - Type-safe API calls
 * - Centralized error handling
 */

import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// Type definitions
export interface AnswerResponse {
  question: string;
  answer: string;
  sources: string[];
  confidence?: number;
}

export interface DocumentUploadResponse {
  success: boolean;
  message: string;
  filename?: string;
  chunks_created?: number;
}

export interface StatsResponse {
  total_documents: number;
  collection_name: string;
  embedding_model: string;
  llm_model: string;
}

export interface HealthResponse {
  status: string;
  message: string;
}

// Raw API functions for SWR
export const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/health');
  return response.data;
};

export const fetchStats = async (): Promise<StatsResponse> => {
  const response = await api.get<StatsResponse>('/stats');
  return response.data;
};

export const askQuestion = async (question: string): Promise<AnswerResponse> => {
  const response = await api.post<AnswerResponse>('/query', { question });
  return response.data;
};

export const uploadDocument = async (file: File): Promise<DocumentUploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<DocumentUploadResponse>(
    '/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};
