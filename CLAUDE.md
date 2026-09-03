# SAN Talk Docs - CLAUDE.md

## Overview
Product documentation for **Tartini** (product formerly named "SAN Talk AI" / "Talk AI") — the first tool of our **Plataforma de IA para Empresas**. Tartini = **comunicação omnichannel + gestão de equipe com IA**; it **has** atendimento tools but is **not** positioned as a customer-service/helpdesk product (atendimento is one capability, not the identity). Built with Mintlify. NOTE: the public docs have been rebranded to **Tartini** (docs lead the product UI, which still says "SAN Talk AI"/"Talk"/"atendimento" and hasn't rebranded) — keep new pages on the **Tartini** name and the platform/communication positioning, and never rename URLs/domains (`talk.saninternet.com`) or API keys (`pyp_live_`).

## Stack
- **Framework**: Mintlify (documentation site generator)
- **Content Format**: Markdown (`.md`) and MDX (`.mdx`) for interactive components
- **Configuration**: `docs.json` for site structure and navigation
- **API Docs**: OpenAPI spec at `/api-reference/openapi.json`
- **Styling**: Mint theme com o DS **papel/tinta** (accent tinta `#14120F`, fundo papel `#FAF7F0`; fonte da verdade: `DESIGN_SYSTEM.md` — atalhos `/ds` e subagente `design-system`)

## Quick Start
```bash
# Install dependencies
npm install

# Start local dev server (runs on localhost:3000)
mintlify dev

# Build for production
mintlify build
```

## Folder Structure

### Content Organization
- **`administracao/`** - Admin console features (companies, users, permissions)
- **`api-reference/`** - API documentation and OpenAPI spec
- **`atendimento/`** - Communication / inbox features (conversations, copilot, widget) — *a use case, not the product's identity*
- **`avaliacao/`** - Evaluation and feedback system
- **`base-de-conhecimento/`** - Knowledge base (documents, Q&A, websites)
- **`campanhas/`** - Campaign creation and metrics
- **`canais/`** - Communication channels (WhatsApp, templates)
- **`concepts/`** - API concepts (authentication, RAG, error handling)
- **`contatos/`** - Contact management
- **`ia-e-personalidade/`** - AI personality and compliance settings
- **`operacoes/`** - Operations features (hours, routing, qualification fields)

### Core Files
- **`index.mdx`** - Homepage
- **`introduction.mdx`** - Getting started guide
- **`quickstart.mdx`** - Quick setup instructions
- **`docs.json`** - Site navigation and configuration
- **`README.md`** - Repo information
- **`CONTRIBUTING.md`** - Contribution guidelines

## Configuration (docs.json)
The `docs.json` file defines:
- **Navigation structure**: Two main tabs ("Documentação" and "API Reference")
- **Page groupings**: Logical organization of content by feature area
- **Theme colors**: papel/tinta — accent tinta `#14120F`, fundo papel `#FAF7F0` (claro) / tinta (escuro); fontes Schibsted + Hanken (regras em `DESIGN_SYSTEM.md`)
- **API settings**: Base URL (`https://api-talk.saninternet.com/v1`), Bearer token auth
- **Links**: Dashboard button, website footer link
- **Context options**: Copy, view, ChatGPT, Claude sharing from docs

## Adding New Pages

1. **Create the markdown file** in the appropriate folder:
   ```
   mkdir -p <feature-folder>
   echo "# Page Title\n\nContent here" > <feature-folder>/page-slug.mdx
   ```

2. **Register in `docs.json`** under the appropriate group:
   ```json
   {
     "group": "Feature Name",
     "pages": ["feature-folder/page-slug"]
   }
   ```

3. **Use MDX for interactive content** (callouts, tabs, code snippets):
   ```mdx
   <Note>This is a note callout</Note>
   <CodeBlock>code example</CodeBlock>
   ```

## Writing Conventions
- **Language**: Portuguese (pt-BR)
- **Tone**: Professional, clear, user-friendly
- **Structure**: H1 for page title, H2/H3 for sections
- **Code blocks**: Include language identifier (json, bash, python)
- **Links**: Use relative paths for internal docs, full URLs for external
- **Images**: Place in `logo/` or subdirectories, reference with `/path/`
- **API examples**: Include curl and code examples when relevant

## Important Files to Know
- **`.mintignore`** - Files/folders to exclude from build
- **`.github/`** - Git configuration and workflows
- **`favicon.svg`** - Site icon
- **`logo/light.svg` and `logo/dark.svg`** - Branding assets

## Common Tasks
- **Update navigation**: Edit `docs.json` groups and pages array
- **Change colors**: Modify `colors` section in `docs.json`
- **Add API endpoint**: Create new file in `api-reference/endpoint/` and reference in docs.json
- **Update branding**: Replace files in `logo/` directory
