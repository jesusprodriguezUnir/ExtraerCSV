#!/bin/bash
# Script para ejecutar la aplicación web de Elasticsearch
# Uso: ./start_web.sh

echo ""
echo "============================================================"
echo "   🌐 Iniciando servidor web - Extractor Elasticsearch"
echo "============================================================"
echo ""

# Verificar si existe .venv
if [ ! -d ".venv" ]; then
    echo "❌ Error: No se encuentra el entorno virtual .venv"
    echo ""
    echo "Crear entorno virtual con:"
    echo "  python3 -m venv .venv"
    echo ""
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate

# Verificar si existen los requisitos
if ! python -m pip list | grep -q Flask; then
    echo "⚙️  Instalando dependencias..."
    pip install -r requirements.txt
fi

# Cargar variables de entorno desde .env (si existe) y exportarlas
if [ -f .env ]; then
    echo "📥 Cargando variables de entorno desde .env"
    set -o allexport
    # shellcheck disable=SC1091
    source .env
    set +o allexport
fi

# Iniciar proxy reverso local (si no hay otro en el puerto)
echo "🔁 Iniciando proxy reverso local (proxy_es.py) en segundo plano..."
python proxy_es.py &
PROXY_PID=$!

# Esperar a que el proxy responda en /health (timeout 20s)
echo "⏳ Esperando proxy en http://127.0.0.1:${PROXY_LISTEN_PORT:-9200}/health"
COUNT=0
HEALTH_URL="http://127.0.0.1:${PROXY_LISTEN_PORT:-9200}/health"
until curl -s "$HEALTH_URL" | grep -q proxy_ok || [ $COUNT -ge 20 ]; do
    sleep 1
    COUNT=$((COUNT+1))
done
if [ $COUNT -ge 20 ]; then
    echo "⚠️  Timeout esperando proxy (continuando sin proxy)"
else
    echo "✅ Proxy levantado"
fi

echo ""
echo "✅ Iniciando servidor..."
echo "📂 Acceder a: http://localhost:5000"
echo "🛑 Presiona Ctrl+C para detener"
echo ""

python app_web.py

# Si la app termina, matar el proxy de fondo
kill $PROXY_PID 2>/dev/null || true
