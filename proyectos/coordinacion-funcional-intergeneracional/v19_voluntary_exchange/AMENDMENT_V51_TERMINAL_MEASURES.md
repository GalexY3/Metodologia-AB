# V51 — Enmienda de medición terminal y reproducibilidad

Fecha 13/11/2026, posterior al inicio de los ocho entrenamientos V51 y **anterior a sus auditorías finales fuera de muestra**. Los ocho entrenadores en ejecución siguen utilizando la versión original del código, fijada en el commit `43421942b36cc7e992de6ef0d2bacd508a10aacb`, y no se reiniciaron.

El preregistro V51 utiliza «al final del episodio» para el balance profesional. La primera versión de la función `scenario` devolvía **únicamente la media de equipos equilibrados a lo largo de48 rondas**. Esa medida temporal y la medida de **equilibrio al terminar la ronda48** no son idénticas. Para evitar interpretar indebidamente el indicador temporal como terminal, se añaden a la salida del evaluador congelado `terminal_balanced_teams`, `terminal_full` y `terminal_food`, conservando sin cambios las métricas y recompensas originales. Los falsadores H51a y H51d se evaluarán mediante `terminal_balanced_teams` y H51a/H51b mediante alimentación media del episodio declarada en el diseño.

Esto supone una **especificación del estimando antes de observar la muestra final**, no una sustitución de los umbrales ni de los checkpoints u1500. Se conservarán también las medias temporales y se explicará si dan conclusiones diferentes.

Las modificaciones de código son exclusivamente instrumentales y no alteran ni redes, ni pesos, ni algoritmos de optimización, ni recompensas, ni horarios de cambio de profesión. Los hashes de código de entrenamiento original y de auditoría se informarán por separado. Todas las políticas profesionales se evaluarán con seis semillas ambientales reservadas997101/107/109/121/131/137,24 mundos por semilla; las de rol reubicado se cotejarán contra el modelo original para la misma semilla.
