import React, { useState } from 'react';
import MusicTypeSelector from './components/MusicTypeSelector';
import VoiceRecorder from './components/VoiceRecorder';
import LyricsDisplay from './components/LyricsDisplay';
import MusicPlayer from './components/MusicPlayer';
import './App.css';

const App: React.FC = () => {
  const [lyrics, setLyrics] = useState<string>('');
  const [musicUrl, setMusicUrl] = useState<string>('');

  return (
    <div className="App">
      <h1>Hi, this is MiloMusic</h1>
      <MusicTypeSelector />
      <VoiceRecorder />
      <LyricsDisplay lyrics={lyrics} />
      <MusicPlayer musicUrl={musicUrl} />
    </div>
  );
};

export default App;