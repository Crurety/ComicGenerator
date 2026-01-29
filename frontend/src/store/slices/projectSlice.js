import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import projectService from '../../services/projectService';

// 异步操作
export const fetchProjects = createAsyncThunk(
  'project/fetchProjects',
  async (_, { rejectWithValue }) => {
    try {
      const response = await projectService.getProjects();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '获取项目失败');
    }
  }
);

export const createProject = createAsyncThunk(
  'project/createProject',
  async (projectData, { rejectWithValue }) => {
    try {
      const response = await projectService.createProject(projectData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '创建项目失败');
    }
  }
);

export const fetchProject = createAsyncThunk(
  'project/fetchProject',
  async (projectId, { rejectWithValue }) => {
    try {
      const response = await projectService.getProject(projectId);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '获取项目详情失败');
    }
  }
);

export const updateProject = createAsyncThunk(
  'project/updateProject',
  async ({ id, ...projectData }, { rejectWithValue }) => {
    try {
      const response = await projectService.updateProject(id, projectData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '更新项目失败');
    }
  }
);

export const deleteProject = createAsyncThunk(
  'project/deleteProject',
  async (projectId, { rejectWithValue }) => {
    try {
      await projectService.deleteProject(projectId);
      return projectId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '删除项目失败');
    }
  }
);

const initialState = {
  projects: [],
  currentProject: null,
  loading: false,
  error: null,
};

const projectSlice = createSlice({
  name: 'project',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentProject: (state) => {
      state.currentProject = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取项目列表
      .addCase(fetchProjects.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.loading = false;
        state.projects = action.payload;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // 创建项目
      .addCase(createProject.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.loading = false;
        state.projects.push(action.payload);
      })
      .addCase(createProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // 获取单个项目
      .addCase(fetchProject.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProject.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProject = action.payload;
      })
      .addCase(fetchProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // 更新项目
      .addCase(updateProject.fulfilled, (state, action) => {
        const index = state.projects.findIndex(p => p.id === action.payload.id);
        if (index !== -1) {
          state.projects[index] = action.payload;
        }
        if (state.currentProject?.id === action.payload.id) {
          state.currentProject = action.payload;
        }
      })
      .addCase(updateProject.rejected, (state, action) => {
        state.error = action.payload;
      })
      // 删除项目
      .addCase(deleteProject.fulfilled, (state, action) => {
        state.projects = state.projects.filter(p => p.id !== action.payload);
        if (state.currentProject?.id === action.payload) {
          state.currentProject = null;
        }
      })
      .addCase(deleteProject.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const { clearError, clearCurrentProject } = projectSlice.actions;
export const selectProjects = (state) => state.project.projects;
export const selectCurrentProject = (state) => state.project.currentProject;
export const selectProjectLoading = (state) => state.project.loading;
export const selectProjectError = (state) => state.project.error;

export default projectSlice.reducer;