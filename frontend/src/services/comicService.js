import apiClient from '../utils/apiClient';

const comicService = {
  getProjectComics: async (projectId) => {
    const response = await apiClient.get(`/comics/project/${projectId}`);
    return response.data;
  },

  getComicImage: async (imageId) => {
    const response = await apiClient.get(`/comics/${imageId}`);
    return response.data;
  },

  createComicImage: async (comicData) => {
    const response = await apiClient.post('/comics', comicData);
    return response.data;
  },

  updateComicImage: async (imageId, comicData) => {
    const response = await apiClient.put(`/comics/${imageId}`, comicData);
    return response.data;
  },

  deleteComicImage: async (imageId) => {
    await apiClient.delete(`/comics/${imageId}`);
  },

  reorderComicImages: async (projectId, imageOrders) => {
    const response = await apiClient.post('/comics/reorder', {
      project_id: projectId,
      image_orders: imageOrders
    });
    return response.data;
  },

  generateImage: async (comicData) => {
    const response = await apiClient.post('/comics/generate', comicData);
    return response.data;
  },

  checkGenerationStatus: async (taskId) => {
    const response = await apiClient.get(`/comics/status/${taskId}`);
    return response.data;
  },
};

export default comicService;
