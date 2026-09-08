# Inventário de telas — Cérebro (`/identity`)

> Fonte: clone da main de 03/09/2026 do repo `tartini-web` (Nuxt 3 / Vue 3, dashboard pt-BR).
> Escopo: tudo em `pages/identity/**`, componentes `components/identity/**` e `components/property/**`,
> `layouts/identity.vue`, services e types relacionados. Leitura de código apenas.

## Submenu do Cérebro

No menu principal do produto (sidebar esquerda, `components/shared/Sidebar.vue`), o item que leva à
área é rotulado **"Cérebro"** (ícone `PhBrain`), aponta para `/identity/overview` e exige nível
Empresa (`requires: 'companyManager'` — Admin ou Gestor da Empresa; Gestor de Área/Unidade e
Atendente não veem o item).

Dentro da área, a sidebar secundária (`components/identity/Sidebar.vue`, cabeçalho "Cérebro") lista,
nesta ordem:

1. **Panorama** — `/identity/overview` (ícone `PhSquaresFour`, item único, sem submenu)
2. **Propriedades** — `/identity/properties` (ícone `CubeIcon`, item único, sem submenu)
3. **Personalidade** — seção expansível (ícone `PersonalityIcon`), expandida por padrão:
   - **Comunicação** — `/identity/personality/communication` (badge de sugestões pendentes: `communication`)
   - **Diretrizes** — `/identity/personality/guidelines` (badge: `guideline`)
   - **Conformidade** — `/identity/personality/compliance` (badge: `compliance`)
4. **Processos** — seção expansível (ícone `PhStack`), expandida por padrão:
   - **Mapeamento** — `/identity/processes` (rota "ativa" também cobre o detalhe `/identity/processes/[id]`, `mapping/[sessionId]` etc. — tudo que não é Grupos/Descobertas/Catálogo)
   - **Descobertas** — `/identity/processes/discovery` (badge: contagem de candidatos a processo pendentes; tooltip do badge: "Candidatos a processo pendentes de revisão")
   - **Grupos** — `/identity/processes/groups`
   - **Catálogo** — `/identity/processes/consistency` (essa aba também cobre `/identity/processes/insights`)
5. **Operações** — seção expansível (ícone `OperationsIcon`), expandida por padrão:
   - **Esclarecimentos** — `/identity/operations/clarifications` (badge: `clarification`)
   - **Campos do contato** — `/identity/operations/qualification` (sem badge; nome interno do catálogo era "Qualificação", mas a tela e a ficha do contato usam "Campos do contato")
   - **Status de contato** — `/identity/operations/contact-statuses` (sem badge)
   - **Roteamento** — `/identity/operations/routing` (badge: `routing`)
   - **Disponibilidade** — `/identity/operations/availability` (sem badge)
   - **Contexto Situacional** — `/identity/operations/situational-context` (badge: `situationalContext`)

Os badges numéricos (fundo `bg-ia-soft`, texto `bg-ia-deep`) mostram sugestões da IA (Tino) pendentes
de revisão, com tooltip "Sugestões do Tino pendentes de revisão" (Personalidade/Operações) ou
"Candidatos a processo pendentes de revisão" (Descobertas) / "Itens pendentes de revisão" (default de Processos).

A rota `/identity` (index) não renderiza conteúdo próprio: mostra um spinner com o texto
"Carregando..." e redireciona automaticamente para `/identity/overview`.

No layout mobile (`layouts/identity.vue`), o cabeçalho fixo mostra o título **"Cérebro"** com um
botão de menu (ícone `PhList`) que abre a sidebar secundária como overlay.

### Acesso e gate por papel

- **Guard de rota** (`middleware/auth.global.ts`, `companyLevelPrefixes = ['/identity']`): exige
  `auth.isCompanyManagerWide` (Admin da Empresa OU Gestor da Empresa). Gestor de Área, Gestor de
  Unidade e Atendente são redirecionados para `/home` ao tentar acessar qualquer rota `/identity/*`.
- Conforme `docs/visibilidade-por-papel.md`, na sidebar principal o item "Cérebro" só aparece para
  Dono da conta, Admin da Empresa e Gestor da Empresa (✅); para Gestor de Área, Gestor de Unidade e
  Atendente aparece ❌ (nem o item nem a rota).
- **Gate por plano** (`utils/entitlements.ts`, `GATED_ROUTES`): dentro do Cérebro, **Panorama**,
  **Propriedades** e **Personalidade** ficam sempre livres (não são gateadas por feature). Já:
  - `/identity/processes/*` exige a feature `processes` (`FEATURE.PROCESSES`).
  - `/identity/operations/*` exige a feature `ai.operations` (`FEATURE.AI_OPERATIONS`).
  O item de menu continua visível mesmo sem a feature; ao abrir a rota sem o plano, o
  `PlanUpgradeWall` (via `usePlanGate`) cobre a tela com o aviso de upgrade em vez de esconder o
  menu ou redirecionar. O nome comercial do plano mínimo usado no upsell é **"Scale"**
  (`UPSELL_MIN_PLAN_LABEL`).
- Na sidebar do Cérebro, o badge de "Descobertas" só busca a contagem se a empresa tiver a feature
  `processes` (`auth.hasFeature(FEATURE.PROCESSES)`), evitando erro 403 e toast automático de
  "recurso fora do plano".

---

## Panorama (`/identity/overview`)

- **Como chegar:** Cérebro > **Panorama** (primeiro item da sidebar do Cérebro, sempre visível).
- **Para que serve:** resumo executivo do "cérebro" da empresa: quanto conhecimento existe, se está
  indexado, se a personalidade e as operações estão completas, quantos processos ativos e o que
  está pendente de revisão. Ponto de entrada rápido para "conversar com o cérebro" (abre o chat de
  teste) e para navegar às demais seções.
- **Quem vê:** Admin/Gestor da Empresa (mesmo gate de todo o `/identity`). Não há diferença de
  conteúdo por papel dentro da própria tela — os dados são da empresa inteira.
- **Plano, créditos e bloqueios:** o card **Processos** vira upsell quando a empresa não tem a
  feature `processes`: o número aparece como travessão (`—`) e a descrição some para
  "Disponível a partir do plano Scale — faça upgrade para mapear seus processos" com status
  "fora do seu plano". Nesse caso as chamadas de API de processos (lista, grupos, descobertas) nem
  são feitas (evita 403/toast automático). Quando a empresa tem a feature, o botão "acessar" do card
  leva a `/identity/processes`, que por sua vez tem seu próprio wall de upgrade caso o plano mude.
- **O que há na tela:**
  - Kicker "cérebro · panorama" e título **"Panorama"**.
  - Frase de veredito logo abaixo do título, com um quadradinho de gradiente e um selo:
    - Sem pendências: **"Cérebro em dia — nada do Tino aguardando sua revisão."** (selo "em dia", tom verde/"ok").
    - Com pendências: texto dinâmico, ex. **"3 sugestões do Tino e 2 descobertas de processo aguardam sua revisão."** (selo "requer atenção", tom "atenção").
  - Um "palco" (hub-and-spoke) com um orbe central animado (`BrainOrb.vue`) ligado por linhas
    animadas a 5 cards, cada um com ícone, selo de status (ponto colorido + texto curto), número
    "herói", descrição e um link **"acessar"**:
    1. **Propriedades** — número = total de fontes; descrição "N documentos · N Q&A · N sites"; status "indexado" (verde) ou "vazio" (cinza); leva a `/identity/properties`.
    2. **Conexões** — número = total de vetores indexados; descrição "O conhecimento das propriedades transformado em memória de resposta"; status "conectado" (azul/IA) se houver vetores, senão "vazio"; leva a `/identity/properties`.
    3. **Processos** — número = processos ativos (ou "—" fora do plano); descrição "Ativos na sua operação" ou texto de upsell; status "ativos"/"nenhum ativo"/"fora do seu plano"; leva a `/identity/processes`.
    4. **Personalidade** — número = soma de itens de comunicação+diretrizes+conformidade; descrição "Comunicação · diretrizes · conformidade"; status "completa" (verde) ou "incompleta" (atenção); leva a `/identity/personality/communication`.
    5. **Operações** — número = itens configurados (ou pendências, em vermelho/atenção, se incompleto); descrição "Esclarecimentos · roteamento · disponibilidade" ou "Falta configurar a &lt;esclarecimentos/roteamento/disponibilidade&gt;"; status "completa"/"incompleta"; leva a `/identity/operations/clarifications`.
  - Em telas estreitas (largura do palco < 800px) os cards empilham em grade 1–2 colunas e o
    orbe/linhas somem.
  - Campo de conversa flutuante sobre a borda inferior do palco: input com placeholder
    **"Converse com o cérebro…"** e botão de enviar (ícone de avião de papel). Enter ou clique
    abrem o chat lateral experimental — se o campo estiver vazio, só abre o chat; se tiver texto,
    já envia a mensagem (auto-send) e limpa o campo. O input some enquanto o chat lateral está aberto.
  - Bloco **"precisa de atenção"** (título em minúsculas, `MetricsSection`, com dica "o que Tino
    propôs e aguarda sua revisão") — só aparece quando há pendências:
    - Linha "N sugestão(ões) do Tino aguardando revisão" com legenda "Tino propôs novos
      conhecimentos a partir das conversas" e link **"ver por categoria →"** para
      `/identity/personality/communication`.
    - Linha "N descoberta(s) de processo pendente(s)" com legenda "padrões que Tino identificou e
      podem virar processos" e link **"revisar descobertas →"** para `/identity/processes/discovery`.
- **Fluxos:**
  - **Ver estado geral:** abrir Panorama, ler o veredito e os 5 cards; clicar "acessar" no card de
    interesse para ir à tela correspondente.
  - **Perguntar ao cérebro:** digitar uma pergunta no campo "Converse com o cérebro…" e apertar
    Enter (ou clicar no botão de enviar) — abre o chat lateral experimental com a pergunta já
    enviada automaticamente.
  - **Resolver pendências:** no bloco "precisa de atenção", clicar "ver por categoria" (sugestões do
    Tino) ou "revisar descobertas" (candidatos a processo) para ir direto à fila de revisão.
- **Regras e limites:** os dados vêm de `useBrainOverview`, que agrega, de forma resiliente
  (`Promise.allSettled`, cada fonte falha isoladamente sem quebrar a tela), os serviços de
  dashboard (`getHomepageData`), propriedades (`getPropertySummary`), pendências de identidade
  (`countPending`) e, só quando a feature `processes` está no plano, processos/grupos/descobertas.
  "Indexado"/"conectado" dependem de `totalVectors`/`indexedVectors` > 0, não apenas de existirem
  fontes cadastradas — cérebro sem nenhum vetor indexado é tratado como "vazio", mesmo com fontes.
  A animação do hub respeita `prefers-reduced-motion` (some os "cometas" de luz nas linhas) e pausa
  quando o palco sai do viewport ou a aba fica oculta.
- **Nomes e termos:** "Tino" = a IA que sugere conhecimento e descobre processos; "cérebro" = toda a
  configuração de conhecimento/personalidade/operações/processos da empresa; "conexões" = vetores
  indexados a partir das propriedades.
- **Perguntas prováveis do usuário:**
  - "Por que o card de Processos está com '—'?" → a empresa não tem a feature `processes` no plano; é preciso upgrade (plano Scale ou superior) para ver e mapear processos.
  - "O que significa 'vazio' no card de Propriedades/Conexões?" → não há fontes cadastradas ou nenhuma foi indexada (sem vetores gerados) ainda.
  - "Para onde vou se quiser revisar o que a IA sugeriu?" → clicar em "ver por categoria" no bloco de pendências, que leva a Comunicação (Personalidade).
- **Incertezas:** o texto exato de erro/estado de carregamento quando `getHomepageData` ou os outros
  serviços falham não é mostrado nesta tela (as seções simplesmente usam os defaults zerados); não
  há indicação visual de "erro" separada de "vazio".



# PARTE A: Propriedades
# Propriedades (dentro do Cérebro) — inventário de telas

Fonte: clone de `tartini-web` (main de 03/09/2026), somente leitura. Escopo: área "Propriedades" dentro de "Cérebro" (`/identity/properties/*`).

Contexto herdado (não repetido aqui): toda `/identity` exige Admin da Empresa ou Gestor da Empresa (`auth.isCompanyManagerWide`); Gestor de Área/Unidade e Atendente são redirecionados para `/home`. O agente de atendimento se chama "Tino".

Confirmação de gate de plano: a rota `/identity/properties` **não** está na lista `GATED_ROUTES` de `utils/entitlements.ts` — não há bloqueio de feature/plano na tela em si. O único gate dentro da tela é pontual: a opção de audiência **"Conhecimento Público (AI Agent)"** exige a feature `ai.autonomous` (liberada a partir do plano **Scale**, constante `UPSELL_MIN_PLAN_LABEL`). Sem essa feature, a opção "Conhecimento Público" some dos formulários de cadastro (`AudienceControl.vue` filtra a opção) e, na listagem, aparece um aviso fixo explicando que "o conteúdo público não é utilizado pelo Tino" nesse plano.

---

## Propriedades e Fontes (`/identity/properties`)

**Como chegar:** menu lateral do Cérebro > "Propriedades" (ícone de cubo). É a raiz da área — sem submenu (ao contrário de Personalidade/Operações, que expandem).

**Para que serve:** É a base de conhecimento central da empresa — lista, filtra e gerencia todos os documentos, perguntas e respostas (Q&A) e sites indexados que alimentam o Tino (AI Agent) e o Copilot.

**Quem vê:** Admin da Empresa e Gestor da Empresa (gate herdado do `/identity`). Não há diferenciação de UI por papel dentro da própria tela — quem entra vê tudo.

**Plano, créditos e bloqueios:**
- Sem gate de rota/feature na tela.
- A opção de audiência "Conhecimento Público (AI Agent)" exige `ai.autonomous` (plano Scale+). Sem a feature, aparece um aviso permanente acima do filtro de audiência:
  > "O **Conhecimento Público (AI Agent)** está disponível a partir do plano {{ UPSELL_MIN_PLAN_LABEL }}. No seu plano, o conteúdo público não é utilizado pelo Tino."
  com botão **"Fazer upgrade de plano"** (leva para Faturamento).
- Envio de documento, criação de Q&A e indexação de site **consomem créditos** (ver seção de cada modal — todos exibem o "selo de IA" com tooltip explicando o consumo).
- Erro 402 `CreditsExhausted` no upload em lote é tratado silenciosamente pelo service (o interceptor global do axios já mostra o aviso de saldo; o service não duplica o toast).

**O que há na tela:**
- Cabeçalho: "Propriedades e Fontes" + link **"saiba mais"** (abre o modal `ExplainerCarousel`).
- Filtro por tipo de conhecimento (multi-seleção, dois botões-pill):
  - **"Conhecimento Público"** / subtítulo "AI Agent" (ícone globo)
  - **"Conhecimento Privado"** / subtítulo "Copilot" (ícone cadeado)
  - Texto de ajuda: "Filtre por tipo de conhecimento. Sem nada selecionado, exibe todos."
- Barra de busca: input com placeholder **"Pesquisar..."** (debounce de 300ms).
- Botões "Adicionar" (rótulo "Adicionar" + três botões): **"Arquivo"**, **"Q&A"**, **"Site"** — cada um abre o modal correspondente.
- Link **"Selecionar"** (alterna modo de seleção em lote; texto vira **"Cancelar seleção"** quando ativo). Com itens selecionados aparece o botão **"Excluir (N)"**.
- Cabeçalho da lista (colunas): Título, Descobertas, Status, Criado por, Audiência (as três últimas somem em telas menores).
- Cada linha mostra: ícone do tipo de fonte, título (nome do arquivo / pergunta / URL, com fallback **"Sem título"**), badge de subpáginas quando é um site-raiz (**"N subpágina(s)"**), ícones de "Descobertas" (sugestões de identidade e candidatos a processo pendentes, com badge numérico pulsante), status, criado por, audiência (**"Público/Privado"**, **"Público"**, **"Privado"** ou **"—"**), menu de ações (⋮).
- Menu de ações por item: **"Ver detalhes"** (some se o item estiver "travado" havia mais de 5 min processando) e **"Excluir"**.
- Estado vazio (sem busca/filtro): título **"Adicionar conteúdo"** com 3 cards clicáveis:
  - **"Enviar documento"** — "PDF, DOCX, XLSX, CSV, TXT ou MD"
  - **"Pergunta e Resposta"** — "Pares de Q&A para treinamento"
  - **"Sincronizar site"** — "Importar conteúdo de websites"
- Estado vazio (com busca/filtro ativo): **"Nenhum conteúdo encontrado"** / "Tente ajustar a busca ou o filtro".
- Estado de carregamento: spinner + "Carregando conteúdo...".
- Estado de erro: "Erro ao carregar" / "Não foi possível carregar o conteúdo. Tente novamente mais tarde."
- Cartão "Tino aprendeu" (aparece embutido logo abaixo de um item recém-indexado, quando o backend retornou um resumo de aprendizado): texto **"Tino aprendeu:"** + resumo truncado em 115 caracteres (com "..."), botão **"Testar conhecimentos adquiridos"** (quando há pergunta sugerida) e um X para dispensar (dispensa é persistida em `localStorage`, chave `property:learning-summary-dismissed`).
- Paginação (`SharedPagination`).
- Estados de status por item, em tempo real via WebSocket (`propertyStatusUpdate`): rótulos exatos — "Extraindo conteúdo" (scraping), "Indexando", "Processando", "Sincronizando páginas" (processing_subpages), "Falhou", "Completo", "Excluindo", "Removido"; quando não há status ativo, mostra **"Indexado"**.
- Itens "travados": se um item fica em PROCESSING por ≥ 5 minutos (`STUCK_THRESHOLD_MS`), a UI considera "travado" e libera a linha para seleção/exclusão (força exclusão) mesmo sem terminar o processamento.

**Fluxos:**
- **Selecionar em lote e excluir:** "Selecionar" ativa checkboxes → seleciona linhas elegíveis (itens travados por status entram, os "presos" com <5min de processamento não) → "Excluir (N)" → modal de confirmação (`SharedDeleteModal`, título "Excluir N item(ns)", corpo "Tem certeza que deseja excluir N item(ns) **selecionados**?") → exclusão otimista (linha marcada "Excluindo" e depois removida via WebSocket).
- **Excluir um item:** menu ⋮ > "Excluir" → mesmo modal, com nome do item; se o item está em PROCESSING, o modal troca o texto para: "Este item está travado em processamento. A exclusão forçada irá removê-lo permanentemente, mesmo que a indexação não tenha sido concluída. Deseja continuar?" (envia `force=true`).
- **Ver detalhes:** clique na linha (ou "Ver detalhes" no menu) abre o `DetailPanel` (ver seção própria).
- **Deep link:** a URL aceita `?contentId=<id>` para abrir o painel de detalhes automaticamente ao carregar a página (usado por notificações/links externos).
- **Notificações em tempo real:** ao concluir indexação em lote (websites), toast **"N indexados com sucesso!"** ou, com falhas, **"N indexados, N falharam"** (N e o tipo variam: "documentos", "Q&A", "páginas"). Descobertas automáticas do Tino (identidade/processo) geram toasts: **"Tino descobriu N candidato(s) a processo a partir de "{nome}". Revise em Descobertas."** e **"Tino gerou N descoberta(s) de identidade a partir de "{nome}". Revise para aprovar."**

**Regras e limites:**
- Paginação server-side (`getAllProperty`), com `perPage` ajustável.
- Filtro por audiência é enviado ao backend (`audience=ai_agent,copilot`).
- Um item "travado" (processando há ≥5min) é a única forma de forçar exclusão de algo preso.

**Nomes e termos:**
- **Fonte** / **Propriedade**: cada documento, Q&A ou página de site cadastrado.
- **Audiência**: quem usa aquele conteúdo — "Público" (`ai_agent`, o AI Agent/Tino usa em atendimento automatizado) vs "Privado" (`copilot`, só o Copilot/equipe interna usa).
- **Descobertas**: itens de identidade ou candidatos a processo que o Tino sugere a partir do conteúdo indexado.
- **Indexado / Indexação**: processo de embutir o conteúdo na base vetorial de conhecimento.

**Perguntas prováveis do usuário:**
- "Por que não vejo a opção de conhecimento público?" → Depende do plano (`ai.autonomous`, a partir do Scale); no código, some do seletor e mostra aviso de upgrade.
- "Posso excluir algo que ainda está processando?" → Sim, com confirmação de exclusão forçada; ou automaticamente liberado após 5 minutos travado.
- "Quem vê o que eu marco como Público?" → O AI Agent (Tino), em atendimento automatizado. "Privado" é só para o Copilot (equipe interna).

**Incertezas:**
- Não foi possível confirmar no front o valor exato do custo em créditos por documento/página/Q&A indexada (o front só exibe texto genérico "consome créditos" e direciona para Faturamento → Consumo; o valor está no backend, fora do escopo lido).
- O botão "Descobertas" (ícones na coluna) depende de `item.aiSuggestions`/`item.processSuggestions` vindos do backend; não confirmei todas as condições de quando o backend gera essas descobertas automaticamente vs. sob demanda.

---

## Modal "Como funcionam as fontes?" — saiba mais (`ExplainerCarousel.vue`)

**Como chegar:** Propriedades e Fontes > link **"saiba mais"** (canto superior direito).

**Para que serve:** Explica rapidamente os 3 tipos de fonte de conhecimento e a diferença entre público e privado, para quem está começando a montar a base.

**Quem vê:** mesma audiência da tela pai (Admin/Gestor da Empresa). Sem diferenciação por papel.

**Plano, créditos e bloqueios:** nenhum — é só conteúdo estático.

**O que há na tela:**
- Título: **"Como funcionam as fontes?"** / subtítulo: "Sua base de conhecimento é alimentada por 3 tipos de fonte".
- Três cartões, cada um com título, descrição e dica ("tip"):
  - **Documentos** — "Upload de arquivos" — "Envie arquivos como PDFs, documentos Word ou textos com informações do seu negócio. Tino lê e aprende todo o conteúdo automaticamente." — dica: "Ideal para manuais, catálogos, políticas internas e documentação técnica."
  - **Perguntas e Respostas** — "Treinamento direto" — "Ensine o Tino a responder do jeito que você quer. Escreva a pergunta que o cliente faria e a resposta ideal, é a forma mais direta de treinar." — dica: "Ideal para FAQs, respostas padrão de atendimento e conhecimento específico."
  - **Websites** — "Sincronização automática" — "Cole o link de um site e Tino aprende automaticamente o conteúdo das páginas e subpáginas." — dica: "Ideal para bases de ajuda, blogs, páginas de produtos e documentação online."
- Rodapé: **"Público"** visível pelo AI Agent / **"Privado"** Copilot.

**Fluxos:** somente leitura; fecha com X ou clique fora.

**Regras e limites:** nenhuma.

**Nomes e termos:** ver glossário geral (Público/Privado, AI Agent, Copilot).

**Perguntas prováveis do usuário:** "Qual a diferença entre os 3 tipos de fonte?" → responder com os 3 cartões acima.

**Incertezas:** nenhuma relevante — conteúdo estático e literal.

---

## Modal "Enviar documento" (`UploadDocumentModal.vue`)

**Como chegar:** Propriedades e Fontes > botão **"Arquivo"** (no grupo "Adicionar") — ou, na lista vazia, o card **"Enviar documento"**.

**Para que serve:** Fazer upload de um ou mais arquivos para a base de conhecimento (documentos, planilhas, textos).

**Quem vê:** Admin/Gestor da Empresa (herdado). Sem diferenciação de UI por papel.

**Plano, créditos e bloqueios:**
- Selo de IA (`AiCostIndicator`) ao lado do título, com tooltip: **"O processamento e indexação do documento na base de conhecimento do Tino consome créditos. Acompanhe seu consumo em Configurações → Faturamento → Consumo."**
- Sem `defaultAudience` fixado pelo chamador (caso desta tela), mostra o `AudienceControl` — e se "Conhecimento Público (AI Agent)" for selecionado, aviso: **"Este conteúdo ficará acessível a clientes através do AI Agent."**
- Limite de tamanho por arquivo: **30 MB** (constante `MAX_UPLOAD_SIZE_MB`, espelha o backend). Acima disso, toast: `"{nome do arquivo} excede o limite de 30 MB."`
- Limite de arquivos por envio: até **10 arquivos** por lote na interface (o array é truncado em 10); o envio real é fatiado em lotes menores pelo helper `chunkFilesBySize` (limite de 10 arquivos OU soma ≤ 30 MB por request, o que vier primeiro) para não estourar o `client_max_body_size` do servidor.
- Falha de crédito (HTTP 402 `CreditsExhausted`) durante o envio em lote é tratada silenciosamente pelo service (o interceptor global do axios mostra o aviso; o modal não duplica).

**O que há na tela:**
- Título: **"Enviar documento"**.
- Controle de Audiência (`AudienceControl`) — "Controle de Audiência" com opções "Conhecimento Público" (AI Agent) e "Conhecimento Privado" (Copilot); a opção pública some sem a feature `ai.autonomous`.
- Área de arraste/seleção (dropzone): estado vazio com texto **"Selecionar arquivos"** / "ou arraste e solte aqui" / rodapé: "PDF, DOCX, XLSX, CSV, TXT ou MD — até 10 arquivos (máx. 30 MB cada)".
- Formatos aceitos no input: `.pdf,.txt,.doc,.docx,.xlsx,.csv,.md,.json` (o `accept` do input inclui `.json`, mas o texto exibido ao usuário não menciona JSON).
- Lista de arquivos selecionados, com nome, tamanho formatado (Bytes/KB/MB/GB) e botão de remover (some durante o envio).
- Botão **"+ Mais arquivos"** (enquanto houver menos de 10 selecionados).
- Barra de progresso durante envio: "Enviando arquivos..." + percentual.
- Rodapé: contador "**N** arquivo(s)" ou "Nenhum arquivo selecionado"; botões **"Cancelar"** e **"Enviar"** (vira "Enviando..." durante o envio).
- Confirmação de descarte ao tentar voltar/fechar com arquivos selecionados: **"Descartar alterações?"** / "Você tem arquivos selecionados. Se voltar agora, eles serão descartados." — botões "Continuar editando" / "Descartar".
- Toggle **"Gerar descobertas de IA"** existe no código mas está **comentado/desativado** (não aparece na tela).

**Fluxos:**
1. Usuário escolhe audiência (ou usa a fixada pelo chamador), seleciona arquivos (clique ou drag-and-drop), remove os que não quer.
2. Clica **"Enviar"** → upload em lote (`uploadDocumentBatch`), barra de progresso reflete o andamento por lote.
3. Sucesso: toast **"N documento(s) enviado(s)!"**, fecha o modal, a listagem recarrega e a paginação volta para a página 1.
4. Falha parcial: toasts de erro por mensagem distinta (deduplicadas); se nada subiu, o erro é propagado e nada fecha.
5. O item aparece na lista com status "Processando"/"Indexando" e, ao concluir, o card "Tino aprendeu" pode aparecer (ver tela principal).

**Regras e limites:** ver "Plano, créditos e bloqueios" acima (30 MB/arquivo, 10 arquivos/lote na UI, formatos aceitos).

**Nomes e termos:** "Lote" = grupo de arquivos enviados numa única requisição multipart (fatiamento interno, transparente ao usuário salvo pela barra de progresso).

**Perguntas prováveis do usuário:**
- "Que tipos de arquivo posso enviar?" → PDF, DOCX, XLSX, CSV, TXT, MD (o input técnico também aceita `.doc` e `.json`, mas não são anunciados na tela).
- "Qual o tamanho máximo?" → 30 MB por arquivo.
- "Posso enviar vários de uma vez?" → Sim, até 10 por envio.

**Incertezas:** não confirmei o valor de créditos cobrado por documento/página processada (fica no backend).

---

## Modal "Perguntas e Respostas" — criar Q&A em lote (`CreateQAModal.vue`)

**Como chegar:** Propriedades e Fontes > botão **"Q&A"** (grupo "Adicionar") — ou, na lista vazia, o card **"Pergunta e Resposta"**.

**Para que serve:** Cadastrar um ou mais pares de pergunta e resposta para treinar o Tino/Copilot diretamente, sem precisar de um documento.

**Quem vê:** Admin/Gestor da Empresa (herdado).

**Plano, créditos e bloqueios:**
- Selo de IA com tooltip: **"O processamento e indexação das perguntas e respostas na base de conhecimento do Tino consome créditos. Acompanhe seu consumo em Configurações → Faturamento → Consumo."**
- Sem a feature `ai.autonomous`, a audiência-padrão nasce só como "Privado" (`copilot`) — a opção "Conhecimento Público" nem aparece no seletor.
- Aviso quando "Conhecimento Público" está marcado: **"Este conteúdo ficará acessível a clientes através do AI Agent."**

**O que há na tela:**
- Título: **"Perguntas e Respostas"**.
- Controle de Audiência (mesmo componente da tela de documento).
- Lista de pares, cada um em um cartão numerado ("Par 1", "Par 2"...):
  - Campo **"Pergunta"** — input de texto — placeholder: *"Como faço para cancelar minha assinatura?"*
  - Campo **"Resposta"** — textarea (3 linhas) — placeholder: *"Você pode cancelar sua assinatura a qualquer momento..."*
  - Botão de remover par (ícone lixeira), só aparece se houver mais de 1 par.
- Botão **"Adicionar outro par"** (adiciona um novo cartão vazio).
- Rodapé: contador "**N** par(es) válido(s)" ou "Nenhum par válido"; botões **"Cancelar"** e **"Adicionar"** (vira "Adicionando..." durante o envio).
- Confirmação de descarte ao voltar/fechar com dados preenchidos: **"Descartar alterações?"** / "Você preencheu dados no formulário. Se voltar agora, eles serão descartados."
- Toggle **"Gerar descobertas de IA"** também existe comentado/desativado no código (não visível).

**Fluxos:**
1. Usuário preenche um ou mais pares de pergunta/resposta (só pares com ambos os campos preenchidos contam como "válidos").
2. Pode adicionar mais pares ou remover os que não usar.
3. Clica **"Adicionar"** → envio em lote (`createQABatch`).
4. Sucesso: toast **"N perguntas e respostas adicionadas com sucesso!"**, fecha o modal, listagem recarrega.

**Regras e limites:** só pares com pergunta E resposta preenchidas (após trim) entram no envio; não há limite de quantidade de pares na UI.

**Nomes e termos:** "Par" = uma pergunta + sua resposta.

**Perguntas prováveis do usuário:**
- "Posso cadastrar várias perguntas de uma vez?" → Sim, adicionando pares no mesmo formulário.
- "A pergunta e resposta ficam visíveis para o cliente final?" → Só se a audiência incluir "Conhecimento Público" (AI Agent); caso contrário fica restrita ao Copilot/equipe.

**Incertezas:** nenhuma relevante além do valor de créditos (backend).

---

## Modal "Sincronizar site" / "Adicionar páginas" (`SyncWebsiteModal.vue`)

**Como chegar:**
- Propriedades e Fontes > botão **"Site"** (grupo "Adicionar") — ou, na lista vazia, o card **"Sincronizar site"**. Abre no modo normal (dois passos: URL → seleção de páginas).
- A partir do painel de detalhes de um site-raiz já indexado > botão **"Adicionar páginas"** — abre em **modo "Adicionar páginas"** (append mode): pula direto para a seleção, mapeando de novo o site e marcando como não-selecionáveis as páginas já indexadas.

**Para que serve:** Importar o conteúdo de um site (uma página só ou várias) para a base de conhecimento, com opção de escolher exatamente quais páginas indexar.

**Quem vê:** Admin/Gestor da Empresa (herdado).

**Plano, créditos e bloqueios:**
- Selo de IA com tooltip: **"A indexação do conteúdo do site na base de conhecimento do Tino consome créditos. O mapeamento das páginas é gratuito. Acompanhe seu consumo em Configurações → Faturamento → Consumo."** — ou seja, **mapear (descobrir páginas) não custa crédito; indexar (processar o conteúdo) custa.**
- Sem a feature `ai.autonomous`, a opção "Conhecimento Público" some do seletor de audiência (mesmo padrão dos outros modais).
- Aviso de alto volume: com **50 ou mais páginas selecionadas** (`VOLUME_WARN_THRESHOLD`), pede confirmação extra antes de indexar: **"Indexar N páginas?"** / "Indexar muitas páginas de uma vez pode levar alguns minutos e consumir mais créditos. Você pode acompanhar o progresso página a página na lista. Deseja continuar?" — botões "Revisar seleção" / "Indexar mesmo assim".
- No modo append (Adicionar páginas), audiência/descobertas/pasta são **herdadas do site-raiz** pelo backend — o modal não reenvia esses campos.

**O que há na tela:**

*Passo 1 — Input (só no modo normal, não aparece no append):*
- Título: **"Sincronizar site"**.
- Controle de Audiência.
- Campo **"URL do Site"** — texto de apoio: "Informe o endereço principal. Vamos mapear as páginas do site — sem custo — para você escolher o que indexar." — placeholder: *"exemplo.com/ajuda"*. Validação de domínio; se inválida: **"URL inválida. Certifique-se de incluir um domínio válido (ex: exemplo.com)"**.
- Toggle **"Incluir subpáginas do site"** (ligado por padrão) — descrição: "Mapeia as páginas do site para você escolher o que indexar. Desligado, indexa apenas o endereço informado." Desligado, pula direto para indexação da única URL informada (sem tela de seleção).
- Rodapé: "Pronto para mapear" (ou "indexar", se subpáginas desligado) / "Aguardando URL válida"; botões "Cancelar" e **"Mapear site"** (ou **"Indexar página"** com subpáginas desligado; "Mapeando..."/"Indexando..." durante a ação).

*Passo 2 — Seleção de páginas:*
- Título: **"Selecionar páginas"** (ou **"Adicionar páginas"** no modo append).
- Sub-cabeçalho: URL raiz do site + contagem — no modo normal "N páginas · N seções"; no append "N novas · N já indexadas".
- Busca **"Filtrar páginas..."** e botão **"Selecionar tudo"**/**"Limpar"**.
- "Expandir tudo" / "Recolher tudo" (desativados durante busca ativa, que força tudo expandido — aviso "Busca ativa — tudo expandido").
- Lista em árvore de pastas (por segmento de URL), com pastas agrupando páginas por caminho; pastas com 12+ páginas soltas na raiz do site são agrupadas sob **"/ (páginas na raiz)"**; seções grandes paginam com botão **"Mostrar mais N"**.
- Cada página: checkbox, título (ou URL se não houver título), badge **"já indexada"** quando aplicável (não-selecionável), URL e descrição (quando disponíveis).
- A homepage do site é sempre indexada automaticamente e não aparece na lista para (des)seleção.
- Estado vazio: "Nenhuma página corresponde a "{busca}"." ou "Nenhuma página encontrada neste site."
- Rodapé: no modo append e sem páginas novas, aviso: "Todas as páginas encontradas já estão indexadas. Use "Reindexar" para atualizar o conteúdo."; acima do threshold de volume, aviso: "Você selecionou muitas páginas — a indexação pode levar alguns minutos e consumir mais créditos."; contador "**N** selecionada(s)" (ou "N de M selecionada(s)" fora do append); botões "Voltar"/"Cancelar" e **"Indexar N página(s)"** (ou **"Adicionar N página(s)"** no append).

*Estados/confirmações adicionais:*
- Carregando (append mode): "Mapeando páginas do site..." com ícone girando.
- **Voltar para o início** (só modo normal): "Voltar para o início?" / "A seleção de páginas será descartada. Você poderá mapear o site novamente." — "Continuar aqui" / "Descartar".
- **Site já cadastrado (409):** "Site já cadastrado" / "Este site já está cadastrado na base de conhecimento. Deseja reindexar? O conteúdo anterior será excluído e substituído pelo novo." — "Cancelar" / **"Reindexar"** (exclui o registro antigo, aguarda a remoção via WebSocket e reenvia o mesmo pedido de indexação).

**Fluxos:**
1. **Sincronizar site (normal):** informa URL → (se "Incluir subpáginas" ligado) mapeia (grátis) → se encontrar só a página raiz, indexa direto sem tela de seleção; se encontrar mais páginas, abre a tela de seleção → usuário marca as páginas desejadas → "Indexar N páginas" → se ≥50, confirma o aviso de volume → indexação assíncrona (1 job por URL) → toast **"Indexação iniciada! Acompanhe o progresso na lista."** → fecha o modal, lista recarrega e cada página aparece com status evoluindo em tempo real via WebSocket.
2. **Adicionar páginas (append, a partir de um site já indexado):** abre já mapeando o site + comparando com as páginas já indexadas (cruzamento por URL normalizada) → tela de seleção mostra só as novas como selecionáveis → "Adicionar N páginas" → toast **"Páginas adicionadas! Acompanhe a indexação na lista."**
3. **Site duplicado:** ao tentar indexar uma URL já cadastrada, o backend responde 409 → modal de confirmação de reindexação → confirma → exclusão forçada do registro antigo, espera confirmação via WebSocket, reenvia o mesmo pedido → toast **"Reindexação iniciada!"**.
4. **Fallback de domínio:** ao mapear, se a URL sem `www.` falhar ou não retornar links, tenta automaticamente a variante com `www.` antes de mostrar erro (silencioso; só a última tentativa mostra toast de erro: *"Erro ao mapear o site."* ou mensagem do backend).

**Regras e limites:**
- Mapeamento (`mapWebsite`) é síncrono e gratuito, não grava nada.
- Indexação (`indexSelectedPages`) é assíncrona (HTTP 202), 1 job por URL selecionada, numa única chamada (sem batching no cliente) — o backend limita a 1..1000 URLs por chamada.
- Deduplicação de páginas por "identidade de caminho" (ignora `www.` vs ápice, barra final e querystring) — evita indexar a mesma página duas vezes.
- Aviso de volume a partir de 50 páginas selecionadas.

**Nomes e termos:** "Mapear" = descobrir os links do site (grátis); "Indexar" = processar e vetorizar o conteúdo (consome créditos); "Site-raiz" (`isCrawlRoot`) = a propriedade que representa o site como um todo, cujas subpáginas ficam agrupadas dentro dela; "Rescrape"/"Reindexar" = reprocessar conteúdo já indexado.

**Perguntas prováveis do usuário:**
- "Mapear um site custa crédito?" → Não, só a indexação (processamento do conteúdo) consome créditos.
- "Posso adicionar mais páginas depois de já ter sincronizado um site?" → Sim, pelo painel de detalhes do site > "Adicionar páginas".
- "O que acontece se eu tentar sincronizar um site que já está cadastrado?" → A tela oferece reindexar (substitui o conteúdo antigo).

**Incertezas:** não confirmei o valor exato do custo em créditos por página indexada nem o teto de 1000 URLs por chamada do lado do backend (citado em comentário do código-fonte do types, não verificado contra o backend real).

---

## Painel de detalhes da propriedade (`DetailPanel.vue` + `DetailPanelSidebar.vue` + `ContentEditor.vue` + `TiptapMarkdownEditor.vue`)

**Como chegar:** Propriedades e Fontes > clique numa linha da lista (ou "Ver detalhes" no menu ⋮), ou deep link `?contentId=`. Painel lateral grande (pode ir para tela cheia).

**Para que serve:** Ver e editar o conteúdo completo de um documento, Q&A ou página de site já cadastrado; gerenciar audiência, subpáginas de um site e excluir o item.

**Quem vê:** Admin/Gestor da Empresa (herdado). Sem diferenciação de UI por papel.

**Plano, créditos e bloqueios:**
- Edição de conteúdo de DOCUMENT/WEBSITE não é permitida enquanto o item está processando ("Aguarde a indexação concluir") ou falhou ("Reindexe antes de editar") — tooltip do botão de editar muda conforme o estado.
- Sites-raiz (`isCrawlRoot`) só permitem editar a **audiência** (não têm conteúdo próprio editável — quem tem conteúdo são as subpáginas).
- Salvar uma edição de conteúdo **reprocessa e reindexa** o item (volta a status "Processando"); o resultado chega por WebSocket com toast **"Conteúdo re-indexado com sucesso!"** ou, em falha, mensagem de erro do backend (ou "Falha ao re-indexar conteúdo. Tente novamente.").
- Limite de caracteres do conteúdo editável: **500.000 caracteres** (`MAX_CONTENT_CHARS`); acima disso o botão Salvar fica bloqueado e mostra "Limite de 500.000 caracteres excedido" no rodapé do editor.

**O que há na tela:**
- Cabeçalho: ícone do tipo, título (nome do arquivo / pergunta / URL), badge **"Editado manualmente"** (com tooltip "Editado manualmente em {data}") quando `manuallyEdited`.
- Modo visualização — botões: Excluir (lixeira), Editar (lápis, desabilitado se não pode editar), Tela cheia/Sair da tela cheia, Fechar, e um separador antes do toggle "Mostrar detalhes"/"Ocultar detalhes" (painel lateral direito).
- Modo edição — botões: **"Cancelar"** e **"Salvar"** (vira "Salvando..." durante o request).
- Faixa de aviso durante reindexação: **"Re-indexando conteúdo... A edição estará disponível ao concluir."**
- Bloco **"Tino aprendeu"** (quando indexado e há resumo): texto completo do aprendizado + botão **"Testar conhecimentos adquiridos"** (quando há pergunta sugerida) — some em modo edição.
- **Conteúdo por tipo:**
  - **Documento:** Controle de Audiência; "Conteúdo do Documento" com nome do arquivo; em visualização, renderiza o markdown (via `TiptapMarkdownEditor` somente-leitura) ou "Conteúdo não disponível"; em edição, editor WYSIWYG markdown (`ContentEditor` modo `markdown`) — ou aviso "Conteúdo indisponível para edição. Tente reindexar o documento." se o backend não tiver o conteúdo editável.
  - **Q&A:** Controle de Audiência; em visualização, "Pergunta" e "Resposta" (texto puro); em edição, dois campos (input de pergunta, textarea de resposta) com dica: "A pergunta deve ser clara e direta. A resposta deve ser completa e informativa." Campos obrigatórios (marcados com *).
  - **Website:** Controle de Audiência; "Informações do Website" (URL, "Incluir subpáginas: Sim/Não", "Última sincronização" quando houver); se não for site-raiz, também mostra "Conteúdo extraído" (mesmo editor markdown dos documentos, com aviso "Refaça o scraping do website para regenerar" se indisponível); se for site-raiz com subpáginas, mostra a seção "Subpáginas".
- **Seção "Subpáginas"** (só site-raiz com páginas filhas): cabeçalho colapsável "Subpáginas (N total, N falha(s))", botões **"Adicionar páginas"** (abre o `SyncWebsiteModal` em append mode) e **"Reindexar"** (só se já houver páginas na lista) — lista de páginas com status (ícone verde = Indexado, vermelho = Falhou, spinner = processando), botão de retry por página que falhou e botão de excluir subpágina individual.
- **Painel lateral "Dados"** (`DetailPanelSidebar`, colapsável): Tipo (badge), e para documentos também Diretório, Tamanho (KB) e Tipo de arquivo (MIME); "Criado por" (quando houver); "Criado em" e "Última atualização" (datas formatadas pt-BR); Status (badge colorido — mostra o valor bruto do enum: INDEXED/PROCESSING/FAILED, não traduzido nesta sub-tela).
- Confirmações modais: **excluir item** ("Tem certeza que deseja excluir "{título}"?"), **excluir subpágina** ("Tem certeza que deseja excluir a subpágina "{url}"?"), **reindexar todas as subpáginas** ("Reindexar subpáginas" / "O conteúdo das páginas já indexadas será re-extraído e re-indexado. Nada é excluído e nenhuma página nova é descoberta. Deseja continuar?").

**Fluxos:**
- **Editar Q&A:** Editar → altera pergunta/resposta/audiência → Salvar → chama endpoint unificado de update → recarrega a propriedade → sai do modo edição.
- **Editar Documento/Website (conteúdo):** Editar → carrega o conteúdo editável (`getEditableContent`) → edita no editor markdown → Salvar → se a audiência mudou, salva o escopo primeiro (`updatePropertyScope`); se o conteúdo mudou e é válido, salva o conteúdo (`updatePropertyContent`, reindexação assíncrona) → recarrega a propriedade.
- **Testar conhecimentos adquiridos:** fecha o painel e abre a sidebar "Copilot" (`ExperimentalChatSidebar`/`useExperimentalChat`) com a fala inicial da IA preenchida pelo resumo de aprendizado e a pergunta sugerida no campo de digitação (usuário ainda precisa clicar em enviar).
- **Adicionar páginas (a partir daqui):** fecha o painel de detalhes e abre o `SyncWebsiteModal` em modo append, pré-carregado com o id/URL do site-raiz.
- **Reindexar subpáginas (todas):** confirma → chama `reindexWebsitePages` → marca otimisticamente as páginas indexadas como "Processando" → toast **"Reindexação iniciada! O conteúdo das páginas será atualizado."**; o WebSocket confirma a transição real.
- **Retry de subpágina falhada:** clique no ícone de retry → marca como "Processando" e chama `retryProperty`.
- **Excluir subpágina:** confirma → chama `deleteProperty` → remove da lista local → toast **"Subpágina excluída com sucesso!"**.

**Regras e limites:**
- Limite de conteúdo editável: 500.000 caracteres.
- Botão "Salvar" só habilita se: (Q&A) pergunta e resposta preenchidas; (documento/website) houve edição de conteúdo válida OU mudança de audiência.
- Root websites (`isCrawlRoot`) nunca têm editor de conteúdo próprio — só audiência.

**Nomes e termos:** "Editável" = versão em markdown do conteúdo extraído, usada tanto para exibir quanto para editar; "Manualmente editado" = flag que marca quando um humano sobrescreveu o conteúdo extraído automaticamente.

**Perguntas prováveis do usuário:**
- "Por que não consigo editar este documento?" → Está processando, falhou (precisa reindexar antes) ou é um site-raiz (só audiência é editável nesse caso).
- "Se eu editar o texto, ele reprocessa tudo?" → Sim, qualquer edição de conteúdo dispara reindexação assíncrona.
- "Dá para ver quais subpáginas falharam?" → Sim, na seção Subpáginas, com botão de retentar cada uma.

**Incertezas:**
- Não confirmei a regra exata de quando o backend preenche `aiLearningSummary`/`suggestedTestQuestion` (parece ser gerado só na indexação inicial, mas não vi o código do backend).
- O componente-irmão `EditQAModal.vue` parece redundante com a edição inline de Q&A do próprio `DetailPanel` — ver seção "Componentes não referenciados" abaixo.

---

## Modal "Descobertas do Tino para revisão" — sugestões de identidade (`SuggestionsReviewModal.vue`)

**Como chegar:** Propriedades e Fontes > na linha de um item com descobertas pendentes, ícone de "faísca" (AiSparkIcon) na coluna "Descobertas".

**Para que serve:** Revisar itens de identidade (comunicação, diretrizes, conformidade, esclarecimentos, roteamento, contexto situacional) que o Tino sugeriu automaticamente a partir de um documento/Q&A/site específico, para aprovar, editar ou descartar.

**Quem vê:** Admin/Gestor da Empresa (herdado).

**Plano, créditos e bloqueios:** não identifiquei gate específico nesta tela (a geração da sugestão em si ocorre na indexação do conteúdo, que já é onde os créditos são cobrados).

**O que há na tela:**
- Título: **"Descobertas do Tino para revisão"** / subtítulo: "Geradas a partir de: {nome da fonte}".
- Itens agrupados por categoria, na ordem: **Comunicação**, **Diretrizes**, **Conformidade**, **Esclarecimentos**, **Roteamento**, **Contexto Situacional** — cada grupo com contador "({{ N }})" e link **"Ir para o menu"** (navega para a página correspondente em Personalidade/Operações e fecha o modal).
- Dentro de cada pendência: título, corpo (só exibido enquanto pendente), aviso quando a aprovação vai substituir um registro existente: **"Substitui um registro existente ao aprovar"**.
- Ações por item pendente: **"Editar"** (edição inline: campos "Título" e "Conteúdo"), **"Aprovar"**, **"Descartar"**.
- Itens já revisados ficam esmaecidos, com badge **"Aprovada"** ou **"Descartada"**.
- Estado vazio total: "Nenhuma descoberta gerada" / "Tino não gerou itens de identidade a partir deste conteúdo."
- Aviso quando só restam itens já revisados: "Nenhuma descoberta pendente. Tudo que Tino gerou deste conteúdo já foi revisado."

**Fluxos:**
- **Aprovar:** marca o item como aprovado (chama `reviewIdentity` com ação APPROVE), atualiza os badges de contagem na sidebar (Comunicação/Diretrizes/etc.) e emite evento para a lista recarregar.
- **Descartar:** mesmo fluxo, ação REJECT.
- **Editar antes de decidir:** troca para modo edição inline, salva via o serviço correspondente à categoria (comunicação, diretriz, conformidade, esclarecimento, roteamento ou contexto situacional) e mantém o item como pendente para decisão posterior.
- **Ir para o menu:** navega direto para a tela de gestão daquela categoria (ex.: `/identity/personality/communication`) e fecha o modal.

**Regras e limites:** a lista sempre traz pendentes + já revisados (pendentes primeiro), para dar contexto do que já foi decidido sobre aquele conteúdo.

**Nomes e termos:** ver rótulos exatos de categoria acima (idênticos aos usados nos menus de Personalidade/Operações).

**Perguntas prováveis do usuário:** "Por que aparece uma bolinha piscando no ícone de descobertas?" → Indica descobertas pendentes de revisão para aquele conteúdo.

**Incertezas:** não confirmei a lógica exata do backend que decide quando uma sugestão "substitui um registro existente" (`conflictsWithId`).

---

## Modal "Candidatos a processo" (`ProcessSuggestionsReviewModal.vue`)

**Como chegar:** Propriedades e Fontes > na linha de um item com candidatos pendentes, ícone de pilha/stack (PhStack) na coluna "Descobertas".

**Para que serve:** Revisar processos de negócio que o Tino identificou automaticamente a partir de um conteúdo (ex.: um documento descrevendo um fluxo de atendimento), para aprovar (e opcionalmente ativar) ou descartar.

**Quem vê:** Admin/Gestor da Empresa (herdado).

**Plano, créditos e bloqueios:** a área de Processos (mapeamento) em si exige a feature `processes`, mas este modal em particular só lista/revisa candidatos já gerados a partir de uma property — não identifiquei gate adicional na revisão em si.

**O que há na tela:**
- Título: **"Candidatos a processo"** / subtítulo: `Descobertos em "{nome da fonte}"`.
- Lista de candidatos (componente `ProcessesDiscoveryCandidateCard`, fora do escopo desta leitura) com ações de abrir mapeamento, aprovar (com opção de ativar) e descartar.
- Estado vazio: "Nenhum candidato a processo para este conteúdo."
- Confirmação de descarte via `ProcessesDiscardCandidateModal` (fora do escopo desta leitura).

**Fluxos:**
- **Aprovar:** `reviewDiscovery` com ação APPROVE (+ flag `activate` conforme escolha do usuário) → recarrega lista e contagem global de descobertas de processo.
- **Descartar:** pede confirmação → `reviewDiscovery` com ação REJECT.
- **Abrir mapeamento:** não materializa nada — só navega para a sessão de mapeamento de processo (Quattro) associada, em `/identity/processes/mapping/{sessionId}?fromDiscovery={candidateId}`, fechando o modal.

**Regras e limites:** lista sempre com `origin: 'BRAIN'` e `sourcePropertyId` do item clicado — só candidatos originados daquele conteúdo específico.

**Nomes e termos:** "Candidato a processo" = sugestão de fluxo de trabalho detectada automaticamente a partir do conteúdo indexado.

**Perguntas prováveis do usuário:** "O que acontece se eu abrir o mapeamento em vez de aprovar direto?" → Leva para a tela de mapeamento de processo (Quattro) para revisão detalhada, sem consumir o candidato ainda.

**Incertezas:** os componentes `ProcessesDiscoveryCandidateCard` e `ProcessesDiscardCandidateModal` (usados aqui) não fazem parte do escopo de leitura desta tarefa — não documentados em detalhe.

---

## "Testar conhecimentos adquiridos" → sidebar Copilot (`components/identity/ExperimentalChatSidebar.vue` via `useExperimentalChat`)

**Como chegar:** botão **"Testar conhecimentos adquiridos"** no cartão "Tino aprendeu" (lista principal ou painel de detalhes) — ou o botão flutuante **"Copilot"** no canto direito da tela (sempre disponível dentro de `/identity`, layout `layouts/identity.vue`).

**Para que serve:** É o chat real de teste/consulta à base de conhecimento (rótulo do produto: **"Copilot"**), usado para conversar e verificar o que a IA aprendeu com o conteúdo recém-indexado. Não é uma tela própria de Propriedades, mas é o destino direto do fluxo "testar no chat" chamado a partir de Propriedades — por isso documentado aqui de forma resumida (o inventário completo do Copilot deve ficar em outra parte do trabalho).

**Quem vê:** Admin/Gestor da Empresa (herdado do layout `/identity`).

**Plano, créditos e bloqueios:** selo de IA com tooltip **"Cada mensagem enviada ao Copilot utiliza IA e consome créditos. Acompanhe seu consumo em Configurações → Faturamento → Consumo."**

**O que há na tela (resumo):**
- Cabeçalho: **"Copilot"** / "Converse e entenda o Copilot sabe sobre sua empresa" (assim mesmo no código-fonte, sem "o que").
- Seletor de audiência da consulta, rotulado **"Propriedades"**, com opções **"Pública"** (ai_agent) e **"Privada"** (copilot) — mesma terminologia pública/privada da tela de Propriedades, aplicada para restringir contra qual audiência a pergunta de teste é respondida.
- Estado vazio: **"Como posso ajudar?"** / "Envie mensagens para ver o que o Copilot responde com base nas suas propriedades."

**Fluxos (a partir de Propriedades):**
- Clique em "Testar conhecimentos adquiridos" → fecha o painel/cartão de origem → abre a sidebar Copilot já com uma mensagem inicial da IA (o resumo "Tino aprendeu") e a pergunta sugerida pré-preenchida no campo de texto (usuário precisa clicar em enviar — não é automático nesse fluxo).

**Incertezas:** este componente tem 767 linhas e pertence funcionalmente à área "Copilot", não a "Propriedades" — só a parte de abertura/integração (via `useExperimentalChat.openWithInitialMessage`) foi verificada em profundidade aqui. Não documentei exaustivamente o restante da tela (edição de fontes RAG a partir da resposta, anexos, transferências etc.) por estar fora do escopo desta tarefa.

---

## "Consultar Base" / RAG Chat (`components/property/RagChatSidebar.vue` via `useRagChat`) — recurso sem ponto de entrada na UI atual

**Como chegar:** **Não há**, atualmente, nenhum botão ou link visível que abra esta sidebar. Ela é renderizada condicionalmente em `layouts/identity.vue` (`v-if="isLg && isRagChatOpen"`), mas o único gatilho de UI que chamaria `openRagChat()` — um segundo `SharedSidebarBanner` rotulado **"Consulte"** — está **comentado no código-fonte** (`<!-- ... -->`), junto com o comentário indicando que só o banner "Copilot" fica ativo. Não há nenhuma outra chamada a `useRagChat().open()` em todo o projeto.

**Para que serve (pelo código):** Ferramenta de consulta direta ao mecanismo de busca (RAG) da base de conhecimento, com controles técnicos de recuperação — thresholds, reranking, filtros por tipo de fonte — mais próxima de uma ferramenta de debug/QA do que de um recurso voltado ao usuário final.

**Quem vê:** ninguém, na prática — é código morto do ponto de vista de navegação (a menos que outra parte do produto/QA a acesse por algum caminho não encontrado nesta leitura).

**Plano, créditos e bloqueios:** não identificado (a tela nunca é alcançada).

**O que há na tela (para registro, caso seja reativada):**
- Cabeçalho: **"Consultar Base"** / "RAG Chat".
- Estado vazio: "Consulte sua base de conhecimento" / "Faça perguntas para buscar informações na sua base de conhecimento usando RAG."
- Painel de filtros (ícone de "sliders"): **"Configurações de Busca"** — "Tipos de Fonte" (checkboxes: Documentos, Perguntas e Respostas, Websites, Snippets), "Threshold de Similaridade" (slider 0–1, padrão 0,5), "Limite de Resultados" (número, padrão 10, máx. 50), "Usar Reranking" (checkbox).
- Botão de envio: **"Consultar"**.
- Respostas do agente mostram metadados técnicos: quantidade de "chunk(s)" retornados e tempo de recuperação em ms.

**Incertezas:** por que o botão que abriria esta tela está comentado — se é um recurso interno em pausa, uma ferramenta de QA reservada para outro contexto, ou simplesmente esquecida. Recomendo não incluir este recurso na central de ajuda do usuário final até confirmar com o time de produto se ele deve ficar acessível.

---

## Benchmark Competitivo / Strategist Agent (`/identity/properties/intelligence`, `/identity/properties/intelligence/result`) — feature órfã, sem link no menu, dados mockados

**Atenção:** o nome da rota (`intelligence`) e a orientação inicial da tarefa levavam a esperar aqui um "teste/relatório de qualidade da base de conhecimento". **Não é isso.** Pelo código, é um recurso diferente: uma análise de **benchmark competitivo** (framework baseado nos pilares de Marketing de Philip Kotler), conduzida por um "Strategist Agent" via chat, que compara a empresa com concorrentes. E, mais importante: **não encontrei nenhum ponto de entrada no menu ou em qualquer outra tela do produto que leve a esta rota** — não aparece na sidebar do Cérebro (`components/identity/Sidebar.vue` só lista Panorama, Propriedades e Personalidade/Operações, sem submenu de "Inteligência"), nem em nenhum outro `.vue` do projeto.

**Como chegar:** apenas digitando a URL diretamente: `/identity/properties/intelligence`. Não há link de menu, botão ou card em nenhuma outra tela do Cérebro que aponte para cá.

**Para que serve (pelo código):** Iniciar, via chat com um "Strategist Agent", uma análise competitiva de mercado (nome da empresa, site, indústria, até 2 concorrentes) e depois visualizar o resultado em forma de matriz comparativa.

**Quem vê:** Admin/Gestor da Empresa (herdado do layout `/identity`), mas na prática ninguém chega até aqui pela navegação normal.

**Plano, créditos e bloqueios:** não identificado nenhum gate de feature/plano específico no código desta tela.

### Tela inicial (`index.vue`)

- Badge: **"Framework de Análise Competitiva"**.
- Título: **"Descubra como sua empresa se posiciona no mercado"**.
- Subtítulo: "Converse com nosso **Strategist Agent** para uma análise completa baseada nos pilares do Marketing Moderno de Philip Kotler."
- Botão: **"Conversar com Strategist Agent"** → abre um chat inline (`BenchmarkingFrameworkIntakeChat`, fora do escopo desta leitura) que coleta nome da empresa, site, indústria e até 2 concorrentes.
- Ao concluir o intake, cria uma análise (`createAnalysis`) e navega para `/identity/properties/intelligence/{analysis.id}`.

**Achado técnico relevante:** essa navegação para `/identity/properties/intelligence/{id}` **não corresponde a nenhum arquivo de rota existente** — não há `pages/identity/properties/intelligence/[id].vue`, só o arquivo estático `result.vue`. Ou seja, o próprio fluxo interno (chat → criar análise → navegar) parece quebrado/incompleto: ele redireciona para uma URL que o roteamento por arquivo do Nuxt não deveria conseguir resolver da forma esperada.

### Tela de resultado (`result.vue`) — carrega SEMPRE dados fictícios (mock)

- Título da página: **"Benchmark Competitivo"** / subtítulo: "Análise competitiva de mercado, com base em pilares estratégicos do Marketing".
- `loadAnalysis()` não faz nenhuma chamada de API real: espera 800ms e atribui `mockBenchmarkingAnalysis` (de `~/mocks/benchmarking-mock`) — **ignora completamente qualquer id de análise real**, sempre mostra os mesmos dados de exemplo.
- Estado de carregamento: "Gerando matriz comparativa..." / "Aguarde enquanto processamos os dados".
- Estado de erro: "Erro ao carregar dados" / "Ocorreu um erro ao buscar sua análise." com botão **"Tentar Novamente"** (nunca dispara de fato, pois o mock não falha).
- Cartões de resumo: **Score Geral** (%), **Vencedor** ("Você supera os concorrentes"), **Neutro** ("Empate com concorrentes"), **Perdedor** ("Concorrentes estão à frente").
- Tabela **"Análise Detalhada por Recurso"**: agrupada por "Pilar Estratégico" (fundamentos de Kotler), com colunas "Você" vs. cada concorrente/referência global, "Boas Práticas" e "Posição" (ícone vencedor/perdedor/neutro).
- Menu **"Exportar"** com opções **"Exportar PDF"** e **"Exportar Excel"** — **ambas são stubs não implementados** (`console.log('Exportando para PDF...')` / `'Exportando para Excel...'`, com comentário `// TODO: Implementar exportação`). Clicar não gera nenhum arquivo.

**Regras e limites:** nenhuma real — tudo mockado.

**Nomes e termos:** "Strategist Agent" = persona de IA usada nesta análise (distinta do Tino/atendimento e do Copilot); "Pilares de Kotler" = os fundamentos estratégicos de marketing usados para estruturar a matriz comparativa.

**Perguntas prováveis do usuário:** provavelmente nenhuma, já que a tela não é alcançável pela navegação normal do produto. Se um usuário perguntar sobre "benchmark competitivo" ou "Strategist Agent", a resposta correta hoje é que esse recurso existe no código mas não está disponível/publicado na interface.

**Incertezas (importantes):**
- Não confirmei se esta é uma feature "em construção" deliberadamente escondida (flag de ambiente, feature em progresso) ou código morto/abandonado — não há nenhuma referência à rota em nenhum outro lugar do repositório dentro do escopo lido.
- Não encontrei o componente `BenchmarkingFrameworkIntakeChat` no escopo desta tarefa (não estava na lista de arquivos solicitados) — não documentei seu comportamento interno.
- Recomendo fortemente **não incluir esta tela na central de ajuda do usuário final** sem antes confirmar com o time de produto se ela está ativa, planejada ou deve ser ignorada.

---

## Componentes lidos que NÃO estão referenciados em nenhuma tela atual (código morto / legado)

Confirmado por busca em todo o repositório (`.vue`/`.ts`, fora de `node_modules`): nenhum destes quatro componentes é importado ou usado por nenhuma página ou outro componente. Documentados brevemente por terem sido pedidos na leitura, mas **não devem virar artigos na central de ajuda** — não são alcançáveis pelo usuário.

- **`EditQAModal.vue`** — modal "Editar Q&A" com campos Pergunta/Resposta e dica de preenchimento. Redundante com a edição inline de Q&A já existente dentro do `DetailPanel`. Sem nenhuma referência em outro arquivo.
- **`CreateSnippetModal.vue`** — modal "Criar Snippet" (título "Snippet de texto", campos "Título" e "Conteúdo", contador de caracteres, dica: "Snippets são ideais para informações que mudam frequentemente..."). Parece ser um formulário alternativo de Q&A/nota rápida, hoje sem nenhum botão que o abra.
- **`AddContentModal.vue`** — versão antiga/unificada do "Adicionar conteúdo" (um único modal com 3 opções: documento, Q&A, site — cada uma abrindo o sub-modal real), com textos como "Escolha o tipo de conteúdo que deseja adicionar", "Criar conteúdo novo" e "Importar ou sincronizar conteúdo existente". Foi substituído, na tela principal atual, pelos três botões diretos ("Arquivo", "Q&A", "Site").
- **`AddContentSidePanel.vue`** — outra versão legada, um painel único com formulários condicionais por `contentType` (document/qa/website), com textos próprios (ex.: "Upload de Documento", "Pergunta & Resposta", "Sincronizar Website"). Também sem nenhuma referência.

---

## Glossário rápido (Propriedades)

- **Propriedade / Fonte** — cada documento, par de pergunta-e-resposta ou página de site cadastrado na base de conhecimento.
- **Público** (`ai_agent`, rótulo na tela: "Conhecimento Público") — conteúdo usado pelo **AI Agent / Tino** no atendimento automatizado a clientes. Exige plano Scale+ (`ai.autonomous`).
- **Privado** (`copilot`, rótulo na tela: "Conhecimento Privado") — conteúdo usado apenas pelo **Copilot**, o assistente interno da equipe. Disponível em todos os planos.
- **Mapear** — descobrir as páginas de um site (grátis, não indexa nada).
- **Indexar** — processar e vetorizar o conteúdo para a base de conhecimento (consome créditos).
- **Site-raiz** (`isCrawlRoot`) — a propriedade "guarda-chuva" de um site sincronizado com subpáginas; ela mesma não tem conteúdo próprio editável.
- **Descobertas** — sugestões automáticas do Tino a partir de um conteúdo indexado: itens de identidade (comunicação, diretrizes, conformidade, esclarecimentos, roteamento, contexto situacional) ou candidatos a processo.
- **Editado manualmente** — quando um humano sobrescreveu o conteúdo extraído/gerado automaticamente.
- **Tino aprendeu** — resumo em primeira pessoa gerado pela IA após indexar um conteúdo, usado tanto na lista quanto no painel de detalhes para oferecer "testar" o conhecimento no chat Copilot.


# PARTE B: Personalidade
# Personalidade (dentro de Cérebro / `/identity`)

Fonte: clone da main de 03/09/2026, `/private/tmp/claude-501/.../scratchpad/tartini-web`. Rótulo de menu principal: "Cérebro". Grupo no menu lateral: "Personalidade" (`components/identity/Sidebar.vue`, expansível, `personalityExpanded`). Contém 3 telas: Comunicação, Diretrizes, Conformidade.

Acesso: toda a área `/identity` exige Admin da Empresa ou Gestor da Empresa (`auth.isCompanyManagerWide`, `middleware/auth.global.ts`); Gestor de Área/Unidade e Atendente são redirecionados para `/home`. Nenhuma sub-tela de Personalidade tem gate de plano/feature — confirmado por busca (`plan|Plan|feature|Feature|experimental|upgrade|Upgrade`) nos arquivos de página e componentes desta área: nenhuma ocorrência.

## Comunicação (`/identity/personality/communication`)

**Como chegar:** Menu lateral (sidebar do Cérebro) > seção "Personalidade" > item "Comunicação" (ícone `CommunicationIcon`). URL: `/identity/personality/communication`.

**Para que serve:** Permite cadastrar estilos complementares de comunicação (tom formal, casual, técnico, empático etc.) para personalizar como o Tino fala, além dos recursos nativos de comunicação profissional que o Tartini já tem por padrão.

**Quem vê:** Admin da Empresa e Gestor da Empresa (regra geral de `/identity`). Não há diferenciação de comportamento por papel dentro da própria tela — o middleware já barra os demais papéis antes de chegar aqui.

**Plano, créditos e bloqueios:** Nenhum gate de plano ou feature encontrado no código desta tela. Existe um comentário no template comentado (`<!-- ... -->`, portanto NÃO renderizado) que dizia "Você pode criar até **7 estilos** de comunicação" — está comentado no código-fonte (`pages/identity/personality/communication/index.vue`, linha 169), ou seja, esse limite de 7 NÃO está ativo na tela atual (o componente `IdentityPromptList` recebe a prop `maxItems`, mas a página de Comunicação não a passa, então não há limite de itens em vigor aqui).

**O que há na tela:**
- Cabeçalho: título "Comunicação" (h1) e texto de apresentação: "O Tartini já possui recursos nativos de comunicação profissional. Aqui você pode adicionar estilos complementares para personalizar ainda mais o tom do Tino, seja formal, casual, técnico ou empático, adaptando a linguagem ao contexto de cada interação."
- Botão de recolher/expandir a sidebar (`SharedSidebarToggleButton`).
- Bloco "Sugestões do Tino" (componente `IdentityPendingSuggestions`, categoria `communication`) — só aparece quando há sugestões pendentes da IA (ver seção própria abaixo).
- Lista "Estilos cadastrados" (componente `IdentityPromptList`), com:
  - Contagem ao lado do título quando há itens (ex.: "Estilos cadastrados · 3").
  - Botão "Adicionar estilo" (texto exato do botão, com ícone de "+").
  - Cada item cadastrado é um card clicável (mostra título em negrito e a descrição truncada em 2 linhas, mais linha de autoria "editado/criado por Fulano em dd/mm" via `formatAuthorLine`). Não mostra bolinha de Ativo/Inativo aqui (`:show-is-active="false"` — Comunicação não tem toggle de ativo/inativo).
  - Ao clicar no card, ele vira formulário de edição in-line com:
    - Campo de título: placeholder "Ex: Tom formal para clientes corporativos".
    - Campo de texto (textarea, auto-resize até 400px): placeholder "Descreva o estilo de comunicação...".
    - Bloco de "Modelos" (templates) aparece dentro do formulário SOMENTE quando título e texto estão vazios (ex.: ao criar um novo estilo do zero) — mostra até 3 modelos como botões e um link "Explorar modelos".
    - Botão "Excluir" (com ícone de lixeira) quando o item já existe.
    - Botões "Cancelar" e "Salvar" (ou "Adicionar" quando é item novo).
  - Estado vazio: texto exato "Nenhum estilo de comunicação cadastrado".
  - Bloco de "Modelos que outras empresas costumam adotar" no fim da lista (quando não está criando/editando e há modelos disponíveis): mostra até 5 modelos como pills clicáveis (nome truncado em 30 caracteres com "..."), link "Ver todos" (abre modal com todos os modelos), e um botão "Adicionar estilo" ao lado.
  - Aviso "Existem alterações pendentes a serem salvas" (texto exato, em âmbar) quando há edições não salvas em algum outro card.
  - Modal de todos os modelos (`IdentityPromptTemplateModal`): título "Modelos disponíveis" (ou "Modelos para Estilos cadastrados", conforme prop `title`), com abas de categoria: Personalização, Tom de voz, Linguagem, Formatação (rótulos de `categoryLabels`), e grade de cards de modelo (título + trecho do corpo truncado em 150 caracteres).
- Modal `IdentityPendingEditModal` ("Editar sugestão do Tino") — usado quando o usuário clica em "Editar" numa sugestão pendente da IA (ver seção "Sugestões do Tino").

**Fluxos:**
1. **Criar estilo:** clicar "Adicionar estilo" → formulário abre (card com borda preta e sombra) → preencher Título e Estilo de comunicação (ou escolher um modelo, que preenche os dois campos automaticamente) → "Adicionar". Validação: título e texto não podem estar vazios (botão fica desabilitado). Duplicidade: se já existir item com mesmo título (case-insensitive, ignorando espaços) → toast de aviso "Já existe um item com esse título."; se o texto for igual a outro já cadastrado → "Já existe um item com essa descrição." Em caso de sucesso, o backend responde e a lista é atualizada; a página também dispara `refreshAndDetect` do onboarding (indica que criar um estilo pode contar como passo de onboarding).
2. **Editar estilo:** clicar no card → formulário in-line abre com dados atuais → editar → "Salvar". Mesmas validações de duplicidade acima (exceto contra o próprio item).
3. **Excluir estilo:** dentro da edição, clicar "Excluir" → abre modal de confirmação (`SharedDeleteModal`, rótulo de classe "item") → confirmar remove o item da lista.
4. **Usar modelo:** clicar num modelo (nos "atalhos" da lista, no bloco de exploração, ou "Ver todos") → abre/preenche automaticamente o formulário de criação com título e corpo do modelo — usuário ainda pode editar antes de salvar.
5. **Revisar sugestão do Tino:** ver seção "Sugestões do Tino" abaixo (compartilhada entre as 3 telas).

**Regras e limites:**
- Sem limite de quantidade de estilos ativo no código atual (limite de 7 está comentado/desativado).
- Sem campo "Ativo/Inativo" nesta tela (diferente de Diretrizes).
- Título e corpo obrigatórios para salvar (client-side).
- Duplicidade de título OU de corpo bloqueia o salvamento com toast de aviso.
- Itens com `reviewStatus === 'PENDING'` (sugestões da IA ainda não revisadas) não entram nesta lista — aparecem só no bloco de sugestões.
- Registros de origem IA (source `AI`) já aprovados mostram uma marca de origem (`IdentityOriginMarker`) apontando para o documento do Cérebro de onde vieram, quando resolvido via `resolveSourceProperties`.

**Nomes e termos:**
- "Estilo de comunicação" = cada registro cadastrado nesta tela.
- "Tino" = nome do agente de IA de atendimento, mencionado no texto de apresentação e nas sugestões.
- "Sugestões do Tino" = itens propostos pela IA aguardando aprovação/edição/rejeição.

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Quantos estilos de comunicação posso cadastrar?" → Não há limite ativo no código (o texto de limite de 7 está comentado e não aparece na tela).
- "Um estilo de comunicação pode ficar inativo sem ser excluído?" → Não; esta tela não tem toggle Ativo/Inativo (diferente de Diretrizes e Conformidade). Só existe criar, editar e excluir.
- "Se eu editar o texto de uma sugestão do Tino antes de aceitar, o que acontece?" → O texto editado é salvo e a sugestão é automaticamente aprovada (`reviewIdentity('communication', id, 'APPROVE')`) no mesmo ato ("Salvar e aprovar").

**Incertezas:**
- Não encontrei confirmação sobre o que exatamente `refreshAndDetect` (do `useOnboarding`) faz com a criação de um estilo de comunicação — parece disparar detecção de progresso de onboarding, mas o composable não foi lido.
- Não é possível confirmar, só pelo código desta tela, se existe algum limite de caracteres no título ou no corpo do estilo (não há `maxlength` nos campos).
- O texto comentado de limite de "7 estilos" pode ser um vestígio de uma versão anterior do produto — não fica claro se será reativado.

## Diretrizes (`/identity/personality/guidelines`)

**Como chegar:** Menu lateral (sidebar do Cérebro) > seção "Personalidade" > item "Diretrizes" (ícone `PhFileText`). URL: `/identity/personality/guidelines`.

**Para que serve:** Cadastro de diretrizes complementares de atendimento (saudações personalizadas, procedimentos padrão, fluxos específicos do negócio), além das diretrizes nativas de boas práticas que o Tartini já segue.

**Quem vê:** Admin da Empresa e Gestor da Empresa (regra geral de `/identity`).

**Plano, créditos e bloqueios:** Nenhum gate de plano/feature encontrado.

**O que há na tela:**
- Banner condicional `SharedFromFindingBanner`: aparece só quando a rota tem `?from=achado:<id>` (usuário chegou vindo de um "achado" do Diagnóstico). Texto: rótulo "você veio de um achado", explicação (`why`, dinâmica) e botão "voltar ao achado" (com seta para a esquerda). Não é exclusivo de Diretrizes, mas está presente só nesta tela dentre as três de Personalidade (não aparece em Comunicação nem Conformidade no código lido).
- Cabeçalho: título "Diretrizes" (h1) e texto: "O Tartini já possui diretrizes nativas de boas práticas de atendimento. Aqui você pode adicionar diretrizes complementares, como saudações personalizadas, procedimentos padrão e fluxos específicos do seu negócio."
- Bloco "Sugestões do Tino" (`IdentityPendingSuggestions`, categoria `guideline`).
- Lista "Diretrizes cadastradas" (`IdentityPromptList`), com:
  - Botão "Adicionar diretriz".
  - Campo de título: placeholder "Ex: Saudacao inicial" (sem acento, como está escrito no código).
  - Campo de corpo: placeholder "Descreva a diretriz que o agente deve seguir...".
  - Estado vazio: "Nenhuma diretriz cadastrada".
  - Aqui SIM há toggle "Ativo"/"Inativo" por diretriz (bolinha verde = ativo, cinza = inativo na visualização; toggle switch na edição). Ao criar, nasce ativa por padrão (`isActive ?? true`).
  - Mesma estrutura de modelos ("Modelos que outras empresas costumam adotar", modal "Ver todos") com as categorias: Atendimento, Suporte, Conta e acesso, Financeiro.
- Modal `IdentityPendingEditModal` para editar sugestão pendente antes de aprovar — rótulos "Título" e "Diretriz", placeholders "Ex: Saudacao inicial" e "Descreva a diretriz que o agente deve seguir...".

**Fluxos:**
1. **Criar diretriz:** "Adicionar diretriz" → preencher Título + Diretriz (ou usar modelo) → "Adicionar". Mesmas validações de duplicidade de título/corpo do `IdentityPromptList` (toasts "Já existe um item com esse título." / "Já existe um item com essa descrição.").
2. **Editar diretriz:** clicar no card → editar título, corpo e/ou toggle Ativo/Inativo → "Salvar".
3. **Excluir diretriz:** dentro da edição, "Excluir" → modal de confirmação → remove.
4. **Ativar/Inativar:** toggle dentro da edição, salvo junto com "Salvar" (não há ação de toggle isolada fora do formulário de edição).
5. **Revisar sugestão do Tino:** igual às outras telas (ver seção compartilhada).

**Regras e limites:**
- Diretriz tem campo `isActive` (obrigatório na UI, default true ao criar).
- Diretriz tem campo opcional `campaignCategories` no DTO (`GuidelineDto.campaignCategories`, categorias de campanha em que a diretriz vale; vazio/ausente = vale para todas) — **não encontrei nenhum campo de formulário na tela que edite `campaignCategories`**; parece existir no backend/DTO mas não é exposto no formulário desta versão da UI.
- Título e corpo obrigatórios; duplicidade de título ou corpo bloqueia salvar.

**Nomes e termos:**
- "Diretriz" = cada registro desta tela.
- "Ativo"/"Inativo" = se a diretriz está valendo no atendimento ou não (sem excluir).

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Posso desativar uma diretriz sem apagar?" → Sim, toggle Ativo/Inativo dentro da edição.
- "Diretrizes valem só para certas campanhas?" → O tipo de dado (`campaignCategories`) sugere que sim no backend, mas a tela atual não oferece esse controle — não é possível confirmar como isso é definido hoje pela interface.
- "O que muda se eu vim de um achado do Diagnóstico?" → Aparece um banner de contexto explicando por que chegou ali, com botão para voltar ao achado.

**Incertezas:**
- Como (ou se) `campaignCategories` é preenchido hoje, já que não há campo visível no formulário desta tela.
- Por que o banner "Chegou aqui por um achado do Diagnóstico" só está presente no código de Diretrizes entre as três telas de Personalidade (pode ser proposital, por Diretrizes ser destino mais comum de achados de conformidade/atendimento, ou pode ser que as outras telas ainda não tenham recebido esse componente).
- Não confirmei o texto exato de `why` (dinâmico, vem de `useFromFinding`, não lido).

## Conformidade (`/identity/personality/compliance`)

**Como chegar:** Menu lateral (sidebar do Cérebro) > seção "Personalidade" > item "Conformidade" (ícone `PhClipboardText`). URL: `/identity/personality/compliance`.

**Para que serve:** Cadastro das regras de segurança e política da empresa que o Tino deve respeitar em toda conversa (ex.: verificação de identidade antes de tratar de dados sensíveis), além das boas práticas nativas que o Tartini já segue. É a tela mais complexa da área Personalidade: além de criar/editar/excluir regras, define COMO cada regra é cumprida em cada tipo de conversa (receptivo/ativo).

**Quem vê:** Admin da Empresa e Gestor da Empresa (regra geral de `/identity`).

**Plano, créditos e bloqueios:** Nenhum gate de plano/feature encontrado no código desta tela nem dos componentes de Conformidade.

**O que há na tela:**

- Cabeçalho: título "Conformidade" (h1) e texto: "As regras de segurança e política da sua empresa que Tino respeita em toda conversa. O Tartini já segue as boas práticas nativas — aqui ficam as suas."
- Estado de carregamento: `SharedLoading` enquanto busca dados.
- Linha de status (logo abaixo do cabeçalho, com uma bolinha colorida): texto dinâmico (`statusLine`), por exemplo "5 regras no ar · nada aguardando você", ou com pendências: "5 regras no ar · 2 descobertas aguardando você", ou "5 regras no ar · 1 leitura aguardando você". Bolinha fica âmbar (`bg-atencao`) se há descobertas OU leituras aguardando revisão; verde (`bg-ok`) se não há nada pendente. Pluralização: "regra"/"regras", "descoberta"/"descobertas", "leitura"/"leituras" conforme o número.
- Bloco de **Descobertas** (`IdentityComplianceDiscoveries`) — só aparece quando há descobertas pendentes (ver sub-seção própria abaixo).
- Cabeçalho da lista de regras: "Regras no ar · {N}" e texto explicativo: "Toda regra vale nos dois tipos de conversa, sempre. As colunas dizem só **como** cada uma é cumprida em cada um."
- Campo de busca: input tipo `search`, placeholder "Buscar regra", `aria-label="Buscar regra"`. Filtra em tempo real por título ou corpo (case-insensitive).
- Botão "Adicionar regra" (com ícone de "+"), desabilitado enquanto já existe uma regra em criação.
- Componente `IdentityComplianceModeLegend` (legenda "O que significa cada modo de cumprimento" — ver sub-seção abaixo).
- Formulário de regra nova (quando "Adicionar regra" é clicado): aparece ACIMA da tabela, mesmo componente `IdentityComplianceRuleForm` usado para editar (ver sub-seção "Formulário de regra").
- Tabela de regras (`IdentityComplianceRuleTable`) — ver sub-seção abaixo. Só renderiza se há regras visíveis (após filtro de busca).
- Mensagem quando a busca não encontra nada: `Nenhuma regra encontrada para "{busca}".` (aspas curvas “”, valor da busca interpolado).
- Bloco `IdentityComplianceTemplateSuggestions` (modelos de regra) — aparece sempre que não está criando uma regra nova. Ver sub-seção abaixo.
- Rodapé fixo da tela: "Tino lê os documentos do Cérebro e traz aqui as regras de conformidade que encontrar. Você aprova ou mantém como está."
- Modal de confirmação de exclusão (`SharedDeleteModal`), rótulo de classe "regra".

### Sub-seção: Descobertas (`components/identity/compliance/Discoveries.vue`)

**Para que serve:** Mostra as regras de conformidade que o Tino encontrou sozinho ao ler os documentos do Cérebro, ainda não aprovadas — nenhuma delas está valendo no atendimento até ser aprovada. Diferente das outras telas de Personalidade, aqui a "descoberta" já vem com uma leitura de aplicabilidade (em quais fluxos a regra vale e como é cumprida) decidida na mesma extração por IA — aprovar decide as duas coisas (regra + modo) de uma vez.

**O que há na tela:**
- Só renderiza se `items.length > 0`.
- Título: "Tino encontrou {N} regra(s) nos seus documentos" (com ícone de "spark" de IA, `AiSparkIcon`), pluralização "regra"/"regras".
- Texto: "Nenhuma está no ar ainda. Aprove as que valem para a sua operação — o modo de cumprimento já vem preenchido; abra em editar para trocar."
- Badge âmbar "{N} precisa de você" (com ícone de aviso), quando há descobertas que precisam de decisão humana.
- Botão "Aprovar a de rotina" (singular) ou "Aprovar as {N} de rotina" (plural) — aprova em lote todas as descobertas que NÃO precisam de atenção humana (isto é, nenhum fluxo delas está em modo "VERIFY_BY_PROVENANCE").
- Cabeçalho de colunas (visível a partir de telas grandes): coluna de "Receptivo" (subtítulo "o cliente procurou a empresa") e "Ativo" (subtítulo "a empresa procurou o cliente").
- Lista de descobertas, cada uma em um card com:
  - Título da descoberta e, se precisa de atenção, badge "precisa de você" (ícone de aviso).
  - Corpo/descrição da regra.
  - Origem, quando existe (nome da property/documento do Cérebro de onde veio).
  - Se precisa de atenção, texto de explicação: "Tino propôs dispensar a verificação no {receptivo e/ou ativo}, porque ali o contato já veio identificado da base. Até você confirmar, a regra é cumprida ao pé da letra."
  - Se há conflito com regra já existente: "Conflita com uma regra existente; ela será **substituída ao aprovar**." (quando `substituteOnApprove`) ou "Conflita com uma regra existente. Revise antes de aprovar." (caso contrário).
  - Coluna Receptivo e coluna Ativo: mostram o modo de cumprimento proposto para cada fluxo (rótulo de `SATISFACTION_LABELS`), destacado em âmbar quando o modo exige revisão humana.
  - Três botões de ação por linha: ícone de lápis (editar, `aria-label="Editar {título}"`), ícone de X (descartar, `aria-label="Descartar {título}"`), ícone de check (aprovar, `aria-label="Aprovar {título}"`).
- Ao clicar em editar, a linha vira o formulário `IdentityComplianceRuleForm` (variante "discovery") — ver sub-seção "Formulário de regra".
- Paginação: 5 itens por página. Rótulo "{de}–{até} de {N} descoberta(s)". Botões "Anteriores" e "Próximas" (com setas), desabilitados nos limites.

**Fluxos:**
1. **Aprovar uma descoberta diretamente:** clicar no ícone de check → chama `reviewIdentity('compliance', id, 'APPROVE')` → mensagem de sucesso "Sugestão aceita!" (toast padrão do serviço de revisão) → a regra passa a integrar "Regras no ar".
2. **Descartar uma descoberta:** ícone de X → `reviewIdentity('compliance', id, 'REJECT')` → toast "Sugestão negada." → desaparece da lista.
3. **Editar e aprovar uma descoberta:** ícone de lápis → formulário abre in-line, pré-preenchido com título, corpo e os modos propostos pela IA → editar texto e/ou modos → "Aprovar" (ou "Aprovar ao pé da letra") → grava a regra com o texto e modos escolhidos.
4. **Aprovar em lote as "de rotina":** botão "Aprovar {N} de rotina" → dispara N chamadas de aprovação em série (não é uma rota de lote no backend); se todas passarem, toast de sucesso "{N} regra(s) no ar."; se nenhuma passar, toast de erro "Não foi possível aprovar as regras agora."; se parte passar, toast de aviso "{ok} de {total} regras foram aprovadas. As demais continuam na lista."

**Regras e limites:**
- "Precisa de atenção" é definido como: pelo menos um dos dois fluxos (Receptivo/Ativo) está no modo `VERIFY_BY_PROVENANCE` (o único modo que dispensa verificação e por isso é o único que exige confirmação humana).
- Aprovação em lote ("de rotina") só inclui descobertas SEM esse modo em nenhum fluxo.
- Descoberta sem bloco de aplicabilidade (`applicability` ausente) assume modo LITERAL em ambos os fluxos por padrão.

### Sub-seção: Legenda dos modos de cumprimento (`components/identity/compliance/ModeLegend.vue`)

**Para que serve:** Explica em linguagem de negócio (não técnica) o que cada um dos 4 modos de cumprimento de uma regra de conformidade significa, antes que o usuário precise escolher um nos seletores do formulário.

**O que há na tela:**
- Link/botão discreto (fechado por padrão): "O que significa cada modo de cumprimento" (com seta que gira ao abrir/fechar).
- Ao abrir, painel com:
  - Texto: "Toda regra de conformidade vale nos **dois** tipos de conversa, sempre. O que muda entre elas é só o modo, como Tino cumpre a regra em cada uma."
  - Lista de definição (`<dl>`) com os 4 modos, na ordem: Cumprir como está escrito (LITERAL), Perguntar e confirmar (ASK_AND_VERIFY), Não fornecer (WITHHOLD), A origem do contato já identifica, confirmar pelo nome (VERIFY_BY_PROVENANCE). Rótulos exatos vêm de `SATISFACTION_LABELS` (ver Glossário abaixo).
  - Para o modo VERIFY_BY_PROVENANCE, texto extra em âmbar: "precisa da sua confirmação".
  - Para cada modo, dois blocos de texto sob o rótulo "o que isso muda na utilização da regra":
    - **LITERAL:** "Tino segue o texto da regra e nada além dele. É o padrão: nenhuma instrução extra entra na conversa." / "A equipe é avaliada exatamente pelo texto da regra, sem acréscimo."
    - **ASK_AND_VERIFY:** "Antes de tratar do assunto da regra, Tino pede um dado de conferência e espera a resposta. Serve quando não dá para saber quem está do outro lado." / "A equipe passa a ser cobrada por confirmar quem é o cliente antes de tratar do assunto."
    - **WITHHOLD:** "Tino não fornece a informação de que a regra trata, em nenhuma hipótese, e diz ao cliente que aquilo não pode ser resolvido por mensagem." / "A equipe é cobrada por também não fornecer aquilo por mensagem."
    - **VERIFY_BY_PROVENANCE:** "Tino dispensa a conferência porque o contato veio da sua base e já chegou identificado, basta confirmar pelo nome. Tira atrito em campanha, mas retira uma checagem." / "A equipe deixa de ser cobrada por pedir o dado de conferência nesse tipo de conversa."
  - Link "Ver o texto exato que Tino recebe" (alterna para "Ocultar o texto exato que Tino recebe" quando aberto): revela, por modo, o texto literal (a "cláusula") que é injetado no prompt do Tino e na avaliação do Scout (avaliador de qualidade). Rótulos: "texto exato recebido pelo Tino"; quando não há texto adicional: "nada é acrescentado, a regra vai para o Tino exatamente como você escreveu."; quando há: mostra o texto do atendente e, se houver, uma linha "avaliação da equipe: {texto}". Enquanto carrega: "carregando…".

**Fluxos:**
- Abrir a legenda não faz nenhuma chamada de rede — é só um texto estático.
- Abrir "Ver o texto exato que Tino recebe" dispara, na primeira vez, uma chamada por modo (`previewApplicability`) para buscar a cláusula real; falha silenciosamente (painel simplesmente não mostra nada extra) se o endpoint falhar.

**Regras e limites:**
- Ordem fixa dos modos nos seletores e na legenda: LITERAL, ASK_AND_VERIFY, WITHHOLD, VERIFY_BY_PROVENANCE.
- Apenas VERIFY_BY_PROVENANCE exige confirmação humana (retorno `true` de `needsHumanReview`).

**Nomes e termos:**
- "Scout" = o avaliador de qualidade que audita o atendimento (mencionado só aqui, na legenda, como "avaliação da equipe").

### Sub-seção: Formulário de regra (`components/identity/compliance/RuleForm.vue`)

**Para que serve:** Formulário único usado tanto para editar uma descoberta pendente quanto para criar/editar uma regra já no ar — muda só as ações disponíveis no rodapé (variante `discovery` ou `rule`).

**O que há na tela:**
- Campo de título: input, placeholder "Ex: Verificação de titularidade", `aria-label="Título da regra"`.
- Campo de corpo: textarea (3 linhas visíveis, sem redimensionar manualmente), placeholder "Descreva a regra de conformidade...", `aria-label="Texto da regra"`.
- Texto de ajuda: "Escreva como você diria a um atendente novo. O texto vai para o Tino exatamente assim."
- Bloco "como é cumprida": rótulo "vale nos dois tipos de conversa, sempre, aqui você escolhe só o modo de cada um". Dois seletores (`<select>`), um para Receptivo e outro para Ativo, cada um com as 4 opções de modo (rótulos de `SATISFACTION_LABELS`). O rótulo de cada seletor mostra o nome curto do fluxo em minúsculas e a explicação longa (ex.: "receptivo · o cliente procurou a empresa"). Seletor fica com destaque âmbar quando o modo escolhido é VERIFY_BY_PROVENANCE.
- Mensagem de rodapé, dinâmica, conforme o que foi alterado:
  - Se os modos foram tocados: "Sua escolha vale a partir de agora e não volta para a fila."
  - Se só o texto mudou (modos intocados): "Tino vai reler onde esta regra vale em alguns segundos."
  - Se nada mudou: nenhuma mensagem.
- Toggle "Ativo"/"Inativo" — só aparece quando NÃO é uma descoberta (variante `rule`).
- Botão "Excluir" (ícone de lixeira) — só quando é uma regra existente (não é descoberta e não é nova).
- Botão "Descartar" — só quando é descoberta.
- Botão "Cancelar" — sempre.
- Botão "Aprovar ao pé da letra" — só em descoberta; grava a regra com LITERAL/LITERAL explicitamente, marcando a decisão como humana.
- Botão principal (com ícone de check): texto "Aprovar" (descoberta), "Adicionar" (regra nova) ou "Salvar" (regra existente), conforme o caso.
- Texto de rodapé fixo (só para regra existente, não nova): "Deixar inativa é reversível e guarda a leitura do Tino. Excluir apaga as duas coisas: se você recriar a regra depois, ela passa por uma leitura nova."

**Fluxos e regras técnicas importantes:**
- **Presença dos modos no payload decide o comportamento no backend:** se o usuário mexeu em qualquer um dos dois seletores de modo (`modesTouched`), os modos são enviados no payload de salvar e o backend grava isso como decisão humana definitiva, sem reprocessar. Se o usuário só editou o texto (título/corpo) sem tocar nos seletores, os modos NÃO são enviados, e o backend entende que deve reler (IA relê a aplicabilidade da regra).
- Botão de salvar/aprovar fica desabilitado se título ou corpo estiverem vazios.
- Ao aprovar "ao pé da letra" (só em descoberta), os modos LITERAL/LITERAL são enviados explicitamente (mesmo que a IA tivesse proposto outra coisa), carimbando como decisão humana.

**Nomes e termos:**
- "como é cumprida" = seção do formulário com os dois seletores de modo.
- Rótulo do fluxo Receptivo: "o cliente procurou a empresa". Rótulo do fluxo Ativo: "a empresa procurou o cliente".

**Incertezas:**
- Não há `maxlength` explícito nos campos de título/corpo da regra no código lido.

### Sub-seção: Tabela de regras no ar (`components/identity/compliance/RuleTable.vue`)

**Para que serve:** Lista as regras de conformidade já aprovadas (no ar), com o modo de cumprimento vigente em cada fluxo e, quando aplicável, uma releitura proposta pela IA aguardando confirmação.

**O que há na tela:**
- Cabeçalho de colunas (telas grandes): Receptivo / Ativo, com os mesmos subtítulos da tela de Descobertas.
- Cada regra é um card/linha clicável (abre edição in-line ao clicar em qualquer parte da linha, papel `button` com suporte a teclado Enter/Espaço):
  - Bolinha de status: verde (`bg-ok`) = tudo certo; âmbar (`bg-atencao`) = aguardando revisão ou leitura falhou; cinza (`bg-gray-light`) = regra inativa.
  - Título da regra, badge "precisa de você" (quando a leitura de aplicabilidade está PENDING), rótulo "inativa" (quando `isActive` é falso).
  - Corpo da regra (texto integral, quebras de linha preservadas).
  - Linha de metadados/proveniência (`metaLine`), montada com até 4 partes, cada uma só quando existe:
    - "no ar desde {data} · {revisor}" (se foi revisada por alguém) OU "criada em {data} · {criador}" (se foi criada manualmente sem revisão, já nasce aprovada).
    - "descoberta em {nome do documento}" (se veio de um documento do Cérebro).
    - "leitura ajustada por {nome}" (se alguém corrigiu manualmente a leitura de aplicabilidade).
    - "atualizando a leitura…" (se a releitura está em processamento).
  - Se a leitura está pendente (`reviewStatus === 'PENDING'` na aplicabilidade): texto explicando o que a IA propôs, ex.: "Você editou esta regra; Tino releu e propôs dispensar a verificação no {receptivo e/ou ativo}. Até você confirmar, a regra é cumprida ao pé da letra." (varia conforme é primeira leitura ou releitura pós-edição, `version > 1`).
  - Se a releitura falhou (`derivation === 'failed'`): "Não conseguimos reler esta regra depois da sua edição. Até conseguirmos, ela é cumprida pela leitura anterior." + botão "Tentar de novo".
  - Colunas Receptivo/Ativo: mostram o modo EM VIGOR hoje (se a leitura não estiver aprovada, mostra sempre LITERAL, nunca o que a IA propôs); se há uma proposta pendente diferente do modo vigente, mostra "proposto: {modo}" abaixo, em âmbar.
- Ao clicar, a linha vira o mesmo `IdentityComplianceRuleForm` (variante "rule"), pré-preenchido com o modo em vigor.

**Regras e limites:**
- O modo mostrado na tabela é sempre o que está VALENDO (aprovado), nunca uma proposta não confirmada — regra de segurança: nunca mostrar como vigente algo que a IA só sugeriu.
- "Tentar de novo" chama o reprocessamento pelo id do JULGAMENTO (`applicability.id`), não pelo id da regra — são registros diferentes no backend.

### Sub-seção: Sugestões de modelos de Conformidade (`components/identity/compliance/TemplateSuggestions.vue`)

**Para que serve:** Oferece modelos de regras de conformidade comuns para começar rápido, e serve de estado vazio guiado quando a empresa ainda não tem nenhuma regra nem descoberta.

**O que há na tela:**
- **Estado vazio total** (nenhuma regra, sem busca ativa, não está criando): bloco central com:
  - Título: "Nenhuma regra de conformidade ainda".
  - Texto: "Escreva a primeira, ou comece por um destes modelos que outras empresas costumam adotar, você pode ajustar o texto antes de salvar."
  - Até 6 modelos como pills clicáveis + link "Ver todos" se houver mais.
- **Com regras já cadastradas:** bloco discreto (borda tracejada) no fim da lista: "Modelos que outras empresas costumam adotar" + link "Ver todos" (se houver mais de 5) + até 5 pills de modelo (título truncado em 34 caracteres com "…").
- Modelos já usados (mesmo título de uma regra já cadastrada, comparação case-insensitive) somem da vitrine (não aparecem nem desabilitados).
- Caso extremo: sem modelos disponíveis (todos já usados) e sem regras: "Nenhuma regra de conformidade cadastrada."
- Reaproveita o modal `IdentityPromptTemplateModal`, título "Modelos de conformidade", com categorias: Geral, Indústria, Comércio, Serviços.
- Clicar num modelo NÃO cria a regra direto — abre o formulário de criação já preenchido com título e corpo do modelo, para revisão antes de salvar.

**Regras e limites:**
- Modelos de conformidade disponíveis (arquivo `data/templates/compliance.json`), 12 no total, cobrindo: Promessa de Features Futuras, Verificação de Titularidade (categoria Geral); Alteração de Especificação, Comunicação de Garantia Mínima, Coleta Prévia de Dados Técnicos (Indústria); Garantia de Estoque, Definição de Faturamento, Sugestão por Prova Social (Comércio); Promessa de Retorno, Disclaimer de Rentabilidade, Prioridade do Plano Anual, Sondagem de Objetivos (Serviços).

### Conformidade — Fluxos completos

1. **Criar regra do zero:** "Adicionar regra" → formulário abre acima da lista, com modos padrão LITERAL/LITERAL → preencher Título + Texto (ou clicar num modelo, que abre o formulário já preenchido) → escolher os modos de Receptivo e Ativo se necessário → "Adicionar". Regra nasce `isActive: true` por padrão.
2. **Editar regra no ar:** clicar na linha da tabela → formulário in-line → alterar texto e/ou toggle Ativo/Inativo e/ou modos → "Salvar". Se só o texto mudou (sem tocar nos modos), a IA relê a aplicabilidade em alguns segundos e o resultado aparece como pendência (bolinha âmbar + "precisa de você" + texto explicativo) até o usuário confirmar. Se os modos foram alterados manualmente, valem imediatamente e não entram na fila de releitura.
3. **Excluir regra:** dentro da edição, "Excluir" → modal de confirmação (nome da regra, classe "regra") → confirmar remove a regra E a leitura de aplicabilidade; se recriada depois, passa por leitura nova.
4. **Buscar regra:** digitar no campo de busca → filtra por título ou corpo, em tempo real, sem chamada de rede.
5. **Revisar descoberta (regra nova sugerida pela IA):** ver sub-seção Descobertas acima — aprovar (com ou sem edição), aprovar ao pé da letra, descartar, ou aprovar em lote as "de rotina".
6. **Confirmar releitura de regra editada:** quando a IA relê uma regra editada e propõe soltar a verificação em algum fluxo, a linha fica âmbar com "precisa de você"; o usuário abre a edição, confere os modos propostos (já vêm preenchidos) e clica "Salvar" para confirmar, ou ajusta antes de salvar.
7. **Tentar de novo após falha de releitura:** botão "Tentar de novo" na linha da regra reenfileira o reprocessamento; toast de sucesso "Vamos reler esta regra." ou erro "Nao foi possivel reprocessar a leitura agora." (mensagem sem acentuação, como está no código-fonte).
8. **Usar modelo de conformidade:** clicar num modelo → abre formulário de criação pré-preenchido → usuário revisa/ajusta e salva.

### Conformidade — Regras e limites (consolidado)

- Toda regra de conformidade vale SEMPRE nos dois fluxos de conversa (Receptivo e Ativo) — não é possível restringir uma regra a só um fluxo pela tela; o que varia entre os fluxos é apenas o MODO de cumprimento.
- 4 modos possíveis: LITERAL (padrão), ASK_AND_VERIFY, WITHHOLD, VERIFY_BY_PROVENANCE. Somente VERIFY_BY_PROVENANCE exige confirmação humana explícita (é o único que "dispensa" uma verificação).
- Enquanto a leitura de aplicabilidade de uma regra não estiver aprovada (pendente, rejeitada ou inexistente), a regra é cumprida em modo LITERAL por padrão — nunca aplica um modo apenas proposto sem confirmação.
- Editar o texto de uma regra sem tocar nos seletores de modo dispara releitura automática pela IA (assíncrona, com atraso de alguns segundos conforme comentário no código).
- Editar/definir os modos manualmente marca a decisão como humana e definitiva — não é sobrescrita por releituras futuras da IA.
- Descartar/excluir e depois recriar uma regra faz a leitura de aplicabilidade recomeçar do zero.
- Toggle Ativo/Inativo é reversível e preserva a leitura de aplicabilidade; excluir apaga regra e leitura.
- Aprovação em lote das descobertas "de rotina" é feita com N chamadas sequenciais (não transacional) — falha parcial é possível e é comunicada ao usuário via toast proporcional.

### Conformidade — Glossário

- **Regra de conformidade**: registro de política/segurança que o Tino deve seguir.
- **Descoberta**: regra de conformidade que a IA encontrou sozinha nos documentos do Cérebro e ainda não foi aprovada.
- **Regras no ar**: regras já aprovadas e valendo no atendimento.
- **Receptivo**: fluxo em que o cliente procurou a empresa (INBOUND).
- **Ativo**: fluxo em que a empresa procurou o cliente, vindo da base (OUTBOUND).
- **Modo de cumprimento / satisfação**: como a regra é cumprida em cada fluxo (Cumprir como está escrito / Perguntar e confirmar / Não fornecer / A origem do contato já identifica, confirmar pelo nome).
- **Leitura / julgamento de aplicabilidade**: a decisão (da IA ou humana) de onde e como a regra vale, separada da regra em si no banco de dados.
- **Scout**: avaliador de qualidade que audita o atendimento (mencionado na legenda de modos).
- **Tino**: agente de IA de atendimento.

### Conformidade — Perguntas prováveis do usuário e resposta segundo o código

- "Posso fazer uma regra valer só no atendimento ativo (campanha) e não no receptivo?" → Não; toda regra vale sempre nos dois fluxos. O que você controla é COMO ela é cumprida em cada um (inclusive dispensando verificação em um deles via VERIFY_BY_PROVENANCE).
- "Se eu editar o texto de uma regra, ela para de valer até eu confirmar de novo?" → Não; a regra continua valendo com a última leitura aprovada (ou LITERAL, se nunca houve leitura aprovada) enquanto a IA relê em segundo plano; só muda quando você confirmar a nova leitura.
- "Por que uma regra ficou marcada 'precisa de você'?" → Porque a IA propôs dispensar a verificação (VERIFY_BY_PROVENANCE) em pelo menos um dos fluxos, e isso exige sua confirmação explícita.
- "O que acontece se eu clicar 'Aprovar ao pé da letra' numa descoberta?" → A regra é aprovada com modo LITERAL/LITERAL em ambos os fluxos, independentemente do que a IA tinha proposto, e isso é registrado como decisão humana.
- "Posso ver o texto exato que vai para o prompt do Tino?" → Sim, na legenda de modos, atrás do link "Ver o texto exato que Tino recebe" (carrega sob demanda).

### Conformidade — Incertezas

- Não encontrei o texto de `useFromFinding` (`why` dinâmico) nem confirmação de que o banner de achado do Diagnóstico também aparece em Conformidade (não vi `SharedFromFindingBanner` no código de `pages/identity/personality/compliance/index.vue` — parece que só Diretrizes tem esse banner).
- Não é possível confirmar pelo código lido qual é o atraso exato ("alguns segundos") da releitura automática além do comentário no código-fonte.
- Não encontrei limite de caracteres ou de quantidade de regras de conformidade.
- Não confirmei o comportamento exato quando duas regras entram em conflito (`conflictsWithId`) fora do que está descrito na interface (texto de aviso) — a lógica de detecção de conflito está no backend, não neste código-fonte.

## Sugestões do Tino (bloco compartilhado em Comunicação e Diretrizes)

**Como chegar:** Aparece automaticamente no topo das telas Comunicação e Diretrizes (componente `IdentityPendingSuggestions` / `components/identity/PendingSuggestions.vue`), acima da lista de itens cadastrados, só quando há sugestões pendentes daquela categoria. (Conformidade usa um bloco próprio e mais rico, `IdentityComplianceDiscoveries` — ver seção Conformidade acima — em vez deste componente genérico.)

**Para que serve:** Mostra registros (estilos de comunicação ou diretrizes) que o Tino sugeriu ao analisar o conteúdo do Cérebro, para o usuário aceitar, editar-e-aceitar, ou negar, antes que passem a valer no atendimento.

**Quem vê:** Mesmos papéis da área (Admin/Gestor da Empresa).

**Plano, créditos e bloqueios:** Nenhum encontrado.

**O que há na tela:**
- Cabeçalho: "Sugestões do Tino" + badge circular com a contagem.
- Texto: "Tino analisou o conteúdo do Cérebro e sugeriu os registros abaixo. Eles **não afetam o atendimento** enquanto não forem aceitos."
- Cada sugestão é um card com borda destacada (`border-ia/40`):
  - Selo "Sugerido pelo Tino" (com ícone de spark de IA).
  - Título e corpo da sugestão.
  - Bloco "Por que Tino sugeriu: {aiRationale}" — só quando a IA registrou uma justificativa.
  - Marca de origem (`IdentityOriginMarker`) — quando há `sourcePropertyId`, aponta para o documento do Cérebro de origem.
  - Aviso de conflito: "Conflita com um registro existente; ele será **substituído ao aprovar**." (quando `substituteOnApprove`) ou "Conflita com um registro existente. Revise antes de aprovar." (caso contrário) — mesmo padrão de texto da tela de Conformidade, mas com "registro" no lugar de "regra".
  - Três botões: "Negar" (ícone X, estilo de erro), "Editar" (ícone lápis), "Aceitar" (ícone check).

**Fluxos:**
1. **Aceitar direto:** botão "Aceitar" → aprova a sugestão como está (`review(categoria, id, 'APPROVE')`) → recarrega a lista da página (evento `reviewed`).
2. **Negar:** botão "Negar" → rejeita (`REJECT`) → some da lista.
3. **Editar antes de aceitar:** botão "Editar" → abre o modal `IdentityPendingEditModal` ("Editar sugestão do Tino") com os campos Título e (Estilo de comunicação/Diretriz, conforme a tela) pré-preenchidos → texto do modal: "Ajuste o conteúdo antes de aprovar. Ao salvar, a sugestão será aplicada e ativada." → botões "Cancelar" e "Salvar e aprovar" → ao salvar, o item é atualizado com o novo texto E aprovado no mesmo ato (update + `reviewIdentity(..., 'APPROVE')`).

**Regras e limites:**
- Botões ficam desabilitados individualmente enquanto aquele item específico está em processamento (evita duplo clique).
- "Salvar e aprovar" só habilita quando título e corpo não estão vazios.

**Nomes e termos:**
- "Sugestão do Tino" = item ainda não revisado, proposto pela IA.
- `aiRationale` = "Por que Tino sugeriu" (justificativa da IA).

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Uma sugestão do Tino já vale no atendimento assim que aparece?" → Não; o texto da própria tela garante que sugestões "não afetam o atendimento enquanto não forem aceitas".
- "Se eu editar uma sugestão, preciso aprovar depois separadamente?" → Não; salvar a edição no modal já aprova a sugestão no mesmo clique ("Salvar e aprovar").

**Incertezas:**
- Não localizei o componente `IdentityOriginMarker` (mencionado/usado, mas fora do escopo de arquivos pedidos) — não confirmei o texto exato exibido na marca de origem.
- Não confirmei visualmente (sem rodar o app) o texto do badge de contagem nem eventuais diferenças de rótulo entre categorias além do que está no template genérico.

---

## Observações finais

- As 3 telas de Personalidade (Comunicação, Diretrizes, Conformidade) e o bloco de Sugestões do Tino não têm nenhum texto de erro genérico de rede fora dos toasts padrão dos services (`services/identity.service.ts`, `services/identity-review.service.ts`, `services/identity-applicability.service.ts`), listados nas seções acima.
- Toasts de erro genéricos por operação (mensagens exatas de `identity.service.ts`), reutilizados nas 3 telas:
  - Comunicação: "Erro ao carregar estilos de comunicação.", "Estilo de comunicação adicionado!", "Erro ao adicionar estilo de comunicação.", "Estilo de comunicação atualizado!", "Erro ao atualizar estilo de comunicação.", "Estilo de comunicação removido!", "Erro ao remover estilo de comunicação."
  - Diretrizes: "Erro ao carregar diretrizes.", "Diretriz adicionada!", "Erro ao adicionar diretriz.", "Diretriz atualizada!", "Erro ao atualizar diretriz.", "Diretriz removida!", "Erro ao remover diretriz."
  - Conformidade: "Erro ao carregar regras de conformidade.", "Regra adicionada!", "Erro ao adicionar regra.", "Regra atualizada!", "Erro ao atualizar regra.", "Regra removida!", "Erro ao remover regra."
  - Revisão de sugestões (todas as categorias): "Sugestão aceita!", "Sugestão negada.", "Erro ao aceitar sugestão.", "Erro ao negar sugestão." (mensagens do backend têm prioridade quando presentes, via `err.response?.data?.message`).


# PARTE C: Operações
# Cérebro > Operações — inventário de telas

Fonte: clone da main de 03/09/2026 em `tartini-web`. Área acessada pelo menu principal **Cérebro** (rota raiz `/identity`) > seção **Operações** na sidebar secundária. Toda a área exige papel Admin da Empresa ou Gestor da Empresa (`auth.isCompanyManagerWide`); Gestor de Área/Unidade e Atendente são redirecionados para `/home` (middleware `auth.global.ts`, fora do escopo destes arquivos).

Gate de plano: TODAS as rotas `/identity/operations/*` (as seis: availability, routing, qualification, clarifications, situational-context, contact-statuses) caem no mesmo matcher em `utils/entitlements.ts`:
```
{ match: (p) => p.startsWith('/identity/operations'), feature: FEATURE.AI_OPERATIONS }
```
Não há gate diferenciado por sub-tela nem por painel dentro delas — é um único `PlanUpgradeWall` cobrindo qualquer uma das seis rotas quando o plano não tem `ai.operations`. Texto do wall (idêntico para as seis, vem de `components/billing/PlanUpgradeWall.vue`):
- Rótulo da feature: "Operação do Tino" (mapa `LABELS['ai.operations']`)
- Título: **"Operação do Tino não está no seu plano"**
- Subtexto: **"Disponível a partir do plano Scale. Faça upgrade para liberar este recurso."**
- Botão: **"Fazer upgrade de plano"** (ícone de seta), leva para `/settings/billing/credits?planos=1`
- Rodapé: "Plano atual: {auth.planCode}" (se existir)
- Sem botão de fechar (X) quando o bloqueio é de ROTA (não é o gatilho manual) — `canDismiss` é falso; a única saída é clicar em outro item do menu, que continua visível e clicável ao lado do blur.
- O item de menu correspondente continua visível na sidebar mesmo sem a feature (comentário no código: "Cérebro: Processos e Operações seguem no menu, mas o plano sem a feature vê o wall ao abrir").

## Disponibilidade (`/identity/operations/availability`)

**Como chegar:** Menu principal "Cérebro" > sidebar secundária, seção "Operações" > item "Disponibilidade" (ícone de relógio).

**Para que serve:** Definir o fuso horário base da empresa e as faixas de horário em que a IA/empresa está em atendimento, por dia da semana.

**Quem vê:** Só Admin/Gestor da Empresa acessam a rota (redirecionamento em nível de `/identity` como um todo). Não há diferenciação de papel dentro da própria tela — não encontrei `canManage`/checagem de papel específica neste arquivo (a página não usa `auth.isCompanyManagerWide` diretamente, ao contrário de "Status de contato").

**Plano, créditos e bloqueios:** Gate padrão da área (`ai.operations`, ver introdução). Sem "experimental" ou aviso adicional específico desta tela.

**O que há na tela:**
- Cabeçalho: "Disponibilidade" + "Configure os horários de funcionamento e disponibilidade da empresa."
- Skeleton de carregamento (placeholders animados) enquanto `isLoading`.
- Dois cartões de resumo (grid 2 colunas):
  - "Dias configurados": `{n}/7` (ícone `PhCalendarDots`, fica verde/"ok" se > 0)
  - "Faixas de horário": contagem total de slots (ícone `PhClock`)
- Cartão "Fuso Horário" (`PhGlobe`):
  - Texto: "Define o fuso horário base para os horários de atendimento"
  - Badge (só desktop) com o fuso selecionado formatado, ex. "São Paulo (GMT-3)"
  - `<select>` (aria-label "Fuso horário") com as opções fixas (hardcoded, não vem da API):
    - São Paulo (GMT-3) — valor `America/Sao_Paulo`, padrão
    - Fortaleza (GMT-3)
    - Manaus (GMT-4)
    - Cuiabá (GMT-4)
    - Rio Branco (GMT-5)
    - New York (GMT-5)
    - Los Angeles (GMT-8)
    - London (GMT+0)
    - Lisbon (GMT+0)
  - Ao trocar o `<select>` (`@change`), chama `updateAvailability({ timezone })` imediatamente — não há botão "Salvar" separado para o fuso.
- Cartão "Horários de Atendimento" (`PhClock`):
  - Texto: "Clique em um dia para editar. Use **Seg-Sex** ou **Todos** para replicar."
  - Se não há nenhum slot configurado, alerta (ícone `PhWarning`, cor "atenção"): "Nenhum horário configurado. Clique em um dia da semana abaixo para adicionar horários de atendimento."
  - Durante a replicação (`isReplicating`), aparece um spinner com o texto "Replicando horários..." cobrindo a lista.
  - Lista de dias (componente `IdentityTimeSlotList`, ver abaixo).

### Lista de horários por dia (`components/identity/TimeSlotList.vue`)
- 7 linhas, uma por dia da semana, na ordem **Segunda-feira, Terça-feira, Quarta-feira, Quinta-feira, Sexta-feira, Sábado, Domingo** (ou seja, começa na segunda e termina no domingo — não é ordem 0-6 do JS).
- Estado colapsado de cada dia mostra:
  - Nome do dia
  - Prévia dos horários já cadastrados, formato `HH:mm - HH:mm` separados por " | " (ex.: "09:00 - 12:00 | 13:00 - 18:00")
  - Linha de autoria do slot mais recentemente atualizado: "Última alteração por {nome} em {data}" (via `formatAuthorLine`)
  - Botões "Seg-Sex" e "Todos" (só aparecem se o dia já tem pelo menos 1 slot) — replicam os horários DESSE dia para os outros
  - Contador à direita: "Sem horário" / "1 horário" / "N horários"
- Clicar num dia expande o card (só um por vez; clicar em outro dia enquanto há alterações pendentes é bloqueado — os outros dias ficam com opacidade reduzida e `cursor-not-allowed`).
- Estado expandido:
  - Lista de faixas de horário do dia, cada uma com dois campos `type="time"` (início / "até" / fim) e botão de lixeira (`PhTrash`, aria-label "Remover horário") para remover a linha.
  - Se não há nenhuma faixa: "Nenhum horário cadastrado para este dia."
  - Botão "Adicionar horário" (ícone `PhPlus`) — adiciona uma linha vazia (start/end em branco).
  - Rodapé: botões "Cancelar" e "Salvar" (Salvar fica desabilitado se alguma faixa tiver início ou fim vazio — `canSave`).
- Aviso global: "Existem alterações pendentes a serem salvas" aparece abaixo da lista quando há um dia em edição com mudanças não salvas (comparação profunda via `lodash.isEqual` contra o snapshot original).

**Fluxos:**
1. **Trocar fuso horário:** selecionar no `<select>` → chama a API imediatamente (`PUT /operations/availability`) → toast de sucesso "Fuso horário atualizado!" (ou erro).
2. **Configurar horários de um dia:** clicar no dia → expande → adicionar/remover faixas com os campos de hora → "Salvar" → a página primeiro identifica quais slots existentes sumiram da lista nova e chama `DELETE /operations/availability/slots/:id` para cada; depois, para cada slot restante, faz `PUT` (se já tinha id) ou `POST /operations/availability/slots` (se é novo) com `{ dayOfWeek, startTime, endTime, isActive: true }`; ao final recarrega os dados (`loadData`) e roda `refreshAndDetect()` do onboarding. Toasts individuais por chamada de API ("Horário adicionado!", "Horário atualizado!", "Horário removido!").
3. **Replicar horários de um dia:** clicar "Seg-Sex" (aplica aos dias 1-5, ou seja, segunda a sexta) ou "Todos" (aplica a todos os 7 dias, 0-6) a partir de um dia que já tem horários — para cada dia de destino (exceto o próprio dia de origem), apaga todos os slots existentes daquele dia e cria cópias exatas dos slots de origem. Mostra spinner "Replicando horários..." durante o processo. Ao terminar: toast "Horários replicados para todos os dias!" ou "Horários replicados para Seg-Sex!" conforme o alvo.

**Regras e limites:**
- Não há limite documentado de quantidade de faixas por dia.
- Salvar um dia é bloqueado (botão desabilitado) se qualquer faixa tiver início ou fim vazio.
- Trocar de dia em edição é bloqueado enquanto há alterações pendentes não salvas no dia atualmente expandido.
- O fuso horário é uma lista fechada de 9 opções fixas no front-end (não é uma lista dinâmica de todos os fusos IANA) — não há campo de busca ou digitação livre.
- Formato de horário é `HH:mm` (input nativo `type="time"`); não há indicação de suporte a intervalos que cruzam a meia-noite (ex.: 22:00–02:00) — não há validação visível de que `endTime > startTime`.
- Dia da semana no backend usa `dayOfWeek` numérico: 0 = Domingo, 1 = Segunda, ..., 6 = Sábado (convenção JS padrão), mas a ORDEM DE EXIBIÇÃO na tela começa em Segunda.

**Nomes e termos:**
- "Fuso Horário", "Horários de Atendimento", "Faixa de horário" / "faixas de horário" (cada intervalo início-fim), "Dias configurados".

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Posso ter mais de uma faixa de horário no mesmo dia?" — Sim, pode adicionar quantas quiser com "Adicionar horário".
- "O fuso horário afeta cada faixa individualmente?" — Não, é um único fuso horário para a conta inteira, salvo separadamente das faixas.
- "Dá para copiar o horário de um dia para outro individualmente (ex.: só terça)?" — Não; a réplica só tem dois alvos possíveis: "Seg-Sex" (todos os dias úteis) ou "Todos" (os 7 dias). Não há réplica para um único dia específico.
- "O que acontece com os horários que já existiam no dia de destino ao replicar?" — São apagados e substituídos pelos horários do dia de origem.

**Incertezas:**
- Não encontrei validação de que `endTime` deva ser maior que `startTime`, nem checagem de sobreposição entre faixas do mesmo dia.
- Não encontrei nenhuma indicação de papel/permissão restringindo escrita nesta tela especificamente além do gate geral de `/identity` (Admin/Gestor da Empresa); ao contrário de "Status de contato", não vi um `canManage` computado aqui — presumo que qualquer usuário que acesse a rota pode editar, mas não confirmei se há alguma trava adicional no backend.
- Não sei se o backend valida fuso horário fora da lista fixa (ex.: se um valor customizado salvo por API antiga apareceria como texto cru — o computed `selectedTimezoneLabel` cai para `timezone.value` cru se não encontrar na lista).

## Roteamento (`/identity/operations/routing`)

**Como chegar:** Menu principal "Cérebro" > sidebar secundária, seção "Operações" > item "Roteamento" (ícone customizado `RoutingIcon`). Tem badge de contagem de sugestões pendentes (`countKey: 'routing'`).

**Para que serve:** Definir critérios de transferência automática de conversas para atendentes humanos — as condições sob as quais Tino deve encaminhar o atendimento.

**Quem vê:** Mesmo gate geral da área (Admin/Gestor da Empresa + feature `ai.operations`). Não há diferenciação de papel dentro da própria tela.

**Plano, créditos e bloqueios:** Gate padrão da área. Não encontrei nenhum "teste de roteamento" ou simulação — a tela é só CRUD de critérios de texto livre; não existe motor de regras estruturado nem preview de qual conversa cairia em qual critério.

**O que há na tela:**
- Cabeçalho: "Roteamento" + "Defina os critérios para transferência automática de conversas para atendentes humanos. Configure as condições que determinam quando Tino deve encaminhar o atendimento." (há um comentário HTML comentado no código mencionando um limite de 7 critérios, mas está desativado — ver Regras e limites.)
- Bloco "Sugestões do Tino" (componente `IdentityPendingSuggestions`, categoria `routing`) — só aparece se houver itens pendentes (ver seção compartilhada "Sugestões do Tino" mais abaixo).
- Lista de critérios cadastrados (componente `IdentityPromptList`, compartilhado com Esclarecimentos):
  - Título da seção: "Critérios cadastrados" (+ contagem, ex. "Critérios cadastrados · 3")
  - Botão "Adicionar critério"
  - Placeholder do título: "Ex: Transferir cliente irritado"
  - Placeholder da descrição: "Descreva quando e como o roteamento deve ocorrer..."
  - Mensagem de lista vazia: "Nenhum critério de roteamento cadastrado"
  - Templates prontos (10 modelos em `data/templates/routing.json`, ex.: "Insatisfação, reclamação ou linguagem agressiva", "Cliente solicita falar com atendente humano", "Urgência ou prazo crítico" etc. — ver arquivo completo no repositório).
- Modal "Editar sugestão do Tino" (`IdentityPendingEditModal`) para editar uma sugestão da IA antes de aprovar — rótulos "Nome" e "Critério de roteamento", mesmos placeholders acima.

### Cartão de item (visão e edição) — componente `PromptList` (compartilhado por Roteamento e Esclarecimentos)
- **Visão (colapsado):** bolinha de status (verde = Ativo, cinza = Inativo, com tooltip "Ativo"/"Inativo"), título, descrição (até 2 linhas), linha de autoria "Última alteração por {nome} em {data}", e se o registro veio da IA e ainda aponta para uma property existente, uma marca de origem clicável "Origem: {nome da property}" (ver seção "Marca de origem" mais abaixo).
- **Edição (expandido):** campo de título (input) e campo de descrição (textarea com auto-resize até 400px); se ambos os campos estão vazios, mostra os "Modelos" sugeridos (até 5 chips + botão "Explorar modelos" se houver mais). Toggle "Ativo"/"Inativo". Botão "Excluir" (só aparece em item já existente, com id). Botões "Cancelar" e "Salvar" (desabilitado se título ou descrição vazios).
- Ao salvar, checa duplicidade: se já existe outro item com o MESMO título (case-insensitive, aparado): toast de aviso "Já existe um item com esse título."; se já existe outro com a MESMA descrição: "Já existe um item com essa descrição." — nesses casos o salvamento é bloqueado.
- Item novo em edição mas não salvo, ao trocar de card, vira um "card pendente" com borda de atenção e rótulo "Novo" — ao clicar nele, retoma a edição de onde parou. Aviso "Existem alterações pendentes a serem salvas" some acima da área de templates enquanto isso.
- Modal de exclusão (`SharedDeleteModal`): título "Excluir item", texto "Tem certeza que deseja excluir item **{título}**?", botões "Cancelar" / "Excluir".
- Modal "Ver todos" os modelos (`IdentityPromptTemplateModal`): título "Modelos para Roteamento" (ou "disponíveis" se sem título), grade de cards clicáveis com título e trecho do corpo (até 150 caracteres + "...").

**Fluxos:**
1. **Criar critério do zero:** "Adicionar critério" → preenche título + descrição (ou escolhe um modelo, que preenche os dois campos) → "Salvar" → `POST /operations/routing` com `toolAction: TRANSFER_TO_HUMAN` fixo e `isActive` (padrão true) → toast "Critério adicionado!" → aparece na lista.
2. **Editar critério existente:** clicar no card → editar campos → "Salvar" → `PUT /operations/routing/:id` → toast "Critério atualizado!".
3. **Excluir critério:** dentro da edição, "Excluir" → modal de confirmação → "Excluir" → `DELETE /operations/routing/:id` → toast "Critério removido!" → some da lista.
4. **Revisar sugestão do Tino:** ver seção compartilhada "Sugestões do Tino" mais abaixo — "Aceitar" aprova direto; "Editar" abre o modal, que ao salvar chama `updateRoutingCriterion` seguido de `reviewIdentity('routing', id, 'APPROVE')` (ou seja, salva o texto editado E aprova no mesmo clique, com o botão "Salvar e aprovar"); "Negar" rejeita.

**Regras e limites:**
- `toolAction` do critério é sempre `TRANSFER_TO_HUMAN` ao criar pela tela — os outros valores do enum (`SEND_ATTACHMENT`, `END_CONVERSATION`, `FLAG_SUPERVISOR`, `SCHEDULE_CALLBACK`, `REDIRECT_CHANNEL`, `PRIORITY_QUEUE`) existem no tipo mas não são usados/selecionáveis nesta tela — não há seletor de ação na UI.
- Havia um limite de "até 7 critérios de roteamento por conta" mencionado em comentário HTML comentado no template (desativado, não está em vigor no código atual).
- Título e descrição não podem se repetir entre critérios da mesma conta (comparação case-insensitive e sem espaços nas pontas).
- Itens com `reviewStatus === 'PENDING'` (sugestões da IA ainda não revisadas) NÃO aparecem na lista "Critérios cadastrados" — só no bloco "Sugestões do Tino" acima.

**Nomes e termos:**
- "Critério" (não "regra"); "roteamento"; "transferência automática"; "Sugestões do Tino"; "Origem" (property de onde uma sugestão foi extraída).

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Posso configurar o roteamento para outra ação além de transferir para humano (ex.: encerrar a conversa)?" — Não pela tela; toda criação usa `TRANSFER_TO_HUMAN`, apesar de o backend suportar outras ações no tipo.
- "Existe um jeito de simular/testar uma conversa contra os critérios de roteamento?" — Não encontrei nada assim no código desta tela.
- "Quantos critérios posso cadastrar?" — Não há limite ativo no código atual (o limite de 7 está comentado/desligado).

**Incertezas:**
- Não confirmei se o backend aplica algum limite de quantidade mesmo com o aviso desativado no front (o comentário sugere que existiu ou existirá um limite de 7, mas o componente `PromptList` também suporta uma prop `maxItems` que aqui não é passada — logo, sem limite ativo do lado do front).
- Não vi nesta leitura se existe alguma ordem/prioridade entre critérios quando mais de um se aplica à mesma conversa (não há campo de ordenação na tela).

## Campos do contato (`/identity/operations/qualification`)

**Como chegar:** Menu principal "Cérebro" > sidebar secundária, seção "Operações" > item "Campos do contato" (ícone `PhClipboardText`). Não tem badge de sugestões pendentes.

**Nomenclatura:** No código, o id do item de menu é `qualification`, a rota é `/identity/operations/qualification`, o service chama-se `getQualificationFields`/`QualificationFieldDto`, e há um comentário explícito no `Sidebar.vue`:
> "'Qualificação' era o nome interno do catálogo. Na ficha e na conversa o atendente vê 'Campos do contato' — o nome único evita a tradução mental."

Ou seja: **"Qualificação" é o nome técnico/interno (rotas, DTOs, variáveis)**; **"Campos do contato" é o único nome exposto na interface** (título da página, item de menu, textos de ajuda) e é também como a ficha do contato e a conversa se referem a esses dados — não há uso do termo "Qualificação" em nenhum texto visível ao usuário nesta tela.

**Para que serve:** Definir os campos de informação que Tino coleta durante a conversa (e que a equipe também pode preencher manualmente na ficha do contato) — nome da empresa, e-mail, orçamento etc. — e a pergunta exata que Tino faz para obter cada um.

**Quem vê:** Gate geral da área. Não há checagem de papel adicional na própria página.

**Plano, créditos e bloqueios:** Gate padrão da área (`ai.operations`).

**O que há na tela:**
- Cabeçalho: "Campos do contato" + "Defina os campos que Tino coleta durante a conversa e que a equipe também pode preencher à mão na ficha do contato. Cada campo representa uma informação a guardar sobre a pessoa — nome da empresa, e-mail, orçamento — e a pergunta que Tino faz para obtê-la."
- Layout de duas colunas em telas largas (`lg:flex-row`): à esquerda o formulário/lista de campos; à direita (ou embaixo, no mobile) um painel fixo "Exemplo de conversa" com preview ao vivo.
- **Lista de campos** (componente `IdentityQualificationFieldList`):
  - Botão "Adicionar campo"
  - Mensagem de lista vazia: "Nenhum campo cadastrado"
  - Cada campo em visão colapsada mostra: label do campo, badge do tipo (ex. "TEXTO", "NÚMERO" — em maiúsculas mono), badge "Obrigatório" (se aplicável), e a pergunta de coleta (até 2 linhas).
  - Em edição, campos do formulário:
    - **"Chave (identificador único)"** — input, placeholder "ex: budget", com tooltip de ajuda: "Identificador único do campo, usado internamente para referência. Use nomes simples sem espaços ou caracteres especiais. Ex: 'budget', 'company_name'."
    - **"Label (nome exibido)"** — input, placeholder "ex: Orçamento disponível", tooltip: "Nome amigável exibido para identificar este campo nas interfaces e relatórios. Ex: 'Orçamento disponível', 'Nome da empresa'."
    - **"Tipo do campo"** — select, tooltip: "Define o formato esperado da resposta do contato. Escolha o tipo que melhor representa a informação a ser coletada (texto, número, e-mail, etc.)." Opções: Texto (`TEXT`), Número (`NUMBER`), Moeda (`CURRENCY`), Data (`DATE`), Sim/Não (`BOOLEAN`), E-mail (`EMAIL`), Telefone (`PHONE`), URL (`URL`).
    - **"Pergunta para coleta"** — textarea, placeholder "ex: Qual o orçamento disponível para este projeto?", tooltip: "A pergunta exata que Tino fará ao contato durante a conversa para coletar esta informação. Seja claro e objetivo."
    - Toggle **"Obrigatório"/"Opcional"** com tooltip: "Quando obrigatório, o agente insistirá em coletar esta informação antes de prosseguir na conversa."
    - Botão "Excluir" (só em item existente) e botões "Cancelar"/"Salvar" ("Adicionar" no card de criação).
  - Ao salvar, checa duplicidade (case-insensitive) de: chave (toast "Já existe um campo com essa chave."), label ("Já existe um campo com esse label.") e pergunta ("Já existe um campo com essa pergunta.") — bloqueia se duplicado.
  - Item novo não salvo, ao trocar de card, vira "card pendente" com borda de atenção e rótulo "Novo".
  - Modal de exclusão: "Excluir campo", "Tem certeza que deseja excluir campo **{label ou chave}**?".
- **Painel "Exemplo de conversa"** (componente `IdentityQualificationConversationExample`):
  - Kicker: "Exemplo de conversa"
  - Simula uma janela de chat com cabeçalho "Tino" (avatar com iniciais "Tino"), selo mono "ia/agente", indicador "online" (bolinha verde).
  - Se não há campos: estado vazio com ícone de balão e texto "Adicione campos do contato para visualizar como será a conversa do agente."
  - Se há campos: monta uma conversa simulada — mensagem inicial de Tino "Olá! Para melhor atendê-lo, preciso coletar algumas informações.", depois, para até os primeiros 4 campos, a pergunta de cada um (ou "Qual o seu {label em minúsculo}?" se a pergunta estiver vazia) seguida de uma resposta de exemplo do "Visitante" (valor fixo por tipo: TEXT="Teste", NUMBER="42", CURRENCY="R$ 5.000,00", DATE="15/03/2026", BOOLEAN="Sim", EMAIL="joao@empresa.com", PHONE="(11) 99999-0000", URL="https://empresa.com", outros = "Resposta exemplo"). Se houver mais de 4 campos, insere uma mensagem "... e mais N pergunta(s) sobre {labels restantes}." Por fim, "Obrigado! Com essas informações consigo dar continuidade ao seu atendimento."
  - Esse preview reage EM TEMPO REAL ao que está sendo digitado no formulário de edição (mesmo antes de salvar) — é montado via `computed` que mescla os campos salvos com o formulário em edição no momento (`previewFields`).
  - Rodapé do painel: "visualização simulada"; input mock "Digite sua mensagem..." (não funcional).

**Fluxos:**
1. **Criar campo:** "Adicionar campo" → preencher Chave, Label, Tipo, Pergunta, Obrigatório → o preview à direita já mostra a pergunta em tempo real → "Salvar" (rotulado "Adicionar" no card de criação) → `POST /operations/qualification/field` com `order` = quantidade atual + 1 → toast "Campo adicionado!" → aparece na lista e no preview definitivo.
2. **Editar campo:** clicar no card → alterar campos → "Salvar" → `PUT /operations/qualification/field/:id` → toast "Campo atualizado!".
3. **Excluir campo:** dentro da edição, "Excluir" → confirmação → `DELETE /operations/qualification/field/:id` → toast "Campo removido!".

**Regras e limites:**
- Chave, Label e Pergunta são obrigatórios para salvar (botão desabilitado sem os três preenchidos).
- Chave, Label e Pergunta não podem se repetir (comparação case-insensitive, aparada) entre os campos já cadastrados.
- Tipo padrão ao criar: "Texto" (`TEXT`). "Obrigatório" padrão: desmarcado (Opcional).
- `order` é atribuído automaticamente como `length + 1` ao criar (não há reordenação manual visível na tela).
- Não há limite máximo de campos (`maxItems` não é usado nesta tela).

**Nomes e termos:**
- "Campo" (nunca "campo de qualificação" na UI); "Chave", "Label", "Tipo do campo", "Pergunta para coleta", "Obrigatório"/"Opcional"; internamente "qualificação"/"qualification" (não aparece ao usuário).

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Por que às vezes vejo 'Qualificação' e às vezes 'Campos do contato'?" — Na interface só existe "Campos do contato"; "Qualificação" é nome interno de sistema (URLs, nomes de variável) e não deveria aparecer para o usuário final.
- "Dá para reordenar os campos na tela?" — Não há controle de reordenação visível; a ordem é a de criação.
- "O campo aparece na ficha do contato mesmo que o cliente nunca converse com o Tino?" — Segundo a descrição da própria tela, sim: "que a equipe também pode preencher à mão na ficha do contato" — mas o preenchimento manual em si acontece em outra tela (ficha do contato), fora do escopo lido aqui.

**Incertezas:**
- Não vi nenhuma tela de reordenação (drag-and-drop ou setas) para os campos, ao contrário de "Status de contato" que tem mover para cima/baixo — pode ser uma limitação real ou algo não coberto pelos arquivos lidos.
- Não confirmei no código lido se existe algum limite de campos imposto pelo backend (só ausência de limite no front).

## Esclarecimentos (`/identity/operations/clarifications`)

**Como chegar:** Menu principal "Cérebro" > sidebar secundária, seção "Operações" > item "Esclarecimentos" (ícone `PhQuestion`). Tem badge de contagem de sugestões pendentes (`countKey: 'clarification'`).

**Para que serve:** Configurar quando e como Tino deve pedir esclarecimentos adicionais ao contato antes de prosseguir com o atendimento (ex.: mensagens vagas, pedidos sem detalhe suficiente).

**Quem vê:** Gate geral da área.

**Plano, créditos e bloqueios:** Gate padrão da área (`ai.operations`).

**O que há na tela:** Estrutura idêntica à de Roteamento (mesmo componente `PromptList`), com textos próprios:
- Cabeçalho: "Esclarecimentos" + "Configure quando e como Tino deve pedir esclarecimentos ao contato. Defina as situações em que informações adicionais são necessárias antes de prosseguir com o atendimento." (também com um comentário HTML desativado sobre limite de 7 esclarecimentos por conta).
- Bloco "Sugestões do Tino" (categoria `clarification`).
- Lista "Esclarecimentos cadastrados":
  - Botão "Adicionar esclarecimento"
  - Placeholder do título: "Ex: Clarificar produto de interesse"
  - Placeholder da descrição: "Descreva quando e como o agente deve pedir esclarecimento..."
  - Mensagem de lista vazia: "Nenhum esclarecimento cadastrado"
  - 14 templates prontos em `data/templates/clarifications.json` (ex.: "Esclareça mensagens curtas", "Detalhe o problema com o produto", "Solicite o número do pedido", "Confirme o endereço de entrega" etc.)
- Modal "Editar sugestão do Tino": rótulos "Nome" e "Esclarecimento", mesmos placeholders.
- Demais comportamentos de card (visão/edição, duplicidade, card pendente, modal de exclusão "Excluir item") são idênticos aos descritos em Roteamento, pois usam o mesmo componente `PromptList`.

**Fluxos:** Iguais aos de Roteamento, trocando os endpoints:
1. Criar: `POST /operations/clarifications` → toast "Esclarecimento adicionado!"
2. Editar: `PUT /operations/clarifications/:id` → toast "Esclarecimento atualizado!"
3. Excluir: `DELETE /operations/clarifications/:id` → toast "Esclarecimento removido!"
4. Revisar sugestão: mesmo fluxo "Salvar e aprovar" via `updateClarification` + `reviewIdentity('clarification', id, 'APPROVE')`.

**Regras e limites:**
- Título e descrição não podem se repetir (mesma checagem case-insensitive do `PromptList`).
- Limite de 7 esclarecimentos mencionado em comentário desativado no template — não está em vigor no código atual.
- Itens `PENDING` não entram na lista principal, só no bloco de sugestões.

**Nomes e termos:**
- "Esclarecimento" (equivalente ao "Critério" de Roteamento, mas para pedir mais informação em vez de transferir).

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Qual a diferença entre Esclarecimentos e Campos do contato?" — Esclarecimentos são instruções de comportamento em texto livre para quando a mensagem do contato está vaga ou incompleta ("se o cliente disser X, pergunte Y"); Campos do contato são estruturados (chave, tipo, obrigatoriedade) e coletam dados específicos e permanentes na ficha da pessoa.
- "Quantos esclarecimentos posso cadastrar?" — Sem limite ativo no código atual.

**Incertezas:**
- Mesmas incertezas estruturais do Roteamento (limite real do backend, ordem de aplicação quando vários esclarecimentos poderiam valer para a mesma mensagem).

## Painel compartilhado "Sugestões do Tino" (aparece em Roteamento, Esclarecimentos e Contexto Situacional)

Componente `components/identity/PendingSuggestions.vue`. Não é uma rota própria — é um bloco embutido no topo do conteúdo das três telas que têm sugestões pendentes de revisão da IA (`clarification`, `routing`, `situational_context` — os mesmos que têm badge na sidebar). Só é renderizado quando há pelo menos 1 item pendente na categoria.

**O que há no painel:**
- Cabeçalho: "Sugestões do Tino" + badge numérico com a contagem.
- Texto de contexto: "Tino analisou o conteúdo do Cérebro e sugeriu os registros abaixo. Eles **não afetam o atendimento** enquanto não forem aceitos."
- Um cartão por sugestão, cada um com:
  - Selo "Sugerido pelo Tino" (ícone de "AI spark")
  - Título e corpo da sugestão
  - Se houver `aiRationale`: caixa com "**Por que Tino sugeriu:** {texto}"
  - Se houver origem (`sourcePropertyId`): marca de "Origem" (ver componente `OriginMarker` abaixo)
  - Se a sugestão conflita com um registro existente (`conflictsWithId`): alerta (ícone `PhWarning`, cor "atenção") com um dos dois textos:
    - Se será substituído automaticamente: "Conflita com um registro existente; ele será **substituído ao aprovar**."
    - Caso contrário: "Conflita com um registro existente. Revise antes de aprovar."
  - Três botões de ação: "Negar" (ícone X), "Editar" (ícone lápis), "Aceitar" (ícone check) — todos desabilitados individualmente enquanto aquele item está em processamento (evita duplo clique).

**Fluxos:**
1. **Aceitar:** clique em "Aceitar" → chama `review(categoria, id, 'APPROVE')` (composable `useIdentityReview`) → em caso de sucesso, emite `reviewed` para a página recarregar sua lista e os badges.
2. **Negar:** clique em "Negar" → `review(categoria, id, 'REJECT')` → mesma atualização.
3. **Editar:** clique em "Editar" → emite `edit` com o item → a página-mãe abre o modal `IdentityPendingEditModal` (título "Editar sugestão do Tino", texto "Ajuste o conteúdo antes de aprovar. Ao salvar, a sugestão será aplicada e ativada.") → ao clicar "Salvar e aprovar", a página chama o `update` específico da categoria (ex. `updateRoutingCriterion`) com os campos editados e, em seguida, `reviewIdentity(categoria, id, 'APPROVE')` — ou seja, editar e aprovar é UM único ato, não dois.
4. Toast de sucesso ao revisar: "Sugestão aceita!" ou "Sugestão negada." (vem do service `identity-review.service.ts`, `reviewIdentity`).

**Regras e limites:**
- Endpoint de revisão é compartilhado pelas 6 categorias possíveis de identidade (`PATCH /identity/review/{category}/{id}`), mas nas telas de Operações só 3 categorias aparecem: `clarification`, `routing`, `situational_context` (as outras três — `communication`, `guideline`, `compliance` — pertencem à seção "Personalidade", fora do escopo de Operações).
- "Campos do contato" e "Status de contato" e "Disponibilidade" NÃO têm esse painel nem contagem de pendentes — confirmado tanto pela ausência de `countKey` no item de menu quanto pela ausência de `IdentityPendingSuggestions` nos respectivos arquivos de página.

### Marca de "Origem" (`components/identity/OriginMarker.vue`)
Usada dentro dos cards de sugestão E dos cards já aprovados nas listas (Roteamento, Esclarecimentos, Contexto Situacional) quando o registro veio da IA (`source === 'AI'`) e tem `sourcePropertyId`.
- Se a property de origem ainda existe: link clicável "Origem: {nome da property}" que leva para `/identity/properties?contentId={id}` (com ícone conforme o tipo: `PhGlobe` para WEBSITE, `PhChatText` para QA, `PhFileText` para DOCUMENT/outros); tooltip mostra o nome completo.
- Se a property foi removida (não existe mais / sem nome): texto cinza não clicável "Origem: conteúdo removido das propriedades".
- Não renderiza nada se não houver `sourcePropertyId`.

## Contexto Situacional (`/identity/operations/situational-context`)

**Como chegar:** Menu principal "Cérebro" > sidebar secundária, seção "Operações" > item "Contexto Situacional" (ícone `PhLightning`). Tem badge de contagem de sugestões pendentes (`countKey: 'situationalContext'`).

**Para que serve:** Registrar situações temporárias que afetam o comportamento de Tino — manutenções programadas, promoções, mudanças de horário — cada uma com um período de validade opcional (início/fim).

**Quem vê:** Gate geral da área. Não há checagem de papel adicional na página.

**Plano, créditos e bloqueios:** Gate padrão da área (`ai.operations`). Havia um limite de itens (`MAX_ITEMS`) todo desativado no código — a constante está comentada (`// const MAX_ITEMS = 10;`) e todo o texto/contagem relacionado também está comentado no template ("Limite de até {MAX_ITEMS} contextos por conta.", contador "{items.length} de {MAX_ITEMS} utilizados"). Ou seja, hoje **não há limite de quantidade em vigor** nesta tela, embora o código sugira que existiu (ou está planejado) um limite de 10.

**O que há na tela:**
- Cabeçalho: "Contexto Situacional" + "Registre situações temporárias que afetam o comportamento do Tino, como manutenções programadas, promoções ou mudanças de horário."
- Bloco "Sugestões do Tino" (categoria `situational_context`).
- Skeleton de carregamento (3 blocos animados).
- Botão "Adicionar contexto" (ícone `PhPlus`), desabilitado se já há um item em criação ou edição.
- **Formulário de novo item / edição** (card com borda destacada):
  - Campo de título — input, placeholder "Ex: Manutenção programada"
  - Campo de instrução — textarea, placeholder "Descreva a situação e como o agente deve se comportar durante este período..."
  - Dois campos de data/hora lado a lado: **"Início"** e **"Fim"** — ambos `type="datetime-local"` (data E hora, não só data), ambos opcionais.
  - Toggle **"Ativo"/"Inativo"** (padrão: Ativo)
  - No modo edição (item existente): botão de lixeira "Excluir contexto" (aria-label) ao lado do toggle.
  - Botões "Cancelar" e "Adicionar" (criação) / "Salvar" (edição) — desabilitados se título ou instrução vazios.
- **Cards de itens já cadastrados**, cada um mostrando:
  - Título, instrução (até 2 linhas)
  - Período formatado (ícone `PhCalendarDots`): ver "Regras e limites" abaixo para as 4 variações de texto
  - Marca de "Origem" (se for sugestão da IA aprovada, com property ainda existente)
  - Badge de status no canto direito, com 4 estados possíveis (ver abaixo)
  - Clicar no card abre a edição embutida (a não ser que já haja outro item em criação/edição)
- Estado vazio: ícone de calendário + "Nenhum contexto situacional cadastrado" + "Adicione situações temporárias que afetam o comportamento do atendimento."
- Modal de exclusão (`SharedDeleteModal`, `class-name="contexto situacional"`): "Excluir contexto situacional", "Tem certeza que deseja excluir contexto situacional **{título}**?".
- Modal "Editar sugestão do Tino": rótulos "Título" e "Instrução", mesmos placeholders do formulário principal.

**Status calculado (client-side, não vem pronto da API) — função `getStatus`:**
| Condição | Rótulo exibido | Classe visual |
|---|---|---|
| `!item.isActive` | **Inativo** | cinza |
| ativo, `startDate` no futuro | **Agendado** | neutro |
| ativo, `endDate` no passado | **Expirado** | cinza |
| ativo, dentro do período (ou sem datas) | **Ativo** | verde |
A checagem é feita comparando `new Date(startDate/endDate)` com `new Date()` (hora local do navegador) toda vez que a tela renderiza — não há atualização automática em tempo real (só recalcula ao re-renderizar/recarregar).

**Formatação do período exibido — função `getDateRangeText`:**
- Com início e fim: `"{início} — {fim}"` (formato `dd/mm/aaaa hh:mm`, locale pt-BR, via `toLocaleDateString`)
- Só com início: `"A partir de {início}"`
- Só com fim: `"Até {fim}"`
- Sem nenhuma data: `"Sem período definido"`

**Fluxos:**
1. **Criar contexto:** "Adicionar contexto" → preencher título, instrução, opcionalmente início/fim, toggle Ativo/Inativo → "Adicionar" → `POST /operations/situational-context` com `startDate`/`endDate` convertidos para ISO (`null` se vazios) → toast "Contexto situacional adicionado!" → o novo item é inserido no TOPO da lista (`unshift`).
2. **Editar contexto:** clicar no card → alterar campos → "Salvar" → `PUT /operations/situational-context/:id` → toast "Contexto situacional atualizado!".
3. **Ativar/desativar rapidamente:** existe um método `handleToggleActive` no script que chama `updateSituationalContext(id, { isActive: !isActive })`, mas não encontrei nenhum elemento de UI (botão/switch na visão colapsada) que dispare esse método diretamente — o toggle visível só existe DENTRO do formulário de edição. Ver Incertezas.
4. **Excluir contexto:** dentro da edição, ícone de lixeira "Excluir contexto" → modal de confirmação genérico (botões "Cancelar"/"Excluir") → `DELETE /operations/situational-context/:id` → toast "Contexto situacional removido!".
5. **Revisar sugestão do Tino:** igual ao padrão comum — Aceitar/Negar/Editar (Editar chama `updateSituationalContext` + `reviewIdentity('situational_context', id, 'APPROVE')`, botão "Salvar e aprovar").

**Regras e limites:**
- Título e instrução são obrigatórios; datas são opcionais.
- Os campos de data usam `datetime-local` — ou seja, o usuário escolhe data E HORA de início/fim, não só o dia.
- A conversão para o formulário usa o fuso horário LOCAL do navegador (`toLocalDateTimeValue` ajusta pelo offset do timezone do navegador) — não há relação visível com o fuso horário configurado na tela "Disponibilidade"; são dois conceitos de tempo independentes no código lido.
- Limite de quantidade (`MAX_ITEMS = 10`) existe no código mas está inteiramente comentado/desativado — não impede criação de novos itens hoje.
- Itens com `reviewStatus === 'PENDING'` não entram na lista principal, só no painel de sugestões.

**Nomes e termos:**
- "Contexto situacional" (ou apenas "contexto"); "Instrução" (o campo de texto livre, equivalente ao "prompt" das outras telas); status: Ativo, Agendado, Expirado, Inativo.

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Um contexto sem data de início/fim vale para sempre?" — Sim: sem `startDate`/`endDate`, o status calculado é "Ativo" (contanto que `isActive` esteja marcado) e o texto do período mostra "Sem período definido".
- "Se eu desativar manualmente um contexto que está dentro do período, ele passa para 'Agendado' ou 'Expirado'?" — Não: o status "Inativo" tem prioridade sobre qualquer cálculo de data; um contexto desativado sempre mostra "Inativo", independente das datas.
- "O horário de início/fim é o fuso da empresa (o mesmo de Disponibilidade) ou o do meu computador?" — Pelo código, os campos `datetime-local` são tratados no fuso horário local do NAVEGADOR do usuário ao converter para exibição; não vi nenhuma referência ao fuso salvo em "Disponibilidade" nesta tela.
- "Quantos contextos situacionais posso ter?" — Não há limite em vigor no código atual (havia um limite de 10 planejado/comentado).

**Incertezas:**
- Existe uma função `handleToggleActive` implementada no script, mas não localizei o elemento de UI que a dispara diretamente na visão colapsada do card — pode ser um recurso incompleto/pendente de UI, código morto, ou algo que só é alcançável de um jeito que não identifiquei nesta leitura.
- Não confirmei se `MAX_ITEMS` está de fato desativado também no backend, ou só no front (o comentário sugere que o valor 10 é conhecido, então pode ter sido um limite retirado recentemente ou a ser reativado).
- Não confirmei a relação entre o fuso horário desta tela (implícito, do navegador) e o fuso configurado em "Disponibilidade" — parecem independentes, mas não vi nenhuma nota explícita confirmando ou negando isso.

## Status de contato (`/identity/operations/contact-statuses`)

**Como chegar:** Menu principal "Cérebro" > sidebar secundária, seção "Operações" > item "Status de contato" (ícone `PhFlag`). Não tem badge de sugestões pendentes (não é gerado por IA).

**Para que serve:** Manter a lista de status que a equipe usa na ficha do contato para indicar em que ponto do relacionamento cada pessoa está (ex.: "Lead", "Cliente ativo", "Inativo"). A ordem definida aqui é a ordem do seletor na ficha do contato.

**Quem vê:** Leitura é aberta a qualquer um que acesse a rota (gate geral da área). ESCRITA (criar, editar, reordenar, excluir) exige `auth.isCompanyManagerWide` (Admin ou Gestor da Empresa) — computado local `canManage`. Se `canManage` é falso, a tela mostra a lista somente-leitura (sem botões de ação) e o rodapé: **"Só um administrador ou gestor da empresa pode alterar esta lista."** O comentário no código esclarece: "Gestor de Área/Unidade lê, mas não configura o catálogo da empresa" — ou seja, mesmo dentro do grupo que já passou pelo gate geral de `/identity` (que já exige Admin/Gestor da Empresa para entrar), aqui há uma segunda checagem redundante de papel — o que sugere que a intenção original previa acesso de leitura mais amplo (possivelmente Gestor de Área/Unidade) a esta tela especificamente.

**Plano, créditos e bloqueios:** Gate padrão da área (`ai.operations`) — mesmo que o conteúdo em si (status de contato) não pareça diretamente ligado à IA, a rota cai no mesmo prefixo `/identity/operations` e portanto no mesmo `PlanUpgradeWall`.

**O que há na tela:**
- Cabeçalho: "Status de contato" + "A lista de status que a equipe usa na ficha do contato para dizer em que ponto do relacionamento cada pessoa está — por exemplo 'Lead', 'Cliente ativo' ou 'Inativo'. A ordem aqui é a ordem que aparece no seletor da ficha."
- Estado de carregamento: componente `SharedLoading`.
- Lista de status (cards), cada um mostrando:
  - Bolinha colorida com a cor do status (`background-color: status.color`)
  - Nome do status + badge "Padrão" (se `isDefault`)
  - Contagem de contatos: "{N} contato" / "{N} contatos" (singular/plural conforme N)
  - Se `canManage`, botões de ação (com tooltips): "Mover para cima" (`PhArrowUp`), "Mover para baixo" (`PhArrowDown`), "Editar" (`PhPencilSimpleLine`), "Excluir" (`PhTrash`) — os de mover ficam desabilitados nas extremidades da lista.
- **Edição embutida** (substitui a linha ao clicar em "Editar"):
  - Seletor de cor nativo (`type="color"`, aria-label "Cor do status")
  - Input de nome, placeholder "Nome do status", `maxlength="40"` (Enter salva, Esc cancela)
  - Botão de confirmar (ícone check, tooltip "Salvar", desabilitado se nome vazio)
  - Botão de cancelar (ícone X, tooltip "Cancelar")
  - Checkbox: "Atribuir por padrão a contatos sem status"
- **Criação:** botão "Adicionar status" (ícone `PhPlus`, só visível se `canManage`) abre um card com os mesmos campos (cor, nome — placeholder "Ex.: Cliente ativo" —, checkbox de padrão) e botões "Salvar"/"Cancelar"; se já existir um status padrão, o checkbox mostra ao lado: `(hoje é "{nome do status padrão}")`.
- Estado vazio (lista): "Nenhum status cadastrado. Sem lista, o seletor da ficha do contato fica vazio."
- **Confirmação de exclusão com contagem** (embutida no card, não é um modal separado): quando o backend responde 409 (status em uso), aparece dentro do próprio card:
  - Mensagem vinda do backend (`error.message`, texto exato não fixo no front — é o que a API retornar)
  - Texto fixo complementar: "Os contatos não são apagados nem movidos para outro status — apenas ficam sem status."
  - Botões: **"Excluir mesmo assim"** e **"Cancelar"**

**Fluxos:**
1. **Criar status:** "Adicionar status" → escolher cor (padrão `#22C55E`, um verde) e nome (até 40 caracteres) → opcionalmente marcar "Atribuir por padrão..." → "Salvar" → `POST /operations/contact-statuses` → toast "Status criado!" → lista recarrega (`reload`).
2. **Editar status:** "Editar" → mesmos campos preenchidos → "Salvar" (ou Enter) → `PUT /operations/contact-statuses/:id` → toast "Status atualizado!".
3. **Reordenar:** setas para cima/baixo → troca a posição na lista local e envia a lista COMPLETA de ids na nova ordem via `PUT /operations/contact-statuses/reorder` → recarrega (sem toast de sucesso específico para reordenar — só erro tratado silenciosamente pelo service, que teria seu próprio toast de erro se falhasse).
4. **Excluir status (sem uso):** "Excluir" → `DELETE /operations/contact-statuses/:id` (sem `force`) → toast "Status removido." → some da lista.
5. **Excluir status (em uso por contatos):** "Excluir" → backend responde 409 com a contagem de contatos afetados → a tela captura isso como `ContactStatusInUseError` (contagem extraída da mensagem via regex `/(\d+)\s+contato/`) → exibe a confirmação embutida no card com a contagem → usuário pode "Excluir mesmo assim" (repete o DELETE com `force=true`, aí sim remove, toast "Status removido.") ou "Cancelar" (fecha a confirmação sem excluir).

**Regras e limites:**
- Nome do status: até 40 caracteres, obrigatório para salvar (botão desabilitado se vazio).
- Cor: campo de cor nativo do navegador (hex), padrão `#22C55E` para novo status.
- No máximo um status pode ser "Padrão" por empresa (comentário no tipo `ContactStatusCatalogItem`: "Atribuído por padrão a contato sem status definido. No máximo um por empresa.") — a tela mostra qual é o atual ao criar um novo, mas não impede visualmente marcar outro como padrão (presumivelmente o backend desmarca o anterior automaticamente).
- Excluir um status em uso NÃO apaga nem move os contatos — eles ficam sem status atribuído.
- Só Admin/Gestor da Empresa pode criar, editar, reordenar ou excluir; qualquer papel que acesse a rota pode LER a lista.

**Nomes e termos:**
- "Status de contato" (ou apenas "status"); "Padrão" (o status atribuído automaticamente a contatos sem status); ficha do contato = onde o status é selecionado/exibido por conversa/pessoa.

**Perguntas prováveis do usuário e resposta segundo o código:**
- "Quem pode criar ou editar status de contato?" — Só Admin da Empresa ou Gestor da Empresa; outros papéis que consigam ver a tela (se houver algum caminho de acesso) só leem.
- "Se eu excluir um status que está em uso, o que acontece com os contatos?" — Eles não são apagados nem movidos para outro status; simplesmente ficam sem status. A tela avisa isso explicitamente antes de confirmar.
- "Posso ter mais de um status marcado como padrão?" — O tipo de dado diz que não ("no máximo um por empresa"), embora eu não tenha visto uma trava explícita na UI impedindo marcar um segundo (presume-se que o backend resolve isso ao salvar).
- "A ordem dos status importa?" — Sim, é a ordem exibida no seletor da ficha do contato.

**Incertezas:**
- Não vi no código lido o texto exato que o backend devolve na mensagem de erro 409 (contagem de contatos) — a tela apenas reexibe `error.message` como veio da API; não é um texto fixo no front.
- A dualidade de gate (rota inteira já exige Admin/Gestor da Empresa via middleware global, e a própria tela reforça isso com `canManage` para escrita) sugere que a intenção de produto pode ter sido abrir a LEITURA desta tela específica a mais papéis (ex. Gestor de Área/Unidade) no futuro — mas hoje, pelo middleware, ninguém abaixo de Gestor da Empresa chega até aqui de qualquer forma. Não confirmei se isso éینtencional ou resquício de uma versão anterior.


# PARTE D: Processos
# Processos (dentro de Cérebro / `/identity/processes`)

> Fonte: clone da main de 03/09/2026 em `tartini-web`. Leitura integral dos arquivos listados no escopo.
> Convenção: strings entre aspas duplas são texto literal copiado do código (JSX/template), sem parafrasear.

## Glossário rápido

- **Processo**: um playbook de atendimento — como a empresa resolve um tipo de pedido. Tem 5W2H (o quê/por quê/quem/quando/onde/quanto), um passo a passo (`howSteps`) e saídas (`transitions`). Entidade principal do módulo (`types/process.ts`).
- **Playbook**: sinônimo usado na UI para "o passo a passo que Tino segue" (ex.: "Cada processo é um playbook que Tino segue nas conversas reais").
- **Grupo (de processos)**: conjunto de processos com ordem (`sortOrder`), referenciado por campanhas. Pode ter fluxo próprio (`flowMode: ISOLATED`, padrão de grupos novos) ou herdar o fluxo global (`INHERIT`, legado).
- **Candidato / Descoberta**: sugestão de processo que a IA identifica ao vasculhar conversas reais ainda não mapeadas como processo formal. Vive em `/identity/processes/discovery`.
- **Sessão de mapeamento**: conversa guiada com o agente de mapeamento (nome de produto **Quattro** — ver "Incertezas") que constrói/edita um processo passo a passo. Rota `/identity/processes/mapping/[sessionId]`.
- **Cobertura do Tino / Cobertura da IA**: % ponderado de etapas do playbook que a IA resolve sozinha (FULL=1, PARTIAL=0.5, NONE/UNKNOWN=0), calculado em `calcCoverage()`.
- **Capacidade da IA (aiCapability)**: por etapa ou por processo — `FULL` (Resolve totalmente), `PARTIAL` (Resolve parcialmente), `NONE` (Não resolve / Handoff), `UNKNOWN` (A avaliar).
- **Transição / Saída**: para onde a conversa vai quando o processo termina com um desfecho (`COMPLETED`, `PARTIAL`, `FAILED`, `MISSING_DATA`). Alvo pode ser outro `PROCESS`, `TRIAGE`, `TRANSFER` (setor) ou `END`.
- **Catálogo**: auditoria estrutural do cadastro de processos (sem depender de conversas) — rota `/identity/processes/consistency`. Antiga "Auditoria" foi renomeada/redistribuída (ver seções mortas abaixo).
- **Diagnóstico**: análise de execução de UM processo (o previsto no mapeamento × o que roda nas conversas reais, com recorte de período). Migrou para o Scout (`/scout/processes/[id]`) — fora do escopo desta área, mas linkado a partir daqui.

## Rotas mortas (confirmadas por leitura de código)

### `/identity/processes/diagnosis/[id]` — redireciona para `/scout/processes/[id]`
Arquivo: `pages/identity/processes/diagnosis/[id].vue`. `definePageMeta({ layout: false, middleware: (to) => navigateTo(`/scout/processes/${to.params.id}`, { replace: true }) })`. Comentário no código: "O diagnóstico do processo migrou para `/scout/processes/[id]`. A fronteira é o período: tela com recorte de período é Scout, tela com botão de salvar é Identidade, e nenhuma tem os dois. [...] A rota sobrevive só para não quebrar links, favoritos e os drills antigos." Não tem UI própria (`<div />` vazio). Não aparece na sidebar.

### `/identity/processes/insights` — redireciona para `/scout/processes`
Arquivo: `pages/identity/processes/insights.vue`. `definePageMeta({ layout: false, middleware: () => navigateTo('/scout/processes', { replace: true }) })`. Comentário: "Auditoria › Execução foi extinta como tela. Ela misturava dois planos e não entregava nenhum: análise com recorte de período (que é Scout) e fila viva (que é Operação). O conteúdo foi redistribuído — funil, transições, motivos e intervenções viraram evidência dentro de achados no Diagnóstico e o catálogo quebrado ficou em Identidade, onde tem salvar. A rota sobrevive só para não quebrar links e favoritos." Não tem UI própria.

Nota importante para a central de ajuda: o pedido original menciona `insights.vue` como tela a documentar, mas pelo código ela é a MESMA categoria de rota-fantasma que `diagnosis/[id].vue` — não uma tela de conteúdo.


---

## Mapeamento (`/identity/processes`)

**Como chegar:** Menu principal "Cérebro" > sidebar do Cérebro > seção "Processos" > item "Mapeamento" (é a página raiz do módulo, `pages/identity/processes/index.vue`).

**Para que serve:** Lista todos os processos (playbooks) já mapeados da empresa, com filtros por status/cobertura/prioridade/setor e busca; é também o ponto de entrada para iniciar uma nova sessão de mapeamento com o agente de IA.

**Quem vê:** Admin da Empresa e Gestor da Empresa (regra geral de `/identity`, ver contexto). Não há diferenciação adicional de conteúdo por papel dentro da própria tela.

**Plano, créditos e bloqueios:** Toda a área exige a feature de plano `processes` (gate herdado do `/identity/processes/*`, não repetido aqui). Dentro da tela, um indicador de custo de IA (`AiCostIndicator`, variante "badge") mostra o tooltip: "Mapear com o Quattro e manter processos ativos consome créditos de IA. Acompanhe o consumo em Configurações → Faturamento → Consumo."

**O que há na tela:**
- Header: título "Processos da empresa"; subtítulo dinâmico "{{N}} mapeados · {{M}} ativos · Tino usa esses como playbooks nas conversas reais."; botão "Novo processo" (ícone +) — só aparece se já existir ao menos 1 processo.
- Banner de Descobertas pendentes (só se `discoveryCount > 0`): cartão clicável com ícone de bandeja; texto "{{N}} sugestão de processo para analisar" (singular) ou "{{N}} sugestões de processo para analisar" (plural); descrição "A Quattro identificou um novo candidato a processo / novos candidatos a processo nas conversas reais. Revise e decida o que vira playbook."; link "Revisar descobertas" → `/identity/processes/discovery`.
- Bloco "O que é mapear um processo": explica "Cada processo é um **playbook** que Tino segue nas conversas reais. Em vez de preencher formulário, você **conversa** com a Quattro em 3 passos:" e lista os 3 passos (`HOW_IT_WORKS`):
  1. "Você descreve" — "Conta com suas palavras como o atendimento acontece. O Quattro pergunta o que faltar."
  2. "O Quattro monta o playbook" — "As etapas, canais e setores se estruturam em tempo real ao lado da conversa."
  3. "Você publica" — "O processo vira um playbook que Tino passa a seguir nas conversas reais."
- Bloco "Comece por um exemplo": "A Quattro abre a conversa com uma mensagem pronta — é só responder." — 4 cartões-modelo (`STARTER_TEMPLATES`) clicáveis que já iniciam uma sessão de mapeamento com uma mensagem "seed":
  - "2ª via de boleto" — "Cliente pede uma cópia atualizada do boleto vencido." (seed: "Quero mapear o processo de 2ª via de boleto: o cliente pede uma cópia atualizada do boleto vencido e a gente precisa reenviar o PDF.")
  - "Solicitação de reembolso" — "Cliente pede a devolução de um valor que pagou." (seed correspondente)
  - "Reset de senha" — "Cliente esqueceu a senha e precisa recuperar o acesso." (seed correspondente)
  - "Agendamento" — "Cliente quer marcar um horário de atendimento." (seed correspondente)
- Divisor "Já mapeados".
- Estado vazio (nenhum processo cadastrado): "Você ainda não mapeou nenhum processo" / "Escolha um exemplo acima ou comece do zero — a Quattro monta o playbook com você em poucos minutos." / botão "Mapear primeiro processo".
- Painel de filtros (só quando há processos):
  - Abas de status (eixo principal, com contagem): "Todos", "Ativos", "Inativos".
  - Campo de busca: placeholder "Buscar processo", `aria-label="Buscar processo"`; botão "x" com título/aria-label "Limpar busca".
  - Grupo "Cobertura do Tino": pills "Todas" + por faixa (`COVERAGE_META`: "Cobre bem", "Cobre em parte", "Pouca cobertura"), cada uma só aparece se tiver count > 0.
  - Grupo "Prioridade": pills "Todas" + Baixa/Média/Alta/Crítica (ordem crítica→baixa exibida, mas do maior para o menor: `PRIORITY_ORDER` invertido), cada uma só aparece com count > 0.
  - Grupo "Setor" (só se houver setores): pills "Todos" + um por setor único encontrado nos processos (ordenado pt-BR); clicar de novo no mesmo setor desmarca.
  - Rodapé do painel: contagem "N processo(s)" + botão "Limpar filtros" (só aparece com filtro ativo).
- Grid de cards de processo (`ProcessesCard`, 1/2/3 colunas conforme largura) com paginação (`SharedPagination`, 12 por página por padrão).
- Estado "nenhum resultado" para filtro/busca sem match: "Nenhum processo encontrado" (+ " para "{{query}}"." se houver busca) e botão "Limpar filtros".
- Modal de exclusão (`SharedDeleteModal`) reutilizado nesta tela para excluir processo.

**Cartão de processo (`ProcessesCard`):**
- Nome do processo; chips de setor (`whoSectors`); toggle de Ativo/Inativo (com título "Ativo"/"Inativo").
- Descrição (ou "Sem descrição.").
- Bloco de cobertura: se não há playbook (`howSteps` vazio), mostra badge cinza "Sem playbook" com tooltip "Este processo ainda não tem playbook. Conclua o mapeamento para o Tino conseguir conduzi-lo."; caso contrário mostra "Cobertura do Tino" com barra tricolor (verde=full, âmbar=partial, vermelho=none) e badge "{{score}}% · {{label da faixa}}" — tooltip "Cobertura do Tino: quanto deste processo Tino resolve sozinho, com base na avaliação de cada etapa do playbook."
- Rodapé: badge "Prioridade {{label}}" (tooltip "Prioridade do processo"); texto "· há X min/h/d" ou data pt-BR (baseado em `updatedAt`); botões de ícone "Ver fluxo", "Editar processo", "Excluir processo".
- Clicar no cartão (fora dos botões) abre o detalhe do processo.

**Fluxos:**
1. **Criar processo do zero:** clicar "Novo processo" ou "Mapear primeiro processo" → chama `startMapping({})` → navega para `/identity/processes/mapping/{sessionId}`.
2. **Criar a partir de exemplo:** clicar num cartão de exemplo → `startMapping({})` com query `seed` (a mensagem-modelo) → mesma rota de mapeamento, que usa o seed para pré-preencher a primeira mensagem do usuário.
3. **Editar processo existente com o agente:** no cartão, ícone "Editar processo" → `startMapping({ processId })` → abre sessão de mapeamento vinculada ao processo.
4. **Ativar/desativar processo:** toggle no cartão → `updateProcessStatus(id, !isActive)`, atualiza a lista in-place.
5. **Excluir processo:** ícone de lixeira no cartão → abre `SharedDeleteModal` → confirmar → `deleteProcess(id)` → toast de sucesso "Processo excluído." e remove da lista.
6. **Ver fluxo:** ícone "Ver fluxo" → navega para `/identity/processes/flow?processId={id}`.
7. **Abrir detalhe:** clicar no cartão → `/identity/processes/{id}`.
8. **Testar processo (ainda não implementado):** ação `test` (chamada por outro botão do cartão, mas não visível diretamente no template lido) dispara um toast informativo: "Em breve: teste isolado do processo. Por enquanto, valide pelo playground do Tino." — Nota: não encontrei o botão de "Testar" no template do `Card.vue` lido (só flow/editar/excluir); o handler existe na página mas o emit `test` pode estar sem gatilho visível no card atual (ver Incertezas).

**Regras e limites:**
- Paginação client-side: o serviço retorna todos os processos de uma vez (`getProcesses()`), o front pagina (12 por página, ajustável via `SharedPagination`).
- Trocar qualquer filtro/busca volta para a página 1 automaticamente.
- Busca (`query`) casa contra nome e descrição/`whatIs`, case-insensitive.
- Cobertura, capacidade e prioridade são calculadas/exibidas a partir do playbook (`howSteps`); processo sem etapas mapeadas é tratado como "sem playbook", distinto de "0% de cobertura".

**Nomes e termos:** ver Glossário no topo do arquivo. Adicionalmente: o agente que conduz a conversa de mapeamento é chamado **"Quattro"** no código (constante `AGENT_NAME` em `utils/process.ts`), com o comentário: "Nome do agente de IA que conduz a conversa guiada de mapeamento. [...] a IA que atende as conversas reais é referida de forma genérica ('a IA de atendimento') — não é necessariamente este mesmo agente." Ou seja, Quattro (mapeamento) é uma personagem distinta de Tino (atendimento real) — ver Incertezas.

**Perguntas prováveis do usuário e resposta:**
- "Por que aparece 'Quattro' às vezes e 'Tino' em outras?" → Quattro é quem conduz a conversa de mapeamento (a entrevista que monta o playbook); Tino é quem atende o cliente de verdade seguindo esse playbook. São nomes de produto distintos no código atual.
- "Processo mapeado mas sem cobertura aparece como quê?" → Se não tiver nenhuma etapa (`howSteps` vazio), aparece como "Sem playbook", não como 0%.
- "Dá para reordenar/mudar estrutura do processo direto na lista?" → Não; a lista só ativa/desativa, exclui, abre o detalhe/fluxo, ou reabre a conversa de mapeamento para editar estrutura.

**Incertezas:**
- O botão de "Testar processo" (evento `test`) é escutado na página (`@test="testProcess"`), mas não localizei o elemento que o dispara dentro do `ProcessesCard.vue` atual (o card só emite `open/toggle/edit/delete/flow`). Pode ter sido removido do card e o handler ficou órfão, ou pode existir em outro lugar (ex.: dentro do detalhe) que não foi encontrado nesta leitura — vale confirmar com o time antes de documentar esse botão para o usuário final.
- Não confirmei se existe algum limite máximo de processos por empresa (não vi validação de quantidade no código lido).

---

## Detalhe do processo (`/identity/processes/[id]`)

**Como chegar:** Mapeamento (lista) > clicar em qualquer cartão de processo. Também alcançável por links de "conserto" vindos do Catálogo/Diagnóstico.

**Para que serve:** Mostra o processo mapeado por completo (5W2H, cobertura, passo a passo, saídas, recomendações da IA) e permite editar conteúdo, reabrir o mapeamento, ativar/desativar, excluir, ver fluxo e ver diagnóstico (na Scout).

**Quem vê:** Admin/Gestor da Empresa (regra geral).

**Plano, créditos e bloqueios:** Herdado da área (feature `processes`). Nenhum gate adicional encontrado nesta tela especificamente.

**O que há na tela:**
- Banner opcional `SharedFromFindingBanner` — aparece quando o usuário chegou via um link de "conserto" a partir de um achado do Catálogo/Diagnóstico (contexto de volta com `why`/`back`).
- Header: nome do processo; chips de setor; badge "Ativo"/"Inativo" (bolinha verde/cinza); `ProcessesCapabilityBadge` (capacidade geral da IA); se `aiAssessmentStale`, badge "Avaliação desatualizada" com tooltip "As etapas deste processo mudaram depois da última avaliação de capacidade do Tino." e botão de texto "Reavaliar" (ou "Abrindo…" durante o carregamento) que chama `editWithAgent()`.
- Descrição do processo (ou "Processo de atendimento mapeado." como fallback).
- Botões de ação no header: "Diagnóstico" (ícone coração; título "Diagnóstico deste processo: o previsto no mapeamento × o que acontece nas conversas"; navega para `/scout/processes/{id}`, fora desta área), "Ver fluxo" (título "Ver o fluxo de saídas deste processo"; navega para `/identity/processes/flow?processId={id}`), "Editar conteúdo" (só some quando já em edição; título "Editar os textos que Tino envia e os códigos que selecionam cada etapa"), "Ativar"/"Desativar", "Excluir", "Editar com o Quattro" (ícone chat; texto muda para "Abrindo…" enquanto inicia a sessão).
- Se não encontrado (id inválido ou de outra empresa): "Processo não encontrado" / "O processo pode ter sido removido ou não pertence à sua empresa." / botão "Voltar para processos".
- Corpo, quando não está em "Editar conteúdo": componente `ProcessesReview` (ver abaixo) + `ProcessesToolsSection` (ferramentas/conectores vinculados).
- Corpo, quando em "Editar conteúdo": componente `ProcessesContentEditor` (ver abaixo).
- Modal de exclusão (`SharedDeleteModal`).

**`ProcessesReview` (visão consolidada, somente leitura):**
- Bloco "5W2H do processo": O quê (`whatIs`), Por quê (`why`), Quem (chips de setor + texto livre `who`), Quando (`whenTrigger`), Onde (chips de canal com ícone, via `channelIcon`/`channelLabel`), Quanto (badge de prioridade "Prioridade {{label}}"). Campos vazios mostram "—".
- Bloco "Cobertura do Tino": número grande com o score (%), frase "Tino resolve sozinho {{full}} de {{total}} etapas. {{none}} pede passagem para um humano." ou "Sem handoff obrigatório." se `none === 0`; legendas "totalmente / parcialmente / não resolve".
- Bloco "Material de referência" (só se `reference` preenchido): texto livre.
- Bloco "Passo a passo (COMO)": lista de `ProcessesStepRow`; se o processo tiver `selectorField`, mostra selo "Etapa escolhida pelo campo `{{selectorField}}` do disparo" (para deixar claro que não é sequência, é catálogo); estado vazio "Nenhuma etapa mapeada ainda."
- Bloco "Saídas (estados finais)" ("Para onde a conversa segue em cada desfecho do processo."): lista as transições persistidas, ordenadas por desfecho (Concluído→Parcial→Falhou→Faltou dado), com rótulo do alvo ("Triagem · Atendimento geral", "Encerrar conversa", "Transferir · {{setor}}", "Processo · {{nome}}"), escopo de etapas quando houver, e condição opcional (`t.condition`). Estado vazio: "Nenhuma saída definida — todo desfecho volta para a triagem por padrão."
- Bloco "Recomendações da Quattro" (só se `aiAssessment.recommendations` não vazio): lista com marcador "•".

**Cada etapa (`ProcessesStepRow`):**
- Número de ordem; selo circular de capacidade (✓ full / ! parcial / ✕ none / · desconhecido, com título = label da capacidade).
- Texto legível da etapa (`plainDescription` se houver, senão `description`); se houver `selectorValue`, mostra o código à direita (título "Código que seleciona este passo no disparo").
- `aiReason` (motivo da avaliação de capacidade), se houver.
- Bloco "Texto enviado" (só se `content` preenchido) — mostra o roteiro literal que a IA envia.
- Condições (`if`/`then`), se houver.
- Selo "Portão" (ícone cadeado) se `step.gate`; lista "Chaves exigidas:" com as `requiresFieldKeys`.

**`ProcessesContentEditor` (edição textual, sem passar pelo agente):**
- Comentário de arquitetura explícito no código: o mapeamento conversacional é o único caminho para mudar ESTRUTURA (adicionar/remover/reordenar etapas, portões, condições), porque a avaliação de capacidade depende das ferramentas da empresa e as transições/cursor de conversas vivas referenciam posição numérica dos passos. O editor de conteúdo só mexe no que é seguro editar sozinho: textos e código de seleção.
- Campos: "O que é" (textarea, placeholder "O que este processo é, em uma ou duas frases."), "Por que existe" (textarea, placeholder "O resultado que este processo protege ou gera para a empresa."), "Prioridade" (botões Baixa/Média/Alta/Crítica), "Campo do disparo que escolhe a etapa" (input, placeholder "ex.: tipo_abordagem — deixe vazio se as etapas acontecem em sequência"), "Material de referência" (textarea, placeholder "Tabela de códigos, políticas, tom e postura esperados, links padrão…", ajuda: "Vale para toda conversa deste processo, inclusive nas respostas do cliente — onde não há roteiro.").
- Texto dinâmico abaixo do campo seletor: se preenchido, "Cada etapa é uma alternativa. O disparo traz o código em `{{selectorField}}` e só a etapa correspondente é enviada."; se vazio, "As etapas acontecem em sequência, na mesma conversa."
- Seção "Etapas": aviso "O texto vai como está escrito. Use colchetes para os dados que vêm do disparo — ex.: `[Nome]`, `[valor]`, `[link]`." e "Para adicionar, remover ou reordenar etapas — e para mexer em portões e condições — use o Quattro: ele reavalia o que Tino consegue fazer e ajusta os dados exigidos junto."
- Validação bloqueante: código de seleção repetido entre etapas → mensagem "Código repetido em mais de uma etapa ({{códigos}}). A seleção casaria com a primeira e ignoraria as demais — corrija antes de salvar." (impede salvar).
- Aviso não bloqueante: etapas sem código no modo catálogo → "Etapas sem código ({{ordens}}) nunca serão selecionadas por um disparo."
- Por etapa: campo de descrição operacional (placeholder "O que Tino faz nesta etapa"), campo de código (só no modo catálogo, placeholder "código"), campo de descrição em linguagem de negócio (placeholder "Mesma etapa em linguagem de negócio (lida por atendentes)"), textarea de roteiro (placeholder "Texto que Tino envia nesta etapa. Deixe vazio para ele redigir a mensagem.").
- Botões: "Cancelar", "Salvar conteúdo" (ou "Salvando…"). Mensagem de sucesso: "Conteúdo do processo salvo."

**`ProcessesToolsSection` (ferramentas/conectores do processo):**
- Título "Ferramentas"; descrição "Conectores que Tino pode usar quando conduz este processo. Selecione só as ferramentas que o roteiro precisa — o próprio processo diz quando usá-las."
- Botão "Vincular conector" (só se houver conectores disponíveis não vinculados ainda).
- Picker: "Conectores disponíveis" com botões por conector.
- Estado vazio: "Nenhuma ferramenta vinculada"; se a empresa não tem NENHUM conector cadastrado: "Conecte uma integração em [Conectores](/settings/connectors) e depois vincule as ferramentas aqui."; se já tem conectores mas nenhum vinculado a este processo: "Vincule um conector para o Tino poder executar as ações deste processo."
- Cada vínculo expandido mostra: resumo "todas as ferramentas habilitadas do conector" ou "N ferramenta(s) selecionada(s)"; botão de lixeira "Desvincular do processo"; lista de tools do conector como checkboxes (ajuda: "Nenhuma marcada = todas as habilitadas do conector. Marque para restringir ao que o processo usa."); campo "Instrução de uso (opcional)" (textarea, placeholder "Ex.: use apenas para consultar; nunca crie ou altere registros."); botão "Salvar seleção" (ou "Salvando...") que só aparece havendo alteração.
- Mensagens de sucesso: "{{servidor}} vinculado ao processo.", "Ferramentas do processo atualizadas.", "{{servidor}} desvinculado do processo."

**Fluxos:**
1. **Reavaliar capacidade (aviso de avaliação desatualizada):** botão "Reavaliar" no header → `startMapping({ processId })` → abre sessão de mapeamento na fase de avaliação.
2. **Editar conteúdo:** botão "Editar conteúdo" → troca a visualização para `ProcessesContentEditor` → salvar chama `updateProcess()` e volta para a visão de leitura com o processo atualizado.
3. **Editar estrutura com o agente:** botão "Editar com o Quattro" → `startMapping({ processId })` → navega para a sessão de mapeamento.
4. **Ativar/desativar, excluir:** mesmo padrão da lista.
5. **Ver fluxo / Ver diagnóstico:** navegação direta para `/identity/processes/flow?processId=` ou `/scout/processes/{id}` (este último fora do escopo do Cérebro).

**Regras e limites:**
- Editar `description` de uma etapa marca a avaliação de capacidade como desatualizada no backend (comentário no código); a tela então oferece "Reavaliar".
- No editor de conteúdo, string vazia limpa o campo (para permitir voltar de "catálogo" para "sequência" apagando o campo seletor); nunca envia `undefined` para não ser ignorado pelo PATCH.
- Transições (saídas) vêm de um endpoint próprio (`getProcessTransitions`), não do GET do processo; falha ao buscar não quebra a tela — a seção de saídas mostra estado vazio.

**Nomes e termos:** reforça Glossário. "5W2H" é o nome usado na própria interface para o bloco de campos descritivos do processo.

**Perguntas prováveis do usuário:**
- "Como mudo o texto que a IA manda numa etapa sem reabrir a conversa toda?" → Usar "Editar conteúdo" no detalhe do processo; dá para mudar textos e código de seleção, mas não estrutura (adicionar/remover/reordenar etapas, portões, condições) — isso exige o agente de mapeamento.
- "Por que apareceu 'Avaliação desatualizada'?" → Porque as etapas do processo mudaram desde a última vez que a IA avaliou a capacidade; use "Reavaliar".
- "Cadê o histórico de conversas que passaram por este processo?" → Não é nesta tela; fica no Diagnóstico (Scout), fora do Cérebro.

**Incertezas:**
- Não encontrei validação de tamanho máximo de texto nos campos do editor de conteúdo (whatIs, why, reference, etc.) nem contagem de caracteres na interface.

---

## Grupos (`/identity/processes/groups`)

**Como chegar:** Sidebar do Cérebro > "Processos" > "Grupos".

**Para que serve:** Reúne processos relacionados num conjunto com fluxo próprio, para uso por campanhas (o conjunto de processos disponíveis numa campanha é fechado ao grupo).

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Herdado da área (`processes`). Sem gate adicional nesta tela.

**O que há na tela:**
- Header: botão voltar (título/aria-label "Voltar para processos") para `/identity/processes`; título "Grupos de processos"; subtítulo "Reúna os processos que Tino pode encadear numa campanha. Cada grupo tem seu próprio fluxo."; botão "Novo grupo" (só aparece se já existir ao menos 1 grupo).
- Estado vazio: ícone; "Nenhum grupo ainda"; "Crie um grupo para reunir processos relacionados e disponibilizá-los a uma campanha."; botão "Criar primeiro grupo".
- Toolbar: contagem "N grupo(s)"; filtro segmentado "Todos" / "Ativos" / "Inativos".
- Grid de cartões de grupo: nome; badge "Ativo"/"Inativo"; descrição (se houver, truncada em 2 linhas); chips dos até 3 primeiros membros ordenados (o primeiro tem ícone de estrela preenchida e título "{{nome}} (inicial)"; os demais mostram iniciais); indicador "+N" se houver mais de 3; estado "Nenhum processo no grupo ainda." se vazio; rodapé com contagem "N processo(s)", botão de lixeira "Excluir grupo" e botão "Abrir".
- Tile extra no fim do grid: "Novo grupo" / "Reúna processos relacionados para uma campanha." (atalho de criação).
- Modal de exclusão (`SharedDeleteModal`).

**Fluxos:**
1. **Criar grupo:** "Novo grupo"/"Criar primeiro grupo"/tile → navega para `/identity/processes/groups/new` (tratado pela mesma página de detalhe, com `groupId === 'new'`).
2. **Abrir grupo:** clique no cartão ou botão "Abrir" → `/identity/processes/groups/{id}`.
3. **Excluir grupo:** ícone de lixeira → confirmação → `deleteProcessGroup(id)` → toast "Grupo excluído."

**Regras e limites:** Nenhuma paginação nesta lista (todos os grupos carregados de uma vez); filtro é só client-side por status.

**Nomes e termos:** "Processo inicial" = membro marcado com estrela, por onde a campanha começa (metadado apenas visual/organizacional na lista, mais relevante na tela de configuração do grupo).

---

## Configuração do grupo — criar/editar (`/identity/processes/groups/[groupId]`, inclui `/groups/new`)

**Como chegar:** Grupos > "Novo grupo" (cria) ou clicar/"Abrir" num cartão de grupo (edita). É a mesma página Vue (`groups/[groupId]/index.vue`) — quando `groupId === 'new'` ela entra em modo de criação.

**Para que serve:** Definir nome, descrição, status e o conjunto de processos-membros do grupo, incluindo se cada processo entra com fluxo próprio ou herdando o fluxo global (e opcionalmente importando o fluxo global como ponto de partida).

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Herdado da área. Sem AiCostIndicator nesta tela (não há custo de IA aqui — é cadastro puro).

**O que há na tela:**
- Header: botão voltar "Voltar para grupos" → `/identity/processes/groups`; título dinâmico ("Novo grupo" ou nome do grupo); badge Ativo/Inativo (só quando não é novo); subtítulo "Defina os processos do grupo e como o fluxo se comporta."
- Abas (`NavTabs`): "Configuração" (ativa aqui) e "Fluxo" — a aba "Fluxo" fica desabilitada em modo criação, com dica "Salve o grupo antes de editar o fluxo"; ao clicar nela (grupo já existente) navega para `/identity/processes/groups/{id}/graph`.
- Estado de erro ao carregar: "Não foi possível carregar o grupo" / "Verifique a conexão e tente de novo." / botão "Tentar de novo".
- Campo "Nome" (input, placeholder "Ex.: Suporte financeiro").
- Toggle "Grupo ativo".
- Campo "Descrição" (textarea, placeholder "Para que serve este grupo? (opcional)").
- Seção "Processos do grupo": contagem "{{N}} no grupo" + "· {{M}} importados" se houver membros trazidos por import.
  - Nota explicativa fixa: "A lista **não tem ordem fixa** — serve só para visualizar. Marque o processo **inicial** com a estrela para definir por onde a campanha começa (opcional). Processos trazidos por um **fluxo global** aparecem aninhados sob ele e saem junto."
  - Lista em "floresta": cada processo raiz tem botão de estrela (título "Processo inicial" quando marcado, "Marcar como inicial" quando não), nome, um badge de origem do fluxo — "fluxo próprio" (losango) ou "herda global" (ícone de setas), e botão "Remover do grupo" (ou "Remover do grupo (os importados saem junto)" quando tem filhos).
  - Quando um membro tem "prévia de import" pendente (marcado para importar mas ainda não salvo): bloco tracejado "Ao salvar, traz {{N}} processo(s) pelo fluxo global:" listando os nomes com selo "será importado".
  - Quando um membro já trouxe importados de verdade (persistidos): bloco "trouxe {{N}} processo(s) pelo fluxo global — saem junto com {{nome}}" com sublista de cada processo importado, selo "importado" e ícone de cadeado (indicando que não pode ser removido isoladamente, só junto com o pai).
  - Estado vazio da lista: "Nenhum processo no grupo ainda."
  - Bloco "Adicionar processo": select "Adicionar processo ao grupo…" (só lista processos ainda não membros) + botão "Adicionar" (desabilitado sem seleção).
  - Toggle "Importar fluxo global ao adicionar": texto explicativo muda conforme o estado — ligado: "Copia o fluxo global atual — pode trazer processos dependentes junto."; desligado: "Entra sem fluxo — você monta o fluxo dele dentro do grupo."
  - Aviso fixo (âmbar): "Ao salvar, esta lista **substitui o conjunto inteiro** de processos do grupo."
- Rodapé: botão "Cancelar" (volta para a lista) e botão principal "Criar grupo" (modo novo) / "Salvar grupo" (modo edição), com estado "Salvando…" durante o request.

**Fluxos:**
1. **Criar grupo:** preencher nome (obrigatório — senão toast de aviso "Dê um nome ao grupo."), adicionar processos, marcar inicial (opcional), marcar quais processos importam fluxo global, salvar → `createProcessGroup(dto)`; se algum membro estava marcado para importar, chama em seguida `importGroupFlow(created.id, { processIds })`; toast "Grupo criado e fluxo importado." (se importou) ou "Grupo criado." (se não); redireciona para a URL do grupo criado.
2. **Editar grupo:** mesmo formulário, salvar chama `updateProcessGroup(id, dto)` (substitui a lista de membros inteira) + `importGroupFlow` se houver pendências de import; toast "Grupo atualizado."; recarrega os dados.
3. **Adicionar processo ao grupo:** selecionar no dropdown, clicar "Adicionar" — se o toggle "Importar fluxo global ao adicionar" estiver ligado, o processo é marcado para importação (mostrada como prévia até salvar).
4. **Marcar processo inicial:** clicar na estrela ao lado do processo.
5. **Remover processo:** clicar no X — remove o processo e, se ele tiver trazido importados (proveniência), remove os descendentes junto.
6. **Ir para o fluxo do grupo:** aba "Fluxo" (só com grupo já salvo) → `/identity/processes/groups/{id}/graph`.

**Regras e limites:**
- Nome é obrigatório para salvar.
- Salvar SEMPRE substitui o conjunto inteiro de membros (não faz merge) — refletido no tipo `UpdateProcessGroupDto` (`members` substitui) e reforçado por aviso na tela.
- `sortOrder` enviado ao backend segue a ordem de exibição, com o processo inicial sempre em primeiro lugar.
- Import de fluxo é um passo separado (endpoint `import-flow`) disparado só para os processos marcados como pendentes de import no momento do save.
- A prévia do fecho de import (`globalFlowClosure`) é só visual — roda com as arestas globais carregadas no load; os membros reais só passam a existir depois do save.
- Membro "importado" (com pai) só pode ser removido junto do pai que o trouxe — não há remoção isolada de um nó filho na árvore.

**Nomes e termos:**
- **Processo inicial**: por onde a campanha do grupo começa (estrela).
- **Fluxo próprio (`ISOLATED`)** vs **herda global (`INHERIT`)**: modo do fluxo do grupo — badge "fluxo próprio" (losango preto) ou "herda global" (ícone de setas). Grupos novos são `ISOLATED` por padrão (comentário no tipo `ProcessFlowMode`).
- **Importar fluxo global**: copiar as arestas do fluxo global de um processo (e transitivamente dos processos que ele aponta) para dentro do grupo.

**Perguntas prováveis do usuário:**
- "Se eu tirar um processo do grupo, os que eu importei com ele também saem?" → Sim, remover um processo remove junto todos os que ele trouxe por import.
- "Editar a lista de processos apaga o que já estava lá?" → Sim, salvar sempre substitui a lista inteira de membros do grupo, não soma.
- "A ordem que aparece na tela é a ordem que a campanha segue?" → Não necessariamente — a nota da tela diz que a lista "não tem ordem fixa" e serve só para visualizar; o que importa para o começo é o processo marcado como inicial.

**Incertezas:**
- Não encontrei limite máximo de processos por grupo no código lido.
- Não confirmei se um mesmo processo pode pertencer a mais de um grupo simultaneamente (o tipo permite, mas não vi validação explícita nem impedimento na tela).

---

## Fluxo do processo (`/identity/processes/flow?processId=`)

**Como chegar:** Não está na sidebar diretamente. Alcançado por: botão "Ver fluxo" no cartão da lista de Mapeamento, botão "Ver fluxo" no detalhe do processo, ou links de conserto do Catálogo (achados `ORPHAN_TARGET`/`EXPECTED_GAP` apontam para cá via `process_transition` fix target).

**Para que serve:** Mostra, em grafo, para onde a conversa vai a partir de UM processo específico em cada desfecho possível (fluxo GLOBAL desse processo, `scope: 'global'`) — é a visão só-leitura do fluxo. Não é usada para grupos (isso é a tela de fluxo do grupo, separada).

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Herdado da área. Sem gate próprio.

**O que há na tela:**
- Se a URL não tiver `processId`, redireciona automaticamente para `/identity/processes` (a tela sempre exige um processo em foco).
- Header: botão voltar (título/aria-label "Voltar" — respeita a origem: volta para o Catálogo/Diagnóstico se veio de lá, senão cai no detalhe do processo, senão na lista); título "Fluxo · {{nome do processo}}"; subtítulo "Para onde a conversa segue em cada desfecho deste processo. Clique em outro processo para abrir o fluxo dele."; botão "Editar com o Quattro" (ou "Abrindo…").
- Estado de erro: "Não foi possível carregar o fluxo" / "Falha ao buscar as saídas do processo. Verifique a conexão e tente de novo." / botão "Tentar de novo".
- Estado vazio (processo sem nenhuma saída definida): ícone; "Nenhuma saída definida ainda" / "Este processo não tem saídas — todo desfecho cai na triagem por padrão. Defina as saídas editando o processo com o Quattro."
- Legenda acima do grafo: um item por desfecho (bolinha colorida + label: Concluído/Parcial/Falhou/Faltou dado) + item "Padrão → triagem" (linha tracejada).
- Componente `FlowGraph` (ver detalhes técnicos abaixo) — aqui em modo `editable=false` (só leitura); clicar num processo-alvo do grafo navega para o fluxo DAQUELE processo (`node-click`).
- Rodapé: "Arraste para mover, role para dar zoom. Clique num processo-alvo para abrir o fluxo dele."

**Fluxos:**
1. **Ver saídas de um processo:** abre o grafo já centralizado nele.
2. **Navegar para outro processo:** clicar num nó de processo externo → recarrega a tela com esse `processId`.
3. **Editar as saídas:** esta tela é só leitura; o botão "Editar com o Quattro" abre uma sessão de mapeamento (`startMapping({ processId })`) — a edição do fluxo GLOBAL de um processo isolado passa pelo agente, não por um editor direto na tela (diferente do fluxo de GRUPO, que tem editor direto — ver próxima seção).

**Regras e limites:**
- Alvos de tipo `PROCESS` que apontam para fora do foco atual são mostrados como o processo real (nome verdadeiro), nunca escondidos ou genéricos — comentário no código: "alvos PROCESS fora de focusIds são mostrados como o processo REAL (honesto), nunca colapsados em triagem".
- Desfecho sem regra cadastrada é sempre desenhado como seta tracejada para "Triagem" (comportamento padrão do motor).

**Nomes e termos:** "Fluxo" aqui = grafo de saídas de UM processo (equivalente ao GLOBAL, `groupId: null`), diferente do "Fluxo do grupo" (próxima seção), que edita arestas por grupo/campanha.

**Incertezas:**
- Não há edição direta de arestas nesta tela (só visualização); para editar o fluxo global de um processo fora do contexto de grupo, o único caminho encontrado no código é reabrir a conversa de mapeamento com o Quattro — não localizei uma tela de edição direta do fluxo GLOBAL (fora de grupo) equivalente ao `FlowFocusEditor` usado nos grupos.

---

## Fluxo do grupo (`/identity/processes/groups/[groupId]/graph`)

**Como chegar:** Configuração do grupo > aba "Fluxo" (só habilitada com o grupo já salvo).

**Para que serve:** Editar, em grafo interativo, para onde a conversa vai em cada desfecho de cada processo do grupo — isto é, o fluxo específico daquela campanha/grupo — além de mostrar um painel de "saúde do fluxo" com alertas estruturais.

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Herdado da área. Sem custo de IA aqui (edição estrutural, não conversa com agente).

**O que há na tela:**
- Header: botão voltar "Voltar para grupos"; título = nome do grupo (ou "Fluxo do grupo" enquanto carrega); badge Ativo/Inativo; subtítulo "Para onde Tino leva a conversa em cada desfecho, nesta campanha. A edição é por processo; o fluxo global de cada processo continua independente."
- Abas: "Configuração" / "Fluxo" (ativa).
- Estado de erro: "Não foi possível carregar o fluxo" / "Falha ao buscar o fluxo do grupo. Verifique a conexão e tente de novo." / "Tentar de novo".
- Estado "grupo sem processos": "Grupo sem processos" / "Adicione processos ao grupo para montar o fluxo de transições." / botão "Ir para a configuração".
- Seletor de modo do fluxo (dois cartões clicáveis, mutuamente exclusivos):
  - "Herdar fluxo global" — "Cada processo segue o global; o que você definir aqui **sobrescreve** só nesta campanha."
  - "Fluxo próprio do grupo" — "Ignora o global — só vale o que você montar aqui. Desfecho sem saída cai na **triagem**."
  - Trocar o modo dispara `updateProcessGroup` imediatamente (sem botão salvar separado); mostra "Salvando…" enquanto processa; toast "Grupo agora tem fluxo próprio (não herda o global)." ou "Grupo agora herda o fluxo global."
- `FlowFocusEditor` em `scope="group"`, `all-view` habilitado (permite alternar entre "Grupo completo" — visão geral só leitura — e cada processo do grupo individualmente, editável) — ver detalhes abaixo.
- Seção "Saúde do fluxo — validação estrutural do grafo":
  - 3 indicadores numéricos: "Processos no grupo", "Saídas definidas", "Desfechos cobertos" (N/total).
  - Cartão de alerta "Ciclo sem escape" (âmbar, único problema tratado como falha real): "{{processo}} → {{processo}} → … formam um ciclo sem saída para fora — a conversa pode ficar presa. Defina um desfecho que leve à triagem, a um setor ou ao encerramento."
  - Cartão informativo (não é falha) por "beco sem saída": "{{processo}} cai na triagem" / "Não tem saídas próprias, então os desfechos seguem para a triagem. Comportamento esperado — defina saídas só se quiser outro destino."
  - Cartão informativo por processo "inalcançável" (nenhuma transição de outro processo do grupo leva até ele): "{{processo}} é acionado só pela triagem" / "Nenhuma transição leva até ele a partir dos outros processos — mas a triagem ainda encaminha a conversa quando necessário."
  - Cartão informativo "Desfechos na triagem por padrão" (quando há desfechos sem regra explícita): "Desfechos sem regra explícita caem na triagem. Isso é esperado — defina uma regra só se quiser outro destino." + lista por processo dos desfechos sem regra.
  - Se não houver ciclo sem escape: cartão verde "Fluxo válido — com a triagem ativa, nenhum desfecho fica perdido."

**Editor de fluxo (`FlowFocusEditor`, componente compartilhado):**
- Barra "Visualizando fluxo do:" com botão "Grupo completo" (visão consolidada, só leitura) + um botão por processo do grupo (nome do processo); o processo ativo fica destacado.
- No modo "Grupo completo": legenda "Visão do **grupo completo** (só leitura). Clique num processo — na barra acima ou no próprio grafo — para editar o fluxo dele."
- Com um processo focado (editável): legenda "Clique numa **saída** (chip) para definir o destino de **{{processo}}** nesta campanha. Outro processo do grupo aparece esmaecido — clique nele para editar o fluxo dele. Desfecho sem saída cai na triagem por padrão."
- Clicar num chip de aresta (desfecho) abre o modal `FlowEdgeEditorModal` (ver abaixo) — pré-preenchido se a aresta já existir NO ESCOPO do grupo, ou como "nova" (cria override do grupo) se a aresta mostrada vier herdada do fluxo global.

**Modal "Editar saída" / "Nova saída" (`FlowEdgeEditorModal`):**
- Campo "Processo de origem" (select, entre os processos do grupo).
- Campo "Desfecho" (select: Concluído/Parcial/Falhou/Faltou dado).
- Campo "Tipo de alvo" (cartões de rádio, com dica por tipo):
  - "Processo" — "Encadeia para outro processo do grupo."
  - "Triagem" — "Volta para o atendimento geral."
  - "Transferir" — "Transfere para um setor humano."
  - "Encerrar" — "Finaliza a conversa."
- Campo condicional "Processo de destino" (se Processo) ou "Setor de destino" (se Transferir); para Triagem/Encerrar mostra texto "{{dica do tipo}} Sem alvo a configurar."
- Campo "Em qual etapa (opcional)" (só aparece se o processo de origem tiver etapas mapeadas): chips clicáveis "Etapa N"; texto de ajuda "Vazio = qualquer etapa." e explicação "A saída dispara quando o desfecho ocorre na(s) etapa(s) escolhida(s)."; aviso não bloqueante se outra saída do mesmo processo/desfecho já cobre etapas sobrepostas: "Já existe outra saída deste processo para o mesmo desfecho com etapas sobrepostas. O motor não bloqueia, mas o desempate fica ambíguo."
- Campo "Condição (opcional)" (input texto, placeholder "Ex.: cliente sem orçamento aprovado"; ajuda "Texto livre — contexto para o Tino, não avaliado pelo motor.").
- Validações ao salvar (toast de aviso, bloqueiam o salvar): "Escolha o processo de origem." (sem origem), "Escolha o processo de destino." (tipo Processo sem destino), "Escolha o setor de destino." (tipo Transferir sem setor).
- Botões: "Remover" (só em edição de aresta existente; lixeira), "Cancelar", "Salvar saída" (ou "Salvando…").
- Mensagens de sucesso: "Saída atualizada.", "Saída criada.", "Saída removida."

**Grafo (`FlowGraph`, renderizador comum a `flow.vue` e ao editor de grupo):**
- Construído com Vue Flow + layout automático via dagre (`rankdir: LR`, da esquerda para a direita).
- Tipos de nó: "processo" (retângulo com nome, selo "processo", selo "inicial" quando é o processo inicial do grupo, selo "fora do grupo" quando o alvo é um processo que existe mas não pertence ao grupo em foco), "Triagem" (nó tracejado, subtítulo "Atendimento geral"), "terminal" — "Encerrar" (subtítulo "Finaliza a conversa") ou "Transferir" (subtítulo = nome do setor, estilo laranja).
- Arestas coloridas por desfecho (`OUTCOME_HEX`): verde=Concluído, âmbar=Parcial, vermelho=Falhou, cinza=Faltou dado; tracejada + cinza quando é o comportamento PADRÃO (nenhuma regra explícita, cai na triagem).
- Cada aresta tem um chip de rótulo (o nome do desfecho + escopo de etapa, se houver) — clicável quando `editable=true` (abre o editor); tooltip "Editar saída".
- Interação: pan (arrastar) e zoom (scroll); zoom mínimo 0.3, máximo 1.6; nós não são arrastáveis (`nodes-draggable: false`).
- Reenquadra automaticamente ("fit view") a cada troca de dados/foco.

**Fluxos:**
1. **Alternar modo do fluxo do grupo:** clicar em "Herdar fluxo global" ou "Fluxo próprio do grupo" → salva na hora.
2. **Criar/editar uma saída:** focar um processo (botão no switcher, ou clicar nele no grafo em visão "Grupo completo") → clicar num chip de desfecho → preencher o modal → "Salvar saída". Se a aresta clicada era herdada do global, salvar CRIA uma aresta nova só do grupo (override), não altera a global.
3. **Remover uma saída (do grupo):** abrir o editor numa aresta existente do próprio escopo do grupo → "Remover".
4. **Ver o grupo inteiro:** botão "Grupo completo" no switcher — grafo consolidado, sem clique de edição nas arestas (só navegação entre processos).

**Regras e limites:**
- Só é possível editar "in place" uma aresta do PRÓPRIO escopo (a aresta do grupo, quando `scope=group`); uma aresta herdada do fluxo global aparece no grafo mas ao clicar vira criação de um override novo do grupo (não modifica a global).
- "Saúde do fluxo" é calculada 100% no cliente (comentário explícito: "a API não valida o grafo"), a partir dos membros do grupo e das transições carregadas.
- Único problema tratado como falha real (com alerta âmbar) é "ciclo sem escape" (processos que só levam uns aos outros, sem saída para fora do ciclo); becos-sem-saída, inalcançáveis e desfechos órfãos são tratados como comportamento esperado/informativo, não como erro — porque a triagem sempre resolve o caso default.
- Escopo por etapa: duas saídas do mesmo processo/desfecho podem ter etapas sobrepostas sem bloqueio do sistema, mas com aviso de ambiguidade (o motor real desempata por prioridade/recência, não replicado no front).

**Nomes e termos:**
- **Fluxo global** vs **fluxo do grupo (override)**: o global vale para o processo em qualquer contexto; o override vale só dentro daquele grupo/campanha.
- **Ciclo sem escape**: sequência de processos que se encadeiam entre si sem nenhuma saída para triagem/setor/encerramento.
- **Beco sem saída**: processo sem nenhuma transição configurada (cai na triagem em todo desfecho) — tratado como normal, não como erro.
- **Inalcançável**: processo que nenhuma transição de outro processo do grupo aponta para ele (só acessível via triagem).

**Perguntas prováveis do usuário:**
- "Editar o fluxo aqui muda o processo em outras campanhas?" → Não, quando o grupo está em modo "Fluxo próprio" ou quando você edita uma aresta específica do grupo, isso fica restrito a esta campanha; o fluxo global do processo continua independente.
- "Um processo sem saída definida quebra o atendimento?" → Não — por padrão, qualquer desfecho sem regra cai na triagem (atendimento geral); a tela trata isso como esperado, não como erro.
- "O que é considerado um problema de verdade no fluxo?" → Só ciclo sem escape (processos presos girando entre si sem chegar a um fim).

**Incertezas:**
- Não confirmei se existe algum limite de profundidade/tamanho para o grafo (quantos processos um grupo suporta antes de degradar a visualização).
- Não encontrei nesta leitura uma forma de editar o fluxo GLOBAL (fora de um grupo) diretamente por um editor gráfico equivalente — parece que a única forma é pelo agente de mapeamento (ver seção "Fluxo do processo").

---

## Descobertas (`/identity/processes/discovery`)

**Como chegar:** Sidebar do Cérebro > "Processos" > "Descobertas" (com badge de contagem de pendentes). Também alcançável pelo banner de "Descobertas pendentes" na tela de Mapeamento.

**Para que serve:** Fila de revisão de candidatos a processo que a IA identificou automaticamente — a partir de conteúdo já indexado no Cérebro ou de documentos enviados especificamente para essa análise — para o usuário decidir se aprova (materializa como processo) ou descarta.

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Herdado da área (`processes`). Sem indicador de custo de IA visível nesta tela especificamente (diferente do Mapeamento).

**O que há na tela:**
- Rótulo técnico acima do título: "ia/processos · descobertas".
- Título "Descobertas de processos"; subtítulo "Candidatos que Tino extraiu do Cérebro e de documentos enviados, aguardando sua revisão."
- Selo de contagem: "{{N}} pendente(s)" (só aparece se `count > 0`).
- Zona de upload (drag-and-drop ou clique): "Arraste documentos ou **selecione arquivos** para descobrir processos"; ajuda "até 10 arquivos · {{N}} MB cada · pdf, docx, txt"; aceita `.pdf,.txt,.doc,.docx,.xlsx,.csv,.md,.json`. Durante o upload mostra loading; ao terminar mostra resumo "{{N}} na fila" / "{{N}} ignorados".
- Painel de filtros:
  - Abas de origem (eixo principal, com contagem): "Todas", "Cérebro", "Upload".
  - Busca por nome: placeholder "Buscar por nome", `aria-label="Buscar candidato"`.
  - Toggle "incluir revisados"; quando ligado, aparecem os filtros de status de revisão: "Todos", "Pendentes", "Aprovados", "Descartados" (cada um com contagem).
  - Rodapé: contagem "N candidato(s)" + "Limpar filtros" (quando há filtro ativo).
- Lista de cartões (`ProcessesDiscoveryCandidateCard`, ver abaixo) com paginação (10 por página).
- Estado "nenhum resultado para os filtros" (há candidatos mas nenhum casa com o filtro): "Nenhum candidato com esses filtros" / "Ajuste ou limpe os filtros para ver os candidatos." / botão "Limpar filtros".
- Estado "fila realmente vazia": "Nada na fila" / "Quando Tino descobrir um processo no Cérebro ou num upload, ele aparece aqui para revisão."
- Modal de confirmação de descarte (`ProcessesDiscardCandidateModal`, ver abaixo).

**Cartão de candidato (`ProcessesDiscoveryCandidateCard`):**
- Nome do candidato (nome do processo sugerido).
- Selo de origem: "Cérebro · {{nome do conteúdo de origem}}" (com ícone de "faísca de IA") ou "Upload · {{nome do documento}}" (com ícone de upload).
- Texto relativo de criação + status: "há {{X}} min/h/dia(s) · pendente/aprovado/descartado".
- Descrição (primeiro campo não vazio entre `whatIs`/`why`/`who` do snapshot).
- Gatilhos sugeridos, como chips: "gatilho: "{{texto}}""".
- Nota fixa: "Abrir o mapeamento não descarta este candidato — ele fica pendente até você publicar o processo mapeado."
- Ações (só quando ainda não revisado — cartões revisados ficam com opacidade reduzida e sem ações): botão "Abrir mapeamento"; botão "Aprovar" com dropdown de 2 opções — "Aprovar" ("cria o processo inativo") e "Aprovar e publicar ativo" ("já entra em operação"); botão "Descartar" (vermelho).

**Modal "Descartar este candidato?" (`ProcessesDiscardCandidateModal`):**
- Rótulo técnico "ia/processos · descobertas".
- Título "Descartar este candidato?"
- Texto: "O candidato **{{nome}}** sai da fila de revisão. Você ainda pode revê-lo ativando "incluir revisados"."
- Botões "Cancelar" e "Descartar" (com ícone de lixeira).

**Fluxos:**
1. **Enviar documento para análise:** arrastar/selecionar arquivo(s) (até 10 por vez, formatos válidos, cada um até o limite de MB configurado) → `uploadDiscoveryDocuments()` → resposta mostra quantos entraram na fila e quantos foram ignorados (duplicados/etc.) → a lista é recarregada; quando o processamento assíncrono da IA termina, chega um evento de socket (`processDiscoveryCreated`) com toast "Tino descobriu {{N}} candidato(s) a processo em "{{fonte}}"." e a lista/lista de contagem são atualizadas automaticamente. Se o mesmo conteúdo já tinha gerado candidatos pendentes, chega `processDiscoveryDuplicate` (só para uploads feitos por esta tela) com toast de aviso "{{N}} candidato(s) já estava(m) na fila — nada novo foi criado a partir de "{{fonte}}".".
2. **Abrir mapeamento a partir de um candidato:** botão "Abrir mapeamento" → `openMappingFromDiscovery(candidate.id)` → navega para `/identity/processes/mapping/{sessionId}?fromDiscovery={candidateId}` — ação sem efeito colateral: NÃO materializa nem descarta o candidato (comentário no código: "não materializa, não indexa no RAG, não consome o draft").
3. **Aprovar como inativo:** dropdown "Aprovar" → opção "Aprovar" → `review(id, { action: 'APPROVE', activate: false })` → cria o processo já como inativo (precisa ser ativado manualmente depois, na lista de Mapeamento).
4. **Aprovar e publicar ativo:** dropdown "Aprovar" → opção "Aprovar e publicar ativo" → `review(id, { action: 'APPROVE', activate: true })` → cria o processo já ativo.
5. **Descartar:** botão "Descartar" → modal de confirmação → `review(id, { action: 'REJECT' })` → some da fila padrão (mas reaparece com "incluir revisados" ligado, com status "descartado").

**Regras e limites:**
- Upload: até 10 arquivos por vez; tipos aceitos `.pdf, .txt, .doc, .docx, .xlsx, .csv, .md, .json`; tamanho máximo por arquivo definido por `MAX_UPLOAD_SIZE_MB` (constante compartilhada — valor exato não confirmado nesta leitura, ver Incertezas); arquivo com formato inválido gera aviso "Formato não suportado: {{nome}}"; arquivo maior que o limite gera aviso "{{nome}} excede o limite de {{N}} MB."
- Aprovar um candidato materializa (cria de fato) um processo — a resposta da API indica se foi criado (`created`) ou atualizado por conflito, e quantas transições globais vieram junto (não exibido diretamente na UI lida, mas presente no tipo de retorno).
- Ao aprovar, o dashboard/onboarding da empresa é atualizado na hora (fase "Processos" do progresso de onboarding).
- Paginação client-side (10 por página); ao aprovar/descartar a lista encolhe e a página atual é ajustada automaticamente para não ficar vazia.
- Duplicatas de origem `BRAIN` (conteúdo indexado no Cérebro) não geram o toast de aviso de duplicado — só uploads feitos diretamente nesta tela (`PROCESS_UPLOAD`) geram esse aviso.

**Nomes e termos:**
- **Origem "Cérebro" (`BRAIN`)**: candidato derivado de um conteúdo já indexado no Cérebro (base de conhecimento).
- **Origem "Upload" (`PROCESS_UPLOAD`)**: candidato vindo de um documento enviado especificamente nesta tela — NÃO indexa o documento no Cérebro (comentário no código: "process-only, NÃO indexa no Cérebro").
- **Aprovar** = materializar o candidato como processo real (inativo por padrão, ou ativo se escolhida a opção "publicar ativo").
- **Descartar** = rejeitar o candidato (sai da fila padrão, mas fica rastreável em "incluir revisados").

**Perguntas prováveis do usuário:**
- "Enviar um documento aqui coloca o conteúdo dele na base de conhecimento?" → Não — o upload desta tela serve só para descobrir processos, não indexa o documento no Cérebro.
- "Se eu abrir o mapeamento de um candidato e não terminar, ele some da fila?" → Não, abrir o mapeamento não descarta nem materializa o candidato; ele continua pendente até o processo ser publicado.
- "Aprovar já coloca o processo em produção?" → Só se escolher "Aprovar e publicar ativo"; a opção "Aprovar" simples cria o processo inativo.
- "Posso ver os candidatos que já descartei?" → Sim, ativando o toggle "incluir revisados" e filtrando por status "Descartados".

**Incertezas:**
- Não confirmei o valor exato de `MAX_UPLOAD_SIZE_MB` (constante importada de `~/utils/media`, não lida nesta análise).
- O tipo `ProcessDiscoveryDuplicateEvent`/evento de socket tem uma nota no próprio código-fonte pedindo confirmação com a API ("CONTRATO (confirmar com a API)"), então o comportamento exato desse evento pode mudar.

---

## Sessão de mapeamento (`/identity/processes/mapping/[sessionId]`)

**Como chegar:** Não está na sidebar diretamente (a sidebar aponta para "Mapeamento" = a lista `/identity/processes`). Alcançada por: "Novo processo"/exemplos na lista, "Editar processo"/"Editar com o Quattro" no cartão ou no detalhe, "Reavaliar" quando a avaliação está desatualizada, "Abrir mapeamento" numa Descoberta, "Editar com o Quattro" na tela de Fluxo.

**Para que serve:** Interface de chat em tempo real com o agente de mapeamento (Quattro), que conduz uma entrevista guiada para construir ou editar um processo (5W2H + passo a passo + avaliação de capacidade + saídas), com um painel de prévia ao lado e uma etapa final de revisão antes de publicar.

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Indicador de custo de IA (`AiCostIndicator`, variante "badge") no topo, com tooltip: "A conversa de mapeamento com o Quattro e a avaliação de capacidade consomem créditos de IA. Veja o consumo em Configurações → Faturamento → Consumo."

**O que há na tela:**
- Layout dividido em dois modos: "mapping" (conversa + prévia lado a lado) e "review" (revisão final antes de publicar).
- Topbar: botão voltar (título/aria-label "Voltar"); nome do processo (ou "Novo processo") + "· mapeamento conversacional" (escondido em telas pequenas); indicador de custo de IA; botões contextuais:
  - Modo mapeamento: "Sair" (título "Volta para a lista. Seu rascunho fica salvo."); "Salvar alterações" (editando) / "Salvar sem publicar" (criando), desabilitado sem nome preenchido, com estado "Salvando…"; "Revisar" / "Revisar e publicar" (com indicador pulsante quando o mapeamento chegou à fase final).
  - Modo revisão: "Voltar à conversa"; "Publicar processo" (ou "Publicando…").
- Banner "Avaliar capacidade" (aparece quando já existe playbook mas ainda não foi avaliado, em qualquer fase): "A Quattro pode avaliar a capacidade dela em cada etapa do playbook." + botão "Avaliar capacidade" (ou "Avaliando…") + botão "Pular por ora" (título "Segue para a revisão sem avaliar. A avaliação pode ser feita depois.").
- Banner de conclusão (quando a fase chega a "Saídas"): "**Processo mapeado!** Revise o playbook e publique para o Tino começar a seguir." + botão "Revisar e publicar".
- Indicador de fases no topo do chat (`ProcessesMappingChat`), em ordem: Triagem, Descoberta, Contexto, Playbook, Avaliação, Revisão, Saídas — com check nas concluídas e destaque na atual.
- Aviso fixo enquanto não chega à fase final: "O mapeamento só fica completo depois da etapa **Saídas**."
- **Chat (`ProcessesMappingChat`):**
  - Mensagens do usuário (à direita, avatar com inicial do nome) e da Quattro (à esquerda, avatar com ícone de IA, rótulo "Quattro" + selo "IA"); suporta **negrito** simples no texto.
  - Dica opcional por mensagem da IA (`meta.tip`), em card amarelo com rótulo "DICA" e botão de copiar (tooltip "Copiado!"/"Copiar dica").
  - Indicador de "digitando" (3 pontinhos) enquanto aguarda resposta.
  - Composer: textarea que cresce automaticamente; placeholder muda conforme o estado — "Aguardando resposta do Quattro…" (enviando) ou "Responda ao Quattro…"; Enter envia (Shift+Enter quebra linha); digitar em qualquer lugar da página foca automaticamente o composer (atalho de conveniência); rodapé explicativo: "O Quattro está pensando — aguarde a resposta antes de enviar outra mensagem." (enviando) ou "O Quattro extrai os campos 5W2H automaticamente — você só conversa." (ocioso).
- **Prévia (`ProcessesMappingPreview`), ao lado do chat:**
  - Cabeçalho: "Processo sendo mapeado"; nome (ou "Novo processo"); selos "5W2H" e "Rascunho"; barra de cobertura (`ProcessesCoverageBar`).
  - Cartões por campo, com borda tracejada quando ainda vazio: "O QUÊ — Qual é o processo?", "POR QUÊ — Por que isso importa?", "QUANDO — Quando o processo é disparado?", "QUEM — Setores envolvidos?", "ONDE — Em quais canais?", "COMO — Qual é o passo a passo?" (lista de `ProcessesStepRow`), "FERRAMENTAS — O que Tino vai usar?" (tools MCP sugeridas pela avaliação, agrupadas por conector, com nota "Ao salvar, essas ferramentas ficam vinculadas ao processo — ajuste depois na página do processo."), "QUANTO — Qual a prioridade?"
  - Texto padrão em campos ainda vazios: "A Quattro preenche/identifica/monta [...] conforme a conversa avançar." (varia por campo).
  - Rodapé fixo: botão "Sair" e botão "Revisar".
- **Modo revisão ("Revisão final"):**
  - Título "Revisão final" / "Confira o playbook que Tino vai seguir. Volte à conversa para ajustar qualquer ponto com a Quattro."
  - Componente `ProcessesReview` (mesmo usado no detalhe do processo, ver seção anterior) mostrando o 5W2H, cobertura e passo a passo.
  - Seção "Revisar saídas": "Para cada desfecho do processo, defina para onde a conversa segue. Aceite, edite ou descarte as sugestões da Quattro. As saídas são gravadas ao publicar." — componente `ProcessesTransitionReview` (ver detalhes abaixo).
  - Seção "Fluxo do processo" (só se houver saídas para mostrar): grafo (`FlowGraph`) de prévia; legenda muda conforme o contexto — "Como a conversa segue hoje em cada desfecho deste processo." (editando processo existente) ou "Prévia das saídas que serão gravadas ao publicar." (processo novo).
  - Cartão final: "Tudo certo com o playbook?" / "Publicar deixa o processo ativo para o Tino seguir nas conversas reais." + botões "Voltar à conversa" e "Publicar processo".
- Modal de confirmação ao sair com rascunho não salvo (`SharedConfirmModal`): "Você tem alterações que ainda não foram salvas neste processo. Se sair agora, elas ficam apenas no rascunho da conversa. Deseja sair mesmo assim?"
- Aviso nativo do navegador (beforeunload) ao tentar fechar a aba/recarregar com alterações não salvas.
- Estado de sessão não encontrada: "Sessão não encontrada" / "A sessão de mapeamento expirou ou não pertence à sua empresa." / botão "Voltar para processos".

**`ProcessesTransitionReview` (revisão de saídas sugeridas pela IA):**
- Banner fixo: "**Salvar o processo não salva as saídas.** As saídas abaixo só são gravadas ao publicar. Todo desfecho sem regra volta para a **triagem** por padrão."
- Estado vazio: "Nenhuma saída definida ainda. Cada desfecho volta para a triagem por padrão — você pode defini-las na conversa com a IA ou depois no grafo de transições."
- Um cartão por saída sugerida (ou já persistida, ao editar): desfecho (badge colorido), alvo (rótulo do tipo: "Triagem · Atendimento geral", "Encerrar conversa", "Transferir · {{setor}}", "Processo · {{nome}}", "Processo novo · {{nome}}" ou "Processo · escolher"), condição opcional ("Quando: {{texto}}"), selo de escopo de etapa, selo "salva" (para saídas já persistidas).
- Estado "processo novo, ainda não existe" (`isNew`): "Processo novo — ainda não existe." + botão "Criar agora" (ou "Criando…") + botão "Mandar pra triagem".
- Estado "sugestão de processo não resolvida" (a IA sugeriu um nome que não bateu com nenhum processo existente): "Não encontrei o processo «{{nome}}». Escolha o destino:" — se houver um candidato aproximado (match parcial por substring/tokens ≥50%), mostra "Parece ser:" com botão "Usar «{{nome candidato}}»" (não vincula sozinho, só sugere); select "Escolher processo…"; botão "Criar este" (ou "Criando…"); botão "Mandar pra triagem".
- Modo edição por cartão: select "Tipo de alvo" (com dica de cada tipo), select condicional de processo/setor, chips de etapa "Etapa N" (rodapé "Vazio = qualquer etapa"), campo "Condição (opcional)" (placeholder "Ex.: quando faltou orçamento").
- Ações por cartão: badge "Aceita" (quando já resolvido e não em edição), botão editar (lápis), botão descartar (lixeira) — cartão descartado fica esmaecido com botão "Reincluir esta saída".
- Ao criar um processo "agora" a partir de uma sugestão: `createProcess({ name, isActive: false })` → toast "Processo "{{nome}}" criado (desativado). Edite-o depois para detalhar."

**Fluxos:**
1. **Iniciar mapeamento do zero ou por exemplo:** a sessão já chega criada (a lista já chamou `startMapping`); se veio de um exemplo, a mensagem "seed" é pré-preenchida no composer automaticamente.
2. **Conversar:** digitar e enviar mensagens; a Quattro responde e vai preenchendo a prévia e avançando de fase.
3. **Avaliar capacidade:** quando já existe playbook (etapas) e ainda não foi avaliado, aparece o banner de avaliação; "Avaliar capacidade" dispara `assessMapping()` e recarrega a sessão.
4. **Salvar sem publicar:** botão "Salvar sem publicar" (criando) ou "Salvar alterações" (editando) → `mapping.save(false)` → toast "Processo salvo sem publicar (desativado). Ative quando quiser que Tino o utilize." (criando) ou "Alterações salvas." (editando) → navega para o detalhe do processo.
5. **Revisar e publicar:** botão "Revisar"/"Revisar e publicar" → troca para o modo revisão → ajustar as saídas sugeridas (aceitar/editar/descartar/criar processo novo) → "Publicar processo" → `mapping.save(true)` → toast "Processo publicado! Tino já vai usar como playbook." → persiste as saídas (`persistTransitions`, cria/atualiza/remove conforme o plano coletado do `TransitionReview`) → se havia saída sem alvo definido, toast de aviso "{{N}} saída(s) sem alvo definido ficaram de fora. Defina-as depois no grafo de transições."; se sucesso ao persistir saídas, toast "Saídas atualizadas no grafo de transições." → se a sessão veio de uma Descoberta (`fromDiscovery`), rejeita o draft de origem para não duplicá-lo na fila → atualiza a detecção de onboarding → navega para o detalhe do processo publicado.
6. **Sair sem salvar:** botão "Sair"/voltar → se há alterações não persistidas (`dirty`), pede confirmação antes de sair.

**Regras e limites:**
- O mapeamento só é considerado "completo" ao chegar à fase `transitions` (Saídas) — é o que ativa o banner de conclusão e o indicador pulsante no botão "Revisar".
- "Avaliar capacidade" fica disponível sempre que há passos mapeados e ainda sem avaliação — independente da fase da conversa ou de como a sessão foi aberta (comentário explícito no código sobre corrigir um bug anterior em que sessões vindas de Descoberta ou edição não mostravam o botão).
- Salvar sem publicar cria/atualiza o processo mas NÃO grava as saídas (transições) — isso só acontece ao publicar.
- Publicar reconcilia as saídas: cria as novas resolvidas, atualiza as alteradas, remove as descartadas; linhas inalteradas não são reenviadas (evita duplicar transições ao republicar um processo já editado).
- Resolução de nome de processo sugerido pela IA como alvo de saída é normalizada (ignora acentos/maiúsculas/pontuação) e só vincula automaticamente em match exato; candidatos parecidos (score ≥ 50% de sobreposição de tokens, ou substring) são só sugeridos, nunca vinculados sozinhos.
- Abrir uma sessão de mapeamento a partir de uma Descoberta não consome nem materializa o candidato — só ao publicar o processo o draft de origem é rejeitado (para não duplicar na fila).

**Nomes e termos:** reforça Glossário — "Quattro" é o nome do agente aqui; "fase" = uma das 7 etapas da conversa guiada (Triagem, Descoberta, Contexto, Playbook, Avaliação, Revisão, Saídas).

**Perguntas prováveis do usuário:**
- "Posso sair no meio da conversa e continuar depois?" → Sim, "Sair" volta para a lista mantendo o rascunho da conversa; se havia alterações não salvas como processo, pede confirmação antes.
- "Salvar sem publicar deixa o Tino usando o processo?" → Não — o processo fica desativado; é preciso ativá-lo (na lista ou no detalhe) ou publicar diretamente pela revisão.
- "As saídas sugeridas pela IA são salvas junto quando eu salvo o processo?" → Não, só ao publicar (na etapa de revisão) as saídas são de fato gravadas.

**Incertezas:**
- Não confirmei o texto exato de todas as mensagens/dicas que a Quattro pode enviar (o conteúdo da conversa é gerado dinamicamente pelo backend/IA, não está no código do front).
- Não encontrei limite de mensagens ou de tempo de sessão de mapeamento no código lido.

---

## Catálogo (`/identity/processes/consistency`)

**Como chegar:** Sidebar do Cérebro > "Processos" > "Catálogo" (a mesma aba/entrada da sidebar cobre também `/identity/processes/insights`, que hoje é uma rota morta redirecionando para o Scout — ver seção de rotas mortas). Também alcançável por links de conserto do Diagnóstico (Scout) e por "ver no diagnóstico" nesta própria tela.

**Para que serve:** Auditoria estrutural do cadastro de processos — problemas que dá para detectar só olhando o cadastro, sem depender de conversas reais (saídas sem destino, gatilhos repetidos, processos sem passo a passo, avaliação desatualizada, etc.), com gravidade e um botão de conserto para cada achado.

**Quem vê:** Admin/Gestor da Empresa.

**Plano, créditos e bloqueios:** Herdado da área (`processes`). Sem custo de IA direto nesta tela (o relatório é determinístico/recalculado a cada carregamento, não uma nova chamada de IA).

**O que há na tela:**
- Banner opcional `SharedFromFindingBanner`: aparece só quando a URL carrega `?from=achado:<id>` (chegou via link de conserto de outro lugar) — mostra "você veio de um achado" + o motivo (`why`) + botão "voltar ao achado".
- Header: botão voltar (título/aria-label "Voltar para processos"); título "Catálogo"; descrição "O que está quebrado no cadastro dos processos, sem depender de conversas: saídas sem destino, gatilhos repetidos, processos sem passo a passo. Cada achado traz o problema, a gravidade e o próximo passo."; botão "Reavaliar" (ícone de setas circulares, gira durante o carregamento) — refaz a consulta do relatório.
- Linha de metadados: "{{N}} inconsistência(s) no catálogo" + "gerado {{data/hora pt-BR}}".
- Barra de filtros (fixa no topo ao rolar — `sticky`):
  - Gravidade: pills "Alta"/"Média"/"Baixa" (multi-seleção, com contagem por gravidade).
  - Select "Todos os tipos" + um tipo por `ConsistencyType` presente nos achados, com contagem — ordem de exibição: "saída sem destino", "gatilhos repetidos", "destino inexistente", "sem passo a passo", "avaliação desatualizada", "não avaliado", "nunca acionado".
  - Busca: placeholder "Buscar processo..." (casa contra nome do processo, detalhe do achado e o tipo).
- Linha "mostrando X de Y" + "· Z fora do filtro" (quando há filtro ativo) + botão "limpar filtros".
- Resultados agrupados por gravidade (mais graves primeiro), cada grupo com um "kicker" ("alta prioridade"/"média prioridade"/"baixa prioridade") e contagem de achados.
- Cada achado (cartão): badge de gravidade; rótulo do tipo (`CONSISTENCY_TYPE_LABEL`, ex.: "saída sem destino", "gatilhos repetidos"); nome do processo (se houver); texto do problema (`detail`, pt-BR, pronto para exibir, gerado pelo backend); bloco "→ como resolver" com o texto pronto (`howToFix`, também do backend); botão "ver no diagnóstico →" (link, não botão de ação — evidência, não conserto — navega para `/scout/processes/{id}`, fora do Cérebro); botão de conserto com o rótulo específico do tipo de achado e seta (ver tabela abaixo).
- Botão "Carregar mais ({{N}})" quando há mais achados além do teto de exibição por página (30 por vez) — comentário no código: "não é paginação: é teto declarado, com o resto atrás de uma ação explícita", motivado por catálogos de empresas grandes passarem de 400 achados.
- Estado vazio: se sem filtro ativo, "Catálogo consistente" / "Nenhum problema estrutural encontrado no cadastro dos processos."; se com filtro ativo e nada corresponde, "Nada corresponde aos filtros" / "Ajuste a gravidade, o tipo ou a busca para ver os achados."

**Tipos de achado e conserto padrão (`CONSISTENCY_TYPE_LABEL` / `CONSISTENCY_ACTION` / `CONSISTENCY_FIX_KIND`):**
| Tipo (rótulo na tela) | Botão de conserto | Para onde leva |
|---|---|---|
| `UNMAPPED_EXIT` — "saída sem destino" | "Definir o próximo passo em Fluxo" | `/identity/processes/flow?processId=` |
| `DUPLICATE_TRIGGERS` — "gatilhos repetidos" | "Corrigir a descrição em Processos › Cadastro" | `/identity/processes/{id}` |
| `ORPHAN_TARGET` — "destino inexistente" | "Definir o próximo passo em Fluxo" | `/identity/processes/flow?processId=` |
| `NO_PLAYBOOK` — "sem passo a passo" | "Reescrever a etapa X em Mapeamento" ou "Reescrever o passo a passo em Mapeamento" | abre sessão de mapeamento (`startMapping`) |
| `STALE_ASSESSMENT` — "avaliação desatualizada" | idem acima (mapeamento) | idem |
| `UNASSESSED` — "não avaliado" | idem acima (mapeamento) | idem |
| `NEVER_ENGAGED` — "nunca acionado" | "Corrigir a descrição em Processos › Cadastro" | `/identity/processes/{id}` |

Cada botão de conserto tem, internamente, um "porquê" pronto (`why`) que acompanha o link (ex.: para saída sem destino: "Desfecho sem próximo passo declarado devolve a conversa para a triagem."; para gatilhos repetidos: "A hora de entrar no processo vem da descrição e do gatilho. Se as palavras do cliente não batem com elas, a IA não encontra o processo."; para etapas: "O texto da etapa é o que a IA tenta cumprir. Se ele falha nas conversas reais, é o texto que muda.").

**Fluxos:**
1. **Reavaliar o catálogo:** botão "Reavaliar" → refaz `getConsistencyReport()` (é sempre recalculado no servidor a cada consulta — "Reavaliar" é essencialmente um refetch) → toast "Catálogo reavaliado."
2. **Filtrar achados:** por gravidade (multi), tipo (único) e busca por texto — combinam-se (E lógico).
3. **Consertar um achado:** botão de conserto → navega (ou abre sessão de mapeamento, para os tipos ligados a etapas) para a superfície correta, carregando contexto de volta (`?from=achado:{tipo}:{processo}&back=/identity/processes/consistency&why=...`), de forma que a tela de destino mostre o banner "você veio de um achado" com o motivo e um link para voltar.
4. **Ver evidência de execução:** link "ver no diagnóstico →" (só evidência, nunca ação) → `/scout/processes/{id}` (fora do Cérebro).
5. **Ver mais achados além do teto:** botão "Carregar mais (N)" — aumenta o teto de exibição em 30.

**Regras e limites:**
- O relatório é 100% determinístico e recalculado a cada GET; não há um botão de "gerar" versus "reavaliar" — os dois são a mesma chamada.
- Teto de exibição de 30 achados por vez, independente da paginação tradicional — existe para não travar a tela em empresas com catálogos grandes (>400 achados mencionado no comentário do código).
- Trocar qualquer filtro reseta o teto de volta a 30 (`visible = PAGE_SIZE`).
- O conserto de um achado só é oferecido quando o achado tem `processId` (achados sem processo associado não têm botão de conserto nem link de diagnóstico).

**Nomes e termos:**
- **Achado**: cada problema estrutural encontrado (uma linha do relatório).
- **Gravidade**: Alta / Média / Baixa (`Severity`).
- **Evidência vs. conserto**: distinção explícita no código — "ver no diagnóstico" é sempre link (mostra o impacto real em conversas), o botão de ação é sempre o conserto (edita o cadastro).

**Perguntas prováveis do usuário:**
- "'Reavaliar' consome créditos de IA?" → Não há indicação de custo de IA nesta tela; o relatório parece ser cálculo determinístico sobre o cadastro, não uma chamada de modelo (mas não há confirmação explícita no comentário do código — ver Incertezas).
- "Por que só vejo 30 achados mesmo tendo mais?" → É um teto proposital de exibição (não some nada, só precisa clicar em "Carregar mais").
- "Cadê a nota de aderência/uso do processo aqui?" → Não fica aqui; isso é execução (Diagnóstico, no Scout) — o Catálogo só olha o cadastro.

**Incertezas:**
- Não confirmei se "Reavaliar" tem algum custo (créditos de IA) — o código não indica chamada de IA nesta tela, mas não há confirmação explícita nem indicador de custo visível.
- Não encontrei nesta leitura a lista completa de regras que geram cada tipo de achado (a lógica de geração vive no backend, fora do escopo desta auditoria de frontend).

---

## Modal "Candidatos a processo" — fora da área Processos, mas reutiliza os mesmos componentes (`components/property/ProcessSuggestionsReviewModal.vue`)

**Como chegar:** Não fica em `/identity/processes/*` — é um modal aberto a partir de um item de conteúdo (property) na Base de Conhecimento do Cérebro (`/identity/properties`, fora do escopo desta auditoria). Documentado aqui só porque reaproveita os mesmos componentes de Descobertas (`ProcessesDiscoveryCandidateCard`, `ProcessesDiscardCandidateModal`).

**Para que serve:** Mostra, a partir de UM conteúdo específico do Cérebro (documento, FAQ, site), quais candidatos a processo foram descobertos a partir dele — mesma revisão (aprovar/publicar/descartar/abrir mapeamento) da tela de Descobertas, mas filtrada a essa origem.

**O que há na tela:** Título "Candidatos a processo"; subtítulo "Descobertos em "{{nome do conteúdo}}""; lista de `ProcessesDiscoveryCandidateCard` (mesmo componente da tela de Descobertas); estado vazio "Nenhum candidato a processo para este conteúdo."

**Observação:** Não é uma tela nova a documentar em detalhe (mesmo comportamento de Descobertas), mas é bom saber que esse ponto de entrada existe, já que um usuário pode perguntar "eu vi candidatos a processo aparecerem dentro de um documento da base de conhecimento, isso é diferente da tela de Descobertas?" — resposta: é a mesma lógica e os mesmos cartões, só filtrada a esse conteúdo específico.

---

## Mensagens de erro genéricas (toasts de serviço, aplicam-se a todas as telas desta área)

Quando uma chamada falha e o backend não manda uma mensagem específica, os serviços mostram estes textos padrão (toast de erro):
- Processos: "Erro ao buscar processos.", "Erro ao buscar o processo.", "Erro ao criar o processo.", "Erro ao atualizar o processo.", "Erro ao alterar o status do processo.", "Erro ao excluir o processo."
- Descobertas: "Erro ao enviar documentos para descoberta de processos.", "Erro ao carregar candidatos a processo.", "Erro ao aprovar candidato." / "Erro ao descartar candidato.", "Erro ao abrir o mapeamento a partir do candidato."
- Grupos: "Erro ao buscar os grupos de processos.", "Erro ao buscar o grupo de processos.", "Erro ao criar o grupo de processos.", "Erro ao atualizar o grupo de processos.", "Erro ao importar o fluxo no grupo.", "Erro ao excluir o grupo de processos."
- Mapeamento: "Erro ao iniciar o mapeamento.", "Erro ao carregar a sessão de mapeamento.", "Erro ao enviar a mensagem.", "Erro ao avaliar a capacidade da IA.", "Erro ao salvar o processo."
- Transições: "Erro ao buscar as transições.", "Erro ao buscar o fluxo efetivo.", "Erro ao criar a transição.", "Erro ao atualizar a transição.", "Erro ao excluir a transição."
- Catálogo/métricas: "Erro ao auditar a consistência do catálogo." (as demais métricas — funil, qualidade, cobertura, uso, diagnóstico, recall do roteador — pertencem à área de Diagnóstico no Scout, fora deste escopo, mas usam o mesmo padrão de toast).
- Aprovar/descartar candidato de descoberta tem toast de SUCESSO padrão também: "Candidato aprovado!" / "Candidato descartado." (nota: a tela de Descobertas em si usa textos ligeiramente diferentes vindos do composable — "processo materializado" não aparece como toast direto na tela, mas o serviço genérico usa esses).
- Sempre que o backend manda uma mensagem própria (`err.response.data.message`), ela substitui o texto padrão acima.

---

## Achado fora de escopo (não é tela de Processos, mas foi tocado durante a leitura)

O arquivo `types/tools.ts` (mencionado no escopo original desta tarefa) define `ToolAction`, `ToolAssignment` etc. — mas isso é a estrutura de "ferramentas" ligada a CAMPANHAS (ações como `TRANSFER_TO_HUMAN`, `SEND_ATTACHMENT`, `END_CONVERSATION`, `PRIORITY_QUEUE`), um conceito diferente das "Ferramentas" (conectores MCP) vistas em `ProcessesToolsSection.vue`, que usa `~/types/mcp` e `~/services/mcp.service`. Não encontrei nenhum uso de `types/tools.ts` dentro das páginas/componentes de `/identity/processes/*` lidas nesta auditoria — parece pertencer a outra área do produto (provavelmente configuração de campanhas), não à área de Processos do Cérebro.

