# Ejemplos del piloto AB-M038–M042

Los archivos de esta carpeta representan plantillas y ejemplos SINTÉTICOS, sin datos empíricos ni agentes ejecutados. Ninguna cifra puede utilizarse como evidencia científica.

- tasks.json — orden y contratos de los siete roles de AB; para iniciar el workflow, no para afirmar que los agentes estén activos.
- rows_synthetic.json — resultados inventados solo para probar la mecánica del análisis pareado.
- scientific_audit_unknown.json — informe deliberadamente no aprobado; el gate debe bloquear la aceptación editorial.

Ejecutar desde la raíz del repositorio:

    python -m ab_tools workflow-init --tasks examples/ab_tools_demo/tasks.json --out demo_workflow.json
    python -m ab_tools workflow-ready --file demo_workflow.json
    python -m ab_tools meta-compare --rows examples/ab_tools_demo/rows_synthetic.json --out demo_comparison.json

No subir resultados de demostración como hallazgos 1/3.
