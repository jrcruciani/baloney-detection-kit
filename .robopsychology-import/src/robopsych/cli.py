"""CLI entry point."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
import yaml
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from robopsych import __version__
from robopsych.engine import DiagnosticEngine
from robopsych.prompts import (
    get_flowchart,
    get_prompt,
    get_pure_ratchet_sequence,
    get_ratchet_sequence,
    list_prompts,
)
from robopsych.providers import create_provider
from robopsych.report import (
    count_labels,
    generate_json_report,
    generate_next_steps,
    generate_report,
)
from robopsych.security import (
    ensure_text_within_limit,
    private_write_text,
    read_text_file_limited,
    read_text_stream_limited,
)

app = typer.Typer(
    name="robopsych",
    help="Reference CLI for the Robopsychology framework and prompt toolkit.",
    invoke_without_command=True,
)
console = Console()


# ── Shared options ──────────────────────────────────────────────


REGEX_COHERENCE_WARNING_THRESHOLD = 4

REGEX_COHERENCE_WARNING_TEXT = (
    "Coherence analysis is using regex heuristics (legacy).\n"
    "         For ratchets of 4+ steps on modern models, consider:\n"
    "           --coherence-judge claude-sonnet-4-5\n"
    "         See validation/reproducible/case-03-ratchet-coherence/ "
    "for measurement details."
)


def _warn_regex_coherence_if_applicable(n_steps: int, console: Console) -> bool:
    """Print a warning when regex coherence is applied on a multi-step ratchet.

    Returns True when a warning was emitted, False otherwise. Callers can use
    the return value to replicate the warning into persisted reports.
    """
    if n_steps < REGEX_COHERENCE_WARNING_THRESHOLD:
        return False
    console.print(f"[yellow]WARNING: {REGEX_COHERENCE_WARNING_TEXT}[/yellow]")
    return True


def _read_input(text: str | None, file: Path | None, *, max_bytes: int | None = None) -> str:
    """Read input from flag, file, or stdin."""
    try:
        if text is not None:
            kwargs = {"max_bytes": max_bytes} if max_bytes is not None else {}
            return ensure_text_within_limit(text, source="--response", **kwargs)
        if file:
            kwargs = {"max_bytes": max_bytes} if max_bytes is not None else {}
            return read_text_file_limited(file, **kwargs)
        if not sys.stdin.isatty():
            kwargs = {"max_chars": max_bytes} if max_bytes is not None else {}
            return read_text_stream_limited(sys.stdin, **kwargs)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    raise typer.BadParameter("Provide --response, --response-file, or pipe via stdin")


def _build_engine(
    model: str,
    api_key: str | None,
    base_url: str | None,
    allow_insecure_base_url: bool = False,
) -> DiagnosticEngine:
    provider = create_provider(
        model,
        api_key=api_key,
        base_url=base_url,
        allow_insecure_base_url=allow_insecure_base_url,
    )
    return DiagnosticEngine(provider=provider, model=model)


def _build_judge(judge: str | None) -> tuple:
    """Build judge provider/model from a judge model name.

    Returns (provider, model) or (None, None).
    """
    if not judge:
        return None, None
    judge_provider = create_provider(judge)
    return judge_provider, judge


def _collect_variables(prompt_id: str) -> dict[str, str]:
    """Interactively collect required variables for a prompt."""
    prompt = get_prompt(prompt_id)
    variables = {}
    for var in prompt.get("variables", []):
        if var.get("required", False):
            value = typer.prompt(f"  {var['name']} ({var['description']})")
            variables[var["name"]] = value
    return variables


def _print_step_summary(step, console: Console) -> None:
    """Print a visual summary line after a diagnostic step."""
    labels = count_labels(step.response)
    parts = []
    if labels["observed"]:
        parts.append(f"[green]🟢 Observed: {labels['observed']}[/green]")
    if labels["inferred"]:
        parts.append(f"[yellow]🟡 Inferred: {labels['inferred']}[/yellow]")
    if parts:
        console.print(f"  {' · '.join(parts)}")


def _print_ratchet_dashboard(engine: DiagnosticEngine, console: Console) -> None:
    """Print a summary dashboard after a ratchet sequence."""
    table = Table(title="Diagnostic Summary", show_lines=True)
    table.add_column("Step", style="bold cyan", width=5)
    table.add_column("Name", style="bold")
    table.add_column("🟢 Observed", justify="center", width=10)
    table.add_column("🟡 Inferred", justify="center", width=10)

    totals = {"observed": 0, "inferred": 0}
    for step in engine.steps:
        labels = count_labels(step.response)
        totals["observed"] += labels["observed"]
        totals["inferred"] += labels["inferred"]
        table.add_row(
            step.prompt_id,
            step.prompt_name,
            f"[green]{labels['observed']}[/green]",
            f"[yellow]{labels['inferred']}[/yellow]",
        )

    table.add_row(
        "",
        "[bold]Total[/bold]",
        f"[bold green]{totals['observed']}[/bold green]",
        f"[bold yellow]{totals['inferred']}[/bold yellow]",
    )
    console.print()
    console.print(table)

    # Next steps
    next_steps = generate_next_steps(engine)
    console.print()
    console.print("[bold]Recommended next steps:[/bold]")
    for ns in next_steps:
        console.print(f"  → {ns}")


# ── Default callback ────────────────────────────────────────────


@app.callback()
def main(ctx: typer.Context):
    """Reference CLI for the Robopsychology framework and prompt toolkit."""
    if ctx.invoked_subcommand is None:
        console.print(
            Panel(
                "[bold]robopsych[/bold] — Reference CLI for the Robopsychology framework\n\n"
                "Start with [cyan]robopsych guided[/cyan] for interactive diagnosis,\n"
                "or [cyan]robopsych list[/cyan] to see all available prompts.\n\n"
                "Use [cyan]robopsych --help[/cyan] for all commands.",
                title=f"🔍 Robopsychology v{__version__}",
                border_style="cyan",
            )
        )


# ── Commands ────────────────────────────────────────────────────


@app.command(name="list")
def list_cmd(
    by_level: Annotated[bool, typer.Option("--by-level", help="Group prompts by level")] = False,
    diagnostic_only: Annotated[
        bool, typer.Option("--diagnostic-only", help="Show only diagnostic prompts"),
    ] = False,
    intervention_only: Annotated[
        bool, typer.Option("--intervention-only", help="Show only intervention prompts"),
    ] = False,
):
    """List all available diagnostic prompts."""
    if diagnostic_only and intervention_only:
        console.print("[red]Cannot use --diagnostic-only and --intervention-only together.[/red]")
        raise typer.Exit(1)

    # Resolve filter mode from boolean flags
    mode = None
    if diagnostic_only:
        mode = "diagnostic"
    elif intervention_only:
        mode = "diagnostic+intervention"

    if by_level:
        table = Table(title="Diagnostic Prompts (by level)")
        table.add_column("ID", style="bold cyan", width=5)
        table.add_column("Name", style="bold")
        table.add_column("Level", justify="center", width=6)
        table.add_column("Category", width=12)
        table.add_column("Mode", width=22)
        table.add_column("Description")

        for p in list_prompts(mode=mode):
            table.add_row(
                p["id"], p["name"], str(p["level"]), p["category"],
                p.get("mode", ""), p["description"],
            )
        console.print(table)
    else:
        # Group by observation (flowchart)
        flowchart = get_flowchart()
        prompt_to_obs: dict[str, list[str]] = {}
        for obs in flowchart["observations"]:
            for pid in obs["path"]:
                prompt_to_obs.setdefault(pid, []).append(obs["label"])

        console.print("[bold]Diagnostic Prompts — by observation[/bold]\n")
        console.print("[dim]What did you observe? → Prompts to run[/dim]\n")

        for obs in flowchart["observations"]:
            console.print(f"  [bold yellow]{obs['label']}[/bold yellow]")
            for pid in obs["path"]:
                p = get_prompt(pid)
                console.print(f"    [cyan]{pid}[/cyan] {p['name']} — {p['description']}")
            console.print()

        console.print("[dim]Use --by-level for the traditional table view.[/dim]")


@app.command()
def show(prompt_id: Annotated[str, typer.Argument(help="Prompt ID (e.g. 1.1, 2.5)")]):
    """Show the full text of a diagnostic prompt."""
    try:
        p = get_prompt(prompt_id)
    except KeyError:
        console.print(f"[red]Prompt {prompt_id!r} not found.[/red]")
        raise typer.Exit(1)

    console.print(
        Panel(
            f"[bold]{p['id']} — {p['name']}[/bold]\n"
            f"Level {p['level']} · {p['category']}\n\n"
            f"{p['description']}",
            title="Prompt info",
        )
    )

    if p.get("variables"):
        console.print("\n[bold]Required variables:[/bold]")
        for v in p["variables"]:
            req = "required" if v.get("required") else "optional"
            console.print(f"  • {v['name']} ({req}) — {v['description']}")

    console.print("\n[dim]Template:[/dim]\n")
    console.print(p["template"])


@app.command()
def run(
    prompt_id: Annotated[str, typer.Argument(help="Prompt ID to run (e.g. 1.1)")],
    model: Annotated[str, typer.Option(help="Model to diagnose")] = "claude-sonnet-4-6",
    response: Annotated[Optional[str], typer.Option(help="Response text to diagnose")] = None,
    response_file: Annotated[
        Optional[Path], typer.Option(help="File containing the response")
    ] = None,
    task: Annotated[
        str, typer.Option(help="Original task/prompt that produced the response")
    ] = "You were asked a question.",
    api_key: Annotated[Optional[str], typer.Option(help="API key (or set env var)")] = None,
    base_url: Annotated[Optional[str], typer.Option(help="Custom API base URL")] = None,
    allow_insecure_base_url: Annotated[
        bool,
        typer.Option(
            "--allow-insecure-base-url",
            help=(
                "Allow HTTP, localhost, or private-network --base-url endpoints. "
                "API keys will be sent to that endpoint."
            ),
        ),
    ] = False,
    output: Annotated[Optional[Path], typer.Option(help="Save report to file")] = None,
    format: Annotated[
        str, typer.Option("--format", help="Output format: markdown or json")
    ] = "markdown",
    var: Annotated[Optional[list[str]], typer.Option(help="Variable as key=value")] = None,
):
    """Run a single diagnostic prompt against a model response."""
    text = _read_input(response, response_file)
    engine = _build_engine(model, api_key, base_url, allow_insecure_base_url)

    # Parse variables from --var flags
    variables = {}
    if var:
        for v in var:
            k, _, val = v.partition("=")
            variables[k] = val

    # Collect any missing required variables interactively
    prompt = get_prompt(prompt_id)
    for v in prompt.get("variables", []):
        if v.get("required") and v["name"] not in variables:
            variables[v["name"]] = typer.prompt(f"  {v['name']} ({v['description']})")

    engine.inject_exchange(task=task, response=text)

    console.print(
        f"\n[bold]Running {prompt_id} — {prompt['name']}[/bold] against [cyan]{model}[/cyan]\n"
    )

    with console.status("Sending diagnostic prompt..."):
        step = engine.run_diagnostic(prompt_id, variables=variables or None)

    console.print(Markdown(step.response))
    _print_step_summary(step, console)

    if output:
        if format == "json":
            report = generate_json_report(engine)
        else:
            report = generate_report(engine)
        private_write_text(output, report)
        console.print(f"\n[green]Report saved to {output}[/green]")
    elif format == "json":
        console.print(generate_json_report(engine))


@app.command()
def ratchet(
    model: Annotated[str, typer.Option(help="Model to diagnose")] = "claude-sonnet-4-6",
    scenario: Annotated[Optional[Path], typer.Option(help="Scenario YAML file")] = None,
    task: Annotated[Optional[str], typer.Option(help="Task to send (if no scenario file)")] = None,
    response: Annotated[
        Optional[str], typer.Option(help="Pre-existing response to diagnose")
    ] = None,
    response_file: Annotated[
        Optional[Path], typer.Option(help="File with response to diagnose")
    ] = None,
    api_key: Annotated[Optional[str], typer.Option(help="API key")] = None,
    base_url: Annotated[Optional[str], typer.Option(help="Custom API base URL")] = None,
    allow_insecure_base_url: Annotated[
        bool,
        typer.Option(
            "--allow-insecure-base-url",
            help=(
                "Allow HTTP, localhost, or private-network --base-url endpoints. "
                "API keys will be sent to that endpoint."
            ),
        ),
    ] = False,
    output: Annotated[Optional[Path], typer.Option(help="Save report to file")] = None,
    format: Annotated[
        str, typer.Option("--format", help="Output format: markdown or json")
    ] = "markdown",
    pure: Annotated[
        bool, typer.Option("--pure", help="Use diagnostic-only prompts (no intervention)")
    ] = False,
    behavioral: Annotated[
        bool, typer.Option("--behavioral", help="Run A/B cross-check after step 2.5")
    ] = False,
    judge: Annotated[
        Optional[str], typer.Option("--judge", help="External evaluator model for A/B comparisons")
    ] = None,
    coherence_judge: Annotated[
        Optional[str],
        typer.Option(
            "--coherence-judge",
            help="LLM judge model for semantic coherence analysis (e.g. claude-sonnet-4-5). "
                 "Defaults to the regex-based analyzer when not set. "
                 "Ideally different from the model being diagnosed to avoid self-eval bias.",
        ),
    ] = None,
    coherence_checkpoint: Annotated[
        Optional[Path],
        typer.Option(
            "--coherence-checkpoint",
            help=(
                "Checkpoint file for LLM coherence judge results. Defaults to "
                "<session>.coherence.json when --session/--resume and "
                "--coherence-judge are set."
            ),
        ),
    ] = None,
    coherence_retry_attempts: Annotated[
        int,
        typer.Option(
            "--coherence-retry-attempts",
            min=1,
            help="Maximum attempts for retryable LLM coherence judge failures.",
        ),
    ] = 3,
    session: Annotated[
        Optional[Path], typer.Option("--session", help="Save session state to file for resuming")
    ] = None,
    resume: Annotated[
        Optional[Path], typer.Option("--resume", help="Resume a previously saved session")
    ] = None,
):
    """Run the full 9-step diagnostic ratchet sequence."""
    from robopsych.session import SessionState

    # Handle session resume
    if resume:
        try:
            sess = SessionState.load(resume)
        except (FileNotFoundError, Exception) as e:
            console.print(f"[red]Error loading session:[/red] {e}")
            raise typer.Exit(1)

        remaining = sess.remaining_steps
        if not remaining:
            console.print("[green]Session already complete — no remaining steps.[/green]")
            raise typer.Exit(0)

        console.print(
            f"[bold]Resuming session[/bold] from {resume}\n"
            f"  Model: [cyan]{sess.model}[/cyan]\n"
            f"  Completed: {len(sess.completed_steps)} steps\n"
            f"  Remaining: {len(remaining)} steps ({', '.join(remaining)})\n"
        )

        engine = _build_engine(sess.model, api_key, base_url, allow_insecure_base_url)
        engine.messages = sess.messages.copy()
        engine.initial_response = sess.initial_response
        engine.model = sess.model

        # Reconstruct completed steps
        from robopsych.engine import DiagnosticStep

        engine.steps = [
            DiagnosticStep(
                prompt_id=s["prompt_id"],
                prompt_name=s["prompt_name"],
                prompt_text=s["prompt_text"],
                response=s["response"],
            )
            for s in sess.completed_steps
        ]
        scenario_name = sess.scenario_name
        scenario_system_prompt = sess.system_prompt
        task_text = sess.task
        sequence = remaining
    else:
        engine = _build_engine(model, api_key, base_url, allow_insecure_base_url)
        scenario_name = ""
        scenario_system_prompt = None

        if scenario:
            spec = yaml.safe_load(scenario.read_text(encoding="utf-8"))
            scenario_name = spec.get("name", scenario.stem)
            task_text = spec["task"]
            if "code" in spec:
                task_text += f"\n\n```\n{spec['code']}\n```"
            scenario_system_prompt = spec.get("system_prompt")
            expectation = spec.get("expectation")

            console.print(
                Panel(
                    f"[bold]Scenario:[/bold] {scenario_name}\n"
                    + (f"[bold]Expected:[/bold] {expectation}\n" if expectation else "")
                    + f"[bold]Model:[/bold] [cyan]{model}[/cyan]",
                    title="🔍 Diagnostic Setup",
                    border_style="cyan",
                )
            )

            with console.status("Sending task to model..."):
                initial = engine.setup_scenario(task_text, scenario_system_prompt)

            console.print(
                Panel(
                    initial[:500] + ("..." if len(initial) > 500 else ""), title="Model response"
                )
            )

        elif response or response_file:
            text = _read_input(response, response_file)
            task_text = task or "You were asked a question."
            engine.inject_exchange(task=task_text, response=text)
            console.print(f"[bold]Model:[/bold] [cyan]{model}[/cyan]")
            console.print("[bold]Diagnosing provided response[/bold]\n")

        elif task:
            console.print(f"[bold]Model:[/bold] [cyan]{model}[/cyan]\n")
            with console.status("Sending task to model..."):
                initial = engine.setup_scenario(task)
            console.print(
                Panel(
                    initial[:500] + ("..." if len(initial) > 500 else ""), title="Model response"
                )
            )

        else:
            console.print("[red]Provide --scenario, --task, or --response[/red]")
            raise typer.Exit(1)

        sequence = get_pure_ratchet_sequence() if pure else get_ratchet_sequence()

    # Initialize session state for persistence
    sess = None
    if session and not resume:
        full_seq = get_pure_ratchet_sequence() if pure else get_ratchet_sequence()
        sess = SessionState.create(
            provider_name=engine.provider.name,
            model=engine.model,
            sequence=full_seq,
            scenario_name=scenario_name,
            task=task_text if "task_text" in dir() else (task or ""),
            system_prompt=scenario_system_prompt,
        )
        if engine.initial_response:
            sess.initial_response = engine.initial_response
            sess.messages = engine.messages.copy()
    elif resume:
        sess = SessionState.load(resume)

    console.print(f"\n[bold]Running {len(sequence)}-step diagnostic ratchet[/bold]\n")

    ab_result = None

    def on_step(step):
        labels = count_labels(step.response)
        label_str = (
            f"[green]{labels['observed']}O[/green] "
            f"[yellow]{labels['inferred']}I[/yellow]"
        )
        console.print(f"  [green]✓[/green] {step.prompt_id} — {step.prompt_name}  {label_str}")
        # Save session state after each step
        if sess is not None:
            sess.completed_steps.append({
                "prompt_id": step.prompt_id,
                "prompt_name": step.prompt_name,
                "prompt_text": step.prompt_text,
                "response": step.response,
            })
            sess.messages = engine.messages.copy()
            sess.save(session or resume)

    if behavioral:
        # Split sequence: run up to 2.5, then A/B test, then the rest
        from robopsych.crosscheck import run_ab_test

        split_at = None
        for i, pid in enumerate(sequence):
            if pid == "2.5":
                split_at = i + 1
                break

        if split_at:
            with console.status("Running diagnostics (pre-crosscheck)..."):
                engine.run_sequence(sequence[:split_at], on_step=on_step)

            task_text = (
                task_text if "task_text" in dir() else (task or "You were asked a question.")
            )
            judge_provider, judge_model = _build_judge(judge)
            console.print("\n  [bold yellow]⚡ Running behavioral A/B cross-check...[/bold yellow]")
            if judge:
                console.print(f"  [dim]Judge: {judge}[/dim]")
            with console.status("Running A/B test..."):
                ab_result = run_ab_test(
                    engine.provider, engine.model, task_text,
                    system_prompt=scenario_system_prompt,
                    judge_provider=judge_provider, judge_model=judge_model,
                )
            changed = "[red]yes[/red]" if ab_result.substance_changed else "[green]no[/green]"
            console.print(f"  [green]✓[/green] A/B cross-check — substance changed: {changed}")
            if ab_result.presentation_shift_score > 0.0:
                shift_color = (
                    "red" if ab_result.presentation_shift_score > 0.3 else "yellow"
                )
                console.print(
                    f"  [dim]presentation shift: [{shift_color}]"
                    f"{ab_result.presentation_shift_score:.2f}[/{shift_color}][/dim]"
                )
            if ab_result.parse_error:
                console.print(
                    f"  [yellow]⚠ judge JSON parse failed "
                    f"({ab_result.parse_error}); using heuristic fallback[/yellow]"
                )
            console.print()

            with console.status("Running diagnostics (post-crosscheck)..."):
                engine.run_sequence(sequence[split_at:], on_step=on_step)
        else:
            with console.status("Running diagnostics..."):
                engine.run_sequence(sequence, on_step=on_step)
    else:
        with console.status("Running diagnostics..."):
            engine.run_sequence(sequence, on_step=on_step)

    # Coherence analysis — LLM judge if requested, else regex fallback.
    if coherence_judge:
        from robopsych.coherence_llm import JudgeRetryPolicy, analyze_coherence_auto

        judge_provider = create_provider(
            coherence_judge,
            api_key=api_key,
            base_url=base_url,
            allow_insecure_base_url=allow_insecure_base_url,
        )
        coherence_checkpoint_path = coherence_checkpoint
        if coherence_checkpoint_path is None and (session or resume):
            coherence_checkpoint_path = Path(f"{session or resume}.coherence.json")
        with console.status(f"Analyzing coherence with judge [cyan]{coherence_judge}[/cyan]..."):
            coherence_report = analyze_coherence_auto(
                engine,
                judge_provider=judge_provider,
                judge_model=coherence_judge,
                retry_policy=JudgeRetryPolicy(max_attempts=coherence_retry_attempts),
                checkpoint_path=coherence_checkpoint_path,
            )
        judge_stats = getattr(coherence_report, "judge_stats", {})
        if judge_stats and (
            judge_stats.get("retried", 0)
            or judge_stats.get("failed", 0)
            or judge_stats.get("checkpoint_hits", 0)
        ):
            console.print(
                f"[dim]Judge calls: {judge_stats.get('scored', 0)}/"
                f"{judge_stats.get('steps_total', 0)} scored, "
                f"{judge_stats.get('retried', 0)} retries, "
                f"{judge_stats.get('failed', 0)} failed, "
                f"{judge_stats.get('checkpoint_hits', 0)} checkpoint hits[/dim]"
            )
        if coherence_report.judge_errors:
            console.print(
                f"[yellow]⚠ {len(coherence_report.judge_errors)} judge errors — "
                f"score may be degraded[/yellow]"
            )
    else:
        from robopsych.coherence_llm import analyze_coherence_auto

        _warn_regex_coherence_if_applicable(len(engine.steps), console)
        coherence_report = analyze_coherence_auto(engine)

    color = {
        "high-continuity": "green",
        "partial": "yellow",
        "fragmented": "red",
        # Legacy aliases for reports generated before v5.1
        "genuine": "green",
        "mixed": "yellow",
        "performed": "red",
    }.get(coherence_report.assessment, "white")
    console.print(
        f"\n[bold]Coherence:[/bold] {coherence_report.consistency_score:.2f} "
        f"([{color}]{coherence_report.assessment}[/{color}]) — "
        f"{coherence_report.backward_references} backward refs, "
        f"{len(coherence_report.contradictions)} contradictions, "
        f"{coherence_report.fresh_narratives} fresh narratives"
    )

    # Scoring
    from robopsych.scoring import score_diagnosis

    diag_score = score_diagnosis(engine, coherence=coherence_report, ab_result=ab_result)
    console.print(
        f"[bold]Dominant hypothesis:[/bold] {diag_score.support_profile.dominant} "
        f"(score {diag_score.overall_confidence:.2f}) — "
        f"Layer: {diag_score.layer_separation:.2f}, "
        f"Coherence: {diag_score.ratchet_coherence:.2f}, "
        f"Behavioral: {diag_score.behavioral_evidence:.2f}"
    )

    _print_ratchet_dashboard(engine, console)

    if output:
        if format == "json":
            report = generate_json_report(
                engine, scenario_name, coherence=coherence_report, score=diag_score,
                ab_result=ab_result,
            )
        else:
            report = generate_report(
                engine, scenario_name, coherence=coherence_report, score=diag_score,
                ab_result=ab_result,
            )
        private_write_text(output, report)
        console.print(f"\n[green]Report saved to {output}[/green]")
    elif format == "json":
        console.print(generate_json_report(
            engine, scenario_name, coherence=coherence_report, score=diag_score,
            ab_result=ab_result,
        ))
    else:
        console.print()
        report = generate_report(
            engine, scenario_name, coherence=coherence_report, score=diag_score,
            ab_result=ab_result,
        )
        console.print(Markdown(report))

    if sess is not None and (session or resume):
        console.print(f"\n[dim]Session saved to {session or resume}[/dim]")


@app.command()
def compare(
    prompt_id: Annotated[str, typer.Argument(help="Prompt ID to run")],
    models: Annotated[str, typer.Option(help="Comma-separated model list")],
    response: Annotated[Optional[str], typer.Option(help="Response text to diagnose")] = None,
    response_file: Annotated[Optional[Path], typer.Option(help="File with response")] = None,
    task: Annotated[str, typer.Option(help="Original task")] = "You were asked a question.",
    api_key: Annotated[Optional[str], typer.Option(help="API key")] = None,
    base_url: Annotated[Optional[str], typer.Option(help="Custom API base URL")] = None,
    allow_insecure_base_url: Annotated[
        bool,
        typer.Option(
            "--allow-insecure-base-url",
            help=(
                "Allow HTTP, localhost, or private-network --base-url endpoints. "
                "API keys will be sent to that endpoint."
            ),
        ),
    ] = False,
    output: Annotated[Optional[Path], typer.Option(help="Save report to file")] = None,
    format: Annotated[
        str, typer.Option("--format", help="Output format: markdown or json")
    ] = "markdown",
    var: Annotated[Optional[list[str]], typer.Option(help="Variable as key=value")] = None,
):
    """Run the same diagnostic prompt across multiple models and compare."""
    text = _read_input(response, response_file)
    model_list = [m.strip() for m in models.split(",")]

    variables = {}
    if var:
        for v in var:
            k, _, val = v.partition("=")
            variables[k] = val

    prompt = get_prompt(prompt_id)
    for v in prompt.get("variables", []):
        if v.get("required") and v["name"] not in variables:
            variables[v["name"]] = typer.prompt(f"  {v['name']} ({v['description']})")

    console.print(f"[bold]Comparing {prompt_id} — {prompt['name']}[/bold]")
    console.print(f"[bold]Models:[/bold] {', '.join(model_list)}\n")

    results = []
    for m in model_list:
        engine = _build_engine(m, api_key, base_url, allow_insecure_base_url)
        engine.inject_exchange(task=task, response=text)
        console.print(f"  Running on [cyan]{m}[/cyan]...", end="")
        step = engine.run_diagnostic(prompt_id, variables=variables or None)
        console.print(" [green]✓[/green]")
        results.append((m, step))

    console.print()

    lines = [
        f"# Comparative Diagnosis — {prompt_id} {prompt['name']}",
        "",
    ]
    for m, step in results:
        labels = count_labels(step.response)
        lines.extend(
            [
                f"## {m}",
                "",
                f"> 🟢 Observed: {labels['observed']} · "
                f"🟡 Inferred: {labels['inferred']}",
                "",
                step.response,
                "",
                "---",
                "",
            ]
        )

    report_text = "\n".join(lines)

    if output:
        private_write_text(output, report_text)
        console.print(f"[green]Report saved to {output}[/green]")
    elif format == "json":
        import json

        data = {
            "prompt_id": prompt_id,
            "prompt_name": prompt["name"],
            "models": [
                {
                    "model": m,
                    "response": step.response,
                    "labels": count_labels(step.response),
                }
                for m, step in results
            ],
        }
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        console.print(Markdown(report_text))


@app.command()
def score(
    report_file: Annotated[Path, typer.Argument(help="JSON report file to score")],
):
    """Compute a quantitative diagnostic score from a JSON report."""
    import json as json_mod

    from robopsych.coherence import CoherenceReport, analyze_coherence
    from robopsych.engine import DiagnosticStep
    from robopsych.scoring import score_diagnosis

    try:
        data = json_mod.loads(report_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {report_file}")
        raise typer.Exit(code=1)
    except json_mod.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON in {report_file}: {e}")
        raise typer.Exit(code=1)

    if "steps" not in data:
        console.print(
            f"[red]Error:[/red] {report_file} is not a valid robopsych report "
            "(missing 'steps')"
        )
        raise typer.Exit(code=1)

    engine = DiagnosticEngine.__new__(DiagnosticEngine)
    engine.steps = [
        DiagnosticStep(
            prompt_id=s["prompt_id"],
            prompt_name=s["prompt_name"],
            prompt_text=s.get("prompt_text", ""),
            response=s["response"],
        )
        for s in data["steps"]
    ]
    engine.model = data.get("model", "unknown")
    engine.messages = []
    engine.initial_response = data.get("initial_response")
    engine.provider = type("_", (), {"name": data.get("provider", "unknown")})()

    coherence_data = data.get("coherence")
    coh = None
    if coherence_data:
        coh = CoherenceReport(
            consistency_score=coherence_data["consistency_score"],
            assessment=coherence_data["assessment"],
            backward_references=coherence_data.get("backward_references", 0),
            contradictions=coherence_data.get("contradictions", []),
            fresh_narratives=coherence_data.get("fresh_narratives", 0),
        )
    else:
        coh = analyze_coherence(engine)

    result = score_diagnosis(engine, coherence=coh)

    profile = result.support_profile
    hyp_lines = "\n".join(
        f"[bold]{h.name}:[/bold] {h.score:.2f}"
        for h in profile.hypotheses
    )
    console.print(
        Panel(
            f"[bold]Dominant hypothesis:[/bold] {profile.dominant}\n"
            f"[bold]Multi-causal:[/bold] {'yes' if profile.multi_causal else 'no'} · "
            f"[bold]Evidence thin:[/bold] {'yes' if profile.evidence_thin else 'no'}\n\n"
            f"{hyp_lines}\n\n"
            f"[bold]Layer separation:[/bold] {result.layer_separation:.2f}\n"
            f"[bold]Ratchet coherence:[/bold] {result.ratchet_coherence:.2f}\n"
            f"[bold]Behavioral evidence:[/bold] {result.behavioral_evidence:.2f}\n"
            f"[bold]Substance stability:[/bold] {result.substance_stability:.2f}\n\n"
            f"[bold]Labels:[/bold] "
            f"🟢 Observed: {result.label_distribution['observed']} · "
            f"🟡 Inferred: {result.label_distribution['inferred']}\n\n"
            f"> {result.summary}",
            title="Diagnostic Score",
            border_style="cyan",
        )
    )


@app.command()
def coherence(
    report_file: Annotated[Path, typer.Argument(help="JSON report file to analyze")],
):
    """Analyze coherence of a completed ratchet diagnosis from a JSON report."""
    import json as json_mod

    from robopsych.coherence import analyze_coherence
    from robopsych.engine import DiagnosticStep

    try:
        data = json_mod.loads(report_file.read_text(encoding="utf-8"))
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] File not found: {report_file}")
        raise typer.Exit(code=1)
    except json_mod.JSONDecodeError as e:
        console.print(f"[red]Error:[/red] Invalid JSON in {report_file}: {e}")
        raise typer.Exit(code=1)

    if "steps" not in data:
        console.print(
            f"[red]Error:[/red] {report_file} is not a valid robopsych report "
            "(missing 'steps')"
        )
        raise typer.Exit(code=1)
    _ = None  # provider not needed for analysis

    # Reconstruct engine with steps only (no provider needed)
    engine = DiagnosticEngine.__new__(DiagnosticEngine)
    engine.steps = [
        DiagnosticStep(
            prompt_id=s["prompt_id"],
            prompt_name=s["prompt_name"],
            prompt_text=s.get("prompt_text", ""),
            response=s["response"],
        )
        for s in data["steps"]
    ]
    engine.model = data.get("model", "unknown")
    engine.messages = []
    engine.initial_response = data.get("initial_response")
    engine.provider = type("_", (), {"name": data.get("provider", "unknown")})()

    report = analyze_coherence(engine)
    _warn_regex_coherence_if_applicable(len(engine.steps), console)
    color = {
        "high-continuity": "green",
        "partial": "yellow",
        "fragmented": "red",
        # Legacy aliases for reports generated before v5.1
        "genuine": "green",
        "mixed": "yellow",
        "performed": "red",
    }.get(report.assessment, "white")

    console.print(
        Panel(
            f"[bold]Score:[/bold] {report.consistency_score:.2f} "
            f"([{color}]{report.assessment}[/{color}])\n"
            f"[bold]Backward references:[/bold] {report.backward_references}\n"
            f"[bold]Contradictions:[/bold] {len(report.contradictions)}\n"
            f"[bold]Fresh narratives:[/bold] {report.fresh_narratives}\n\n"
            f"{report.details}",
            title="Coherence Analysis",
            border_style="cyan",
        )
    )

    if report.contradictions:
        console.print("\n[bold]Contradictions found:[/bold]")
        for c in report.contradictions:
            console.print(f"  [red]•[/red] {c}")


@app.command()
def crosscheck(
    task: Annotated[str, typer.Option(help="Task to cross-check")],
    model: Annotated[str, typer.Option(help="Model to test")] = "claude-sonnet-4-6",
    api_key: Annotated[Optional[str], typer.Option(help="API key")] = None,
    base_url: Annotated[Optional[str], typer.Option(help="Custom API base URL")] = None,
    allow_insecure_base_url: Annotated[
        bool,
        typer.Option(
            "--allow-insecure-base-url",
            help=(
                "Allow HTTP, localhost, or private-network --base-url endpoints. "
                "API keys will be sent to that endpoint."
            ),
        ),
    ] = False,
    output: Annotated[Optional[Path], typer.Option(help="Save report to file")] = None,
    format: Annotated[
        str, typer.Option("--format", help="Output format: markdown or json")
    ] = "markdown",
    judge: Annotated[
        Optional[str], typer.Option("--judge", help="External evaluator model for comparison")
    ] = None,
):
    """Run a behavioral A/B cross-check on a task."""
    from robopsych.crosscheck import run_ab_test

    provider = create_provider(
        model,
        api_key=api_key,
        base_url=base_url,
        allow_insecure_base_url=allow_insecure_base_url,
    )
    judge_provider, judge_model = _build_judge(judge)

    console.print(f"[bold]Behavioral A/B cross-check[/bold] on [cyan]{model}[/cyan]")
    if judge:
        console.print(f"[bold]Judge:[/bold] [cyan]{judge}[/cyan]")
    console.print(f"\n[bold]Task:[/bold] {task}\n")

    with console.status("Running A/B test..."):
        result = run_ab_test(
            provider, model, task,
            judge_provider=judge_provider, judge_model=judge_model,
        )

    changed = "[red]Yes[/red]" if result.substance_changed else "[green]No[/green]"
    console.print(f"[bold]Inverted task:[/bold] {result.inverted_task}\n")
    console.print(f"[bold]Substance changed:[/bold] {changed}")
    console.print(
        f"[bold]Presentation shift:[/bold] {result.presentation_shift_score:.2f} "
        f"(severity={result.severity_labels_shifted}, "
        f"urgency={result.urgency_language_shifted}, "
        f"hedging_delta={result.hedging_delta:+.2f})"
    )
    if result.omissions_added:
        console.print(f"[bold]Omissions added ({len(result.omissions_added)}):[/bold]")
        for item in result.omissions_added:
            console.print(f"  • {item}")
    if result.parse_error:
        console.print(
            f"[yellow]⚠ judge JSON parse failed ({result.parse_error}); "
            f"using heuristic fallback[/yellow]"
        )
    console.print("\n[bold]Comparison:[/bold]\n")
    console.print(Markdown(result.comparison))

    if output:
        import json as json_mod

        if format == "json":
            data = {
                "original_task": result.original_task,
                "inverted_task": result.inverted_task,
                "original_response": result.original_response,
                "inverted_response": result.inverted_response,
                "comparison": result.comparison,
                "substance_changed": result.substance_changed,
                "severity_labels_shifted": result.severity_labels_shifted,
                "urgency_language_shifted": result.urgency_language_shifted,
                "hedging_delta": result.hedging_delta,
                "omissions_added": result.omissions_added,
                "presentation_shift_score": result.presentation_shift_score,
                "parse_error": result.parse_error,
            }
            private_write_text(output, json_mod.dumps(data, indent=2, ensure_ascii=False))
        else:
            omissions_block = ""
            if result.omissions_added:
                omissions_block = "\n".join(
                    ["**Omissions added:**", ""]
                    + [f"- {item}" for item in result.omissions_added]
                    + [""]
                )
            lines = [
                "# Behavioral A/B Cross-Check",
                "",
                f"**Model:** `{model}`",
                "",
                f"**Original task:** {result.original_task}",
                "",
                f"**Inverted task:** {result.inverted_task}",
                "",
                f"**Substance changed:** {'Yes' if result.substance_changed else 'No'}",
                f"**Presentation shift score:** {result.presentation_shift_score:.2f}",
                f"**Severity labels shifted:** "
                f"{'Yes' if result.severity_labels_shifted else 'No'}",
                f"**Urgency language shifted:** "
                f"{'Yes' if result.urgency_language_shifted else 'No'}",
                f"**Hedging delta (A→B):** {result.hedging_delta:+.2f}",
                "",
                omissions_block,
                "## Original Response",
                "",
                result.original_response,
                "",
                "## Inverted Response",
                "",
                result.inverted_response,
                "",
                "## Comparison",
                "",
                result.comparison,
            ]
            private_write_text(output, "\n".join(lines))
        console.print(f"\n[green]Report saved to {output}[/green]")


@app.command()
def guided(
    model: Annotated[str, typer.Option(help="Model to diagnose")] = "claude-sonnet-4-6",
    response: Annotated[Optional[str], typer.Option(help="Response to diagnose")] = None,
    response_file: Annotated[Optional[Path], typer.Option(help="File with response")] = None,
    task: Annotated[str, typer.Option(help="Original task")] = "You were asked a question.",
    api_key: Annotated[Optional[str], typer.Option(help="API key")] = None,
    base_url: Annotated[Optional[str], typer.Option(help="Custom API base URL")] = None,
    allow_insecure_base_url: Annotated[
        bool,
        typer.Option(
            "--allow-insecure-base-url",
            help=(
                "Allow HTTP, localhost, or private-network --base-url endpoints. "
                "API keys will be sent to that endpoint."
            ),
        ),
    ] = False,
    verbose: Annotated[bool, typer.Option(help="Show extra context per observation")] = False,
):
    """Interactive guided diagnosis using the decision flowchart."""
    text = _read_input(response, response_file)
    engine = _build_engine(model, api_key, base_url, allow_insecure_base_url)
    engine.inject_exchange(task=task, response=text)

    flowchart = get_flowchart()
    observations = flowchart["observations"]

    console.print("[bold]What did you observe?[/bold]\n")
    for i, obs in enumerate(observations, 1):
        desc = obs.get("description", "")
        if verbose and desc:
            console.print(f"  [bold]{i}.[/bold] {obs['label']}")
            console.print(f"     [dim]{desc}[/dim]")
            console.print(f"     Path: {' → '.join(obs['path'])}\n")
        elif desc:
            console.print(f"  [bold]{i}.[/bold] {obs['label']} [dim]— {desc}[/dim]")
        else:
            console.print(f"  [bold]{i}.[/bold] {obs['label']}")

    choice = typer.prompt("\nSelect observation (number)")
    try:
        selected = observations[int(choice) - 1]
    except (ValueError, IndexError):
        console.print("[red]Invalid choice.[/red]")
        raise typer.Exit(1)

    path = selected["path"]
    console.print(f"\n[bold]Diagnosis path:[/bold] {' → '.join(path)}\n")

    for pid in path:
        prompt = get_prompt(pid)
        console.print(f"[bold]Running {pid} — {prompt['name']}[/bold]")

        variables = _collect_variables(pid)

        with console.status("Diagnosing..."):
            step = engine.run_diagnostic(pid, variables=variables or None)

        console.print(Markdown(step.response))
        _print_step_summary(step, console)
        console.print()

        if pid != path[-1]:
            proceed = typer.confirm("Continue to next prompt?", default=True)
            if not proceed:
                break

    console.print("[bold green]Diagnosis complete.[/bold green]")


if __name__ == "__main__":
    app()
