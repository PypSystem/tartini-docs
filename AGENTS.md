# Instruções para agentes

As regras de escrita, o contexto do produto, os tipos de artigo, a especificação de
capturas e o checklist de publicação estão em [CLAUDE.md](./CLAUDE.md). Este arquivo só
repete o essencial da ferramenta.

## Mintlify

- `docs.json` é a navegação: toda página nova entra lá no mesmo commit; página
  renomeada ganha um `redirect`.
- Páginas em MDX com frontmatter `title`, `sidebarTitle` e `description`.
- `npx mint dev` para ver localmente; `npx mint broken-links` e
  `python3 scripts/lint-central.py` antes de commitar.
- Push na `main` publica. Commit local sempre; push só quando o dono pedir.
- Componentes: https://www.mintlify.com/docs/components. Não usar HTML quando existe
  componente equivalente.
