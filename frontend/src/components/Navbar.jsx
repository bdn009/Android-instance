import { useNavigate } from 'react-router-dom';
import { LogOut, Cpu, User } from 'lucide-react';
import useAuthStore from '../services/authStore';

export default function Navbar() {
    const { user, logout } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="sticky top-0 z-50 glass border-b border-surface-700/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    {/* Logo */}
                    <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center shadow-glow">
                            <Cpu className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-lg font-bold gradient-primary-text">CloudRoid</h1>
                            <p className="text-[10px] text-surface-400 -mt-0.5 tracking-wider uppercase">Instance Manager</p>
                        </div>
                    </div>

                    {/* User Area */}
                    <div className="flex items-center gap-4">
                        {user && (
                            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-800/50 border border-surface-700/30">
                                <User className="w-3.5 h-3.5 text-primary-400" />
                                <span className="text-sm text-surface-300">{user.email}</span>
                            </div>
                        )}
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-surface-400 
                         hover:text-white hover:bg-surface-800/50 transition-all duration-300"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="hidden sm:inline">Logout</span>
                        </button>
                    </div>
                </div>
            </div>
        </nav>
    );
}
