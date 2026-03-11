import { useEffect, useRef, useState } from 'react';
import { Smartphone, Monitor } from 'lucide-react';

export default function LiveStream({ instanceId, isRunning }) {
    const canvasRef = useRef(null);
    const wsRef = useRef(null);
    const [connected, setConnected] = useState(false);

    useEffect(() => {
        if (!isRunning || !instanceId) return;

        const token = localStorage.getItem('cloudroid_token');
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/stream/${instanceId}?token=${token}`;

        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => setConnected(true);
        ws.onclose = () => setConnected(false);

        ws.onmessage = async (event) => {
            const canvas = canvasRef.current;
            if (!canvas) return;

            if (event.data instanceof Blob) {
                // Binary frame — render as image on canvas
                const bitmap = await createImageBitmap(event.data);
                const ctx = canvas.getContext('2d');
                canvas.width = bitmap.width;
                canvas.height = bitmap.height;
                ctx.drawImage(bitmap, 0, 0);
                bitmap.close();
            }
        };

        return () => {
            ws.close();
            setConnected(false);
        };
    }, [instanceId, isRunning]);

    const sendTouch = (e) => {
        const canvas = canvasRef.current;
        const ws = wsRef.current;
        if (!canvas || !ws || ws.readyState !== WebSocket.OPEN) return;

        const rect = canvas.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * (canvas.width || 1080);
        const y = ((e.clientY - rect.top) / rect.height) * (canvas.height || 1920);

        ws.send(JSON.stringify({ x, y, action: 'tap' }));
    };

    if (!isRunning) {
        return (
            <div className="device-frame aspect-[9/16] max-h-[450px] mx-auto flex flex-col items-center justify-center gap-3">
                <Smartphone className="w-10 h-10 text-surface-600" />
                <p className="text-xs text-surface-500 font-medium">Instance Offline</p>
            </div>
        );
    }

    return (
        <div className="device-frame aspect-[9/16] max-h-[450px] h-[55vh] relative group mx-auto">
            <canvas
                ref={canvasRef}
                onClick={sendTouch}
                className="w-full h-full object-contain cursor-pointer bg-black"
            />

            {/* Connection indicator */}
            <div className="absolute top-2 right-2 flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-black/60 backdrop-blur-sm">
                <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-400 animate-pulse' : 'bg-surface-500'}`} />
                <span className="text-[10px] text-surface-300">{connected ? 'LIVE' : 'CONNECTING'}</span>
            </div>

            {/* Placeholder overlay when no frames yet */}
            {!connected && (
                <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80">
                    <Monitor className="w-8 h-8 text-primary-400 animate-pulse mb-2" />
                    <p className="text-xs text-surface-400">Connecting to stream...</p>
                </div>
            )}

            {/* Touch ripple effect hint */}
            <div className="absolute bottom-2 left-1/2 -translate-x-1/2 px-2 py-0.5 rounded-full bg-black/50 
                      opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-surface-400">
                Click to interact
            </div>
        </div>
    );
}
