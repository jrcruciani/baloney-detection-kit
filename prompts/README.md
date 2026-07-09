# Prompt Matrix

Use these prompts as copy-paste distributions of the same framework. They differ
by context, not by values: every variant preserves the BDK loop:

**Trigger -> Mode -> Protocol -> Output -> Review**

| Prompt | Use when | Copy target |
|--------|----------|-------------|
| [`prompt-compact.md`](prompt-compact.md) | You have a short custom-instructions field | Personal LLM settings |
| [`prompt-full.md`](prompt-full.md) | You want the complete default behavior in one prompt | System prompt or project instruction |
| [`prompt-high-stakes.md`](prompt-high-stakes.md) | False validation could cause material harm | Medical, legal, financial, safety, public-sector, political, or mental-health-adjacent assistants |
| [`prompt-agent.md`](prompt-agent.md) | The assistant can use tools, retrieval, agents, or MCP | Agent runtime instructions |
| [`prompt-reviewer.md`](prompt-reviewer.md) | You need to review an answer after it was generated | Human/AI review pass |
| [`prompt-second-opinion.md`](prompt-second-opinion.md) | You want external critique from a model that has not seen the first answer | External reviewer |

## Selection rule

Choose the smallest prompt that preserves rigor in your context:

1. If you are an individual user, start with `prompt-compact.md`.
2. If you are configuring an assistant, use `prompt-full.md` or `ROOT_PROMPT.md`.
3. If the domain can create material harm, use `prompt-high-stakes.md`.
4. If the runtime has tools or subagents, use `prompt-agent.md`.
5. If the response already exists, use `prompt-reviewer.md`.
6. If you want external contrast, use `prompt-second-opinion.md`; treat it as
   critique diversity, not independent evidence.

## Versioning

If you embed a prompt in a product, classroom, evaluation, or team workflow, pin
the repository commit and note which prompt file you used. See
[`../VERSIONING.md`](../VERSIONING.md).
