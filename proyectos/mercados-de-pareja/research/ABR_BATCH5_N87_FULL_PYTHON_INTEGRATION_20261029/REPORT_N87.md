# N87 — Integración de supervivencia ejecutada sobre ESBM v2 ORIGINAL

**Ciclo AB-R válido únicamente técnico, grado 0/3 científico.** Usuario adjuntó tres archivos que verificamos byte a byte contra GitHub. Pre-ejecución: freeze 4482b9936c47820dd719f1a177d9c01079b10239, paquete completo en N87_PREEXEC_FREEZE.tar.gz, SHA256 8baf8a3cda6546cc161835061236f2c894f79545914fd24025a2dc0d1a5d3719. Contiene A–J, fuente instrumentación, 10 tests y manifiesto de hashes; el código original ESBM y helper N86 permanecen intactos.

## Ejecución e invariantes A–J

En una carpeta aislada con copia de los archivos exactos, se ejecutó Python 3.13.5 (NumPy 2.3.5, NetworkX 3.6.1). El instrumento carga y ejecuta esbm_dynamic.py, verifica SHA y crea una variante instrumentada en memoria. **19 de 19 tests pasan** (9 anteriores +10 nuevos). El código original y la variante producen salidas anteriores **exactamente iguales** en 60 combinaciones seis semillas x diez escenarios, incluidas series temporales track. Se repitió el contraste para crear archivo original íntegro. No fue una reinstalación de paquetes desde cero.

Las 60 ejecuciones instrumentadas muestran **13.668 relaciones formadas, 10.028 rupturas y 3.640 activas censuradas**, conservación exacta, entradas en 16 períodos por cada corrida y hasta 61 niveles distintos de riesgo de ruptura. Todas las pruebas predefinidas de alteración del SHA, eventos al horizonte, censura anticipada, cohorte escalonada, igualdad de salidas históricas y RMST4 acotada se completaron sin fallos.

## Resultados numéricos artificiales

| Escenario sintético | Formadas | Rupturas | Censuradas | Elegibles RMST4 | RMST4 |

|---|---:|---:|---:|---:|---:|

| mixed_random | 1360 | 988 | 372 | 1160 | 2.921 |

| heterosexual_restricted | 1165 | 854 | 311 | 987 | 2.997 |

| institutional_segregation | 1312 | 937 | 375 | 1123 | 3.003 |

| explicit_norm_preference | 1447 | 1030 | 417 | 1251 | 3.047 |

| popularity_ranking | 1341 | 972 | 369 | 1138 | 2.998 |

| visibility_balancing | 1443 | 1090 | 353 | 1235 | 2.873 |

| private_rejection_learning | 1482 | 1085 | 397 | 1257 | 2.892 |

| public_rejection_signal | 1254 | 932 | 322 | 1061 | 2.918 |

| longer_partnerships | 857 | 468 | 389 | 767 | 3.486 |

| shorter_partnerships | 2007 | 1672 | 335 | 1653 | 2.327 |

El horizonte de 4 ticks se limita a uniones formadas antes del tick 13 para asegurar cuatro ticks de seguimiento. RMST4 no es comparable directamente con la antigua media de uniones terminadas: población, censura y estimando distintos. Las variantes largas/base/cortas dan 3.486/2.921/2.327 por reglas de hazard sintéticas. No inferir efectos en personas.

## Registro y límites

U136 actualiza P-UNION-DURATION sin cambio científico. Fuentes 97, priors 30, updates 136. Avance ponderado 39.05 a 39.65 % por mejora del simulador y QA, sin alterar originalidad 10% ni validación externa 5%. CT2 7/100 ordinal. **21 de 40 ciclos válidos; primera tanda N83–N87 completada 5/5, otros 19 N88–N106 quedan reservados sin liberar otra tanda.** STOP_R5 externo sigue. Nada de validación humana, aceptación de licencias, contacto con autores, acceso a rutas prohibidas, SSJY o merge main.

El JSON completo de 60 resultados se generó en el runtime y su SHA256 92dc697811fb90db44bb31bd5b0ba782cb3549d01bfb77affa4da129eb8dc500 figura en el resumen; el documento de GitHub ofrece agregados de todos los escenarios. El archivo íntegro se entrega como adjunto. Test transcript SHA256 50c0269e779fdeb59e66638f4b41cbe053b1dfdf15a4dd29de5331eb4b9bab1a. El código fuente congelado está en archivo tar.gz junto a preregistro, en la rama privada.