import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import projectSlice from './slices/projectSlice';
import editorSlice from './slices/editorSlice';
import characterSlice from './slices/characterSlice';
import storySlice from './slices/storySlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    project: projectSlice,
    editor: editorSlice,
    character: characterSlice,
    story: storySlice,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['editor/addLayer'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;