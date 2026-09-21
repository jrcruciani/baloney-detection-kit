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

## Prompts en español

Las traducciones preventivas están en
[`prompts/intervention/es/`](../prompts/intervention/es/) y
[`ROOT_PROMPT.es.md`](../ROOT_PROMPT.es.md), autocontenido.
`bdk apply compact --lang es` y `bdk apply full --lang es` funcionan sin SDKs de
proveedores; `--output archivo.md` guarda el prompt. El idioma predeterminado
sigue siendo `en`; no hay sustitución silenciosa por inglés si falta un idioma
o una variante.

Los encabezados de sección, nombres de modos y etiquetas de salida permanecen
en inglés intencionadamente para el análisis automático. La prosa española
traduce el contrato canónico sin localizar sus reglas. `scripts/sync_prompts.py`
sincroniza el bloque completo español y las copias del paquete; `--check`
detecta divergencias sin escribir.

Se requiere revisión humana del español y aprobación del comportamiento y la
versión antes de integrar. Se conserva `prompt-v2.0` para alinearlo con el
contrato inglés; las pruebas estructurales no demuestran calidad semántica,
equivalencia de comportamiento ni eficacia. Portugués y francés siguen
aplazados en [#10](https://github.com/jrcruciani/baloney-detection-kit/issues/10);
no se incluyen copias de skills o plugins en español.

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
