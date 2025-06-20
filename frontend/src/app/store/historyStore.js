// src/store/historyStore.js
import { create } from 'zustand';

export const useHistoryStore = create((set) => ({
  data: [],
  setData: (newData) => set({ data: newData }),
}));
