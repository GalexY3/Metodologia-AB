# V187 — Calibración de un rival clásico de convenciones

15/11/2026. El turno V182–V186 produjo progreso verificable: código y evidencia publicados, un negativo causal y una intervención que localiza pérdida de información en el piloto comunicativo. No acreditó originalidad ni 2/3. Antes de ampliar ese piloto, necesitamos un rival privado competente.

Fuente: Spike, Stadler, Kirby y Smith (2017), *Minimal Requirements for the Emergence of Learned Signaling*, DOI10.1111/cogs.12351, secciones3.1–4.1. El enlace de código matspike/Cogscisignaling devuelve404 en GitHub y su API al consultarlo. Se construye una implementación independiente de los mecanismos descritos; no afirmar ejecución ni paridad con el código original.

## A–C. Modelo de referencia

Diez agentes, cinco significados y cinco símbolos, contexto completo. En cada interacción elegir emisor y receptor distintos uniformemente, y un significado uniforme. Cada agente dispone de una urna de asociaciones significado/símbolo, inicialmente un ejemplar de cada una de las25asociaciones. El emisor muestrea un símbolo proporcionalmente a los ejemplares de la fila del significado; el receptor muestrea su interpretación proporcionalmente a la columna del símbolo. Ambos añaden la asociación utilizada solo tras acierto. No comparten parámetros, urnas ni gradientes.

Comparar PURE, memoria sin límite, con LIMITED35, máximo35ejemplares por agente. Al añadir un ejemplar que excedería el límite, eliminar un ejemplar anterior elegido uniformemente y conservar el nuevo. Compleción operativa explícita: si una fila o columna está vacía, elegir uniformemente. No imponer correspondencias biyectivas ni eliminar todos los competidores.

## D–F. Ejecución y criterio

100semillas187001–187100,20000interacciones por semilla y condición. Cintas uniformes de siete valores por interacción compartidas entre condiciones: selección de agentes, significado, símbolo, interpretación y posibles borrados. Siempre consumir el mismo número de valores, aunque una condición no necesite borrar. Guardar estados, éxitos y precisión comunicativa exacta a100,1000,5000y20000interacciones. No seleccionar solo convergencias.

La precisión comunicativa es la esperanza sobre todos los pares ordenados de agentes distintos, los cinco significados y las políticas estocásticas actuales. No sustituirla por una racha de aciertos. La literatura presenta mayor fiabilidad de comunicación óptima con memoria limitada. Gate previo de competencia: LIMITED35 precisión>=.99 en al menos80/100semillas al final y diferencia de precisión media frente aPURE>=.05. Si falla, no llamarlo rival competente para el siguiente experimento; auditar fidelidad y conservar el fallo antes de decidir una revisión. Es calibración frente a un efecto conocido, no una contribución original.

## G–J. Validación y límites

Contrastar todas las transiciones de una implementación legible en Python con el núcleoNumba mediante cintas compartidas y prefijos1,16,64,256,1024 en tres fixtures por condición. Comprobar conservación del número de ejemplares y el límite, incluyendo urnas vacías. Registrar protocolo y hashes antes de la campaña.

No trasladar automáticamente un resultado de diez agentes simétricos a un emisor tabular y un receptor neuronal con tarea aritmética. Esa adaptación requiere otra campaña y controles de presupuesto. No es grokking ni formación de cooperación a partir de intereses opuestos. CT2 histórico61 permanece; nueva rama sin puntuación; N2=N3=0. Dos hilos CPU, prioridadBelowNormal y seisCPU; no lanzar trabajadores adicionales ni mensajería externa.
