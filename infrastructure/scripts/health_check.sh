#!/bin/bash
# ──────────────────────────────────────────────────────────
# CloudRoid — Health Check Script
# Checks the status of all services and containers
# ──────────────────────────────────────────────────────────

echo "╔══════════════════════════════════════════════════╗"
echo "║          CloudRoid Health Check                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# Check Docker containers
echo "▶ Docker Services:"
docker compose ps 2>/dev/null || docker-compose ps 2>/dev/null
echo ""

# Check Backend API
echo "▶ Backend API:"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
    echo "  ✅ Backend is healthy"
else
    echo "  ❌ Backend is unreachable"
fi
echo ""

# Check PostgreSQL
echo "▶ PostgreSQL:"
if docker exec cloudroid-postgres pg_isready -U cloudroid -d cloudroid_db > /dev/null 2>&1; then
    echo "  ✅ PostgreSQL is ready"
else
    echo "  ❌ PostgreSQL is down"
fi
echo ""

# Check Redis
echo "▶ Redis:"
if docker exec cloudroid-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo "  ✅ Redis is responding"
else
    echo "  ❌ Redis is down"
fi
echo ""

# Check Waydroid
echo "▶ Waydroid:"
if command -v waydroid &> /dev/null; then
    RUNNING=$(waydroid status 2>/dev/null | grep -c "RUNNING" || echo "0")
    echo "  ✅ Waydroid installed — $RUNNING container(s) running"
else
    echo "  ⚠️  Waydroid not installed on this host"
fi
echo ""

# System resources
echo "▶ System Resources:"
echo "  CPU:    $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')% used"
echo "  Memory: $(free -h | awk '/Mem:/ {print $3 "/" $2}')"
echo "  Disk:   $(df -h / | awk 'NR==2 {print $3 "/" $2 " (" $5 " used)"}')"
echo ""

# Check listening ports
echo "▶ Active Ports:"
echo "  3000 (Frontend):  $(ss -tlnp | grep -q ':3000' && echo '✅ Listening' || echo '❌ Not bound')"
echo "  8000 (Backend):   $(ss -tlnp | grep -q ':8000' && echo '✅ Listening' || echo '❌ Not bound')"
echo "  5432 (PostgreSQL): $(ss -tlnp | grep -q ':5432' && echo '✅ Listening' || echo '❌ Not bound')"
echo "  6379 (Redis):     $(ss -tlnp | grep -q ':6379' && echo '✅ Listening' || echo '❌ Not bound')"
