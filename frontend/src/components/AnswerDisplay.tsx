/**
 * Answer Display component - shows the AI-generated answer with sources.
 * 
 * Best practices applied:
 * - React.memo to prevent unnecessary re-renders (rerender-memo)
 * - Direct imports from antd submodules (bundle-barrel-imports)
 * - useMemo for expensive computations (sources rendering)
 * - Explicit conditional rendering with ternary (rendering-conditional-render)
 * - Early return pattern for conditional rendering
 */

import { memo, useMemo } from 'react';
import Card from 'antd/es/card';
import Divider from 'antd/es/divider';
import Tag from 'antd/es/tag';
import Typography from 'antd/es/typography';
import type { AnswerResponse } from '../api/client';

const { Paragraph, Text, Title } = Typography;

interface AnswerDisplayProps {
  answer: AnswerResponse;
  show?: boolean;
}

// Memoized component for performance
export const AnswerDisplay = memo(function AnswerDisplay({ 
  answer, 
  show = true 
}: AnswerDisplayProps) {
  // Early return for conditional rendering
  if (!show) {
    return null;
  }

  // Memoize sources rendering to prevent recalculation
  const sourcesContent = useMemo(() => {
    if (!answer.sources || answer.sources.length === 0) {
      return null;
    }

    return (
      <>
        <Divider />
        <Paragraph>
          <Text strong>📚 Sources:</Text>
        </Paragraph>
        <div style={{ marginTop: '8px' }}>
          {answer.sources.map((source, index) => (
            <Tag key={index} color="blue" style={{ margin: '4px' }}>
              {source}
            </Tag>
          ))}
        </div>
      </>
    );
  }, [answer.sources]);

  // Memoize confidence display
  const confidenceContent = useMemo(() => {
    if (!answer.confidence) {
      return null;
    }

    return (
      <Paragraph type="secondary" style={{ marginTop: '12px' }}>
        Confidence: {(answer.confidence * 100).toFixed(0)}%
      </Paragraph>
    );
  }, [answer.confidence]);

  return (
    <Card 
      title={
        <span style={{ fontSize: '15px', fontWeight: 600, color: '#262626' }}>
          Answer
        </span>
      }
      style={{ 
        background: '#ffffff',
        border: '1px solid #e8e8e8'
      }}
      bodyStyle={{ padding: '20px' }}
    >
      <div style={{ background: '#fafafa', padding: '12px 16px', borderRadius: '6px', marginBottom: '20px' }}>
        <Text style={{ fontSize: '13px', color: '#8c8c8c', marginBottom: '4px', display: 'block' }}>
          Question:
        </Text>
        <Text style={{ fontSize: '14px', color: '#262626' }}>
          {answer.question}
        </Text>
      </div>
      
      <Paragraph 
        style={{ 
          fontSize: '14px', 
          lineHeight: '1.6',
          color: '#262626',
          marginBottom: '20px'
        }}
      >
        {answer.answer}
      </Paragraph>

      {sourcesContent}
      {confidenceContent}
    </Card>
  );
});
