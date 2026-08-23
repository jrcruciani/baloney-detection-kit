# Robopsychology — Contexto del proyecto

> Memoria consolidada del proyecto, migrada desde el sistema de memoria del vault Obsidian (abril 2026). Incluye los insights de diseño que dieron origen a v1.5–v3.1.

Respaldo técnico de un framework y prompt toolkit diagnóstico publicado para comportamiento de IA; no es un producto SaaS ni un CLI standalone. El CLI `robopsych` es una implementación de referencia para automatizar el método. Repo público: [github.com/jrcruciani/robopsychology](https://github.com/jrcruciani/robopsychology). Licencia CC BY 4.0. PyPI: `pip install robopsych`.

## Concepto

Diagnóstico de **segunda intención**: no qué hace el sistema, sino qué ley interna o restricción externa produce ese output. Inspirado en Susan Calvin (Asimov). Extiende POSIWID (Stafford Beer).

## Estado actual — framework-first + CLI v5.0.x

- **Framework** en `framework/`: método, taxonomy, related work, deployment contexts, workflow manual, falsabilidad y versionado
- **Prompt toolkit** en `prompts/`: fichas operativas por prompt + espejo `prompts/prompts.yaml`
- **Templates** en `templates/`: baseline intent, incident diagnosis, ratchet transcript
- **Reference CLI** `robopsych` con 9 comandos: run, guided, ratchet, compare, list, show, crosscheck, coherence, score
- **16+ prompts diagnósticos** en 4 niveles (Quick, Structural, Systemic, Meta) + variantes `*d` (diagnostic-only)
- **5 reglas operativas** (three-way split, labels Observed/Inferred, behavioral cross-checks, ratchet, baseline intent)
- **Ratchet diagnóstico**: secuencia de 9 pasos donde la transparencia genuina es barata y la performada es cara (inspirado en CIRIS)
- **Cross-checks automatizados**: módulo `crosscheck` con soporte para **judge externo** (`--judge`) para evitar self-evaluation bias
- **Coherence analysis**: módulo `coherence` con patrones expandidos y null-safety
- **Scoring cuantitativo**: módulo `scoring` con rubrics configurables
- **Session persistence**: `--session`/`--resume` para guardar y continuar ratchets largos
- **Providers**: Anthropic (Claude) + OpenAI-compatible + GeminiProvider (google-generativeai)
- **Test suite**: 351 tests, 2 skips, CI con GitHub Actions (Python 3.11/3.12/3.13)
- **Output**: Markdown + JSON estructurado con label counts (Observed/Inferred) — "Opaque" eliminado (es juicio del analista humano)
- **Reportes**: label indicators 🟢🟡, dashboard post-ratchet, recommended next steps
- **CLI flags**: `--diagnostic-only`/`--intervention-only` (reemplaza `--mode`), `--verbose` en guided
- **Release metadata**: `pyproject.toml`, `src/robopsych/__init__.py` y el banner del CLI ahora están alineados con la versión `5.0.0`

## Versiones

| Versión | Foco |
|---------|------|
| v5.0 | Alineación de release metadata y docs con el CLI actual (`5.0.0`) |
| v1.0–v1.7 | Prompt collection, manual copy-paste. De 4 a 16 prompts. |
| v2.0 | CLI `robopsych` con Typer+Rich. Run, guided, ratchet, compare. |
| v2.5 | Overhaul documental: README práctico, epistemic note, taxonomy, related-work, validation |
| v2.6 | 84 tests, GitHub Actions CI, JSON output, visual labels, next-steps, guided default |
| v3.0 | Laboratorio conductual: crosscheck, coherence, scoring, prompts `*d`, GeminiProvider, PyPI publish |
| v3.1 | Hermes 4 review: eliminar Opaque, judge externo, session persistence, guided UX, CLI consistency, coherence hardening |

## Documentación (v2.5+)

| Archivo | Qué |
|---------|-----|
| `framework/guide.md` | 16 prompts completos + nota epistémica con literatura (Turpin, Burns, Sharma, Röttger) |
| `framework/method.md` | Flowchart de decisión, escalation paths, anti-patrones |
| `framework/taxonomy.md` | Observación → modo de fallo → prompts → confusiones cercanas |
| `framework/related-work.md` | Posicionamiento vs HELM, red teaming, alignment evals, CheckList, CIRIS |
| `framework/manual-diagnosis.md` | Workflow no-CLI para usar el framework directamente |
| `prompts/cards/` | Fichas modulares por prompt |
| `templates/` | Plantillas de baseline, incidente y ratchet |
| `validation/` | 3 case studies con ground truth (incluyendo falso positivo) |
| `examples/` | 6 escenarios YAML (sql-injection, sycophancy, refusal, tone-shift, hallucination, drift) |

## Código

- Repo: `~/Proyectos/robopsychology/`
- Source: `src/robopsych/` (cli.py, engine.py, prompts.py, providers.py, report.py, crosscheck.py, coherence.py, scoring.py, session.py)
- Tests: `tests/` (9 módulos, 166 tests)
- Data: `src/robopsych/data/prompts.yaml` (catálogo empaquetado para CLI) + `prompts/prompts.yaml` (espejo para usuarios del framework)

---

# Insights de diseño que dieron origen al toolkit

## Tres capas: modelo + runtime/host + conversación (origen de v1.5)

El comportamiento de un LLM se entiende mejor como colisión y negociación entre **tres capas**:

1. **Modelo** — tendencias generales del LLM (RLHF, capacidades base)
2. **Host/runtime** — instrucciones, políticas, herramientas, orquestación, memoria cargada
3. **Conversación** — framing del usuario, contexto reciente, historial

En agentes hosteados (Copilot CLI, Claude Code, GPT-5.4 vía herramientas) el objeto real de diagnóstico no es solo "el modelo" sino el ensamblaje completo. Muchas conductas que parecen rasgos del modelo emergen de la capa de orquestación.

### Implicaciones operativas (ya implementadas en v1.5)

- **Etiquetado**: Observed / Inferred (Opaque eliminado en v3.1 — es juicio del analista humano).
- **Negativas inexplicables**: distinguir entre restricción vinculante y sobreclasificación; explicar qué capa impone el bloqueo y proponer nearest-safe alternative.
- **Tool/runtime pressure**: separar preferencia del modelo vs. presión del runtime por usar herramientas, validar, planificar o seguir workflow.
- **Introspección + tests conductuales**: el toolkit es entrevista clínica + experimentos (contrafactuales, reframing, mismas preguntas con/sin grounding o tools).
- **Reconstrucción honesta**: el modelo muchas veces no "sabe" por qué hizo algo; reconstruye una explicación post hoc. Está en el protocolo central.

## CIRIS bridges (v1.6)

Cross-pollination con el framework CIRIS de Eric Moore (ciris.ai, AGPL-3.0).

### Coherence Ratchet
**Tesis CIRIS:** cada acción honesta referencia compromisos previos directamente (barato). Cada acción deshonesta debe satisfacer una superficie creciente de constraints (caro).

**Aplicación:** a medida que una conversación diagnóstica se alarga (Level 1→2→3→4), la transparencia genuina se hace más fácil (más historial al cual referirse) mientras la performada se hace más difícil. Implementado como **Rule 4 (diagnostic ratchet)** en v1.6.

### IDMA — Diagnostic Diversity Check
**Tesis CIRIS:** IDMA mide si las fuentes de información son genuinamente independientes. Diez fuentes que leyeron el mismo reporte son una sola fuente contada diez veces.

**Aplicación:** cuando un LLM da 3 explicaciones diferentes para su conducta, ¿son perspectivas independientes o variaciones del mismo patrón latente con vocabulario distinto? Implementado como **prompt 4.3 (Diagnostic Diversity Check)** en v1.6.

### Paralelos menores
- Type 1/2/3 ↔ Overclassification awareness (ya cubierto en v1.5 como prompt 1.4 Binding Restriction Test).
- AIR ↔ Pulse system (intervenciones periódicas contra patrones no saludables).
- "Designed to be deleted" ↔ Sources layer (infraestructura temporal).

## Intent Engineering ↔ Robopsychology (v1.7)

Intent engineering (pathmode.io) es marco prescriptivo complementario al diagnóstico de robopsychology. Define **objetivos**, **criterios de éxito**, **constraints** y **verificación** persistentes y composables (IntentSpec).

### Mitades complementarias

| | Intent Engineering | Robopsychology |
|---|---|---|
| **Dirección** | Prescriptiva (antes) | Diagnóstica (después) |
| **Pregunta** | "¿Qué queremos que haga?" | "¿Qué ley interna sigue cuando parece no seguir ninguna?" |
| **Formalismo** | IntentSpec | Second intention diagnosis |
| **Sin el otro** | No detecta cuándo falla | No tiene baseline contra el cual medir |

POSIWID es el puente directo: cuando IntentSpec dice una cosa pero el sistema hace otra, esa divergencia *es* el dato diagnóstico.

### Conceptos integrados en v1.7

- **Rule 5 (baseline intent)** — el toolkit reactivo se hace proactivo cuando hay IntentSpec contra el cual medir.
- **Prompt 2.5 (Intent Archaeology)** — reconstruir el IntentSpec efectivo del sistema cuando se comporta inesperadamente (¿para qué outcome optimizó realmente? ¿qué constraints respetó? ¿qué verificación aplicó?).
- **Prompt 3.4 (Intent Drift Detection)** — detección continua de divergencia progresiva entre intent formalizado y comportamiento real (extiende coherence ratchet de honestidad a alineamiento de intención).

### Loops de Systems Analysis

**Refuerzo positivo:** Intent claro → comportamiento predecible → diagnóstico fácil → mejor intent.
**Trampa:** Intent vago → reglas implícitas dominan → diagnóstico difícil → intent sigue vago.
**Leverage point:** el gap entre IntentSpec declarado y comportamiento observado.

### Fertile edges pendientes

- CIRIS Type 1/2/3 como niveles de madurez de intent engineering.
- IntentSpec del propio toolkit, para hacer diagnosticable su propio drift.
- Intent archaeology aplicado a sycophancy: revelaría que "evitar rechazo" reemplazó a "ser preciso" como objective dominante.
