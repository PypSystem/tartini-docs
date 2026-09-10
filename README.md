# tartini-docs

Documentação do **Tartini** para o cliente final, publicada com [Mintlify](https://mintlify.com). Cobre canais, inbox, campanhas, base de conhecimento, avaliação (Sotto), configurações, conta e faturamento, além da referência da API pública.

## Como rodar

```bash
npm i -g mint
mint dev          # http://localhost:3000
```

A navegação, o tema e os grupos ficam em `docs.json`. Cada página é um `.mdx` dentro da pasta do seu grupo (`canais/`, `campanhas/`, `api-reference/` …).

## Como publica

O GitHub App do Mintlify acompanha a branch `main`: merge em `main` publica. Não há workflow de deploy neste repo.

## Convenções

- Texto em pt-BR, voltado ao cliente, sem jargão interno. Código, rotas e identificadores em inglês.
- O produto é **Tartini** (nomes anteriores "Talk", "SAN Talk AI" e "Dueto" não aparecem). "Dueto" é só o design system.
- Issue de frontend que muda comportamento visível deve pedir documentação aqui.
- Guia de estilo e componentes em [`DESIGN_SYSTEM.md`](DESIGN_SYSTEM.md); contexto para agentes em [`CLAUDE.md`](CLAUDE.md).

## O ecossistema 4ha

| Repo | Papel |
|---|---|
| `tartini-api` | Backend do Tartini e camada de plataforma: auth, empresa, papéis, assinatura, crédito e o cérebro da empresa |
| `tartini-web` | Dashboard do Tartini (Nuxt) |
| `tartini-chat-widget` | Canal de chat no site do cliente |
| `tartini-whatsapp-gateway` | Canal WhatsApp não-oficial (Go / whatsmeow) |
| `tartini-docs` | Documentação do produto (Mintlify) |
| `4ha-ai-engine` | Motor de IA da plataforma: LLM, RAG e grafos do cérebro (FastAPI) |
| `4ha-admin-web` | Painel administrativo cross-tenant da plataforma |
| `studio`, `studio-template` | Studio, a segunda ferramenta: criação de site com IA (em construção) |
