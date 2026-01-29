import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import storyService from '../../services/storyService';

// 1. 内容理解与分镜生成
export const analyzeStory = createAsyncThunk(
  'story/analyze',
  async (storyText, { rejectWithValue }) => {
    try {
      const data = await storyService.analyzeStory(storyText);
      return data.scenes;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '分析故事失败');
    }
  }
);

// 2. 保存分镜脚本
export const saveStoryboards = createAsyncThunk(
  'story/save',
  async ({ projectId, scenes }, { rejectWithValue }) => {
    try {
      const data = await storyService.saveStoryboards(projectId, scenes);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '保存分镜失败');
    }
  }
);

// 3. 批量生成图片
export const generateAllImages = createAsyncThunk(
  'story/generateAll',
  async (projectId, { rejectWithValue }) => {
    try {
      const data = await storyService.generateAllImages(projectId);
      return data.images;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '批量生成失败');
    }
  }
);

// 获取分镜列表
export const fetchStoryboards = createAsyncThunk(
  'story/fetchAll',
  async (projectId, { rejectWithValue }) => {
    try {
      const data = await storyService.fetchStoryboards(projectId);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '获取分镜失败');
    }
  }
);

const initialState = {
  scenes: [], // 当前的分镜列表
  analyzing: false,
  generating: false,
  error: null,
  activeStep: 0, // 0: 输入故事, 1: 编辑分镜, 2: 生成结果
};

const storySlice = createSlice({
  name: 'story',
  initialState,
  reducers: {
    updateScene: (state, action) => {
      const { index, field, value } = action.payload;
      state.scenes[index][field] = value;
    },
    setActiveStep: (state, action) => {
      state.activeStep = action.payload;
    },
    resetStory: (state) => {
      return initialState;
    }
  },
  extraReducers: (builder) => {
    builder
      // Analyze
      .addCase(analyzeStory.pending, (state) => {
        state.analyzing = true;
        state.error = null;
      })
      .addCase(analyzeStory.fulfilled, (state, action) => {
        state.analyzing = false;
        state.scenes = action.payload;
        state.activeStep = 1; // 自动跳到分镜编辑
      })
      .addCase(analyzeStory.rejected, (state, action) => {
        state.analyzing = false;
        state.error = action.payload;
      })
      
      // Save
      .addCase(saveStoryboards.fulfilled, (state, action) => {
        // 保存成功后不一定跳转，用户可能还在编辑
      })
      
      // Fetch
      .addCase(fetchStoryboards.fulfilled, (state, action) => {
        state.scenes = action.payload;
        if (state.scenes.length > 0) {
            // 如果已有生成好的图片，可能直接跳到最后
            const hasImages = state.scenes.some(s => s.image_url);
            state.activeStep = hasImages ? 2 : 1;
        }
      })
      
      // Generate All
      .addCase(generateAllImages.pending, (state) => {
        state.generating = true;
      })
      .addCase(generateAllImages.fulfilled, (state, action) => {
        state.generating = false;
        state.activeStep = 2;
        // 更新 scenes 中的 image_url
        // 后端返回的是 comic_images 列表，我们需要匹配回 scenes
        // 简单起见，这里重新 fetch 或者假设后端返回顺序一致
        // 实际上后端生成完应该刷新整个 scenes
      })
      .addCase(generateAllImages.rejected, (state, action) => {
        state.generating = false;
        state.error = action.payload;
      });
  },
});

export const { updateScene, setActiveStep, resetStory } = storySlice.actions;

export const selectStoryScenes = (state) => state.story.scenes;
export const selectStoryStatus = (state) => ({
  analyzing: state.story.analyzing,
  generating: state.story.generating,
  error: state.story.error,
  activeStep: state.story.activeStep
});

export default storySlice.reducer;
