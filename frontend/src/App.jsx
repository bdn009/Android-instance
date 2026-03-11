import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import useAuthStore from './services/authStore';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';

function ProtectedRoute({ children }) {
    const { isAuthenticated } = useAuthStore();
    return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function GuestRoute({ children }) {
    const { isAuthenticated } = useAuthStore();
    return isAuthenticated ? <Navigate to="/dashboard" replace /> : children;
}

export default function App() {
    return (
        <Router>
            <Toaster
                position="top-right"
                toastOptions={{
                    duration: 4000,
                    style: {
                        background: '#1e293b',
                        color: '#f8fafc',
                        border: '1px solid rgba(148, 163, 184, 0.15)',
                        borderRadius: '12px',
                        fontSize: '14px',
                    },
                    success: {
                        iconTheme: { primary: '#22d3ee', secondary: '#0f172a' },
                    },
                    error: {
                        iconTheme: { primary: '#f87171', secondary: '#0f172a' },
                    },
                }}
            />
            <Routes>
                <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
                <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
                <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Router>
    );
}
