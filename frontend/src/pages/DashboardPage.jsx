import { useEffect, useState } from 'react';
import { Plus, Loader2, Cpu, Activity, HardDrive, LayoutGrid } from 'lucide-react';
import Navbar from '../components/Navbar';
import InstanceCard from '../components/InstanceCard';
import ApkUpload from '../components/ApkUpload';
import useInstanceStore from '../services/instanceStore';
import useAuthStore from '../services/authStore';
import toast from 'react-hot-toast';

export default function DashboardPage() {
    const { instances, loading, fetchInstances, createInstance, connectWebSocket, disconnectWebSocket } = useInstanceStore();
    const { fetchUser } = useAuthStore();
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showApkModal, setShowApkModal] = useState(false);
    const [newName, setNewName] = useState('');
    const [creating, setCreating] = useState(false);

    useEffect(() => {
        fetchUser();
        fetchInstances();
        connectWebSocket();
        return () => disconnectWebSocket();
    }, []);

    const handleCreate = async (e) => {
        e.preventDefault();
        if (!newName.trim()) return;

        setCreating(true);
        try {
            await createInstance(newName.trim());
            toast.success(`Instance "${newName}" created`);
            setNewName('');
            setShowCreateModal(false);
        } catch (err) {
            toast.error(err.message);
        }
        setCreating(false);
    };

    const runningCount = instances.filter((i) => i.status === 'running').length;

    return (
        <div className="min-h-screen gradient-dark">
            <Navbar />

            <main className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header Section */}
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-8">
                    <div>
                        <h2 className="text-2xl font-bold text-white">Android Instances</h2>
                        <p className="text-surface-400 text-sm mt-1">Manage your cloud-hosted Android environments</p>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={() => setShowApkModal(true)}
                            className="btn-ghost flex items-center gap-2 text-sm"
                        >
                            <HardDrive className="w-4 h-4" />
                            Upload APK
                        </button>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="btn-primary flex items-center gap-2 text-sm"
                        >
                            <Plus className="w-4 h-4" />
                            New Instance
                        </button>
                    </div>
                </div>

                {/* Stats Bar */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                    <div className="glass rounded-xl p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
                            <LayoutGrid className="w-5 h-5 text-primary-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-white">{instances.length}</p>
                            <p className="text-xs text-surface-400">Total Instances</p>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-green-500/15 flex items-center justify-center">
                            <Activity className="w-5 h-5 text-green-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-white">{runningCount}</p>
                            <p className="text-xs text-surface-400">Running Now</p>
                        </div>
                    </div>
                    <div className="glass rounded-xl p-4 flex items-center gap-4">
                        <div className="w-10 h-10 rounded-xl bg-accent-500/15 flex items-center justify-center">
                            <Cpu className="w-5 h-5 text-accent-400" />
                        </div>
                        <div>
                            <p className="text-2xl font-bold text-white">{instances.length - runningCount}</p>
                            <p className="text-xs text-surface-400">Idle</p>
                        </div>
                    </div>
                </div>

                {/* Instance Grid */}
                {loading ? (
                    <div className="flex flex-col items-center justify-center py-20 gap-4">
                        <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
                        <p className="text-surface-400 text-sm">Loading instances...</p>
                    </div>
                ) : instances.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-20 gap-4">
                        <div className="w-20 h-20 rounded-2xl bg-surface-800/50 flex items-center justify-center">
                            <Cpu className="w-10 h-10 text-surface-600" />
                        </div>
                        <div className="text-center">
                            <p className="text-lg font-semibold text-surface-300">No instances yet</p>
                            <p className="text-sm text-surface-500 mt-1">Create your first Android instance to get started</p>
                        </div>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="btn-primary flex items-center gap-2 text-sm mt-2"
                        >
                            <Plus className="w-4 h-4" />
                            Create Instance
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                        {instances.map((instance) => (
                            <InstanceCard key={instance.id} instance={instance} />
                        ))}
                    </div>
                )}
            </main>

            {/* Create Instance Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowCreateModal(false)} />
                    <div className="relative glass rounded-2xl p-6 w-full max-w-md card-glow">
                        <h3 className="text-lg font-bold text-white mb-4">Create New Instance</h3>
                        <form onSubmit={handleCreate}>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-surface-300 mb-1.5">Instance Name</label>
                                <input
                                    id="create-instance-name"
                                    type="text"
                                    value={newName}
                                    onChange={(e) => setNewName(e.target.value)}
                                    className="input-field"
                                    placeholder="e.g. My Android App"
                                    required
                                    maxLength={100}
                                    autoFocus
                                />
                            </div>
                            <div className="flex gap-3 justify-end">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="btn-ghost text-sm"
                                >
                                    Cancel
                                </button>
                                <button
                                    id="create-instance-submit"
                                    type="submit"
                                    disabled={creating || !newName.trim()}
                                    className="btn-primary text-sm flex items-center gap-2 disabled:opacity-50"
                                >
                                    {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                                    Create
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* APK Upload Modal */}
            {showApkModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowApkModal(false)} />
                    <div className="relative glass rounded-2xl p-6 w-full max-w-md card-glow">
                        <h3 className="text-lg font-bold text-white mb-4">Upload APK</h3>
                        <ApkUpload onUploaded={() => { }} />
                        <div className="mt-4 flex justify-end">
                            <button
                                onClick={() => setShowApkModal(false)}
                                className="btn-ghost text-sm"
                            >
                                Close
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
