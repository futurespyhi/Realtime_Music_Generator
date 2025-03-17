import axios from 'axios';

const API_BASE_URL = 'http://your-backend-url';

export const uploadAudio = async (audioFile: File) => {
  const formData = new FormData();
  formData.append('file', audioFile);
  const response = await axios.post(`${API_BASE_URL}/upload-audio`, formData);
  return response.data;
};

export const generateLyrics = async (text: string, musicType: string) => {
  const response = await axios.post(`${API_BASE_URL}/generate-lyrics`, { text, musicType });
  return response.data;
};

export const generateMusic = async (lyrics: string) => {
  const response = await axios.post(`${API_BASE_URL}/generate-music`, { lyrics });
  return response.data;
};