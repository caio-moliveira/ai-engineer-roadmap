from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langfuse.langchain import CallbackHandler
from tavily import TavilyClient
from langchain.agents.middleware import ModelFallbackMiddleware

load_dotenv()

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
langfuse_handler = CallbackHandler()

_SKILLS_SCRIPTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills", "powerpoint", "scripts")


@tool
def tavily_search(query: str) -> str:
    """Search the web for information using Tavily."""
    results = tavily_client.search(query, max_results=5)
    return json.dumps(results, ensure_ascii=False)


@tool
def build_pptx(spec_file: str, output_file: str) -> str:
    """Generate a .pptx file from a presentation spec JSON.
    Brand colors must be embedded in spec_file under the 'brand' key.

    Args:
        spec_file: Absolute path to presentation_spec.json
        output_file: Absolute path for the output .pptx file
    """
    if _SKILLS_SCRIPTS not in sys.path:
        sys.path.insert(0, _SKILLS_SCRIPTS)
    from generate_from_spec import generate_ppt_from_spec
    return generate_ppt_from_spec(spec_file, output_file)

CURRENT_DIR   = os.path.dirname(os.path.abspath(__file__))
REPO_PATH     = r"E:\job-work\ai-engineer-roadmap"
CV_DIR        = os.path.join(CURRENT_DIR, "docs")
ARTIFACTS_DIR = os.path.join(CURRENT_DIR, "artifacts")

# Shared rate-limited model — all agents go through the same token bucket.
# 0.5 req/s = 30 req/min. At ~3 000 tokens/req → ~90 k TPM (well under the 200 k limit).
# _rate_limiter = InMemoryRateLimiter(
#     requests_per_second=0.5,
#     check_every_n_seconds=0.05,
#     max_bucket_size=2,
# )
# _model = init_chat_model("openai:gpt-5.4-nano", rate_limiter=_rate_limiter)


# ── Subagent definitions ─────────────────────────────────────────────────────

REPO_SCANNER = {
    "name": "repo-scanner",
    "description": "Catalog the AI engineer roadmap repository structure and locate all README files.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the Repo Scanner Agent. Your only job: catalog README files — do NOT interpret content.

IMPORTANT: Only scan the exact directories listed below. Never glob the full /repo/ tree.
Never read inside .venv, node_modules, __pycache__, or any directory whose name starts with a dot.

Run `glob` with pattern "**/README.md" on each of these directories individually:
  /repo/01-fundamentals/
  /repo/02-rag/
  /repo/03-ai-agents/
  /repo/04-infra-ocr-models/
  /repo/05-fine-tuning/

Also include /repo/README.md directly (root README).

Collect all found paths into a list. Write ONE artifact with `write_file`:

/artifacts/repo_catalog.json:
{
  "readme_paths": ["/repo/README.md", "/repo/01-fundamentals/README.md", ...],
  "stats": {"total_readmes": N}
}

Return: {"status":"success","artifacts_generated":["/artifacts/repo_catalog.json"],"errors":[]}
""",
    "tools": [],
}

BRAND_RESEARCHER = {
    "name": "brand-researcher",
    "description": "Search the web for Jornada de Dados brand identity and produce a brand guide.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the Brand Research Agent.

Run these searches with `tavily_search`:
1. "Jornada de Dados identidade visual cores logo"
2. "Jornada de Dados Luciano Galvão posicionamento marca engenheiro IA"

Extract: primary colour, accent colour, text colour (hex), brand voice.
If search yields no hex values, use defaults: primary #1B2A4A, accent #00C2CB, text #FFFFFF.

Write ONE artifact with `write_file`:

/artifacts/brand_guide.md — use this exact structure:
```
# Brand Guide: Jornada de Dados

## Pesquisa
<2-3 paragraphs summarising findings>

## Estilo Visual
```json
{"primary_color":"#hex","accent_color":"#hex","text_color":"#hex","brand_voice":"<one sentence>"}
```
```

Return: {"status":"success","artifacts_generated":["/artifacts/brand_guide.md"],"errors":[],"warnings":[]}
""",
    "tools": [tavily_search],
}

CV_READER = {
    "name": "cv-reader",
    "description": "Read the candidate CV and extract professional info for the About Me slide.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the CV Reader Agent.

1. Call `read_file` with path="/docs/CaioMachado-AI-p.md".
2. Extract:
   - Full name and current role/title
   - 3–4 key professional experiences or positions
   - Main technical skills and specialties
   - A concise one-sentence positioning statement
   - Why this person teaches this AI engineering course

3. Write ONE artifact with `write_file`:

/artifacts/about_me.md — use this exact structure:
```
# Sobre Mim: <Full Name>
**Cargo**: <current role>
**Bio**: <one-sentence positioning>

## Destaques
- <experience 1>
- <experience 2>
- <key technical skills>
- <community / teaching highlight>

## Mensagem Principal
<why I teach this course — 1-2 sentences>
```

Return: {"status":"success","artifacts_generated":["/artifacts/about_me.md"],"errors":[]}
""",
    "tools": [],
}

README_STRUCTURER = {
    "name": "readme-structurer",
    "description": "Read course READMEs and produce an ordered slide outline.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the README Structuring Agent.

CRITICAL: process one block at a time — never read all READMEs simultaneously.

1. `read_file` → /artifacts/repo_catalog.json  (get readme_paths)
2. `read_file` → /artifacts/about_me.md
3. `read_file` → /artifacts/brand_guide.md
4. For each README path (sequentially): `read_file` and extract theme, key concepts, main technologies.

Build the slide outline following this fixed order:
  - Slide 1  : type "capa"        — course title + subtitle
  - Slide 2  : type "sobre_mim"   — instructor (pull from about_me.md)
  - Slide 3  : type "course_intro"— what the course covers
  - Slides 4-5 per block: type "bloco_intro" (block overview) + type "content" (list of lessons)
    Blocks: 01-llm-fundamentals, 02-rag, 03-ai-agents, 04-ocr, 05-fine-tuning
  - Last slide: type "conclusao"  — next steps / call to action

Rules:
  - One slide per block introduction, one slide per block lessons. DO NOT create one slide per lesson.
  - The slide for block lessons should be a list of all lessons of that block.

Write ONE artifact with `write_file`:

/artifacts/slide_outline.json — array of slide objects:
[
  {"id":1,"type":"capa","title":"...","subtitle":"..."},
  {"id":2,"type":"sobre_mim","title":"Sobre Mim","source":"/artifacts/about_me.md"},
  {"id":3,"type":"course_intro","title":"...","bullets":["..."]},
  {"id":4,"type":"bloco_intro","title":"Bloco 1: ...","objective":"...","bullets":["..."],"source_readmes":["..."]},
  {"id":5,"type":"content","title":"Aulas — Bloco 1","bullets":["..."],"source_readmes":["..."]},
  ...
  {"id":N,"type":"conclusao","title":"...","bullets":["..."],"main_message":"..."}
]

Return: {"status":"success","artifacts_generated":["/artifacts/slide_outline.json"],"errors":[]}
""",
    "tools": [],
}

NARRATIVE_BUILDER = {
    "name": "narrative-builder",
    "description": "Build the final presentation spec with full slide content and brand colours embedded.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the Narrative Builder Agent.

1. `read_file` → /artifacts/slide_outline.json
2. `read_file` → /artifacts/about_me.md
3. `read_file` → /artifacts/brand_guide.md
   — parse the JSON block inside the "## Estilo Visual" section to extract brand colours.

4. For each slide in the outline, write polished final content:
   - capa: compelling subtitle referencing Jornada de Dados
   - sobre_mim: fill from about_me.md (bio, bullets, main_message)
   - bloco_intro: add a hook sentence connecting to the previous block's outcome
   - conclusao: 3–5 actionable takeaways spanning all blocks
   - The slides with the block lessons should be a list of all lessons of that block.

5. Write ONE artifact with `write_file`:

/artifacts/presentation_spec.json:
{
  "title": "Jornada de Dados — Engenheiro de IA",
  "subtitle": "...",
  "author": "<name from about_me.md>",
  "course": "Jornada de Dados — Engenheiro de IA",
  "aspect_ratio": "16:9",
  "brand": {
    "primary_color": "#hex",
    "accent_color": "#hex",
    "text_color": "#hex"
  },
  "slides": [ <full slide objects with id, type, title, subtitle?, bio?, bullets, objective?, main_message> ]
}

CRITICAL: For "sobre_mim" slides, "bio" MUST be a plain string (one sentence from the **Bio** line in about_me.md). NEVER set "bio" to a dict or nested object.

Return: {"status":"success","artifacts_generated":["/artifacts/presentation_spec.json"],"errors":[]}
""",
    "tools": [],
}

PPT_BUILDER = {
    "name": "ppt-builder",
    "description": "Render presentation_spec.json into a .pptx file using the build_pptx tool.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": f"""You are the PowerPoint Builder Agent. Render content only — do NOT modify it.

1. `read_file` → /artifacts/presentation_spec.json  (confirm it exists and has a "slides" array)
2. Call the `build_pptx` tool with:
   - spec_file   = "{ARTIFACTS_DIR}/presentation_spec.json"
   - output_file = "{ARTIFACTS_DIR}/presentation_final.pptx"
3. The tool returns a string starting with "Successfully generated" on success or "Error:" on failure.
   - On error: report failure immediately with the error message.

Return: {{"status":"success","summary":"Generated presentation_final.pptx","artifacts_generated":["/artifacts/presentation_final.pptx"],"errors":[]}}
""",
    "tools": [build_pptx],
}


# ── Supervisor ───────────────────────────────────────────────────────────────

_store        = InMemoryStore()
_checkpointer = MemorySaver()

supervisor = create_deep_agent(
    model="openai:gpt-5.4-nano",
    system_prompt=f"""You are the Presentation Pipeline Supervisor.

Goal: produce a PowerPoint for "Jornada de Dados — Engenheiro de IA".
Inputs: Repository at {REPO_PATH} | CV at {CV_DIR} | Brand via web search

STRICTLY follow this phase order. Run ONE task at a time and wait for "status":"success" before proceeding.

Phase 1 — gather raw inputs (sequentially):
  task(agent="repo-scanner",     instruction="Scan /repo/ and write /artifacts/repo_catalog.json.")
  task(agent="brand-researcher", instruction="Research Jornada de Dados brand and write /artifacts/brand_guide.md.")
  task(agent="cv-reader",        instruction="Read /docs/CaioMachado-AI-p.md and write /artifacts/about_me.md.")

Phase 2 — structure slides:
  task(agent="readme-structurer", instruction="Read /artifacts/repo_catalog.json, /artifacts/about_me.md and /artifacts/brand_guide.md, then read each README and write /artifacts/slide_outline.json.")

Phase 3 — write final content:
  task(agent="narrative-builder", instruction="Read /artifacts/slide_outline.json, /artifacts/about_me.md and /artifacts/brand_guide.md, then write /artifacts/presentation_spec.json with full slide content and brand colours embedded.")

Phase 4 — render PPTX:
  task(agent="ppt-builder", instruction="Read /artifacts/presentation_spec.json and call build_pptx to generate /artifacts/presentation_final.pptx.")

On error: retry once with a corrected instruction. Report failure if it persists.
On full pipeline success, report the output path of presentation_final.pptx.
""",
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            "gpt-5.1-mini",
            "gpt-4.1-mini",
        ),
    ],
    subagents=[
        REPO_SCANNER,
        BRAND_RESEARCHER,
        CV_READER,
        README_STRUCTURER,
        NARRATIVE_BUILDER,
        PPT_BUILDER,
    ],
    backend=CompositeBackend(
        default=FilesystemBackend(root_dir=CURRENT_DIR, virtual_mode=True),
        routes={
            "/docs/": FilesystemBackend(root_dir=CV_DIR, virtual_mode=True),
            "/repo/": FilesystemBackend(root_dir=REPO_PATH, virtual_mode=True),
        },
    ),
    checkpointer=_checkpointer,
    store=_store,
)


# ── Streaming display ────────────────────────────────────────────────────────

# ANSI colours
_C = {
    "reset":     "\033[0m",
    "bold":      "\033[1m",
    "supervisor":"\033[1;35m",   # bold magenta
    "subagent":  "\033[1;36m",   # bold cyan
    "tool_call": "\033[33m",     # yellow
    "tool_result":"\033[32m",    # green
    "dim":       "\033[2m",      # dim
}

_AGENT_NAMES = {
    "repo-scanner", "brand-researcher", "cv-reader",
    "readme-structurer", "narrative-builder", "ppt-builder",
}


def _label(checkpoint_ns: str, _node: str) -> str:
    """Derive a human-readable [agent/node] label from LangGraph metadata."""
    # checkpoint_ns looks like "repo-scanner:abc123|model" for subagents
    for name in _AGENT_NAMES:
        if name in checkpoint_ns:
            return name
    return "supervisor"


def stream_pipeline(input_messages: list, config: dict) -> None:
    from langchain_core.messages import AIMessageChunk, ToolMessage

    current_label = None

    for chunk, metadata in supervisor.stream(
        {"messages": input_messages},
        config=config,
        stream_mode="messages",
    ):
        ns   = metadata.get("langgraph_checkpoint_ns", "")
        node = metadata.get("langgraph_node", "")
        label = _label(ns, node)

        # ── Label header when agent changes ──────────────────────────
        if label != current_label:
            print()  # blank line between agents
            color = _C["subagent"] if label in _AGENT_NAMES else _C["supervisor"]
            print(f"{color}[{label}]{_C['reset']} ", end="", flush=True)
            current_label = label

        # ── AI message chunks (streamed text + tool calls) ────────────
        if isinstance(chunk, AIMessageChunk):
            # Streamed text
            text = ""
            if isinstance(chunk.content, str):
                text = chunk.content
            elif isinstance(chunk.content, list):
                for part in chunk.content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text += part.get("text", "")
            if text:
                print(text, end="", flush=True)

            # Tool-call name (first chunk that carries the name)
            for tc in chunk.tool_call_chunks or []:
                if tc.get("name"):
                    print(
                        f"\n  {_C['tool_call']}→ {tc['name']}{_C['reset']}",
                        end="", flush=True,
                    )

        # ── Tool results ──────────────────────────────────────────────
        elif isinstance(chunk, ToolMessage):
            preview = str(chunk.content)
            if len(preview) > 500:
                preview = preview[:500] + "…"
            print(
                f"\n  {_C['tool_result']}← {preview}{_C['reset']}",
                flush=True,
            )

    print("\n")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uuid

    thread_id = f"presentation-{uuid.uuid4().hex[:8]}"
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [langfuse_handler],
    }

    print(f"Starting pipeline  (thread: {thread_id})")
    print(f"Artifacts will be written to: {ARTIFACTS_DIR}\n")

    stream_pipeline(
        input_messages=[
            {
                "role": "user",
                "content": (
                    "Generate a complete PowerPoint presentation for the "
                    "'Jornada de Dados — Engenheiro de IA' course. "
                    "Run the full pipeline following the phase order defined in your instructions."
                ),
            }
        ],
        config=config,
    )
