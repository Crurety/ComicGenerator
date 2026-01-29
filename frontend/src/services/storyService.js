import apiClient from '../utils/apiClient';

const storyService = {
  analyzeStory: async (storyText) => {
    const response = await apiClient.post('/stories/analyze', { story_text: storyText });
    return response.data;
  },

  saveStoryboards: async (projectId, scenes) => {
    const response = await apiClient.post('/stories/save', { 
      project_id: projectId,
      scenes 
    });
    return response.data;
  },

  generateAllImages: async (projectId) => {
    const response = await apiClient.post('/stories/generate_all', { project_id: projectId });
    return response.data;
  },

  fetchStoryboards: async (projectId) => {
    const response = await apiClient.get(`/stories/list/${projectId}`);
    return response.data;
  }
};

export default storyService;
