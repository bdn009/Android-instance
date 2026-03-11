import { useState } from 'react';
import { Play, Square, Trash2, MoreVertical, Smartphone } from 'lucide-react';
import useInstanceStore from '../services/instanceStore';
import LiveStream from './LiveStream';
import toast from 'react-hot-toast';

const STATUS_CONFIG = {
    running: {
        class: 'status-running',
        dot: 'bg-green-400',
        label: 'Running',
    },
    starting: {
        class: 'status-starting',
        dot: 'bg-yellow-400 animate-pulse',
        label: 'Starting...',
    },
    stopping: {
        class: 'status-starting',
        dot: 'bg-yellow-400 animate-pulse',
        label: 'Stopping...',
    },
    stopped: {
        class: 'status-stopped',
        dot: 'bg-surface-400',
        label: 'Stopped',
    },
    error: {
        class: 'status-error',
        dot: 'bg-red-400',
        label: 'Error',
    },
};

export default function InstanceCard({ instance }) {
    const { startInstance, stopInstance, deleteInstance } = useInstanceStore();
    const [actionLoading, setActionLoading] = useState(false);
    const [showMenu, setShowMenu] = useState(false);

    const status = STATUS_CONFIG[instance.status] || STATUS_CONFIG.stopped;
    const isRunning = instance.status === 'running';
    const isBusy = instance.status === 'starting' || instance.status === 'stopping';

    const handleStart = async () => {
        setActionLoading(true);
        try {
            await startInstance(instance.id);
            toast.success(`${instance.name} is starting...`);
        } catch (err) {
            toast.error(err.message);
        }
        setActionLoading(false);
    };

    const handleStop = async () => {
        setActionLoading(true);
        try {
            await stopInstance(instance.id);
            toast.success(`${instance.name} stopped`);
        } catch (err) {
            toast.error(err.message);
        }
        setActionLoading(false);
    };

    const handleDelete = async () => {
        if (!confirm(`Delete instance "${instance.name}"? This cannot be undone.`)) return;
        try {
            await deleteInstance(instance.id);
            toast.success(`${instance.name} deleted`);
        } catch (err) {
            toast.error(err.message);
        }
        setShowMenu(false);
    };

    return (
        <div className="glass rounded-2xl overflow-hidden card-glow group">
            {/* Header */}
            <div className="px-5 py-4 flex items-center justify-between border-b border-surface-700/30">
                <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${isRunning ? 'bg-primary-500/20' : 'bg-surface-700/50'
                        }`}>
                        <Smartphone className={`w-4 h-4 ${isRunning ? 'text-primary-400' : 'text-surface-400'}`} />
                    </div>
                    <div>
                        <h3 className="font-semibold text-white text-sm">{instance.name}</h3>
                        <p className="text-[11px] text-surface-500 font-mono">
                            ADB:{instance.adb_port} • Stream:{instance.stream_port}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <div className={status.class}>
                        <span className={`w-1.5 h-1.5 rounded-full ${status.dot}`} />
                        {status.label}
                    </div>

                    {/* Menu */}
                    <div className="relative">
                        <button
                            onClick={() => setShowMenu(!showMenu)}
                            className="p-1.5 rounded-lg text-surface-400 hover:text-white hover:bg-surface-700/50 transition-all"
                        >
                            <MoreVertical className="w-4 h-4" />
                        </button>
                        {showMenu && (
                            <>
                                <div className="fixed inset-0 z-10" onClick={() => setShowMenu(false)} />
                                <div className="absolute right-0 top-full mt-1 w-40 rounded-xl glass-light border border-surface-600/30 py-1 z-20 shadow-xl">
                                    <button
                                        onClick={handleDelete}
                                        className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
                                    >
                                        <Trash2 className="w-3.5 h-3.5" />
                                        Delete Instance
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* Live Stream Area */}
            <div className="px-5 py-4">
                <LiveStream instanceId={instance.id} isRunning={isRunning} />
            </div>

            {/* Actions */}
            <div className="px-5 py-4 border-t border-surface-700/30">
                {isRunning ? (
                    <button
                        onClick={handleStop}
                        disabled={actionLoading || isBusy}
                        className="btn-danger w-full flex items-center justify-center gap-2 text-sm disabled:opacity-50"
                    >
                        <Square className="w-3.5 h-3.5" />
                        Stop Instance
                    </button>
                ) : (
                    <button
                        onClick={handleStart}
                        disabled={actionLoading || isBusy}
                        className="btn-primary w-full flex items-center justify-center gap-2 text-sm disabled:opacity-50"
                    >
                        <Play className="w-3.5 h-3.5" />
                        {isBusy ? 'Please wait...' : 'Start Instance'}
                    </button>
                )}
            </div>
        </div>
    );
}
