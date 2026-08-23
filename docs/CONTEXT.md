# BDK 3.0 - Contexto del proyecto

Baloney Detection Kit es un framework con una implementación Python de
referencia para prevenir amplificación de confianza no sustentada, diagnosticar
comportamientos de sistemas de IA y validar intervenciones.

## Contrato del producto

```text
Detectar riesgo -> Aplicar fricción -> Diagnosticar conducta -> Validar resultados
```

Las capas comparten un único repositorio, vocabulario, esquema de escenarios,
CI, licencia MIT y ciclo de release.

## Superficies

- `PLAYBOOK.md`: protocolo preventivo.
- `prompts/intervention/`: prompts preventivos.
- `framework/diagnosis/`: método diagnóstico.
- `prompts/diagnosis/`: catálogo y fichas diagnósticas.
- `src/bdk/`: CLI y motor de referencia.
- `scenarios/`: escenarios ejecutables.
- `validation/closed-loop/`: calibración de intervenciones.
- `validation/diagnosis/`: validación del diagnóstico.
- `tests/`: pruebas unitarias e integración.

## Reglas de diseño

1. BDK sigue siendo framework-first; el CLI automatiza el método.
2. Las explicaciones diagnósticas son hipótesis, no acceso al interior del
   modelo.
3. Toda diagnosis separa modelo, runtime/host y conversación.
4. Las afirmaciones se etiquetan Observed o Inferred.
5. Los tests conductuales pesan más que el autorreporte del modelo.
6. Los jueces LLM ayudan a revisar; no son ground truth.
7. Los resultados se reportan con casos, modelos, prompts, runs, revisión
   humana y efectos adversos.
8. La licencia de la distribución integrada es MIT.

## Release

- Producto: BDK 3.0.0.
- Namespace Python: `bdk`.
- CLI canónica: `bdk`.
- Alias ejecutable temporal para instalaciones anteriores.
- Python soportado: 3.11, 3.12 y 3.13.
