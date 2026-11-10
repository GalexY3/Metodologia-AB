# Aldea V12: profesiones y grupos variables

Objetivo: aprender a formar k grupos viables entre M profesiones, con pesos neuronales independientes por habitante.

## Economía

N personas, M profesiones, tamaño ideal N/k. Recompensa alimentaria individual r_i=min(n_j/(N/k),(N/k)/n_j). Para N divisible por k, el máximo de cada persona coincide con k grupos de tamaño N/k y las demás profesiones vacías. Los agentes NO conocen k, la cuota, el censo, Dk ni las recompensas contrafácticas.

## Agente

Política equivariante a renombrar las profesiones: cada individuo aplica su propia pequeña MLP a cada profesión, independientemente de M. Posee 128 parámetros privados, 80 para escoger empleo y 48 para anunciar voluntariamente una profesión. Memoria EMA de frecuencias locales. Solo observa su profesión, frecuencias de sus vecinos, ración propia y su cambio, anuncios recibidos y, únicamente en el tratamiento público, bienestar global realizado y su variación.

Con --communication cada habitante anuncia una profesión a sus vecinos justo antes de elegir el trabajo final; el anuncio no obliga a cambiar. El significado de la señal está programado, pero su uso se aprende. Sin comunicación, el agente puede igualmente cambiar por iniciativa propia. La recompensa es personal excepto cuando --alpha 0.1 mezcla 90 % personal y 10 % bienestar agregado. Dk es solo auditoría externa. No hay parámetros compartidos, crítico centralizado ni oráculo de asignación contrafáctica.

## Diseño de transferencia

En N=60 entrenar cruzando M=10,20 con k=2,4. Examinar M=30 y k=3,5,6, nunca empleados para actualizar pesos. Esta prueba de desarrollo no es un test confirmatorio sellado. Se admiten otros N, M, k, redes y grado; si N no es divisible por k, se rechaza para preservar exactitud.

Inicios aleatorios y, por separado, --init trap para sociedades inicialmente atrapadas en 1 o 2 profesiones. Comparar C0 sin mensajes y C1 con anuncios, información social pública y 10 % de recompensa colectiva como tratamientos distintos. No inferir cooperación de un resultado agregado: intervenir comunicación, observar transferencia y probar contra baselines.

## Ejecución

Desde esta carpeta con PyTorch y NumPy instalados:

    python -m unittest -v test_v12.py
    python v12.py --name c0_n60_s1111 --n 60 --m-train 10,20 --k-train 2,4 --updates 350 --batch 24 --horizon 18 --eval-every 70 --eval-batch 32 --eval-horizon 40 --seed 1111

El programa guarda código, parámetros, estado del optimizador, configuraciones, historial y estado bajo runs/NOMBRE. Los resultados son exploratorios.
