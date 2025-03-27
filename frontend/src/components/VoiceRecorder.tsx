import React, { useState } from 'react';

const VoiceRecorder: React.FC = () => {
  const [isRecording, setIsRecording] = useState<boolean>(false);

  const startRecording = () => {
    setIsRecording(true);
    // Call recording API
  };

  const stopRecording = () => {
    setIsRecording(false);
    // Stop recording and upload
  };

  return (
    <div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
    </div>
  );
};

export default VoiceRecorder;