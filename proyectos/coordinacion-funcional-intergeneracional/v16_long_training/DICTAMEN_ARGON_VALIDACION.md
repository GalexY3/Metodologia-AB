# Auditoría independiente de la propuesta de Gemini Argon

**11/11/2026.** Se ha comprobado la formulación matemática y se han ejecutado experimentos sobre el checkpoint de V15 sin modificar pesos. Scripts: argon_b1_b2.py; test_argon_math.py. Datos completos: diagnostics/v15_ops_mlp16_s4111_ARGON_B1B2.json.

## Resultados matemáticos sólidos

El juego de elección unilateral de profesión dispone del potencial exacto de Rosenthal

\[
\Phi(n)=\sum_j\sum_{s=1}^{n_j}\min(s/(N/k),(N/k)/s).
\]

Un cambio unilateral desde a hacia b modifica el potencial en la misma cantidad que cambia la recompensa de quien emigra. Esta propiedad no garantiza que REINFORCE, que actúa con múltiples personas simultáneas, ascienda siempre en potencial.

La recompensa individual 0,5 puede representar media cuota o doble cuota: el régimen de congestión es parcialmente inobservable. La ley de desprendimiento p=1-r, aplicada únicamente a grupos sobreocupados y sin entradas, deja exactamente N/k miembros **en esperanza**, no en cada ejecución. Para N120,k4,un grupo de 60 permanece con 30±3,87 individuos (desviación típica). La probabilidad de retener exactamente 30 es 0,102578.

En una aldea N120,k4 con 2 profesiones de 60, una coalición de **15** emigrantes iguala la utilidad anterior; se necesitan **16** para mejorarla estrictamente. El teorema de Argon confunde en algunos pasajes el umbral de indiferencia y la mejora estricta. Los equilibrios individualmente estables con m<k son una barrera auténtica para métodos unilaterales y un objetivo experimental válido.

## Teoremas o conclusiones que requieren corrección

- **Exceso de grupos.** N12,k10,M12 con doce grupos de una persona es un equilibrio de Nash estricto con m12>k10: un individuo baja de 0,833 a 0,6 si se cambia a otra profesión ocupada. La exclusión general de equilibrios m>k es falsa para cuotas no enteras.
- **U1 para cuotas no enteras.** N120,k80,M120 permite 80 grupos de tamaños uno/dos o 120 grupos unitarios y ambos alcanzan alimentación uno. La fórmula plana no identifica únicamente el número k.
- **U2 no es siempre telescópica.** Para N120,k7, la marginal real del bienestar F(18)-F(17) relativa a F(17)-F(16) vale 0,147805, pero la U2 propuesta por Argon iguala ambas utilidades a 1. No coincide con el producto marginal original cuando la cuota no es entera; para cuota entera puede representar una utilidad marginal normalizada pero cambia el juego.
- **La densidad local no identifica globalmente la rama con certeza.** Pueden cambiar las ocupaciones distantes sin que cambie de igual forma la muestra vecinal. Los falsos signos son mensurables.
- **V15 no imitaba vecinos por su recompensa.** Sus candidatos se basaban en profesión modal, minoritaria, vecino aleatorio y frecuencia local. No se puede atribuir su fracaso a una operación de selección del vecino con mayor recompensa que no está implementada.
- **La regla de congelación V15 no es universal.** El veto de 0,75 sólo se activa cuando k/M>=0,70. No congela directamente una aldea M50,k4 porque 4/50=0,08.
- **La firma de cooperación propuesta tampoco es prueba causal.** Una mezcla heterogénea de decisiones individuales independientes puede producir un Fano sub-binomial, incluso Fano=0 con 30 agentes p=1 y otros 30 p=0. La concentración de destinos puede surgir de convenciones públicas, sin mensajes laterales. Se precisan ablaciones contrafactuales.
- **El pseudocódigo HSD rompe la simetría de etiquetas.** Elegir siempre la primera profesión vacante (vacant[0]) impone una etiqueta privilegiada. Compartir recompensa de vecinos y anuncios de fisión añade nuevos canales de información. Todos pueden ser intervenciones válidas, pero deben declararse y compararse limpiamente.
- **La caída del rango efectivo no es condición necesaria demostrada de grokking.** El diagnóstico requiere desfase entrenamiento/generalización, retención fuera de muestra y repetición por semillas; no un marcador espectral aislado.

Siete pruebas matemáticas automáticas han pasado, entre ellas la identidad de potencial unilateral, contraejemplo Nash m>k, umbral de coalición, efecto binomial, problema U1 y U2 fraccionario.

## Experimentos sobre V15 congelada

Se ejecutaron diez combinaciones M/k, dos inicios (aleatorio y trampa), cinco tratamientos y tres semillas de 48 mundos: **100 condiciones con 144 mundos por condición**, 60 turnos.

- Original: veto individual de movilidad cuando alimento >=0,75 y k/M>=0,70.
- Sin veto.
- Veto dinámico recomendado por Argon cuando alimento >=1-k/N.
- Veto usando signo local: alimento >=0,75 y k por frecuencia de vecinos de la propia profesión <=1.
- Veto con el signo calculado desde el **censo global**, sólo como control ORÁCULO no permitido para agentes.

| M | k | Inicio | Original | Umbral 1-k/N | Sin veto | Signo local | Oráculo no permitido |
|---:|---:|---|---:|---:|---:|---:|---:|
| 12 | 10 | aleatorio | 0,8189 | 0,8069 | 0,8024 | 0,8087 | 0,8412 |
| 16 | 15 | aleatorio | 0,8162 | 0,8078 | 0,8007 | 0,8099 | 0,8349 |
| 24 | 20 | aleatorio | 0,7817 | 0,7932 | 0,7768 | 0,7824 | 0,7960 |
| 40 | 30 | aleatorio | 0,7808 | 0,7808 | 0,7632 | 0,7763 | 0,7983 |
| 80 | 60 | aleatorio | 0,7662 | 0,7114 | 0,7555 | 0,7558 | 0,7662 |
| 50 | 4 | trampa | 0,5000 | 0,5000 | 0,5000 | 0,5000 | 0,5000 |
| 80 | 60 | trampa | 0,4995 | 0,5000 | 0,4994 | 0,4994 | 0,4995 |

Al comparar el umbral sugerido contra el original, mejoró 2 condiciones, empeoró 3 y apenas cambió 15 (tolerancia 0,0005). Quitar completamente el veto mejoró 0/empeoró 5. El signo local simple mejoró 1/empeoró 4. El control global ilegal mejoró 4 y no empeoró ninguna.

La precisión del clasificador local de congestión (excluyendo tamaños exactamente óptimos) fue **0,446** al inicio con M80,k60 y distribución aleatoria; desde la trampa correspondiente, **0,183**. El estimador puede funcionar en determinados escenarios y fallar gravemente en otros. Su fiabilidad depende de red, M y k.

**No apareció ningún rescate sustancial de las trampas tras 60 turnos en estos tratamientos.** Modificar el veto de movimiento no resulta suficiente para aprender fisión coordinada. Esto NO descarta un nuevo entrenamiento HSD: las pruebas B2 reutilizan un modelo aprendido con otra representación.

## Próximas intervenciones de más valor

Mantener la recompensa original en el tratamiento principal, para no confundir cambio de juego con cambio de capacidad neuronal. Diseñar un estimador local de régimen calibrado (incluso con opción de incertidumbre/abstención), ablar el canal de recompensa de vecinos y experimentar explícitamente con propuestas de fisión y respuesta de vecinos. Para cada intervención, medir tanto alimentación como exactitud de k y escape desde dos grupos de 60 en N120,k4,M50. Para inferir cooperación, intervenir mensajes y destinos comunes; la coincidencia de acciones por sí sola no certifica coordinación aprendida.

Los entrenamientos largos V16 constituyen una serie separada y no deben presentarse como test del nuevo HSD. La presencia de un potencial matemático o una mejora tardía aislada no demuestra grokking.
