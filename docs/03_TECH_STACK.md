# 03 — Tech Stack (decisions, with rejects)

Pin exact versions in lockfiles at build time (use the latest stable of each; check release notes if a major version moved).

| Layer | Choice | Why | Rejected |
|---|---|---|---|
| Backend | **Python 3.12 + FastAPI + Pydantic v2** | Clean OO, auto OpenAPI (feeds TS types), easy local-LLM/Qdrant clients | Django (too heavy), Node API (splits OO story) |
| Persistence | **SQLite (WAL) + SQLAlchemy 2.0** with triggers | Zero setup; triggers prove append-only; perfect for demo | Postgres (extra setup, no benefit here); Mongo (weak constraints) |
| Migrations | `schema.sql` + `triggers.sql` applied at startup (Alembic optional) | Triggers are first-class and visible in SDD | — |
| Python tooling | `uv`, `ruff`, `mypy`, `pytest`, `hypothesis`, `httpx` | Fast, modern | pip/venv by hand |
| Frontend | **Next.js (App Router) + React + TypeScript strict** | Routing, SSR landing page, great DX | Vite SPA (fine, but landing SEO/SSR nicer in Next), CRA (dead) |
| Styling | **Tailwind CSS v4** with CSS-variable tokens in `styles/tokens.css` | Maps 1:1 from Stitch output and design system | CSS-in-JS, Bootstrap/MUI (look generic) |
| Components | **shadcn/ui primitives (Radix) fully restyled** | Accessible behaviors, zero visual lock-in | Leaving defaults unstyled |
| Motion | **motion (Framer Motion)**; GSAP only for hero parallax if needed | Declarative, reduced-motion aware | Heavy 3D (Three.js) — not worth it |
| Data fetching | TanStack Query + generated OpenAPI types | Caching, optimistic UI | Redux |
| Charts | **Recharts** for analytics; custom SVG for the timeline/orbit | Quick; timeline needs bespoke design | Chart.js canvas (harder to style) |
| Map (P2) | **MapLibre GL JS** with a key-less dark basemap style and synthetic GeoJSON | Ties to IGIS course; no API key | Google Maps (key/billing), Leaflet (less polished dark) |
| Icons | **Lucide** (stroke 1.5) or custom SVG | Consistent | Emoji, FontAwesome |
| Fonts | **Urbanist** (display/UI) + **JetBrains Mono** (IDs, hashes, numbers) via `next/font` | Close to the reference's geometric sans | Inter/Roboto defaults |
| Realtime | **SSE** (`/decisions/{id}/stream`) | Simple one-way live timeline during generation | WebSockets |
| Local LLM runtime | **Ollama** (REST :11434) | One-line install, background pulls, JSON-schema outputs | llama.cpp raw (more setup), LM Studio (GUI-only) |
| Local LLM | **qwen3:4b** (reuse if already pulled) — see doc 04 for tiers | Strong instruction following + JSON at 4B; you already run Qwen 4B | 7–8B on low-RAM laptops |
| Embeddings | **nomic-embed-text** via Ollama (768-d) | Small, fast, local | Gemini embeddings (keep local-first) |
| Vector DB | **Qdrant Cloud** (user's key) via `qdrant-client`; local `:memory:` mode fallback for tests | Provided key; payload filters | Chroma, FAISS |
| Cloud LLM | **Gemini API** (user's key) via `google-genai` | Multilingual (HI/KN), image generation, fallback narrator | Sending anything sensitive (nothing is) |
| Design generation | **Stitch (MCP)** → HTML/Tailwind → converted to React | User's workflow | Hand-built first pass |
| Agent skill | **taste-skill** in `.agent/skills/` | User's requirement for non-generic UI | — |
| E2E / QA | **Playwright** + `@axe-core/playwright` + Lighthouse CI | Matches doc 12 | Cypress |
| Docs diagrams | **Mermaid** (primary) + PlantUML (class/sequence if needed), rendered to PNG via `mmdc` | Version-controlled UML | Draw.io by hand |
| Runtime | `make dev` runs both; optional `docker-compose.yml` for demo day | Reliability | Requiring Docker for dev |

## Environment variables (`.env.example`, values empty)
```
GEMINI_API_KEY=
GEMINI_TEXT_MODEL=            # discover with list_models at runtime; pick a current flash-class model
GEMINI_IMAGE_MODEL=           # discover with list_models; pick current image-generation model
QDRANT_URL=
QDRANT_API_KEY=
OLLAMA_HOST=http://localhost:11434
LLM_MODEL=qwen3:4b
EMBED_MODEL=nomic-embed-text
DATABASE_URL=sqlite:///./irrigatrace.db
DEMO_AUTH=true
```
Model names change quickly: the agent must call the provider's list-models endpoint and choose, then write the chosen names into `.env` and `docs/ASSUMPTIONS.md`.
