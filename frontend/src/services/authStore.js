import { create } from 'zustand';
import api from './api';

const useAuthStore = create((set, get) => ({
    user: null,
    token: localStorage.getItem('cloudroid_token') || null,
    isAuthenticated: !!localStorage.getItem('cloudroid_token'),
    loading: false,
    error: null,

    register: async (email, password) => {
        set({ loading: true, error: null });
        try {
            await api.post('/auth/register', { email, password });
            // Auto-login after registration
            return await get().login(email, password);
        } catch (err) {
            const msg = err.response?.data?.detail || 'Registration failed';
            set({ loading: false, error: msg });
            throw new Error(msg);
        }
    },

    login: async (email, password) => {
        set({ loading: true, error: null });
        try {
            const { data } = await api.post('/auth/login', { email, password });
            localStorage.setItem('cloudroid_token', data.access_token);
            set({ token: data.access_token, isAuthenticated: true, loading: false });

            // Fetch user info
            const userRes = await api.get('/auth/me');
            set({ user: userRes.data });
            return data;
        } catch (err) {
            const msg = err.response?.data?.detail || 'Login failed';
            set({ loading: false, error: msg });
            throw new Error(msg);
        }
    },

    logout: () => {
        localStorage.removeItem('cloudroid_token');
        set({ user: null, token: null, isAuthenticated: false });
    },

    fetchUser: async () => {
        try {
            const { data } = await api.get('/auth/me');
            set({ user: data, isAuthenticated: true });
        } catch {
            set({ user: null, isAuthenticated: false });
            localStorage.removeItem('cloudroid_token');
        }
    },

    clearError: () => set({ error: null }),
}));

export default useAuthStore;
