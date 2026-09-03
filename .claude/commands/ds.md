# /ds — Design System (papel/tinta) na docs

**Purpose:** Implementar ou revisar o site de documentação (Mintlify) e o conteúdo MDX em
conformidade com o design system **papel/tinta** do Talk AI. Use ao mexer em visual
(`docs.json`, `style.css`, logos), ao escrever/revisar páginas, ou ao auditar aderência
("está no DS?", "revisar o visual", "ajustar cores/tema/dark mode").

## Como funciona

Delegue para o subagente **`design-system`** (o especialista), que carrega o
[`DESIGN_SYSTEM.md`](../../DESIGN_SYSTEM.md) e as fontes da verdade (`docs.json` — validado pelo
schema Mintlify — e `style.css`) e aplica as regras. Passe o alvo em `$ARGUMENTS` (arquivo,
página, pasta, ou "o site inteiro").

## Modos

- **Implementar** — "criar/ajustar X seguindo o DS": configurar via `docs.json`/`style.css`,
  conteúdo com a voz do DS, nos dois temas (claro/escuro).
- **Revisar** — "auditar aderência de X": achar violações (azul San `#004bad`/`#1875f0`/`#007BFF`,
  `#000`, hex/`style=` em MDX, emoji, fontes proibidas, callout sem significado) e reportar com
  `arquivo:linha` + a correção. Com `--fix`, aplica as correções.

## Lembretes rápidos (o núcleo)

- **Site monocromático:** accent tinta `#14120F`, fundo papel `#FAF7F0` (invertidos no dark).
- **Azul San morreu** — `#004bad`/`#1875f0`/`#007BFF` em lugar nenhum.
- **Sinais do produto** só com significado: cobalto = IA, terracota = equipe.
- **Fontes:** Schibsted (títulos) · Hanken (corpo) · IBM Plex Mono (código). Sem Inter/Roboto/Poppins.
- **Sem emoji** — `✓ ✕ — →`. **Voz** afirma, não explica; IA se identifica em mono; pt-BR.
- **Callouts** pelo significado (`Note`/`Warning`/`Tip`/`Check`), com parcimônia.
- **`docs.json` tem schema** — não inventar chaves.

## Checklist

Ver o **Checklist de aderência** do [`DESIGN_SYSTEM.md`](../../DESIGN_SYSTEM.md) §7.
Preview: `mintlify dev`.

## Example Usage

```
/ds revisar atendimento/copilot.mdx
/ds auditar o site inteiro
/ds --fix trocar emojis por ícones tipográficos em administracao/
```
