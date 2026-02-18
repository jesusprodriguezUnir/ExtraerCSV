╔════════════════════════════════════════════════════════════════╗
║           ✅ SOLUCIÓN CON PROXY - INSTRUCCIONES                ║
╚════════════════════════════════════════════════════════════════╝

🎯 OBJETIVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usar un proxy local que bypassea el bloqueo de Kibana
y permite acceder a Elasticsearch con las credenciales que tienes.

═════════════════════════════════════════════════════════════════

⚙️  SETUP (solo primera vez)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Preparar el archivo `.env` copiando `.env.example` y completando las variables necesarias.
  - En particular: `PROXY_TARGET_HOST`, `PROXY_TARGET_PORT`, `PROXY_USER`, `PROXY_PASSWORD`, `PROXY_LISTEN_PORT`.
2. Arrancar el proxy:
   
  Terminal: python proxy_es.py
  Escuchando en: http://127.0.0.1:9200 (o el puerto definido en `PROXY_LISTEN_PORT`)

2. Verificar que está funcionando:
   
   http://127.0.0.1:9200/health

═════════════════════════════════════════════════════════════════

🚀 USAR LA APLICACIÓN WEB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. En OTRA terminal, ejecutar la app web:
   
   python app_web.py
   
2. Acceder a:
   
   http://localhost:5000

3. En el formulario de login, ingresa:

  - Host: http://localhost:9200 (o `http://<PROXY_LISTEN_HOST>:<PROXY_LISTEN_PORT>`)
  - Usuario / Contraseña: usar las credenciales definidas en tu `.env` (`PROXY_USER` / `PROXY_PASSWORD`).
  - Patrón de índices: logs-*

4. Haz clic en "Conectar"

═════════════════════════════════════════════════════════════════

✨ ¿CÓMO FUNCIONA?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tu máquina:
  App web (5000)
      ↓
  Request HTTP
      ↓
  Proxy (9200) ← ← ← ← AQUÍ ESTÁ LA MAGIA
      ↓
  HTTPS a elk.unir.net/elktest.unir.net (443)
      ↓
  Proxy agrega credenciales automáticamente
      ↓
  Respuesta JSON ← Elasticsearch (detrás de Kibana)
      ↓
  Devuelve a app web

═════════════════════════════════════════════════════════════════

📋 COMANDOS RÁPIDOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Terminal 1 - Inicial (si no lo hiciste):
  C:/Proyectos/Temp/ExtraerCSV/.venv/Scripts/python.exe proxy_es.py

Terminal 2:
  C:/Proyectos/Temp/ExtraerCSV/.venv/Scripts/python.exe app_web.py

Terminal 3 - Para probar curl (opcional):
  curl http://localhost:9200/
  curl http://localhost:9200/_cat/indices
  curl -X GET http://localhost:9200/logs-*/_search

═════════════════════════════════════════════════════════════════

✅ VENTAJAS DE ESTA SOLUCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ No necesitas API Key
✓ Usa credenciales que ya tienes
✓ Bypassea el bloqueo de Kibana
✓ Funciona directo en localhost (sin HTTPS)
✓ Maneja autenticación automáticamente
✓ La interfaz web está lista para usar

═════════════════════════════════════════════════════════════════

⚠️  NOTAS IMPORTANTES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• El proxy solo funciona en tu máquina (localhost)
• NO es para producción (SSL, seguridad básica)
• Las credenciales NO deben estar en el repo. Guarda las credenciales en `.env` y no las subas al control de versiones.
• El proxy está pensado para uso local y desarrollo; no usar en producción sin asegurar TLS y acceso restringido.

═════════════════════════════════════════════════════════════════

🆘 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Puerto 9200 ya está en uso"
  → Cambiar puerto en proxy_es.py (línea ~47)
    PROXY_PORT = 9201

"No se puede conectar al proxy"
  → Asegúrate que proxy_es.py esté ejecutándose
  → Prueba: curl http://localhost:9200/health

"Error de autenticación"
  → Verifica que las credenciales en app_web sean:
    Host: http://localhost:9200 (NO https)
    Usuario: dev-academico
    Contraseña: oov7Bah5eimu]e3Aiphiip2L

"El proxy devuelve 502"
  → El servidor elk.unir.net no responde
  → Intenta: curl -k https://elk.unir.net/

═════════════════════════════════════════════════════════════════

🎉 ¡LISTO!

Ya puedes usar la app web sin problemas de Kibana.

Si tienes dudas, revisa los logs del proxy en la terminal.

═════════════════════════════════════════════════════════════════
