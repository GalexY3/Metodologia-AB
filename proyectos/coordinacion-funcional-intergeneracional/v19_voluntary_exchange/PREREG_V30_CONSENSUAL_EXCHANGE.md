# V30 — Contratos de intercambio bilateral voluntario con cuatro especialidades

**Preregistro 12/11/2026, antes de V30.** Esta variante compara instituciones de cumplimiento recíproco frente a donaciones unilaterales costosas. V25–V26 no lograron reciprocidad estable con cuatro profesiones, incluso con tres unidades posibles por trabajador y memoria prolongada. Este contraste **modifica explícitamente la estructura del juego**: que la cooperación sea posible bajo contratos no demostraría que los individuos aprendan a donar altruistamente.

## Mecanismo contrafactual

Cada persona continúa eligiendo privadamente hasta tres propuestas dirigidas por ronda mediante su propia red neuronal, que decide destinatario y si ofrece una unidad en cada oportunidad. La decisión no se enseña, no se imita ni se recompensa colectivamente. Un contrato bilateral entre i y j se ejecuta **únicamente si ambos agentes han enviado voluntariamente al menos una propuesta al otro en esa misma ronda**. Si solo uno ofrece, no hay entrega ni coste. Si ambos ofrecen, cada uno produce exactamente un regalo para el otro y cada uno paga el mismo coste unitario c. Tres propuestas al mismo vecino no multiplican el contrato; la capacidad física máxima sigue siendo tres unidades por persona y ronda.

La liquidación de un contrato recíproco es una **regla institucional impuesta exógenamente**, nunca un comportamiento emergente. Lo que pueden aprender espontáneamente los agentes son sus decisiones voluntarias de proponer, aceptar implícitamente al proponer recíprocamente, elegir socios y cambiar de profesión. No concluir que la institución nació sola; estudiar cómo cambia las condiciones de viabilidad del sistema.

## Tratamientos y comparabilidad

Dos semillas 3111 y 4111 para el brazo contractual y las mismas para un brazo unilateral control, con precio unitario final c=0,04, N48, k4, grado6 anillo. Se preserva el actor de donaciones V25 de nueve características, política privada de ocupaciones V24 categórica, gamma=.995, horizonte48, lote12, escala20, hidden20, coste de cambio0,015 y función de beneficio material 0,20+0,55×cobertura+0,25×plenitud. Ambas redes comienzan desde pesos aleatorios. El comparador unilateral V25 histórico no está emparejado exactamente en número de actualizaciones, por lo que se añaden dos entrenamientos nuevos de control con la misma duración. Cuatro entrenamientos en total.

Entrenamiento de 700 actualizaciones. Precio inicial 0,002 hasta la actualización300, subida hasta 0,04 durante las siguientes200, precio final hasta 700. Evaluación a precio final y checkpoints de 1,140,280,420,560,700. Se mezclan mundos monolíticos y aleatorios durante aprendizaje, sin cuotas profesionales.

## Evaluación y falsadores

En nuevas semillas de mundo, evaluar medios de alimento, nº de contratos aceptados, nº de propuestas no aceptadas, cobertura material de profesiones, distribución de oficios, sensibilidad a red reconectada, movilidad aleatoria y bloqueo de propuestas. Auditar todas las personas con una intervención emparejada en la que se fuerza el primer slot a proponer frente a no proponer, dejando los otros slots y rondas estocásticos. A diferencia del brazo unilateral, el efecto inmediato de proponer depende de si la otra parte también propuso. Separar cuidadosamente efecto inmediato, diferido y total.

Hipótesis V30a: contratos incrementan el alimento medio y las contribuciones efectivamente liquidadas bajo c=0,04 frente al brazo unilateral con arquitectura idéntica. Hipótesis V30b: el acto de proponer muestra retorno individual medio positivo para una fracción considerable de personas cuando el resto ha aprendido a aceptar ofertas complementarias. Hipótesis V30c: la movilidad ocupacional aprendida desde inicios monolíticos supera la movilidad aleatoria y evita mantener especialidades inicialmente homogéneas.

Los controles son una comparación de instituciones **no equivalente** a la emergencia de donaciones unilaterales. Un éxito k4/N48 tampoco basta para el objetivo general: confirmar en k4/N120, nuevas semillas, topologías y reemplazos de agentes, y distinguir la ventaja institucional de las políticas privadas aprendidas.
