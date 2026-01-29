import apiClient from '../utils/apiClient';

const characterService = {
  getCharacters: async () => {
    const response = await apiClient.get('/characters');
    return response.data;
  },

  getCharacter: async (characterId) => {
    const response = await apiClient.get(`/characters/${characterId}`);
    return response.data;
  },

  createCharacter: async (characterData) => {
    const response = await apiClient.post('/characters', characterData);
    return response.data;
  },

  updateCharacter: async (characterId, characterData) => {
    const response = await apiClient.put(`/characters/${characterId}`, characterData);
    return response.data;
  },

  deleteCharacter: async (characterId) => {
    await apiClient.delete(`/characters/${characterId}`);
  },
};

export default characterService;
