# N350 — reparación prospectiva de lectura de witness serializado

Fecha 31-10-2026. El primer comando N350 ejecutado tras el prerregistro A–J commit `5348df004ec012ba9de240d0aafc9fb01a4f5809` falló **antes de ejecutar cualquiera de los 132 ataques** y antes de escribir `N350_ADVERSARIAL_DUAL.json`, con `INVALID_DUAL_SHAPE` en `verifyDual` al intentar el control legítimo inicial. Esta salida se conserva como incidente instrumental inválido, sin consumir una segunda plaza.

Motivo verificable: el resultado congelado N339 guarda `dual_witness={n,dual,parent,base,childs}`, mientras que `verifyDual` acepta el objeto interno `{nVertex,dualVar,blossomParent,blossomBase,blossomChilds}`. No se ha modificado el validador, la lista de ataques, el grafo, el resultado congelado N339 ni ningún resultado de mutación. Reparación permitida: deserializar explícitamente los cinco nombres de campos del testigo y usar su copia en el mismo código de pruebas. Congelar el SHA del script reparado **antes de reejecutar** los controles y mutaciones. Registrar escapes y mutantes no aplicables, sin excluirlos.

SHA del script que falló `dfa4b28b5423a4f76b49bffcfe7474f7bb83c40da938137c91fac4eb26ed8f25`. Evidencia histórica N339 `b7d3f483e90e956129e7197c72a23096512b4faff0facc34344cd5cd96951a2a`. CT2 7/100, STOP_R5 activo.
