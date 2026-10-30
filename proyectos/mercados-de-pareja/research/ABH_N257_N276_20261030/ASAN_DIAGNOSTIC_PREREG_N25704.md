# ASan/UBSan diagnóstico postciclo N257 (NO cuenta como nuevo AB)

**Estado prospectivo antes de ejecutar sanitizer:** el control N257 detectó `BOOST_RETURN_-11` para un grafo sintético n143 `near_tie` semilla `25704`, densidad 0.3 y 3117 aristas, así como timeout en otro `flat`. N258 detectó timeout en grafos n144 `flat` y `near_tie`. **Estos no son los fixtures históricos N242/N246 ausentes.**

**Pregunta discriminante:** ¿puede el sanitizer identificar el tipo de fallo de memoria de la implementación Boost C++ en el fixture n143 ya observado?

**Instrumentos congelados PRE-OUTCOME ASan:**
- Fuente `boost_blossom.cpp` SHA256 `47806e6b331e088d209e51143d18cb5d5cc7a2e2d3d6d8914478bff4b7b8c2d3`.
- Fixture `fixture_N25704_near_tie_n143.txt` SHA256 `0cf31966ff1839a5cf9ca31255b8412eaf6bd5e66502657df90b3ba253b88ee2`; cabecera 143 3117, pesos enteros codificados cardinalidad-first.
- Binario de debug `boost_blossom_asan` SHA256 `2f038079c6e7369e39d5e0222c9a7dea64d9512df6a6558c893111a2233c4a8d`.
- `g++ 14.2`, flags `-std=c++17 -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer`, Linux x86_64.

**Protocolo:** ejecutar exactamente una vez este fixture con binario debug en subprocess aislado, límite wall-clock 8 segundos, ASAN_OPTIONS `abort_on_error=1:detect_leaks=0`, registrar returncode, timeout, stderr íntegro con SHA, extracto de stack trace y RSS. No suponer que todo `SIGSEGV` es fallo Boost: atribuir solo si stack/testigo lo soporta; puede ser conversión/protocolo/overflow o entorno. Las reparaciones exigen prerregistro nuevo. Conservar `N257` negativo original sin sobreescritura. Categoría `POST_HOC_FOCUSED_DIAGNOSTIC`, **no nueva plaza AB**, no prueba humana y CT2 7/100/STOP_R5 humano inalterados.

**No** usar resultados ASan para modificar retroactivamente el prereg de N257 ni afirmar reproducción exacta de N242.