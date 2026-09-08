# CLAUDE.md

Central de ajuda do Tartini, publicada com Mintlify. Conteúdo em MDX, em português do
Brasil, escrito para o usuário final: dono da conta, Administrador, gestores e
atendentes. `docs.json` é a navegação. Push na `main` publica: commit local sempre, push
só quando o dono pedir.

Comandos: `npx mint dev` (preview local), `npx mint broken-links` (links quebrados),
`python3 scripts/lint-central.py` (travessão, vocabulário banido, armadilhas de MDX,
links para páginas inexistentes).

## O modelo

A central da Intercom (https://www.intercom.com/help/pt-BR/) é a referência de
estrutura, tom e mídia. Em uma linha: a central não vende, cada artigo cobre um recurso
e cada seção resolve uma tarefa na mesma ordem, os guias só apontam, toda mudança de
tela tem imagem, e os blocos de destaque são poucos e têm papel fixo.

## Estrutura

Duas abas no `docs.json`: **Central de ajuda** (padrão) e **Para desenvolvedores**
(`api-reference/`, `concepts/`, `desenvolvedores/`). Na central, uma pasta por coleção,
na ordem da jornada:

```
visao-geral · primeiros-passos (guias, configuracao, perguntas-frequentes)
cerebro · tino · inbox · canais · campanhas · scout · metricas
equipe · atendimento · creditos · integracoes · conta
```

A home (`index.mdx`) é uma frase, a busca e os cartões das coleções. Sem pitch.

Fonte da verdade do conteúdo: a interface do produto, lida no repositório
`PypSystem/tartini-web`. Nada que a tela não mostre entra na central. Dúvida fica
marcada no texto como `{/* CONFIRMAR: ... */}`.

## O produto, o mínimo para escrever

- **Nome:** Tartini. Dashboard em https://talk.saninternet.com. Nunca "Talk", "Talk AI"
  ou "SAN Talk".
- **O Cérebro e os agentes.** O Cérebro (menu Cérebro: Panorama, Propriedades,
  Personalidade, Processos, Operações) não é um agente: é o centro. "Tudo parte do
  Cérebro: você entrega o material, ele aprende o seu padrão e coordena o time de
  agentes." Os agentes são quatro, cada um com o seu posto e todos com a mesma fonte:
  o **Tino** fala com o cliente (ligado em Configurações > Atendimento > IA por canal),
  o **Copilot** fica ao lado de quem atende (consulta em todos os planos, modo ativo no
  Scale), o **Scout** lê a conversa depois que fecha (ligado nas Regras de Conversa) e
  o **Quattro** põe a operação por escrito (Cérebro > Processos > Mapeamento, Scale).
  A referência de copy sobre eles é a landing https://www.tartini.com.br/tartini
  (frase canônica: "O Cérebro orquestra os agentes, e eles conversam entre si";
  "Ensinou uma vez, vale para todo o atendimento"; "As habilidades vêm prontas. A
  identidade é sua"; neuroplasticidade: o Cérebro evolui a cada interação). Em texto
  genérico, "os agentes" no plural.
- **Menu principal:** Página Inicial · Inbox · Métricas · Central de Conversas · Cérebro
  · Scout · Campanhas. Configurações no rodapé do menu.
- **Configurações:** Empresa (Informações, Áreas & Unidades, Usuários) · Canais
  (WhatsApp Business, Chat Widget, WABA, Conexão via API) · Atendimento (Regras de
  Conversa, IA por canal, Mensagens Rápidas, SLA de Atendimento, Pesquisa de
  Satisfação) · Cobrança (Assinatura, Créditos) · Análises (Mensagens e Conversas) ·
  Integrações (Conectores, Contatos de Campanha, Webhooks) · Pessoal (Configurações de
  usuário, Segurança).
- **Estrutura e papéis:** Empresa > Área > Unidade, com herança de acesso. Dono da
  conta, Administrador, Gestor da Empresa, Gestor de Área, Gestor de Unidade,
  Atendente. "Proprietário", "Gerente", "OWNER" e "BACKOFFICE" não existem mais.
- **Planos:** Essential (a IA trabalha para dentro), Scale (a IA fala com o cliente:
  Tino, IA por canal, Operações e Processos do Cérebro, Copilot ativo, Campanhas,
  Conectores, API e Webhooks) e Enterprise (sob consulta). Recurso do Scale leva uma
  `<Note>` de disponibilidade.
- **Créditos:** a IA e as mensagens consomem créditos de uma franquia mensal. Sempre
  créditos, nunca tokens, dólar ou reais.

## Tipos de artigo

| Tipo | Título | Esqueleto |
|---|---|---|
| Visão geral ("X explicado") | "O Scout explicado" | O que é, para que serve, o submenu, quem vê, e links para as tarefas |
| Recurso e tarefas | Imperativo: "Defina o SLA de atendimento" | Abertura com o resultado → `<Note>` de papel e plano → por tarefa, separada por `---`: `## verbo`, estado padrão, onde fica (caminho em negrito), `<Steps>` com o botão em negrito, captura, `<Note>` com os detalhes → `## Perguntas frequentes` em `<AccordionGroup>` → `## Artigos relacionados` |
| Guia de início rápido | Gerúndio: "Configurando o Inbox" | Abertura → lista numerada dos passos com âncoras → `## Passo N: verbo`, vídeo, porquê, `###` subtarefas com links, `<Info>` Saiba mais → `## Próximos passos` |
| Perguntas frequentes | "Perguntas frequentes para iniciantes" | Grupos em `##`; cada pergunta é um `<Accordion title="…">` dentro de `<AccordionGroup>`, com a resposta começando respondendo |
| Solução de problemas | "Resolva problemas de conexão" | Sintoma em `##`, causa, correção em passos |

Tamanhos: tarefa entre 500 e 1.200 palavras; guia entre 500 e 1.000; visão geral até
1.500; FAQ sem limite.

## Como escrever

- Segunda pessoa (você, sua equipe); o produto e os agentes na terceira; "nós" só
  quando a SAN age.
- Os agentes conversam entre si. Cada um tem a sua responsabilidade e, quando falta
  uma informação, pergunta ao outro: o Tino e o Copilot consultam o Cérebro, o Scout
  pede ao Cérebro a régua, o Tino entrega o resumo ao Copilot e à equipe, e o Tino e o
  Scout devolvem ao Cérebro o que aprenderam. Nunca descrever um agente como isolado.
- Frases de até 20 palavras. Parágrafos de até duas frases. Enumeração com mais de dois
  itens vira lista.
- `description`: uma frase com o benefício, até 25 palavras.
- O primeiro parágrafo mostra o resultado, nunca descreve o produto.
- Estado padrão antes da ação. Onde fica em negrito com ">" e os rótulos exatos do
  menu. Elemento de interface em negrito, com o texto exato da tela.
- Sempre que a tela deixar claro, diga onde o botão fica: "no canto superior direito",
  "na barra acima do campo de mensagem", "na ponta direita do cabeçalho". A posição
  vem do inventário; sem certeza, não invente.
- Exemplos do mundo de quem lê: loja, clínica, franquia, rede; nomes fictícios.
- O texto do link diz o que a pessoa vai encontrar. Nunca "clique aqui".
- Termos que a interface mostra em inglês ficam em inglês: Copilot, Scout, widget,
  webhook, WABA, handoff, CSAT, SLA.

Vocabulário: pessoas (não gente); processos e etapas (não fluxos); o Tino atende, a IA
responde (não automação, bot, chatbot); créditos (não tokens); vírgula, dois pontos ou
frase nova (nunca travessão); afirmativa direta (nunca "é X, não Y", "nova era",
"potencialize", "transforme", "piloto automático"); o que a tela mostra (nunca
números-estatística ou promessa de resultado).

## Blocos (Mintlify)

| Papel | Componente |
|---|---|
| Limite, permissão, plano, comportamento padrão | `<Note>` |
| Atalho, combinação útil | `<Tip>` |
| Leituras no fim de um passo do guia | `<Info>` com **Saiba mais** e lista de links |
| Ação irreversível, custo em créditos, risco | `<Warning>` |
| Separação entre seções | `---` antes de cada `##` (`python3 scripts/separadores.py` garante em todos os artigos) |
| Sequência de ações | `<Steps>` com `<Step title="verbo">` |
| Artigos relacionados | `## Artigos relacionados` com `<CardGroup cols={2}>` |
| Perguntas frequentes | `<AccordionGroup>` com um `<Accordion title="a pergunta">` por pergunta (`python3 scripts/faq-em-sanfona.py` converte `###` em sanfona) |
| Referência longa | tabela; `<Accordion>` fora das perguntas só para listas de referência, nunca para esconder passos |

Um destaque a cada 150 a 250 palavras, nunca dois seguidos. Sumário automático a
partir de `##` e `###`; nunca `#` no corpo.

## Capturas e vídeos

As capturas ainda não foram feitas. Cada artigo marca o lugar exato com
`{/* CAPTURA: images/<colecao>/<tela>-<acao>.png | alt: estado da tela | olhar: o que
a pessoa deve olhar */}`, e os guias marcam `{/* VÍDEO: tema (duração) */}`. A lista
completa sai com `grep -rn "CAPTURA:" --include=*.mdx .`.

Quando a captura existir, troque o marcador por
`<Frame caption="o que olhar"><img src="/images/..." alt="estado da tela" /></Frame>`.
Especificação: PNG em 2x, largura útil mínima de 1.600 px, recorte no painel
relevante, janela com cantos arredondados e sombra suave sobre fundo branco, alvo
contornado por um retângulo fino (2 px, cantos arredondados, tinta #14120F). Sem setas,
sem texto sobre a imagem, sem cursor. Dados sempre de uma conta de demonstração com
nomes fictícios; nunca cliente real. Vídeo: 45 a 120 s, 16:9, no YouTube não listado,
embutido com `<iframe>` abaixo do título do passo. Quando a tela muda, a captura muda no
mesmo commit.

## Cuidados do MDX

- Nunca chaves `{` `}` nem `<` em texto corrido. Comentário só como `{/* ... */}`;
  comentário HTML quebra o build. Variáveis de template como `{{nome}}` só dentro de
  crase.
- Frontmatter só com `title`, `sidebarTitle` e `description`, entre aspas duplas.
- Links internos absolutos a partir da raiz, sem extensão. Ao renomear uma página,
  registre um `redirect` no `docs.json`. Toda página nova entra no `docs.json` no mesmo
  commit.

## Antes de publicar

- [ ] Um tipo de artigo, um recurso, título com o verbo certo.
- [ ] `description` de uma frase com o benefício.
- [ ] Caminho da tela com os rótulos exatos.
- [ ] Marcador de captura em cada mudança de estado.
- [ ] Nota de plano e de papel quando restringem.
- [ ] Nada que a tela não mostre hoje; dúvida marcada com `CONFIRMAR`.
- [ ] `python3 scripts/lint-central.py` e `npx mint broken-links` limpos.
- [ ] Página no `docs.json`.
