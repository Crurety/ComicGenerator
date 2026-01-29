import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import comicService from '../../services/comicService';

// 异步操作
export const fetchProjectComics = createAsyncThunk(
  'editor/fetchProjectComics',
  async (projectId, { rejectWithValue }) => {
    try {
      const response = await comicService.getProjectComics(projectId);
      return { projectId, comics: response };
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '获取漫画图片失败');
    }
  }
);

export const createComicImage = createAsyncThunk(
  'editor/createComicImage',
  async (comicData, { rejectWithValue }) => {
    try {
      const response = await comicService.createComicImage(comicData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '创建漫画图片失败');
    }
  }
);

export const updateComicImage = createAsyncThunk(
  'editor/updateComicImage',
  async ({ id, ...comicData }, { rejectWithValue }) => {
    try {
      const response = await comicService.updateComicImage(id, comicData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '更新漫画图片失败');
    }
  }
);

export const deleteComicImage = createAsyncThunk(
  'editor/deleteComicImage',
  async (imageId, { rejectWithValue }) => {
    try {
      await comicService.deleteComicImage(imageId);
      return imageId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '删除漫画图片失败');
    }
  }
);

export const reorderComicImages = createAsyncThunk(
  'editor/reorderComicImages',
  async ({ projectId, imageOrders }, { rejectWithValue }) => {
    try {
      await comicService.reorderComicImages(projectId, imageOrders);
      return { projectId, imageOrders };
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '重排序漫画图片失败');
    }
  }
);

export const generateImage = createAsyncThunk(
  'editor/generateImage',
  async (comicData, { rejectWithValue }) => {
    try {
      const response = await comicService.generateImage(comicData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '生成图片失败');
    }
  }
);

export const checkGenerationStatus = createAsyncThunk(
  'editor/checkGenerationStatus',
  async (taskId, { rejectWithValue }) => {
    try {
      const response = await comicService.checkGenerationStatus(taskId);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '检查生成状态失败');
    }
  }
);

const initialState = {
  layers: [],
  selectedLayer: null,
  currentTool: 'select',
  zoom: 1,
  canvasSize: { width: 800, height: 600 },
  loading: false,
  generating: false,
  generationResult: null,
  error: null,
};

const editorSlice = createSlice({
  name: 'editor',
  initialState,
  reducers: {
    setSelectedLayer: (state, action) => {
      state.selectedLayer = action.payload;
    },
    setCurrentTool: (state, action) => {
      state.currentTool = action.payload;
    },
    setZoom: (state, action) => {
      state.zoom = action.payload;
    },
    setCanvasSize: (state, action) => {
      state.canvasSize = action.payload;
    },
    addLayer: (state, action) => {
      state.layers.push(action.payload);
    },
    removeLayer: (state, action) => {
      state.layers = state.layers.filter(layer => layer.id !== action.payload);
      if (state.selectedLayer?.id === action.payload) {
        state.selectedLayer = null;
      }
    },
    clearGenerationResult: (state) => {
      state.generationResult = null;
    },
    updateLayer: (state, action) => {
      const index = state.layers.findIndex(layer => layer.id === action.payload.id);
      if (index !== -1) {
        state.layers[index] = { ...state.layers[index], ...action.payload };
      }
      if (state.selectedLayer?.id === action.payload.id) {
        state.selectedLayer = { ...state.selectedLayer, ...action.payload };
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    clearLayers: (state) => {
      state.layers = [];
      state.selectedLayer = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取项目漫画图片
      .addCase(fetchProjectComics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProjectComics.fulfilled, (state, action) => {
        state.loading = false;
        state.layers = action.payload.comics;
      })
      .addCase(fetchProjectComics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // 创建漫画图片
      .addCase(createComicImage.fulfilled, (state, action) => {
        state.layers.push(action.payload);
      })
      .addCase(createComicImage.rejected, (state, action) => {
        state.error = action.payload;
      })
      // 更新漫画图片
      .addCase(updateComicImage.fulfilled, (state, action) => {
        const index = state.layers.findIndex(layer => layer.id === action.payload.id);
        if (index !== -1) {
          state.layers[index] = action.payload;
        }
        if (state.selectedLayer?.id === action.payload.id) {
          state.selectedLayer = action.payload;
        }
      })
      .addCase(updateComicImage.rejected, (state, action) => {
        state.error = action.payload;
      })
      // 删除漫画图片
      .addCase(deleteComicImage.fulfilled, (state, action) => {
        state.layers = state.layers.filter(layer => layer.id !== action.payload);
        if (state.selectedLayer?.id === action.payload) {
          state.selectedLayer = null;
        }
      })
      .addCase(deleteComicImage.rejected, (state, action) => {
        state.error = action.payload;
      })
      // 重排序漫画图片
      .addCase(reorderComicImages.fulfilled, (state, action) => {
        const { imageOrders } = action.payload;
        imageOrders.forEach(({ image_id, order }) => {
          const index = state.layers.findIndex(layer => layer.id === image_id);
          if (index !== -1) {
            state.layers[index].layer_order = order;
          }
        });
        state.layers.sort((a, b) => a.layer_order - b.layer_order);
      })
      .addCase(reorderComicImages.rejected, (state, action) => {
        state.error = action.payload;
      })
      // 生成图片
      .addCase(generateImage.pending, (state) => {
        state.generating = true;
        state.error = null;
        state.generationResult = null;
      })
      .addCase(generateImage.fulfilled, (state, action) => {
        state.generating = false;
        state.generationResult = action.payload;
      })
      .addCase(generateImage.rejected, (state, action) => {
        state.generating = false;
        state.error = action.payload;
      })
      // 检查生成状态
      .addCase(checkGenerationStatus.fulfilled, (state, action) => {
        // 如果状态完成，可以在这里处理
      });
  },
});

export const {
  setSelectedLayer,
  setCurrentTool,
  setZoom,
  setCanvasSize,
  addLayer,
  removeLayer,
  updateLayer,
  clearError,
  clearLayers,
  clearGenerationResult,
} = editorSlice.actions;

export const selectLayers = (state) => state.editor.layers;
export const selectSelectedLayer = (state) => state.editor.selectedLayer;
export const selectCurrentTool = (state) => state.editor.currentTool;
export const selectZoom = (state) => state.editor.zoom;
export const selectCanvasSize = (state) => state.editor.canvasSize;
export const selectEditorLoading = (state) => state.editor.loading;
export const selectEditorError = (state) => state.editor.error;
export const selectGenerating = (state) => state.editor.generating;
export const selectGenerationResult = (state) => state.editor.generationResult;

export default editorSlice.reducer;