# Design System — Papel/Tinta (docs)

> **Fonte da verdade do visual e da voz desta documentação.** Toda sessão do Claude (e toda
> pessoa) que mexe no site ou no conteúdo deve seguir este documento. Se algo aqui divergir do
> código (`docs.json` + `style.css`), o código vence — e este doc deve ser corrigido.
>
> Atalhos: comando **`/ds`** · subagente **`design-system`**. DS canônico do produto:
> `../tartini-web/DESIGN_SYSTEM.md` (san-web). Este repo é **Mintlify** (tema `mint`) — o DS
> aqui é aplicado por configuração (`docs.json`), não por classes CSS.

---

## 1. O que é e por quê

O Talk AI é uma plataforma onde **equipe (humano) e IA se revezam na mesma conversa**. A
documentação segue a mesma linguagem do produto: **papel e tinta** — superfícies neutras e
quentes, tipografia forte, e **cor só quando carrega significado, nunca decoração**.

Nesta docs quase tudo é monocromático de propósito: tinta sobre papel no claro, papel sobre tinta
no escuro. O accent do site é **tinta**, não azul.

---

## 2. Cores — onde vivem e o que significam

Tudo em `docs.json` (Mintlify não usa CSS vars nossas):

| O quê | Chave | Claro | Escuro |
|---|---|---|---|
| Accent (links, nav ativa, botão) | `colors.primary` / `colors.dark` | `#14120F` (tinta) | — |
| Accent no dark | `colors.light` | — | `#FAF7F0` (papel) |
| Fundo de página | `background.color` | `#FAF7F0` (papel) | `#14120F` (tinta) |

**Referência dos sinais do produto** (para imagens, diagramas e exemplos embutidos):
tinta `#14120F` · papel `#FAF7F0` · sunken `#F1ECE1` · linha `#E2DCCE` · meta `#8D8779` ·
**IA = cobalto `#2667FF`** (só IA) · **equipe = terracota `#EB5E28`** (só equipe) ·
ok `#1F9D55` · erro `#C0341D` · atenção `#B7791F`.

### Proibido

- ❌ **Azul San `#004bad` / `#007BFF` / `#1875f0`** em qualquer lugar do site (era o tema antigo).
- ❌ `#000` puro — tinta é `#14120F`.
- ❌ Hex/`style=` dentro de MDX — conteúdo não carrega cor própria.
- ❌ Cobalto como enfeite (é a cor da IA); roxo como "cor de IA".
- ❌ Gradiente terracota→cobalto como decoração — é ativo de marca do produto, não do site de docs.

---

## 3. Tipografia

Configurada em `docs.json › fonts` (Google Fonts) + `style.css` (código):

| Fonte | Onde | Papel |
|---|---|---|
| **Schibsted Grotesk** 700 | `fonts.heading` | Títulos |
| **Hanken Grotesk** | `fonts.body` | Corpo e UI |
| **IBM Plex Mono** | `style.css` (`code`, `pre`, `kbd`) | Código, linguagem de máquina, voz da IA |

**Proibidas:** Inter, Roboto, Arial, Poppins, Ubuntu. Fraunces é só do marketing do produto —
não entra na docs.

---

## 4. Assets

A marca é o **símbolo do produto** (mesmo `BrandSymbol` do san-web): balão com dois "moradores" —
ponto **terracota** (equipe) e nó em **gradiente** terracota→cobalto (IA; o nó do símbolo é um dos
raros usos legítimos do gradiente). Os dois pontos têm cores fixas nos dois temas; balão e wordmark
seguem o tema.

- `logo/light.svg` — balão + wordmark **"talk ai"** (Schibsted 800, minúsculo, em paths) em
  **tinta** `#14120F`.
- `logo/dark.svg` — idem em **papel** `#FAF7F0`.
- `favicon.svg` — só o símbolo (balão tinta + pontos da marca).
- O wordmark é vetorizado (paths) porque `<img>` não carrega fontes externas de dentro do SVG.
- Screenshots do produto: capturar já no DS papel/tinta (nada do tema azul antigo).

---

## 5. Voz & conteúdo (vale para todo MDX)

- **pt-BR.** Wordmark do produto minúsculo quando isolado; em texto corrido, inicial maiúscula.
- **Afirma, não explica.** Dado, não adjetivo ("Quinze minutos para conectar o WhatsApp", nunca
  "simples e rápido"). O sujeito é o cliente.
- **Transparência:** quando a docs mostra a IA falando, ela se identifica como IA e aparece em
  código/mono. Máquina parece máquina.
- **Sem emoji.** Ícones tipográficos no lugar: `✓ ✕ — → ⇄ ● ▪` (ex.: tabelas de permissão usam
  `✓` e `—`, nunca ✅/❌).
- Callouts Mintlify pelo **significado**, com parcimônia (máx. 1–2 por página):
  `<Note>` informação/contexto · `<Warning>` risco real ou pré-requisito crítico ·
  `<Tip>` atalho prático · `<Check>` estado concluído/verificado.
- Ícones de `<Card>`/nav são os do Mintlify (Font Awesome via `icon=`) — escolha ícones sóbrios,
  de linha, coerentes entre páginas irmãs.

---

## 6. Regras do repo (Mintlify)

- **`docs.json` é validado por schema** (`https://mintlify.com/docs.json`). Não invente chaves —
  `rounded` e `font` (singular) não existem e já foram removidos.
- `style.css` é carregado automaticamente pelo Mintlify — manter mínimo (só o que o `docs.json`
  não cobre).
- Arquivos internos (`DESIGN_SYSTEM.md`, `CLAUDE.md`, `AGENTS.md`) ficam fora do build via
  `.mintignore`.
- Preview local: `mintlify dev`.

---

## 7. Checklist de aderência

- [ ] Zero azul San (`#004bad`/`#007BFF`/`#1875f0`) em config, assets ou conteúdo.
- [ ] Zero `#000` — tinta é `#14120F`. Zero hex/`style=` em MDX.
- [ ] Fontes: Schibsted (títulos) · Hanken (corpo) · IBM Plex Mono (código).
- [ ] Sem emoji — ícones tipográficos (`✓ ✕ — →`).
- [ ] Callouts pelo significado, com parcimônia.
- [ ] Funciona nos dois temas (claro/escuro) — logo certo em cada um.
- [ ] Voz: afirma, não explica; pt-BR; IA se identifica.
