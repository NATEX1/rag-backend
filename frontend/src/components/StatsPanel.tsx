/**
 * Stats Panel component - displays system statistics.
 * 
 * Best practices applied:
 * - Uses SWR for automatic deduplication and caching (client-swr-dedup)
 * - React.memo to prevent unnecessary re-renders (rerender-memo)
 * - Direct imports from antd submodules to avoid barrel imports (bundle-barrel-imports)
 * - Proper error handling with Alert component
 */

import { memo } from 'react';
import Card from 'antd/es/card';
import Statistic from 'antd/es/statistic';
import Alert from 'antd/es/alert';
import { useStats } from '../hooks/useApi';

// Memoized component to prevent re-renders when parent updates
export const StatsPanel = memo(function StatsPanel() {
  const { data: stats, error, isLoading } = useStats();

  // Early return for error state
  if (error) {
    return (
      <Alert
        message="Failed to load statistics"
        description={error.message}
        type="error"
        showIcon
      />
    );
  }

  return (
    <Card 
      title={
        <span style={{ fontSize: '15px', fontWeight: 600, color: '#262626' }}>
          System Stats
        </span>
      }
      loading={isLoading}
      style={{ 
        background: '#ffffff',
        border: '1px solid #e8e8e8'
      }}
      bodyStyle={{ padding: '16px' }}
    >
      <Statistic
        title="Documents"
        value={stats?.total_documents ?? 0}
        valueStyle={{ color: '#dc143c', fontSize: '24px', fontWeight: '600' }}
        titleStyle={{ fontSize: '13px', color: '#595959' }}
      />
      <div style={{ height: '16px' }} />
      <div style={{ fontSize: '13px', color: '#595959', marginBottom: '4px' }}>
        LLM Model
      </div>
      <div style={{ 
        fontSize: '14px', 
        color: '#262626', 
        marginBottom: '12px'
      }}>
        {stats?.llm_model ?? '-'}
      </div>
      <div style={{ fontSize: '13px', color: '#595959', marginBottom: '4px' }}>
        Embedding Model
      </div>
      <div style={{ 
        fontSize: '14px', 
        color: '#262626', 
        marginBottom: '12px'
      }}>
        {stats?.embedding_model ?? '-'}
      </div>
      <div style={{ fontSize: '13px', color: '#595959', marginBottom: '4px' }}>
        Vector Database
      </div>
      <div style={{ 
        fontSize: '14px', 
        color: '#262626'
      }}>
        {stats?.collection_name ?? '-'}
      </div>
    </Card>
  );
});
