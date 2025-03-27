import React from 'react';

interface MusicPlayerProps {
  musicUrl: string;
}

const MusicPlayer: React.FC<MusicPlayerProps> = ({ musicUrl }) => {
  return (
    <div>
      <h3>Generated Music:</h3>
      <audio controls src={musicUrl}>
        Your browser does not support the audio element.
      </audio>
    </div>
  );
};

export default MusicPlayer;