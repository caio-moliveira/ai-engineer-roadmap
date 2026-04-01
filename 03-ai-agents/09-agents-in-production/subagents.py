from __future__ import annotations

import json
import os
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend
from dotenv import load_dotenv
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langfuse.langchain import CallbackHandler
from tavily import TavilyClient



load_dotenv()

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
langfuse_handler = CallbackHandler()

@tool
def tavily_search(query: str) -> str:
    """Search the web for information using Tavily."""
    results = tavily_client.search(query, max_results=5)
    return json.dumps(results, ensure_ascii=False)

CURRENT_DIR   = os.path.dirname(os.path.abspath(__file__))
REPO_PATH     = r"E:\job-work\ai-engineer-roadmap"
CV_DIR        = os.path.join(CURRENT_DIR, "docs")
ARTIFACTS_DIR = os.path.join(CURRENT_DIR, "artifacts")



# ── Subagent definitions ─────────────────────────────────────────────────────

REPO_SCANNER = {
    "name": "repo-scanner",
    "description": "Catalog the AI engineer roadmap repository structure and locate all README files.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": f"""You are the Repo Scanner Agent. Your only job: catalog structure — do NOT interpret content.


1. Use `ls` on "/repo/" to explore the repository structure, then use `glob` or `read_file` to find all README files under "/repo/".
2. Write three artifacts with `write_file`:
   /artifacts/repo_tree_summary.json   — {{tree, course_structure, stats}} from the scan result
   /artifacts/readme_paths.json        — the readme_paths array from the scan result
   /artifacts/course_file_catalog.json — flat list of all files as {{relative_path, absolute_path}}

3. Return exactly:
{{"status":"success","artifacts_generated":["/artifacts/repo_tree_summary.json","/artifacts/readme_paths.json","/artifacts/course_file_catalog.json"],"errors":[]}}

4. Do not edit any README file.
""",
    "tools": [],
}

BRAND_RESEARCHER = {
    "name": "brand-researcher",
    "description": "Search the web for Jornada de Dados brand identity, colours, and positioning.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the Brand Research Agent. Use the tavily_search search tool to gather brand information.

Run these three searches:
1. "Jornada de Dados identidade visual cores logo"
2. "Jornada de Dados plataforma curso engenheiro de dados IA"
3. "Jornada de Dados Luciano Galvão posicionamento marca"

Extract: primary/secondary colours (hex when possible), typography hints, brand voice, logo references.

Write with `write_file`:
  /artifacts/brand_research.md       — markdown with all raw findings
  /artifacts/visual_style_guide.json — {"primary_color":"#hex","secondary_color":"#hex","accent_color":"#hex","text_color":"#hex","heading_font":"...","body_font":"...","brand_voice":"..."}

If search is unavailable, use defaults (primary: #1B2A4A, accent: #00C2CB, text: #FFFFFF) and add a warning.

Return: {"status":"success","artifacts_generated":["/artifacts/brand_research.md","/artifacts/visual_style_guide.json"],"errors":[],"warnings":[]}
""",
    "tools": [tavily_search],
}

CV_READER = {
    "name": "cv-reader",
    "description": "Read the candidate CV and extract professional info for the About Me slide.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the CV Reader Agent.

1. Call `read_file` with path="/docs/CaioMachado-AI-p.docx".
2. From the returned text, extract:
   - Full name and current role/title
   - 3–4 key professional experiences or positions
   - Main technical skills and specialties
   - A concise positioning statement

3. Write with `write_file`:

/artifacts/about_me_slide.json:
{{"id":2,"type":"sobre_mim","title":"Sobre Mim","bio":"<one-sentence positioning>","bullets":["<exp 1>","<exp 2>","<skills>","<community/teaching>"],"main_message":"<why I teach this course>"}}

/artifacts/about_me_bio_short.md — 3–4 line markdown bio.

Return: {{"status":"success","artifacts_generated":["/artifacts/about_me_slide.json","/artifacts/about_me_bio_short.md"],"errors":[]}}
""",
    "tools": [],
}

README_STRUCTURER = {
    "name": "readme-structurer",
    "description": "Parse course README files one block at a time and produce the slide content outline.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the README Content Structuring Agent.

CRITICAL: Load and process ONE block at a time — never read all READMEs simultaneously.

1. `read_file` → /artifacts/readme_paths.json
2. Group entries by top-level block directory (first path segment).
3. For each block (process sequentially):
   a. `read_file` for each README in the block.
   b. Extract: theme, learning objectives, key concepts, main technologies.
4. Map content to the fixed slide order:
   capa → sobre_mim (leave empty) → course_intro → bloco_intro×N → content_slides → conclusao

5. We have 5 blocks of classes: Fundamentals, RAG, AI Agents, OCR and Fine-Tunning. I need a slide for introduction of the block and another slide with the classes for that block.

6. Do not create one slide for each class. Make it concise

Per-slide schema:
{"id": N, "type": "capa|sobre_mim|content|bloco_intro|conclusao", "title": "...", "objective": "...", "bullets": ["..."], "main_message": "...", "source_readmes": ["path"]}

Write with `write_file`:
  /artifacts/block_structure.json       — blocks with module and lesson lists
  /artifacts/course_slides_content.json — ordered array of all slide objects
  /artifacts/slide_bullets_draft.md     — human-readable markdown preview

Return: {"status":"success","artifacts_generated":["/artifacts/block_structure.json","/artifacts/course_slides_content.json","/artifacts/slide_bullets_draft.md"],"errors":[]}
""",
    "tools": [],
}

NARRATIVE_BUILDER = {
    "name": "narrative-builder",
    "description": "Merge course content, brand data, and CV bio into the final master presentation spec.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the Presentation Narrative Agent.

1. Use `read_file` to load all four source artifacts:
   - /artifacts/course_slides_content.json
   - /artifacts/about_me_slide.json
   - /artifacts/brand_research.md
   - /artifacts/visual_style_guide.json

2. Build the final slides array:
   - Insert the about_me slide at position 2 (after capa).
   - Title slide: add a commercial hook referencing Jornada de Dados.
   - Each bloco_intro: reference the previous block's key outcome.
   - Conclusao: 3–5 key takeaways spanning all blocks.

3. Write with `write_file`:
   /artifacts/presentation_master_spec.json:
   {"title":"...","subtitle":"...","author":"...","course":"Jornada de Dados — Engenheiro de IA","brand":{"source":"visual_style_guide.json"},"slides":[...]}

   /artifacts/slide_order_lock.json — ordered list of slide IDs

Return: {"status":"success","artifacts_generated":["/artifacts/presentation_master_spec.json","/artifacts/slide_order_lock.json"],"errors":[]}
""",
    "tools": [],
}

PPT_BUILDER = {
    "name": "ppt-builder",
    "description": "Render the master spec into a .pptx file using the 'powerpoint' skill.",
    "model": "openai:gpt-5.4-nano",
    "system_prompt": """You are the PowerPoint Builder Agent. Render content only — do NOT modify it.

1. Use `read_file` to confirm /artifacts/presentation_master_spec.json exists and is valid JSON.
2. Use `read_file` to confirm /artifacts/visual_style_guide.json exists.
3. Run the following command exactly using `execute_command`:

   python /skills/powerpoint/scripts/generate_from_spec.py \
     --spec-file /artifacts/presentation_master_spec.json \
     --style-file /artifacts/visual_style_guide.json \
     --output-file /artifacts/presentation_final.pptx

4. Check the command output. It must start with "Successfully generated".
   - If it starts with "Error:", report failure with the error message.
5. Use `write_file` to save /artifacts/ppt_generation_report.json:
   {"status":"success","output_file":"/artifacts/presentation_final.pptx","slide_count":<N>,"command_output":"<output from step 3>"}

Return: {"status":"success","summary":"Generated presentation_final.pptx","artifacts_generated":["/artifacts/presentation_final.pptx","/artifacts/ppt_generation_report.json"],"errors":[]}
""",
    "tools": [],
    "skills": ["/skills/powerpoint/"],
}


# ── Supervisor ───────────────────────────────────────────────────────────────

_store        = InMemoryStore()
_checkpointer = MemorySaver()

supervisor = create_deep_agent(
    model="openai:gpt-5.4-nano",
    system_prompt=f"""You are the Presentation Pipeline Supervisor.

Goal: produce a PowerPoint for "Jornada de Dados — Engenheiro de IA" using:
  Repository : {REPO_PATH}
  CV         : {CV_DIR}
  Brand      : web search "Jornada de Dados"

Execution plan — follow this phase order STRICTLY. Run one task at a time and wait for it to complete before starting the next.

Phase 1 (run sequentially — one at a time):
  task(agent="repo-scanner",     instruction="Scan the repository at {REPO_PATH} and write all catalog artifacts.")
  task(agent="brand-researcher", instruction="Research Jornada de Dados brand identity and write brand artifacts.")
  task(agent="cv-reader",        instruction="Read the CV at {CV_DIR} and write the about_me artifacts.")

Phase 2 (after Phase 1):
  task(agent="readme-structurer", instruction="Read /artifacts/readme_paths.json and structure all course README files into slide content.")

Phase 3 (after Phase 2):
  task(agent="narrative-builder", instruction="Merge all artifacts into the final presentation_master_spec.json.")

Phase 4 (after Phase 3):
  task(agent="ppt-builder", instruction="Build the final PPTX from presentation_master_spec.json.")

After each task check the returned status field:
  - "success" → proceed to next phase.
  - "error"   → retry once with a corrected instruction, then report failure if it persists.
  - "warning" → log and continue.

On full pipeline success, report the output path of presentation_final.pptx.
""",
    tools=[],
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


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pprint
    import uuid

    thread_id = f"presentation-{uuid.uuid4().hex[:8]}"
    config = {
        "configurable": {"thread_id": thread_id},
        "callbacks": [langfuse_handler],
    }

    print(f"Starting pipeline  (thread: {thread_id})")
    print(f"Artifacts will be written to: {ARTIFACTS_DIR}\n")

    result = supervisor.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": (
                        "Generate a complete PowerPoint presentation for the "
                        "'Jornada de Dados — Engenheiro de IA' course. "
                        "Run the full pipeline following the phase order defined in your instructions."
                    ),
                }
            ]
        },
        config=config,
    )


    pprint.pprint(result)
