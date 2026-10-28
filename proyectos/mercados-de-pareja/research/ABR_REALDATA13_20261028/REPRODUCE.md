# Reproducibilidad y datos personales · Mixmosa

**Estudio:** observacional, exploratorio. **No usar para perfilar ni calificar personas reales**. No se han republicado IDs ni filas de perfiles en este repositorio.

## Fuentes originales y control de versiones
Clonar por separado los repositorios:
```bash
git clone https://github.com/dankras/mixmosa-anonymized-data.git
git clone --branch research/ab-r-mercados-pareja-20261028 https://github.com/GalexY3/Metodologia-AB.git
```
El primero incluye datos anonimizados de interacciones, swipes, atributos y eventos. No se detectó licencia de redistribución explícita en la raíz consultada; se citan las tablas en origen y no se republican.

Huellas Git blob originales (verificar con `git hash-object`):
- `csv/interactions.csv`: `c4aba45888dc07573b6bd12554f73fb57ebb0479`
- `csv/user_features.csv`: `99679f0e33b55099a4a0705810dd9771019554d0`
- `csv/swiping.csv`: `2820b902bd4a80d57008c03aa0c4e0ff927f6639`
- `csv/events.csv`: `3d58d8335046a71daff6fddb812429240c70af67`

## Ejecutar con Node.js
Se necesita Node compatible con `Object.groupBy` (p. ej. Node 22+) y bibliotecas estándar solamente. Desde un directorio que contenga ambas carpetas, ejecutar:

```javascript
const fs = require("node:fs");
const path = require("node:path");
const base = "./Metodologia-AB/proyectos/mercados-de-pareja/research/ABR_REALDATA13_20261028";
const data = "./mixmosa-anonymized-data/csv";
const payload = {
  interactions: fs.readFileSync(path.join(data, "interactions.csv"), "utf8"),
  features: fs.readFileSync(path.join(data, "user_features.csv"), "utf8"),
  swipes: fs.readFileSync(path.join(data, "swiping.csv"), "utf8"),
  events: fs.readFileSync(path.join(data, "events.csv"), "utf8"),
};
const src = fs.readFileSync(path.join(base, "analyze_mixmosa.js"), "utf8");
const result = new Function("payload", src + "\nreturn runMixmosa(payload)")(payload);
console.log(JSON.stringify(result, null, 2));
const extra = fs.readFileSync(path.join(base, "additional_checks.js"), "utf8");
const supplemental = new Function("payload", extra + "\nreturn run(payload)")(payload);
console.log(JSON.stringify(supplemental, null, 2));
```

El código de la primera ejecución en `analyze_mixmosa.js` corrigió después de un fallo de codificación `income_bucket`. Se conservaron `INVALID_N32_INCOME_01.json`, el commit de reparación y el resultado previo `AGGREGATE_RESULTS.json`; **la versión válida es `AGGREGATE_RESULTS_REPAIRED.json`**. La prueba N32 inválida no cuenta como ciclo extra.

El código no requiere acceso a API privado y produce únicamente métricas de conjunto. **No se ha ejecutado este protocolo desde un clon limpio separado**; las ejecuciones verificadas se realizaron dentro del intérprete de herramientas con CSV recibidos por el conector GitHub.

## Límites metodológicos de reproducción
- `interactions.csv` contiene **1.895** citas completas; la cifra de **2.961** del README no equivale al subconjunto del CSV usado.
- `swiping.csv` contiene **4.437** decisiones dirigidas: 3.790 corresponden a ambas direcciones de las 1.895 citas completas, y 647 quedan fuera de ellas.
- No hay registro temporal detallado ni constancia de publicidad de un rechazo a terceros.
- Las correlaciones por atributo son descriptivas y ponderadas por cita; quienes asisten a más citas contribuyen más.
- Los controles de permutación dentro de evento y de mujer-evento son modelos de intercambio, no experimentos aleatorizados. Reutilizan respuestas dentro del mismo conjunto.
- La popularidad leave-one-dyad-out excluye solo la cita focal, no el resto del evento, de modo que persiste la selección estructural.
