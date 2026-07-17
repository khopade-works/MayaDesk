import { create } from "zustand";

type Theme = "light" | "dark";

interface UiState {
  theme: Theme;
  isSidebarOpen: boolean;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
  toggleSidebar: () => void;
}

/**
 * Minimal Zustand store for global UI state (theme, sidebar). Persistence
 * and system-theme detection will be added when the dashboard shell is
 * built out.
 */
export const useUiStore = create<UiState>((set) => ({
  theme: "light",
  isSidebarOpen: true,
  setTheme: (theme) => set({ theme }),
  toggleTheme: () =>
    set((state) => ({ theme: state.theme === "light" ? "dark" : "light" })),
  toggleSidebar: () =>
    set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
}));
