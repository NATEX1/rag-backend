/**
 * Main App component - aggregates all UI components.
 * 
 * Best practices applied:
 * - Uses SWR mutate for cache invalidation (client-swr-dedup)
 * - React.memo to prevent unnecessary re-renders
 * - Direct imports from antd submodules (bundle-barrel-imports)
 * - useCallback for stable event handlers (rerender-dependencies)
 * - Proper cleanup in useEffect
 * - Explicit conditional rendering with ternary (rendering-conditional-render)
 */

import { memo, useCallback, useEffect, useState } from 'react';
import ConfigProvider from 'antd/es/config-provider';
import Layout from 'antd/es/layout';
import { QuestionOutlined } from '@ant-design/icons';
import { useSWRConfig } from 'swr';
import { AnswerDisplay } from './components/AnswerDisplay';
import { DocumentUpload } from './components/DocumentUpload';
import { QuestionInput } from './components/QuestionInput';
import { StatsPanel } from './components/StatsPanel';
import { KEYS } from './hooks/useApi';

type AnswerData = {
  question: string;
  answer: string;
  sources: string[];
};

// Memoized App component for performance
const App = memo(function App() {
  const { mutate } = useSWRConfig();
  const [latestAnswer, setLatestAnswer] = useState<AnswerData | null>(null);

  // Stable callback for document upload handler
  const handleDocumentUploaded = useCallback(() => {
    // Revalidate stats using SWR's mutate
    mutate(KEYS.stats);
  }, [mutate]);

  // Stable callback for answer received handler
  const handleAnswerReceived = useCallback((e: Event) => {
    const answer = (e as CustomEvent).detail as AnswerData;
    setLatestAnswer(answer);
  }, []);

  useEffect(() => {
    window.addEventListener('documentUploaded', handleDocumentUploaded);
    window.addEventListener('answerReceived', handleAnswerReceived);

    return () => {
      window.removeEventListener('documentUploaded', handleDocumentUploaded);
      window.removeEventListener('answerReceived', handleAnswerReceived);
    };
  }, [handleDocumentUploaded, handleAnswerReceived]);

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#dc143c',
          colorInfo: '#dc143c',
          colorSuccess: '#52c41a',
          colorWarning: '#faad14',
          colorError: '#ff4d4f',
          borderRadius: 8,
        },
      }}
    >
      <Layout style={{ minHeight: '100vh', background: '#f5f5f5' }}>
        <Layout.Header
          style={{
            background: '#ffffff',
            padding: '0 60px',
            display: 'flex',
            alignItems: 'center',
            height: '64px',
            borderBottom: '1px solid #e8e8e8',
          }}
        >
          <div
            style={{
              color: '#262626',
              fontSize: '20px',
              fontWeight: 600,
              letterSpacing: '-0.3px',
            }}
          >
            <QuestionOutlined style={{ marginRight: '10px', fontSize: '22px', color: '#dc143c' }} />
            College RAG
          </div>
        </Layout.Header>

        <Layout.Content style={{ padding: '32px 24px' }}>
          <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'grid', gridTemplateColumns: '320px 1fr', gap: '24px', alignItems: 'start' }}>
            <div style={{ position: 'sticky', top: '88px' }}>
              <StatsPanel />
              <div style={{ marginTop: '24px' }}>
                <DocumentUpload />
              </div>
            </div>
            <div>
              <QuestionInput />
              {latestAnswer ? (
                <div style={{ marginTop: '24px' }}>
                  <AnswerDisplay answer={latestAnswer} />
                </div>
              ) : (
                <div style={{ 
                  marginTop: '24px', 
                  padding: '48px 32px',
                  textAlign: 'center',
                  background: 'white',
                  borderRadius: '8px',
                  border: '1px solid #e8e8e8',
                  color: '#8c8c8c',
                  fontSize: '14px' 
                }}>
                  Ask a question to get started
                </div>
              )}
            </div>
          </div>
        </Layout.Content>
      </Layout>
    </ConfigProvider>
  );
});

export default App;
