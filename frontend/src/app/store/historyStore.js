// src/store/historyStore.js
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useHistoryStore = create(
  persist(
    (set) => ({
      data: [],
      setData: (newData) => set({ data: newData }),
    }),
    {
      name: 'seo-keyword-history', // clave en localStorage
    }
  )
);
