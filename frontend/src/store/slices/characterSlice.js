import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import characterService from '../../services/characterService';

// 异步操作
export const fetchCharacters = createAsyncThunk(
  'character/fetchCharacters',
  async (_, { rejectWithValue }) => {
    try {
      const response = await characterService.getCharacters();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '获取角色模板失败');
    }
  }
);

export const createCharacter = createAsyncThunk(
  'character/createCharacter',
  async (characterData, { rejectWithValue }) => {
    try {
      const response = await characterService.createCharacter(characterData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '创建角色模板失败');
    }
  }
);

export const updateCharacter = createAsyncThunk(
  'character/updateCharacter',
  async ({ id, ...characterData }, { rejectWithValue }) => {
    try {
      const response = await characterService.updateCharacter(id, characterData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '更新角色模板失败');
    }
  }
);

export const deleteCharacter = createAsyncThunk(
  'character/deleteCharacter',
  async (characterId, { rejectWithValue }) => {
    try {
      await characterService.deleteCharacter(characterId);
      return characterId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.error || '删除角色模板失败');
    }
  }
);

const initialState = {
  characters: [],
  selectedCharacter: null,
  loading: false,
  error: null,
};

const characterSlice = createSlice({
  name: 'character',
  initialState,
  reducers: {
    setSelectedCharacter: (state, action) => {
      state.selectedCharacter = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // 获取角色模板列表
      .addCase(fetchCharacters.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCharacters.fulfilled, (state, action) => {
        state.loading = false;
        state.characters = action.payload;
      })
      .addCase(fetchCharacters.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // 创建角色模板
      .addCase(createCharacter.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createCharacter.fulfilled, (state, action) => {
        state.loading = false;
        state.characters.push(action.payload);
      })
      .addCase(createCharacter.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // 更新角色模板
      .addCase(updateCharacter.fulfilled, (state, action) => {
        const index = state.characters.findIndex(c => c.id === action.payload.id);
        if (index !== -1) {
          state.characters[index] = action.payload;
        }
        if (state.selectedCharacter?.id === action.payload.id) {
          state.selectedCharacter = action.payload;
        }
      })
      .addCase(updateCharacter.rejected, (state, action) => {
        state.error = action.payload;
      })
      // 删除角色模板
      .addCase(deleteCharacter.fulfilled, (state, action) => {
        state.characters = state.characters.filter(c => c.id !== action.payload);
        if (state.selectedCharacter?.id === action.payload) {
          state.selectedCharacter = null;
        }
      })
      .addCase(deleteCharacter.rejected, (state, action) => {
        state.error = action.payload;
      });
  },
});

export const { setSelectedCharacter, clearError } = characterSlice.actions;
export const selectCharacters = (state) => state.character.characters;
export const selectSelectedCharacter = (state) => state.character.selectedCharacter;
export const selectCharacterLoading = (state) => state.character.loading;
export const selectCharacterError = (state) => state.character.error;

export default characterSlice.reducer;