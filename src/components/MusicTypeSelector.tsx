import React, { useState } from 'react';

const MusicTypeSelector: React.FC = () => {
  const [musicType, setMusicType] = useState<string>('pop');

  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setMusicType(event.target.value);
  };

  return (
    <div>
      <label htmlFor="music-type">Select Music Type:</label>
      <select id="music-type" value={musicType} onChange={handleChange}>
        <option value="pop">Pop</option>
        <option value="rock">Rock</option>
        <option value="jazz">Jazz</option>
        <option value="hip-hop">Hip-Hop</option>
      </select>
    </div>
  );
};

export default MusicTypeSelector;