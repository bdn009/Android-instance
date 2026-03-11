import { create } from 'zustand';
import api from './api';

const useInstanceStore = create((set, get) => ({
    instances: [],
    loading: false,
    error: null,
    wsConnection: null,

    fetchInstances: async () => {
        set({ loading: true, error: null });
        try {
            const { data } = await api.get('/instances');
            set({ instances: data.instances, loading: false });
        } catch (err) {
            set({ loading: false, error: err.response?.data?.detail || 'Failed to fetch instances' });
        }
    },

    createInstance: async (name) => {
        try {
            const { data } = await api.post('/instances/create', { name });
            set((state) => ({ instances: [...state.instances, data] }));
            return data;
        } catch (err) {
            throw new Error(err.response?.data?.detail || 'Failed to create instance');
        }
    },

    startInstance: async (id) => {
        try {
            const { data } = await api.post(`/instances/${id}/start`);
            set((state) => ({
                instances: state.instances.map((i) => (i.id === id ? data : i)),
            }));
            return data;
        } catch (err) {
            throw new Error(err.response?.data?.detail || 'Failed to start instance');
        }
    },

    stopInstance: async (id) => {
        try {
            const { data } = await api.post(`/instances/${id}/stop`);
            set((state) => ({
                instances: state.instances.map((i) => (i.id === id ? data : i)),
            }));
            return data;
        } catch (err) {
            throw new Error(err.response?.data?.detail || 'Failed to stop instance');
        }
    },

    deleteInstance: async (id) => {
        try {
            await api.delete(`/instances/${id}`);
            set((state) => ({
                instances: state.instances.filter((i) => i.id !== id),
            }));
        } catch (err) {
            throw new Error(err.response?.data?.detail || 'Failed to delete instance');
        }
    },

    connectWebSocket: () => {
        const token = localStorage.getItem('cloudroid_token');
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/updates?token=${token}`;

        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'status_update' && data.instances) {
                    set((state) => {
                        const updated = state.instances.map((inst) => {
                            const upd = data.instances.find((u) => u.id === inst.id);
                            return upd ? { ...inst, status: upd.status } : inst;
                        });
                        return { instances: updated };
                    });
                }
            } catch (e) {
                console.error('WebSocket message parse error:', e);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket closed, reconnecting in 5s...');
            setTimeout(() => get().connectWebSocket(), 5000);
        };

        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
        };

        set({ wsConnection: ws });
    },

    disconnectWebSocket: () => {
        const ws = get().wsConnection;
        if (ws) {
            ws.close();
            set({ wsConnection: null });
        }
    },
}));

export default useInstanceStore;
