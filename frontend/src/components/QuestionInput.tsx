/**
 * Question Input component - allows users to ask questions.
 * 
 * Best practices applied:
 * - Uses SWR Mutation for POST requests (client-swr-dedup)
 * - React.memo to prevent unnecessary re-renders
 * - Direct imports from antd submodules (bundle-barrel-imports)
 * - useCallback for stable function references (rerender-dependencies)
 * - Functional setState for stable callbacks (rerender-functional-setstate)
 * - Event handler contains interaction logic (rerender-move-effect-to-event)
 */

import { memo, useCallback, useState } from 'react';
import Card from 'antd/es/card';
import Button from 'antd/es/button';
import Form from 'antd/es/form';
import Input from 'antd/es/input';
import message from 'antd/es/message';
import { useAskQuestion } from '../hooks/useApi';

// Memoized component for performance
export const QuestionInput = memo(function QuestionInput() {
  const [question, setQuestion] = useState('');
  const { trigger: askQuestion, isMutating: isLoading } = useAskQuestion();

  // Stable callback with functional setState
  const handleClear = useCallback(() => {
    setQuestion('');
  }, []);

  // Interaction logic in event handler, not in effect
  const handleSubmit = useCallback(async (values: { question: string }) => {
    try {
      const result = await askQuestion(values.question);

      // Dispatch custom event with answer
      window.dispatchEvent(
        new CustomEvent('answerReceived', {
          detail: {
            question: result.question,
            answer: result.answer,
            sources: result.sources,
          },
        })
      );

      message.success('Answer generated successfully!');
      setQuestion('');
    } catch (error) {
      console.error('Failed to submit question:', error);
      message.error('Failed to get answer. Please try again.');
    }
  }, [askQuestion]);

  return (
    <Card
      title={
        <span style={{ fontSize: '15px', fontWeight: 600, color: '#262626' }}>
          Ask a Question
        </span>
      }
      extra={
        <Button
          type="text"
          onClick={handleClear}
          disabled={isLoading}
          style={{ color: '#dc143c' }}
        >
          Clear
        </Button>
      }
      style={{ 
        background: '#ffffff',
        border: '1px solid #e8e8e8'
      }}
      bodyStyle={{ padding: '20px' }}
    >
      <Form
        layout="vertical"
        onFinish={handleSubmit}
        disabled={isLoading}
      >
        <Form.Item
          name="question"
          rules={[
            { required: true, message: 'Please enter your question' },
            { min: 1, message: 'Question must be at least 1 character' },
            { max: 2000, message: 'Question must not exceed 2000 characters' },
          ]}
        >
          <Input.TextArea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., When does the college accept new students?"
            autoSize={{ minRows: 4, maxRows: 8 }}
            disabled={isLoading}
            style={{ fontSize: '14px' }}
          />
        </Form.Item>
        <Form.Item style={{ marginBottom: 0 }}>
          <Button
            type="primary"
            htmlType="submit"
            loading={isLoading}
            block
            style={{ 
              height: '40px',
              fontSize: '14px',
              fontWeight: 500
            }}
          >
            Submit
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
});
