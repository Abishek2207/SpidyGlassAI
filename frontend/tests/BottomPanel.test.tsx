import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BottomPanel } from '../src/components/BottomPanel';

describe('BottomPanel Component', () => {
  it('renders waiting states when no data is provided', () => {
    render(<BottomPanel />);
    expect(screen.getByText('Waiting for audio input...')).toBeInTheDocument();
    expect(screen.getByText('Perform a sign language gesture or speak to begin.')).toBeInTheDocument();
  });

  it('renders transcript and translation when provided', () => {
    render(
      <BottomPanel 
        transcript="Hello world" 
        translatedText="नमस्ते दुनिया" 
        aiReply="How can I help you?"
        pipelineStages={['speech', 'translation', 'llm']}
      />
    );
    expect(screen.getByText('Hello world')).toBeInTheDocument();
    expect(screen.getByText('नमस्ते दुनिया')).toBeInTheDocument();
    expect(screen.getByText('How can I help you?')).toBeInTheDocument();
  });
});
