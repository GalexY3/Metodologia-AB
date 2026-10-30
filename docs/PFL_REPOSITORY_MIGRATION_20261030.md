# Politics Fantasy: repositorio independiente · 30/10/2026

El investigador autorizó separar el proyecto del método. Destino canónico: [https://github.com/GalexY3/politics-fantasy-league](https://github.com/GalexY3/politics-fantasy-league), `main`. AB conserva su protocolo, motor Atlas genérico y versiones históricas; las entradas antiguas redirigen y no constituyen otra autoridad.

- Snapshot fuente: `69ed402dd4a3f25207d9e620ede568b5e92ad8af`, etiqueta `pfl-monorepo-final-20261030`.
- Destino publicado y comprobado antes del corte: `903c000c3f6a60f408cc470564471cfba9a1354a`.
- Historia filtrada de PFL y del motor; identidad inicial de blob/modo de 2.743 archivos. SHA originales→extraídos en [COMMIT_MAP.tsv](https://github.com/GalexY3/politics-fantasy-league/blob/main/docs/migration/COMMIT_MAP.tsv). Los 16 workflows de raíz se preservan como originales inertes con hashes en el destino; se retiran los ejecutores de PFL de AB.
- QA Linux de código adaptado `3d66e813a422572b2a2ce7a3155df8dac667e224`: 822 Python +32 subtests, 511 Node y 38 Atlas +104 subtests PASS, cero fallos/skips; instalación, catálogo, continuidad y replay PASS. [Evidencia](https://github.com/GalexY3/politics-fantasy-league/blob/main/docs/migration/linux/MANIFEST.json).
- El test de compatibilidad del corpus PFL vive ahora junto al corpus en el destino; AB conserva las pruebas genéricas del motor.
- Atlas93 conserva SHA `7edd32ca6872071bd34de668c96a75f07b686a3cd4f676ca2237d5e1fde2227d`, 63 nodos, 81 edges, 310 runs y gates 0/6. Mantenimiento: 0 ciclos AB nuevos; sin promoción científica.
- Seguimiento actual: [PFL#1](https://github.com/GalexY3/politics-fantasy-league/issues/1); issue AB#17 conserva su historia y enlaza al nuevo índice.

No se ha reescrito la historia de AB ni eliminado ramas alternativas. Los SHA antiguos permanecen consultables. Los archivos raw/private locales no versionados no forman parte del traslado. La relación con el método queda fijada en [METHOD_REFERENCE.json](https://github.com/GalexY3/politics-fantasy-league/blob/main/METHOD_REFERENCE.json); cambios futuros requieren adopción explícita en el proyecto.
