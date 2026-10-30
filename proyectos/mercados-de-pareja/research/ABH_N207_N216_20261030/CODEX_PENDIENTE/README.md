# CODEX_PENDIENTE · solo tareas imposibles desde este entorno sin acceso a Windows

**No hay Codex disponible ni se presupone su disponibilidad.** Este backlog contiene exclusivamente acciones que necesitan el disco privado/entorno Windows de la persona usuaria, no acciones que solo un modelo de Codex pueda hacer. Los cambios TS, test de 12 fixtures, test de 10 grafos, typecheck Linux y SHA fueron **resueltos por ChatGPT**. Ninguna acción de esta carpeta se ha ejecutado remotamente.

## W01 · Incorporar en el git local privado

En `C:\Programación\ESBM-W-ESBM-01`, abrir PowerShell y comprobar `git status --short`, `git rev-parse HEAD`, `git branch --show-current`. El export original del usuario reclama `eabadd8f`, pero el ZIP no contenía `.git`, por lo que esa relación debe verificarse **desde el equipo**. Hacer copia de cambios locales que no estuvieran en el ZIP. Descargar el `ESBM_W_ESBM01_N207_N216_CODIGO_CORREGIDO.zip` entregado en este chat, comprobar SHA256 `4e463f200b164edd7403efc0a3e26cfc17dd2fdb1b1f67927505ae2555d74ac0` y extraer el subdirectorio `windows-replica/` en el worktree. Comparar `git diff`, no sobrescribir `esbm_dynamic.py`, SRC104, los fixtures originales ni código externo al directorio. Primer commit local sólo de código/contrato; **no hacer push ni merge**.

## W02 · Validación de tipos realmente en Windows

Se hizo `tsc --noEmit` en Linux con `@types/node 25.1.0` PREINSTALADO y symlink, pero el package no fija estas types. Comprobar Node 22.18+ o Node 24 y el compilador de TS. Instalación reproducible de typings, con licencia verificada, **solo previa revisión y permiso para instalar dependencias**. Volver a ejecutar `tsc --noEmit --project tsconfig.json` en Windows y archivar stdout/stderr y exit; no certificar clean-clone antes de hacerlo.

## W03 · Manifiesto Git oficial del código

Verificar que `tools/prepare.mjs` solo lee hashes, copia documentos y escribe metadata, **no ejecuta fixtures ni simulaciones**; tras primer commit local correr sólo preparación, `Get-FileHash -Algorithm SHA256`, y hacer segundo commit de manifests. El manifest del ZIP es **Linux review snapshot**, no una autorización real; para CLI Windows se debe fijar HEAD prospectivo y autorizaciones específicas. Registrar los dos SHAs locales sin inventar su existencia.

## W04 · 60 corridas históricas / matching N144: STOP FUTURO

**NO ejecutar ni preparar automáticamente**. Requiere nueva solicitud explícita del usuario, SHA congelados de inputs/oráculo/código y reporte por eventos; matching exacto con crecimiento exponencial y guardas de componentes que probablemente detengan algunas instancias. Si la traza Python carece de esquema comparable, conservar `SUMMARY_MATCH_ONLY_EVENT_STATE_NOT_VERIFIED`. No elevar cuotas tras outcome ni sustituir por greedy. No usar SSJY, no datos humanos, STOP_R5 intacto.

**No hay tareas cuyo ejecutor deba ser Codex como producto:** puede ser el propio usuario o cualquier agente con permisos de Windows. Codex ausente no detiene los trabajos que podemos realizar aquí.
