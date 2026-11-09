# G0 — sustitución intergeneracional y transmisión de la regla local

**Diseño exploratorio registrado después de P0 y antes de G0.** En P0 la regla de escoger estados relativamente poco observados (minority) permitió coordinar k2..4, extrapoló parcialmente a k5..8, mientras que la política aprendida REINFORCE falló con k4 y todos los nuevos k. Por tanto, esta etapa usa la política minority como **regla social predefinida** y examina su difusión y continuidad, NO su aparición espontánea ni grokking colectivo.

## Escenario y elegibilidad

Población fija N=120, anillo con grado4, un vecino conversado por tick y k=4 o k=5. Se crean comunidades con esa regla local preprogramada; solamente si la comunidad alcanza y MANTIENE TV≤.06 y churn≤.05 en los últimos 10 ticks del periodo previo de 140 pasos, se efectúa un relevo. Se informan todos los casos previos que no cumplan, sin sustitución selectiva. Semillas base fijas = 12000+k*100+s, s=0..19, independientes de los datos de P0 y P1.

## Choque demográfico emparejado

Elegir al azar 25%,50%,75% de nodos que se reemplazarán (r=.25,.5,.75). Mismos nodos y mismos nuevos colores para TODOS los tratamientos emparejados en una semilla/r. Los colores de los nuevos miembros se muestrean independientemente bajo la misma distribución inicial desigual 70% estado0, 30% otros (señal de llegada de novatos, sin mejorar mecánicamente la distribución). El resto conserva exactamente su estado, memoria y topología; cada recién llegado reinicia memoria local a prior uniforme.

Comparar desde el **mismo vector de colores posterior al choque** tres condiciones:
- **Herencia:** los nuevos miembros reciben inmediatamente la regla minority predefinida (protocolo cultural plenamente copiado al nacer).
- **Sin enseñanza:** los nuevos miembros carecen de regla; tienden a conservar su rol (stay) y solo los veteranos pueden adaptarse.
- **Enseñanza por contacto:** comienzan como stay; cada vez que un novato habla con un veterano que conoce minority, con probabilidad preestablecida p=.25 adopta su regla para el tick SIGUIENTE, un mensaje por persona por tick. Los enseñados pueden enseñar desde entonces; no hay acceso global, ni difusor omnisciente.

Hacer **150 ticks** postrelevo, sin intervención según resultados. Contar contactos por individuo, las proporciones de portadores de la regla y el número de transmisiones. En este modelo, transmitir un bit de «saber aplicar la regla» es una asunción fuerte de alta fidelidad: es **difusión cultural programada**, no aprendizaje individual del algoritmo. Todos los tratamientos reciben el mismo choque; la condición de herencia es un benchmark.

## Resultados

Global TV inmediatamente antes y después; reducción de equilibrio; tiempo hasta 10 ticks consecutivos con TV≤.06 y churn≤.05 (o censura a 150); AUC de TV sobre 150 ticks; proporción final de portadores del protocolo; número total de conversaciones y transmisiones; riqueza local.

Agrupar primero dentro de cohorte/semilla/r, no tratar cada tick como réplica. No inferir grokking ni transferencia espontánea del procedimiento. Reportar fallo completo de recuperación si lo hay. Una comunidad puede mantener equilibrio pese a pérdida de conocimiento si una minoría de veteranos repara; por eso el porcentaje de portadores y la composición del choque se miden explícitamente.

## Controles de integridad

Verificar idéntico vector poschoque y mismos nodos reemplazados entre tres condiciones, todos los estados legales 0..k-1, N fijo, como máximo un encuentro por agente y tic, contagio solo a través de parejas y hasta paso siguiente, probabilidad de adopción fija, reproducibilidad por semilla, protocolos exactos de G0 congelados y test del simulador P0 sin cambios.
