import React from 'react';

interface LyricsDisplayProps {
  lyrics: string;
}

const LyricsDisplay: React.FC<LyricsDisplayProps> = ({ lyrics }) => {
  return (
    <div>
      <h3>Generated Lyrics:</h3>
      <p>{lyrics}</p>
    </div>
  );
};

export default LyricsDisplay;