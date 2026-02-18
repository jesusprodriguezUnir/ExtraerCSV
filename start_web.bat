@echo off
REM Script para ejecutar la aplicación web de Elasticsearch
REM Uso: start_web.bat

echo.
echo ============================================================
echo   🌐 Iniciando servidor web - Extractor Elasticsearch
echo ============================================================
echo.

REM Verificar si existe .venv
if not exist ".venv" (
    echo ❌ Error: No se encuentra el entorno virtual .venv
    echo.
    echo Crear entorno virtual con:
    echo   python -m venv .venv
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar si existen los requisitos
python -m pip list | find "Flask" > nul
if errorlevel 1 (
    echo ⚙️  Instalando dependencias...
    pip install -r requirements.txt
)

REM Iniciar aplicación
echo.
REM Cargar .env si existe
if exist .env (
    echo 📥 Cargando variables desde .env
    for /f "usebackq tokens=1* delims==" %%a in (.env) do set "%%a=%%b"
)

echo 🔁 Iniciando proxy reverso local (proxy_es.py) en segundo plano...
start "proxy" /B python proxy_es.py

REM Esperar hasta 20s a que el proxy responda en /health
echo ⏳ Esperando proxy en http://127.0.0.1:%PROXY_LISTEN_PORT%/health
set COUNT=0
setlocal enabledelayedexpansion
:wait_loop
    curl -s http://127.0.0.1:%PROXY_LISTEN_PORT%/health > nul 2>&1
    if not errorlevel 1 (
        echo ✅ Proxy levantado
        goto continue_start
    )
    if %COUNT% GEQ 20 (
        echo ⚠️  Timeout esperando proxy (continuando sin proxy)
        goto continue_start
    )
    timeout /t 1 > nul
    set /a COUNT+=1
    goto wait_loop

:continue_start
echo.
echo ✅ Iniciando servidor...
echo 📂 Acceder a: http://localhost:5000
echo 🛑 Presiona Ctrl+C para detener
echo.

python app_web.py

pause
