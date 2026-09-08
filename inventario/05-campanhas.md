# Inventário de telas — 05 · Campanhas

Fonte: clone da `main` do `tartini-web` em 03/09/2026 (Nuxt 3 + Vue 3, UI em pt-BR). Só leitura. Os textos entre aspas ou em negrito estão transcritos exatamente como aparecem no código (fonte para negritos e caminhos da central de ajuda). O que não foi possível confirmar no código está marcado em **Incertezas**.

Arquivos lidos: `pages/campaigns/**`, `pages/settings/campaign-integrations.vue`, `pages/settings/channels/whatsapp-waba/templates/[channelId].vue`, `components/campaigns/**`, `components/settings/channels/TemplateManagement.vue`, `layouts/campaigns.vue`, `layouts/default.vue`, `utils/campaigns.ts`, `utils/schedule.ts`, `utils/entitlements.ts`, `types/campaigns.ts`, `types/campaign-metrics.ts`, `types/whatsapp-templates.ts`, `services/campaigns.service.ts`, `services/campaign-metrics.service.ts`, `services/template.service.ts`, `services/varejo-online.service.ts`, `services/integration-status.service.ts`, `services/conversation-webhook.service.ts`, `composables/useCampaignCreateWizard.ts`, `composables/useCampaignTestConversation.ts`, `composables/useTemplateSync.ts`, `composables/useAvailabilityImport.ts`, `composables/usePlatformOwner.ts`, `composables/usePlanGate.ts`, `composables/useCreditGate.ts`, `composables/useSettingsMenu.ts`, `components/ui/PlatformGate.vue`, `components/billing/PlanUpgradeWall.vue`, `components/shared/CreditGateBanner.vue`, `components/shared/SubscriptionBanner.vue`, `components/shared/Sidebar.vue`, `components/shared/ConfirmModal.vue`, `middleware/auth.global.ts`, `docs/visibilidade-por-papel.md`, `nuxt.config.ts`, mais os pontos de contato com campanhas em `components/inbox/**`, `components/conversation-center/**`, `pages/conversations/**`, `components/home/**`, `pages/settings/billing/credits.vue`.

---

## 0. Visão geral da área (vale para todas as telas)

### Como chegar
- Menu lateral principal (ícone de megafone) > **Campanhas** (tooltip **Campanhas**), link `/campaigns`, que redireciona para `/campaigns/overview` (tela intermediária mostra "Redirecionando para campanhas...").
- Dentro da área existe uma segunda barra lateral (cabeçalho **Campanhas**) com o submenu, nesta ordem:
  1. **Panorama** → `/campaigns/overview`
  2. **Campanhas** → `/campaigns/dashboard`
- O submenu pode ser recolhido/expandido pelo botão de alternância ao lado do título de cada tela (componente `SharedSidebarToggleButton`). No celular (abaixo de 1024px) a barra vira um cabeçalho fixo **Campanhas** com botão de menu que abre o submenu em gaveta (fecha ao navegar ou no **X**).
- O menu inferior do celular (`components/inbox/MobileMenu.vue`) tem só **Início**, **Inbox**, **Unidade** e **Config**; não há atalho para Campanhas ali. O acesso no celular é pelo menu principal ou pela URL.
- Layout: `overview`, `dashboard`, `create`, `edit/[id]` e `entity/[entityId]` usam o layout `campaigns` (com submenu). A tela de detalhe (`/campaigns/[id]`) e a tela `/campaigns/setup` NÃO declaram layout, portanto usam o layout `default` (só o menu principal, sem o submenu de Campanhas).

### Quem vê (papéis)
- Item de menu **Campanhas**: `requires: 'manager'` → aparece para quem tem papel gestor ou superior em QUALQUER nível (Empresa, Área ou Unidade) ou para `SYSTEM_ADMIN`. **Atendente não vê o item.**
- Guarda de rota (`middleware/auth.global.ts`): apenas `/campaigns/dashboard` está em `managerPages` (não-gestor é redirecionado para `/home`). As demais rotas `/campaigns/*` não têm guarda própria no front; a proteção real é do backend.
- Matriz oficial (`docs/visibilidade-por-papel.md`, linha "Campanhas"): Dono ✅ · Admin da Empresa ✅ · Gestor da Empresa ✅ · Gestor de Área 🔒 (só o escopo dele) · Gestor de Unidade 🔒 · Atendente ❌. O recorte por escopo é feito pelo backend ("cerca hereditária" em `GET /campaigns/all`).
- **Contatos de Campanha** (`/settings/campaign-integrations`): só Admin da Empresa (ou `SYSTEM_ADMIN`) — está em `companyAdminPages` e em `COMPANY_ADMIN_ROUTES` (o tile some do menu de Configurações para os demais e a rota redireciona para `/home`).
- **Templates WhatsApp** (`/settings/channels/whatsapp-waba/templates/:channelId`): prefixo `/settings/channels` → gestor+ em qualquer nível; o backend autoriza pelo papel sobre a unidade dona do canal.
- Atendente no Inbox: vê o nome da campanha na ficha do contato, mas sem link para a campanha (`canOpenCampaign = canAccess('MANAGER')`).

### Plano (feature `campaigns`)
- `utils/entitlements.ts`: `FEATURE.CAMPAIGNS = 'campaigns'` ("Campanhas (agendadas, webhook, follow-ups, métricas, integrações)"). Rotas gateadas: tudo que começa com `/campaigns` e `/settings/campaign-integrations`.
- O item de menu **não é escondido** quando o plano não tem a feature; ao abrir qualquer rota `/campaigns*`, a página não é montada e o **wall de upgrade** (`PlanUpgradeWall`) cobre o conteúdo com blur (as barras laterais continuam clicáveis). Textos do wall: título **Campanhas não está no seu plano**; texto **Disponível a partir do plano Scale. Faça upgrade para liberar este recurso.**; botão **Fazer upgrade de plano** (vai para `/settings/billing/credits?planos=1` e registra a intenção em `POST /subscription/upgrade-intent`); rodapé **Plano atual: {código do plano}**. Não há botão de fechar no bloqueio por rota.
- `hasFeature()` é "fail-open": se os entitlements ainda não carregaram, libera; `SYSTEM_ADMIN` sempre passa. O backend é a autoridade.
- Na Home e no Inbox, sem a feature o front nem chama os endpoints de campanha (evita 403 + toast "fora do plano"); a seção de filtro por tags do Inbox e as tags na ficha do contato somem.

### Gate "plataforma" (PlatformGate) — só na lista e nas integrações
- `pages/campaigns/dashboard.vue` e `pages/settings/campaign-integrations.vue` envolvem o conteúdo em `<PlatformGate :blocked="!isPlatformOwner">`. `isPlatformOwner` vem de `GET /company/integration-status` → `san.available` (composable `usePlatformOwner`). Se falso, o conteúdo fica desfocado, sem interação, com um selo de cadeado e o texto **Campanhas não disponível no seu plano atual** (lista) ou **Integrações de campanha não disponível no seu plano atual** (integrações). Panorama, criação, edição e detalhe NÃO têm esse gate.

### Créditos e assinatura (faixas globais no topo)
- `SharedCreditGateBanner` (`GET /subscription/credit-gate`): faixa vermelha **Sem créditos disponíveis, incluindo a margem extra - contrate agora para evitar a parada** (status `BLOCKED`, IA parada) ou amarela **Créditos do mês esgotados - contrate mais para evitar interrupções** (status `BURST`). Clicar leva a `/settings/billing/credits`. Conta FREE e dark-launch nunca disparam (backend devolve OK).
- `SharedSubscriptionBanner`: **Sua assinatura não está ativa. Acesso em modo somente leitura.** — nesse modo os botões e campos de formulário ficam desabilitados globalmente (CSS `body.subscription-readonly`).
- O código do front não define o custo em créditos por mensagem de campanha. O que existe: (a) no rodapé do assistente, uma estimativa local `créditos estim.` = contatos × unidades × 3 (arredondado); (b) na aba **Cenários**, a estimativa vinda do backend (`GET /campaigns/:id/scenarios/cost`). Em `/settings/billing/credits` a categoria `CAMPAIGN` aparece como consumo "da equipe" (terracota), separado do consumo de IA. Ver Incertezas.

### Canal exigido
- O assistente só lista canais da unidade atual com `type` `WABA` ou `ROOKIE` e `status === 'open'`. Sem canal: aviso **Esta unidade não tem canal WhatsApp conectado** e botão **Conectar canal** (vai para `/settings/channels/whatsapp-rookie`).
- Canal **WhatsApp oficial (WABA)**: exige **Template de abertura** aprovado (obrigatório) e template aprovado para cada follow-up com 24h ou mais. Canal **número não-oficial** (ROOKIE): sem exigência de template.

### Tipos de campanha (origem/gatilho) — nomes que a interface usa
| `triggerType` | Assistente novo (passo 2) | Lista (`/campaigns/dashboard`) | Detalhe (badge) | `TRIGGER_TYPE_LABELS` (tipos) |
|---|---|---|---|---|
| `SCHEDULED` | **Tenho uma lista** (CSV) | **Lista** | **Agendada** | **Agendada** |
| `WEBHOOK` | **Meu sistema envia** | **Webhook** | **Webhook** | **Webhook** |
| `INBOUND_MESSAGE` | **O cliente chega até mim** (palavra-chave) | **Palavra-chave** | **Inbound** | **Mensagem Inbound** |

### Status da campanha — dois conjuntos de rótulos coexistem
| `status` | Lista/filtro (`CAMPAIGN_STATUS_LABELS`) e Home | Detalhe (`getCampaignStatusLabel`) | Significado no código |
|---|---|---|---|
| `DRAFT` | **Rascunho** | **Não Iniciada** | Criada, ainda não iniciada (lista: botão **Iniciar campanha**) |
| `ACTIVE` | **Ativa** | **Ativa** | Em execução (botão **Pausar**) |
| `PAUSED` | **Pausada** | **Pausada** | Pausada (botão **Retomar**) |
| `COMPLETED` | **Concluída** | **Finalizada** | Terminou |
| `ARCHIVED` | **Arquivada** | **Arquivada** | Sem ação na interface (ver Incertezas) |

Campanhas de webhook e de palavra-chave nascem ativas segundo os toasts do assistente ("Campanha ativa — escutando as palavras-chave."); campanhas de lista nascem como rascunho ("Campanha criada! Inicie o disparo quando quiser.").

### Ações que EXISTEM no serviço mas NÃO têm botão em nenhuma tela alcançável
`deleteCampaign` (excluir), `stopCampaign` (parar permanentemente), `removeContactFromAudience` (remover contato da audiência), `cancelWebhookQueueEvent` (cancelar evento da fila). Também não há "duplicar" nem "arquivar" na interface. Os toasts desses serviços existem ("Campanha excluída com sucesso!", "Campanha parada com sucesso!", "Contato removido da audiência com sucesso!", "Evento cancelado com sucesso!"), mas nenhuma tela os chama.

### Glossário curto da área
- **Tino**: nome do agente de IA que conduz as conversas (aparece como "TINO" nas transcrições de teste).
- **Missão livre**: campanha sem processo vinculado, só com um objetivo em texto.
- **Processo preferencial** / **playbook**: processo mapeado em Cérebro › Processos que Tino segue etapa por etapa (`leadProcessId` / `initialProcessId`).
- **Definição de sucesso**: o que conta como conversão (`goalType`): **Processo concluído**, **Transferência qualificada**, **Dados coletados**, **Marcação manual**.
- **Contínuas** × **Projetos**: na lista, campanhas sem fim (webhook, palavra-chave e listas sem data de fim) × listas com data de fim.
- **Follow-up** / **tentativa**: mensagem que Tino manda sozinho quando o contato não responde, contando a partir da 1ª mensagem.
- **Template**: mensagem pré-aprovada pela Meta, exigida em canal WABA para abrir conversa e para mensagens após 24h.
- **Janela de horários** / **janela de execução**: dias e horário em que a campanha pode disparar.
- **Fila de Eventos**: eventos de webhook recebidos fora da janela, aguardando o próximo horário.
- **Execuções**: um registro por contato que entrou na campanha (`campaignExecutions`).
- **Cenários**: testes automatizados em que a IA simula um cliente difícil e avalia critérios.
- **Disparo simulado** / **dry-run**: teste que não envia nem grava nada.
- **Tag**: etiqueta aplicada ao contato por campanhas de palavra-chave (`CAMPAIGN:<id>`) ou manualmente; critério de audiência.

---

## Panorama (`/campaigns/overview`)
Arquivo: `pages/campaigns/overview.vue`. Dados: `GET /campaigns/panorama?days=7|30` (`getCampaignsPanorama`).

- **Como chegar:** menu principal **Campanhas** (cai aqui por redirecionamento de `/campaigns`) ou submenu **Campanhas > Panorama**.
- **Para que serve:** retrato pronto das campanhas no período: um veredito em uma frase, a faixa de sinais (KPIs) e a fila do que precisa de você, com sugestão do agente e atalho para agir.
- **Quem vê:** gestor+ em qualquer nível (item de menu). O backend compõe o panorama "sobre as unidades acessíveis". Sem guarda de rota específica no front.
- **Plano, créditos e bloqueios:** feature `campaigns` (wall de upgrade). Sem PlatformGate. Faixas de crédito/assinatura como em toda a área.
- **O que há na tela:**
  - Kicker **campanhas · panorama** e título **Panorama**; botão de recolher o submenu.
  - Seletor de janela (canto direito): botões **7 dias** e **30 dias** (padrão 7). Trocar recarrega.
  - Estado carregando: **Montando o retrato das suas campanhas.**
  - Estado de erro: **Não foi possível montar o Panorama** / **Houve uma falha ao carregar o retrato deste período. Tente novamente.** / botão **Tentar de novo**.
  - Veredito: quadrado com gradiente + frase (`verdict.text`); abaixo, opcionalmente **▲** ponto forte (`verdict.strength`) e **▼** ponto de atenção (`verdict.concern`), ambos vindos do backend.
  - Faixa de sinais (KPIs, vindos do backend, `kpis[]`): rótulo (`label`), valor (`count` com separador pt-BR ou `percent` arredondado, ou **—** quando nulo), tendência: **▲ melhorou** / **▼ em queda** / **→ estável** / **· sem leitura** (quando não há valor), linha **{valor anterior} · {7|30} dias anteriores** e subtexto (`sub`).
  - Seção **o que precisa de você** (hint **{n} prioridade · por severidade** ou **{n} prioridades · por severidade**): cartões numerados **01**, **02**… com ponto de severidade (alta = vermelho, média = âmbar, baixa = cinza), título, selo da origem (um de **entrega**, **templates**, **abandono**, **fluxo**, **rascunho**), texto de contexto, chips opcionais, bloco **→ o agente sugere** com a recomendação e botão com `actionLabel` que navega para `actionRoute` (ambos definidos pelo backend).
  - Estado vazio da fila: **Tudo em ordem por aqui** / **Nenhuma campanha precisa de intervenção agora. Quando algo travar — entrega, template, fila ou abandono — a prioridade aparece nesta fila com contexto e sugestão.**
  - Rodapé **continuar de onde o panorama aponta** com atalhos **Campanhas →** (`/campaigns/dashboard`) e **Nova campanha →** (`/campaigns/create`).
- **Fluxos:** abrir → escolher 7 ou 30 dias → ler veredito/KPIs → clicar no botão de ação de uma prioridade (vai para a rota que o backend indicou, ex.: detalhe de uma campanha) → ou usar os atalhos do rodapé.
- **Regras e limites:** janela só 7 ou 30 dias; tudo é calculado no servidor; a tela não filtra por unidade (o escopo é o do usuário).
- **Nomes e termos:** "veredito", "sinais", "prioridades", "severidade", "o agente sugere".
- **Perguntas prováveis:** "Por que o Panorama está vazio?" → não há alertas (estado **Tudo em ordem por aqui**) ou a chamada falhou (estado de erro com **Tentar de novo**). "Posso ver por unidade?" → não; só por janela de tempo. "De onde vêm os números?" → do backend (`/campaigns/panorama`); o front não recalcula.
- **Incertezas:** quais KPIs existem (rótulos, fórmulas) e quais alertas/recomendações são gerados — tudo vem do backend e não está no front; `activeCampaigns` é recebido mas não é exibido.

---

## Campanhas — lista unificada (`/campaigns/dashboard`)
Arquivo: `pages/campaigns/dashboard.vue`. Dados: `GET /campaigns/all` (`getAccessibleCampaigns`, lista cross-unidade) + `POST /campaign-metrics/bulk/metrics` (`getBulkMetrics`, taxa de resposta e conversas por campanha; se falhar, a lista funciona sem os números).

- **Como chegar:** submenu **Campanhas > Campanhas**; atalho **Campanhas →** do Panorama; botão **Voltar** do detalhe; redirecionamento de links antigos `/campaigns/entity/:entityId` (chega com `?entityId=` pré-filtrando a unidade).
- **Para que serve:** ver todas as campanhas de todas as unidades que você acessa numa lista só, filtrar, iniciar/pausar/retomar e abrir o detalhe.
- **Quem vê:** gestor+ em qualquer nível; rota em `managerPages` (outros papéis → `/home`). O backend recorta ao escopo.
- **Plano, créditos e bloqueios:** feature `campaigns` (wall). **PlatformGate**: se `san.available` for falso, tudo fica desfocado com o selo **Campanhas não disponível no seu plano atual**.
- **O que há na tela:**
  - Título **Campanhas**, subtítulo **Todas as unidades que você acessa, numa lista só.**, botão **Nova campanha** (`/campaigns/create`).
  - Filtros: busca com placeholder **Buscar campanha…** (filtra pelo título, sem distinguir maiúsculas); select de unidade (só aparece quando há campanhas de mais de uma unidade): **Todas as unidades** + nome de cada unidade; select de status: **Todos os status**, **Rascunho**, **Ativa**, **Pausada**, **Concluída**, **Arquivada**; select de origem: **Todas as origens**, **Lista**, **Webhook**, **Palavra-chave**. Filtros são locais (na memória) e não vão para a URL, exceto `entityId` inicial.
  - Carregando: 4 blocos cinza pulsando.
  - Vazio (nenhuma campanha): **Nenhuma campanha ainda** / **Coloque um processo em movimento: Tino aborda seus contatos e você acompanha o funil de cada conversa.** / botão **Criar a primeira campanha**.
  - Sem resultado para os filtros: **Nenhuma campanha corresponde aos filtros.**
  - Seção **Contínuas** (legenda **sempre ativas · {n}**): campanhas de webhook, de palavra-chave e listas sem data de fim. Cada linha: ícone da origem, título, chip do processo preferencial (`initialProcess.name`) ou **missão livre**, sinal da suíte de cenários (**{n} cenário(s) falhando** em vermelho, tooltip "{n} de {total} cenários não passaram"; **{n} cenário(s) sem rodar** em âmbar, tooltip "{n} de {total} cenários sem execução válida"; **cenários ok** em verde, tooltip "Os {total} cenários passaram na última execução"; nada quando a campanha não tem cenários), linha **{Lista|Webhook|Palavra-chave} · {unidade}**, números **conversas** (`conversationsStarted`) e **resposta** (`responseRate` arredondada, %; **—** enquanto não carrega), selo de status, botão de ação e seta para abrir.
  - Seção **Projetos** (legenda **lista com fim · {n}**): listas com data de fim. Cada linha: **{n} contatos · {unidade}**, barra de progresso com **{x}%** = execuções ÷ contatos da audiência (`_count.campaignExecutions / _count.audienceContacts`, máx. 100), selo de status, botão de ação.
  - Botões de ação por status (só ícone, tooltip): `DRAFT` → **Iniciar campanha** (ícone play; mostra ícone girando enquanto age); `ACTIVE` → **Pausar**; `PAUSED` → **Retomar**. `COMPLETED`/`ARCHIVED` não têm ação. Uma ação por vez (`actingId`).
  - Clicar na linha abre `/campaigns/{id}?fromDashboard=1`.
- **Fluxos:**
  - Iniciar: **Iniciar campanha** → `POST /campaigns/:id/start` → toast **Campanha iniciada com sucesso!** (erro: mensagem do backend ou **Erro ao iniciar a campanha.**); status vira **Ativa** na hora.
  - Pausar: `POST /campaigns/:id/pause` → **Campanha pausada com sucesso!** (erro: **Erro ao pausar a campanha.**); status vira **Pausada**.
  - Retomar: `POST /campaigns/:id/resume` → **Campanha retomada com sucesso!** (erro: **Erro ao retomar a campanha.**); status vira **Ativa**.
  - Erro ao carregar a lista: toast com a mensagem do backend ou **Erro ao carregar campanhas.**; erro nas métricas em lote é silencioso.
- **Regras e limites:** a lista inclui campanhas de todas as unidades acessíveis (não depende da unidade selecionada na sessão); "Contínua" = `triggerType !== 'SCHEDULED'` ou lista sem `schedule.endDate`; a métrica "resposta" é a `responseRate` do backend arredondada; o botão **Iniciar campanha** aparece para qualquer rascunho (inclusive webhook/palavra-chave), diferente do detalhe (ver abaixo).
- **Nomes e termos:** **Contínuas**, **Projetos**, **missão livre**, **conversas**, **resposta**, **Lista/Webhook/Palavra-chave**.
- **Perguntas prováveis:** "Não vejo a campanha da outra unidade" → o backend recorta ao seu papel (Gestor de Unidade só vê a dele); use o filtro **Todas as unidades**. "A lista está borrada com um cadeado" → PlatformGate (`san.available` falso). "Onde excluo uma campanha?" → não há exclusão na interface. "Por que o progresso está em 0%?" → nenhuma execução ainda ou a campanha não foi iniciada.
- **Incertezas:** o critério do backend para `san.available`; se `startCampaign` para webhook/palavra-chave tem efeito; como o backend calcula `responseRate` e `conversationsStarted`.

---

## Redirecionamentos (`/campaigns` e `/campaigns/entity/:entityId`)
- `pages/campaigns/index.vue`: substitui a rota por `/campaigns/overview`; mostra um spinner e **Redirecionando para campanhas...**.
- `pages/campaigns/entity/[entityId].vue`: rota aposentada; ao montar, substitui por `/campaigns/dashboard?entityId={entityId}` (preserva a unidade como filtro para links antigos). Mostra **Redirecionando para Campanhas…**.

---

## Nova campanha — assistente em 3 passos (`/campaigns/create`)
Arquivos: `pages/campaigns/create.vue` (escolhe o assistente), `components/campaigns/create/Wizard.vue` (casca), `composables/useCampaignCreateWizard.ts` (estado, validação, rascunho, envio), `create/StepMission.vue`, `create/ProcessPicker.vue`, `create/SuccessGoalPicker.vue`, `create/StepAudience.vue`, `create/StepLaunch.vue`, `create/PhonePreview.vue`, `create/WebhookCreatedModal.vue`, `create/SectionHeader.vue`, `templates/TemplateAssignment.vue`, `templates/TemplateEditorModal.vue`, `templates/TemplatePreview.vue`.

- **Como chegar:** lista **Campanhas > Nova campanha**; vazio da lista **Criar a primeira campanha**; Panorama **Nova campanha →**. A unidade de contexto é `?entityId=` da URL ou a unidade atual da sessão (`authStore.currentEntityId`). `?legacy=1` abre o assistente antigo (ver seção própria).
- **Para que serve:** criar uma campanha em que Tino aborda contatos (por lista CSV, por webhook do seu sistema ou por palavra-chave recebida), definindo missão, público, canal, horários e follow-ups.
- **Quem vê:** quem chega pelo menu (gestor+). Sem guarda de rota própria; o backend valida.
- **Plano, créditos e bloqueios:** feature `campaigns` (wall). Canal WhatsApp da unidade obrigatório (WABA ou ROOKIE, `status: open`). WABA exige template aprovado. Sem PlatformGate.

### Casca do assistente (todas as etapas)
- Barra superior: botão de recolher o submenu; link **Campanhas** (volta a `/campaigns/dashboard`); **/**; campo do nome com placeholder **Nome da campanha…** (máx. 120 caracteres; fica vermelho quando `showErrors` e o nome está vazio); à direita **salvo automaticamente** (com ícone) na criação ou selo **editando** na edição; botão **Sair**.
- Cabeçalho com o título da etapa: **O que essa campanha vai fazer?** (1), **Quem Tino vai abordar?** (2), **Quando e por onde?** (3); stepper **1 Missão**, **2 Público**, **3 Lançamento** (clicável: voltar sempre; avançar valida as etapas intermediárias e para na primeira inválida, com aviso **Revise os campos destacados antes de avançar.**).
- Trilho **ficha da campanha** (só em telas grandes, `xl`) com contador **{preenchidos}/{total}** e linhas clicáveis (**editar ↗**): **missão** (nome do processo, **Missão livre** ou **A definir no passo 1**), **sucesso** (**Processo concluído** / **Transferência qualificada · {setor}** / **Dados coletados** / **Marcação manual**), **público** (**Lista CSV · {n}**, **Lista (pendente)**, **Lista de contatos** na edição, **Webhook (seu sistema)**, **Palavra-chave · a, b** ou **Palavra-chave**), **unidades** (só quando há mais de uma unidade: **{n} selecionada(s)**), **canal** (**{nome} · WABA** quando oficial), **janela** (**Ao receber palavra-chave** / **Imediato · 24/7** / **Todos os dias · 09:00–18:00** ou **{n} dias · 09:00–18:00**), **follow-ups** (**+24h, +72h**, **+7 dias** para 168h, ou **Nenhum**). Linhas não preenchidas mostram **A definir no passo {n}**.
- Rodapé: na edição **Alterações valem para os próximos disparos e turnos da conversa.**; na criação, enquanto não há lista **As estimativas aparecem quando a lista de contatos for enviada.**; com lista, três números: **contatos** (`n` ou `n ×{unidades}`), **créditos estim.** (`~` contatos × unidades × 3), **duração prev.** (`~` ⌈n/300⌉ dia(s)); para webhook: **variável** / **por contato** / **contínua**; para palavra-chave: **sob demanda** / **por contato** / **contínua**. Indicador **passo {n} de 3**; botões **← Voltar** (a partir do passo 2), **Continuar →** (passos 1 e 2) e no passo 3 **Criar campanha** (**Criando…** enquanto envia) ou, na edição, **Salvar alterações** (**Salvando…**).
- **Continuar →** com etapa inválida: toast de erro **Revise os campos destacados antes de avançar.** e os erros aparecem sob os campos (prefixo **✕**).
- Modal **Sair da criação?**: **Seu progresso fica salvo automaticamente neste navegador — ao voltar, você continua de onde parou.**; botões **Continuar editando**, **Descartar rascunho** (vermelho; apaga o rascunho) e **Sair** (vai para `/campaigns/dashboard?entityId={unidade}`). Na edição o modal é **Sair sem salvar?** / **As alterações não salvas serão perdidas.** com **Continuar editando** e **Sair** (volta ao detalhe `/campaigns/{id}`).
- Sobreposição enquanto envia: **Criando campanha…** (mesmo texto na edição).
- **Rascunho automático:** na criação, o estado é salvo no `localStorage` (chave `campaign-create-draft-v1:{entityId}`) 1 s após cada mudança; ao reabrir, toast **Rascunho recuperado de onde você parou.**; ao criar com sucesso ou descartar, o rascunho é apagado. A edição não usa rascunho. (Há também um `saveDraft()` manual com toasts **Rascunho salvo neste navegador.** / **Não foi possível salvar o rascunho.**, mas nenhum botão o chama.)
- Dados carregados ao abrir: processos ativos, setores ativos, campos de qualificação, canais (filtrados para a unidade atual, WABA/ROOKIE e `open`; se houver exatamente um, é pré-selecionado), unidades do usuário e a disponibilidade da unidade (**Cérebro › Operações**), que pré-carrega os dias e o primeiro horário da janela.

### Etapa 1 · Missão (**O que essa campanha vai fazer?**)
- **① Modo de condução** — subtítulo **Como Tino conduz cada conversa desta campanha.** Dois cartões:
  - **Seguir um processo** (selo **recomendado**): **Tino segue o playbook etapa por etapa e você acompanha o funil de cada conversa. Se o cliente mudar de assunto, ele se adapta.** (padrão)
  - **Missão livre** (selo **simples**): **Sem processo — só um objetivo em texto. Para avisos e recados pontuais.** Ao escolher, aparece **Campanhas com processo têm acompanhamento por etapa e resultados mais consistentes.**; a definição de sucesso vira **Marcação manual** e o processo é limpo. Voltar para processo troca **Marcação manual** por **Processo concluído**.
- **② Escolher processo** (só no modo processo) — subtítulo **Tino segue este playbook etapa por etapa; você acompanha o funil de cada conversa.**
  - Busca **Buscar processo por nome ou setor…**; grade paginada de 6 por página (**‹** / **›**, **{página} / {total}**, **{n} processos**); sem resultado: **Nenhum processo encontrado para "{busca}".**
  - Cada cartão: nome, descrição (2 linhas), barra de 4 traços com **ia total** / **ia parcial** / **ia limitada** / **ia não avaliada** (`aiCapability` FULL/PARTIAL/NONE/UNKNOWN), **{n} etapas**, até 2 chips de setor. Clicar seleciona (clicar de novo desmarca). Se o nome da campanha estiver vazio, ele é preenchido com o nome do processo.
  - Painel do selecionado: **Como Tino vai conduzir · {processo}**, link **Ver processo completo** (abre `/identity/processes/{id}` em nova aba) e a lista numerada das etapas (`plainDescription` ou `description`).
  - Sem processos mapeados: **Você ainda não mapeou processos** / **Mapeie seu primeiro processo em Identidade › Processos para Tino seguir um playbook — ou crie esta campanha com missão livre.** / botões **Mapear processo ↗** (`/identity/processes`, nova aba) e **Criar com missão livre**.
  - Erros: **Não há processos mapeados — use a missão livre.** ou **Escolha o processo que a IA vai seguir.**
- **③ Contexto desta campanha** (modo processo) — subtítulo **O processo é o caminho; o contexto diz a situação em que ele é aplicado nesta campanha.** Caixa **um bom contexto responde**: **Quando** — em que momento este contato acontece — ex.: "1 dia antes do boleto vencer".; **O que Tino já tem** — ex.: "os dados da fatura e o link do boleto vêm com cada contato".; **Ação imediata** — ex.: "já envie o link na conversa — não mande o cliente procurar".; **Condições e prazos** — ex.: "PIX ativa na hora; boleto compensa em até 3 dias úteis". Textarea (3 linhas) com placeholder **Ex.: Enviada 1 dia antes do boleto vencer. Os dados da fatura e o link vêm com cada contato — já envie o link e ofereça PIX ou boleto. Tom de lembrete amigável.** e dica **Depois de escrever, gere o exemplo no passo 3 — abertura vaga é sinal de contexto vago.** Opcional no modo processo.
  - Na missão livre a seção vira **② Objetivo da campanha** — **Tino usa isto como a instrução principal da conversa.**; placeholder **Descreva o que Tino deve fazer nesta campanha.**; dica **Ex.: 'Avisar sobre a manutenção do sistema no domingo, das 2h às 5h'.**; obrigatório (erro **Descreva o objetivo da campanha para continuar.**).
- **④ O que conta como resultado?** (③ na missão livre) — **Define como a campanha mede conversões no painel de resultados.** Opções (rádio):
  - **Processo concluído** — **Tino completou o playbook (ex.: acordo fechado).**
  - **Transferência qualificada** — **Entregar a conversa a um humano com o que foi coletado (ex.: lead quente ao Comercial).** Ao marcar: select **Sem setor específico (fila geral)** + setores ativos; sem setores: **Nenhum setor cadastrado — crie em Operações › Setores.**
  - **Dados coletados** — **Coletar informações-chave do contato.** Ao marcar: chips dos campos de qualificação (**+ {campo}** / **✓ {campo}**); sem campos: **Nenhum campo cadastrado — crie em Operações › Campos do contato.** Erro: **Selecione ao menos um campo a coletar.**
  - **Marcação manual** — **Sua equipe marca as conversões manualmente.**
  - Na missão livre só **Marcação manual** fica habilitada (as outras aparecem esmaecidas).
  - **valor por conversão (opcional)** — **Como calcular o retorno da campanha no painel de resultados.** Seletor **Nenhum** / **Valor fixo** / **Coluna da lista**. **Valor fixo**: campo numérico com placeholder **R$ 0,00** (mín. 0, passo 0,01). **Coluna da lista**: select **Coluna…** com as colunas extras do CSV já enviado, ou campo de texto com placeholder **Ex.: valor_devido (coluna do CSV)** quando ainda não há CSV.
- Erro do nome (barra superior): **Dê um nome interno para a campanha.**

### Etapa 2 · Público (**Quem Tino vai abordar?**)
- **① De onde vêm os contatos** — **A origem dos contatos define como a campanha dispara.** Três cartões:
  - **Tenho uma lista** — **Suba um CSV com os contatos que Tino vai abordar.** (padrão)
  - **Meu sistema envia** — **CRM, e-commerce, cobrança — via URL de webhook.**
  - **O cliente chega até mim** — **Ativa quando alguém escreve uma palavra-chave.**
  - Na edição a origem não muda: cartões esmaecidos e aviso **A origem dos contatos não muda depois da campanha criada.**
- **Lista (CSV):**
  - Área de envio: **Arraste seu CSV aqui ou clique para enviar** / **Colunas obrigatórias: nome e telefone. Colunas extras viram dados do contato.** / link **Baixar modelo de planilha ↓** (baixa `modelo-contatos.csv` com o conteúdo `nome,telefone,email,valor_devido` / `Maria Souza,5511998877665,maria@email.com,289.90`). Aceita `.csv,text/csv`; arrastar e soltar funciona.
  - Formato lido pelo front (`processCsvFile`): separador **vírgula**, primeira linha = cabeçalho, aspas removidas, sem suporte a vírgula dentro de campo. Cabeçalhos reconhecidos (sem distinguir maiúsculas): `nome`/`name` → nome; `telefone`/`phone`/`celular`/`whatsapp` → telefone; `email`/`e-mail` → e-mail; qualquer outra coluna → dado do contato (`contextData[coluna]`, com o nome original da coluna). Linhas sem nome OU sem telefone são ignoradas.
  - Depois do envio: cartão com **{arquivo}**, **{n} linhas**, botão **trocar arquivo**, contadores **contatos válidos** e **linhas ignoradas (sem nome/telefone)** e a faixa **colunas detectadas:** (`nome`, `telefone`, `email` se houver, e as extras).
  - Toasts: **Nenhum contato válido — o CSV precisa das colunas nome e telefone.** (0 contatos); **Erro ao processar arquivo CSV. Verifique o formato do arquivo.**; **Erro ao ler o arquivo CSV.**; genérico **Erro ao processar o arquivo CSV.**
  - Erro da etapa: **Envie um arquivo CSV para continuar.** (não se aplica na edição).
  - Na edição: **A lista de contatos desta campanha é acompanhada no detalhe da campanha (execuções por contato).** (não é possível trocar a lista).
- **Webhook:** caixa **Seu sistema envia os contatos automaticamente** / **Ideal para CRM, e-commerce (carrinho abandonado) ou sistema de cobrança. Após criar a campanha, você recebe uma URL de webhook para configurar no seu sistema — cada contato enviado entra automaticamente na campanha, com os dados que vierem no payload.**
- **Palavra-chave:** campo **palavras-chave que ativam a campanha** (chips; digitar e **Enter** ou sair do campo adiciona; placeholder **digite e tecle Enter…**; **X** remove); **tipo de correspondência**: **Contém** (padrão), **Igual a**, **Começa com**, **Termina com**, **Regex**; **tag aplicada no contato**: seletor de cor (padrão `#3B82F6`) + texto com placeholder **Ex.: BF25** (máx. 100); checkboxes **Diferenciar maiúsculas** (padrão desmarcado) e **Aplicar somente na primeira mensagem** (padrão marcado). Erros: **Adicione ao menos uma palavra-chave.** / **Informe a tag aplicada no contato.**
- **② Perfil do público** (selo **opcional**) — **Refina o tom que Tino usa com esse público.** Chips (um só, clicar de novo desmarca): **Cliente Ativo**, **Ex-cliente**, **Lead**, **Prospect**, **Mix de Perfis**. Campo **contexto sobre esse público (opcional)** com placeholder **Ex.: clientes que atrasaram a fatura de novembro pela primeira vez.**
- **③ Replicar para outras unidades** (selo **opcional**; só na criação, só para lista e só quando o usuário tem mais de uma unidade) — **A campanha é replicada por unidade — mesma lista, canal resolvido automaticamente em cada uma.** Chips com o nome de cada unidade (a atual vem marcada, com selo **atual**, e não pode ser desmarcada).

### Etapa 3 · Lançamento (**Quando e por onde?**)
- **① Canal** — **Por onde as mensagens saem.**
  - Sem canal: **Esta unidade não tem canal WhatsApp conectado** / **Conecte um número para lançar a campanha por aqui.** / botão **Conectar canal** (`/settings/channels/whatsapp-rookie`).
  - Select **Escolha o canal…** com opções **{nome} — WhatsApp oficial (WABA)** ou **{nome} — número não-oficial**. Erro: **Conecte um canal WhatsApp para lançar a campanha.**
  - Canal WABA: bloco **Template de abertura** (selo **obrigatório**) — **A Meta exige um template pré-aprovado para a primeira mensagem de um canal oficial.** com o seletor de template (ver "Seletor de template" abaixo), só templates **Aprovado**. Erro: **Selecione um template de abertura aprovado — o canal oficial exige.**
- **② Quando disparar**
  - Lista: **data de início** (padrão hoje; mínimo hoje) e **data de fim (opcional)** (mínimo = data de início); nota **Sem data de fim, a campanha fica ativa e você pode adicionar novos lotes de contatos depois.** Erro: **Informe a data de início.**
  - Webhook: **Disparar imediatamente ao receber** — **24/7 — cada contato é abordado assim que entra.** (padrão) ou **Somente dentro da janela de horários** — **Fora da janela, o contato aguarda o próximo horário.**
  - Palavra-chave: **Nada a configurar — Tino responde no instante em que o cliente escreve a palavra-chave.**
  - **janela de horários** (**· pré-carregada do funcionamento da unidade**) — aparece para lista e para webhook com janela: chips **Seg Ter Qua Qui Sex Sáb Dom** (padrão seg–sex, ou os dias da disponibilidade da unidade) e horários **das** {09:00} **às** {18:00}. Erros: **Escolha ao menos um dia da semana.** / **O horário inicial precisa ser antes do final.**
- **③ Se o contato não responder** (selo **opcional**) — **Tino retoma sozinho, contando a partir da 1ª mensagem sem resposta. Máx. 4 tentativas.**
  - Linha âncora **Mensagem de abertura** / **enviada quando a campanha começa**.
  - Tentativas (padrão: +24h e +72h): **1ª tentativa**, **2ª tentativa**… com **{4 horas | 1 dia | 2 dias | 3 dias | 7 dias} após a abertura**; em WABA e ≥24h, marcação **· requer template** e ícone de aviso com tooltip **Após 24h em canal oficial exige template aprovado.**; botão **Remover tentativa** (X).
  - **adicionar tentativa:** chips **+ 4 horas após a abertura**, **+ 1 dia após a abertura**, **+ 2 dias após a abertura**, **+ 3 dias após a abertura**, **+ 7 dias após a abertura** (opções 4h, 24h, 48h, 72h, 168h; cada uma só uma vez). Ao chegar a 4: **máximo de 4 tentativas atingido**.
  - Nota quando há tentativas: **Assim que o contato responder, as tentativas seguintes são canceladas — Tino assume a conversa.**
  - WABA com tentativas ≥24h: caixa âmbar **Tentativas após 24h em canal oficial (WABA) exigem template aprovado — configure um para cada uma abaixo.** com **template · {n} dias após a abertura** e um seletor de template por tentativa. (Observação do código: o assistente não exibe erro se faltar template de follow-up; só o de abertura é validado. Ver Incertezas.)
- **Configurações avançadas** (expansível) — legenda **diretrizes extras — o processo já define transferências e encerramento** (modo processo) ou **diretrizes extras para o Tino nesta campanha** (missão livre): campo **diretrizes adicionais** com placeholder **Instruções extras para o Tino nesta campanha…** (salvo como uma única diretriz **Diretrizes da campanha**). Na edição de campanha que já conversou: **Esta campanha já conduziu conversas. A alteração passa a valer na próxima mensagem, inclusive nas conversas em andamento. O texto anterior fica registrado no histórico.** Bloco **ferramentas do Tino** com chips fixos **transferir para humano** e **encerrar conversa** e a nota **governadas pelo fluxo do processo preferencial.** ou **disponíveis para o Tino conforme a missão.**
- **Prévia da abordagem** — **Dê um nome ao agente e veja como Tino abriria a conversa.** Campo **nome do agente** com placeholder **Nome do agente — ex.: Sofia** (máx. 30) e nota **É assim que Tino se apresenta ao cliente na primeira mensagem.** Moldura de celular (cabeçalho com a inicial e o nome do agente ou **Agente**, **online**, **whatsapp**): botão **Gerar exemplo** (**Veja como {agente} abriria esta conversa.**), estado **{agente} está digitando…**, mensagem gerada com **enviado pelo Tino**, botão **Gerar novo exemplo** e a nota **Exemplo ilustrativo — cada contato recebe uma mensagem personalizada com os dados dele.** A prévia chama `POST /campaigns/test` com o primeiro contato do CSV (ou nome **Maria**); se a IA não responder, mostra **Oi! Aqui é {agente | a assistente} — posso te ajudar com um assunto rápido?**. Erro: toast **Erro no teste: {mensagem}**.

### Seletor de template (usado em Template de abertura e nos follow-ups WABA)
Componente `templates/TemplateAssignment.vue`, com a lista de templates do canal (`GET /templates/{canal}/not-rejected`, filtrada a **Aprovado** no assistente).
- Sem template escolhido: botão **Criar novo template** (abre o editor) e, abaixo, **Ou escolha um existente** com a lista (**Carregando templates...** enquanto carrega). Cada item: nome, selo **Aprovado** / **Em revisão** / **Rejeitado** / **Novo**, selo **Em uso** (template já usado por campanha ativa), selo **Não suportado** para template criado fora da plataforma com variável posicional `{{1}}` (tooltip **Template criado fora da plataforma, com variáveis posicionais que a campanha não consegue preencher. Crie um template pelo editor.**; não pode ser selecionado) e a primeira linha do corpo.
- Com template: cabeçalho com nome, selo de status, **Marketing · pt_BR** ou **Utilidade · pt_BR**, selo **Não editável** (tooltip **Template não pode ser editado em campanhas ativas**; no assistente todo seletor com `only-approved` é não editável) ou **Em uso** (tooltip **Este template está em uso em outras campanhas. Modificações criarão uma cópia.**), botões **Editar template** (lápis, quando permitido) e **Remover template** (lixeira). Corpo em 2 linhas.
- Botão de URL com variável: campo **Link do botão "{texto}"** (obrigatório, **\***) com select **Selecione o campo do link…** + campos de variável; nota **Botões de URL usam variável posicional — a Meta não permite nomear. Escolha qual campo preenche a parte variável do link (ex.: "Hash do boleto").**
- Em follow-up: checkbox **Priorizar template sobre IA (enviar mesmo dentro de 24h)**.
- Variáveis `{{campo}}` do template são mapeadas automaticamente para os campos sugeridos pela API (`GET /templates/variable-fields`) ou, se não existirem na lista, para `contextData.{campo}` (coluna do CSV / campo do payload do webhook).

### Editor de template (modal **Criar Template** / **Editar Template**)
Componente `templates/TemplateEditorModal.vue`. Subtítulo **Template de início da conversa** ou **Template de follow-up**.
- Avisos ao editar template existente: **Template entrará em revisão** / **Após modificação, o template ficará com status PENDENTE até aprovação do Meta.**; se em uso por outras campanhas: **Novo template será criado** / **Este template está em uso por {n} campanha(s). Uma cópia será criada para esta campanha.**; se a categoria mudou: **Categoria alterada** / **Mudança de categoria exige exclusão do template atual e criação de um novo no Meta.**
- Campos: **Nome do Template \*** (placeholder **ex: Oferta de Boas-vindas**; ajuda **Nome de exibição do template**; máx. 512), **Categoria** (**Marketing** padrão / **Utilidade**), **Campos Disponíveis** — **Clique para inserir no campo ativo** (chips agrupados em **Contato**, **Campanha**, **IA**, **Dados de Contexto**, vindos da API; inserem `{{variavel}}` no campo em foco), **Corpo da Mensagem \*** (placeholder **Digite sua mensagem e clique nos campos acima para inserir variáveis...**, contador **{n}/1024**), **Cabeçalho (opcional)** (placeholder **Texto do cabeçalho (max 60 chars)**, contador **{n}/60**), **Rodapé (opcional)** (placeholder **Texto do rodapé (max 60 chars)**), **Botões (opcional)** (tipo **Resposta Rápida** / **Link** / **Telefone**; **Texto do botão** máx. 25; **https://...**; **+5511999999999**; **+ Adicionar botão**; máx. 3 → **Máximo de 3 botões atingido.**; **Remover botão**). Em follow-up: **Priorizar template sobre IA** — **Se ativo, o template será enviado mesmo dentro da janela de 24h (não consulta a IA).**
- Prévia à direita (`TemplatePreview`): **Prévia da mensagem** em bolha estilo WhatsApp, com **Escreva o corpo da mensagem...** quando vazio e rodapé **Prévia com dados da campanha** ou **Dados de exemplo para visualização**.
- Validações (bloqueiam **Criar Template** / **Salvar Alterações**): **O nome do template é obrigatório.**; **O nome excede o limite de 512 caracteres.**; **O corpo do template é obrigatório.**; **O corpo excede o limite de 1024 caracteres ({n}).**; **Variável posicional {{1}} não é suportada no editor — use uma variável nomeada (ex.: {{valor}}).**; **Variável {{X}} inválida — use letras minúsculas, números e _, sem espaços (ex.: {{valor_carrinho}}).**; **O corpo não pode começar com uma variável — adicione um texto antes dela.**; **O corpo não pode terminar com uma variável — adicione um texto (ou pontuação) depois dela.**; **O cabeçalho excede o limite de 60 caracteres ({n}).**; **O cabeçalho não pode ter quebra de linha.**; **O cabeçalho não pode ter emojis.**; **O cabeçalho não pode ter caracteres de formatação (\*, _, ~ ou `).**; **O cabeçalho pode conter no máximo uma variável.**; **O rodapé excede o limite de 60 caracteres ({n}).**; **O rodapé não pode ter quebra de linha.**; **O rodapé não aceita variáveis.**; **O número de telefone é obrigatório.**; **Formato inválido. Use: +5511999999999 (10 a 15 dígitos após o +).**; **A URL é obrigatória.**; **A URL deve começar com https:// ou http://**; **A URL pode conter no máximo uma variável {{campo}}.**; **A variável deve ficar no fim do link (ex.: https://exemplo.com/boleto?hash={{hash_boleto}}).**; **O link precisa de uma parte fixa antes da variável — a Meta não aceita o link inteiro variável.**; **Formato de URL inválido.**
- Botões: **Cancelar**, **Criar Template** / **Salvar Alterações**. O template é definido "inline" no payload da campanha; o backend submete à Meta e atualiza o status. Idioma fixo `pt_BR`.

### Fluxo de criação (o que acontece ao clicar **Criar campanha**)
- Validação final das 3 etapas (mostra erros se algo faltar).
- Categoria enviada é sempre `GENERAL`; objetivo enviado = texto da missão livre, ou **Conduzir ativamente o processo "{processo}" com este contato.** + **Contexto desta campanha: {contexto}** no modo processo; `agentName` = nome do agente (ou **Agente** em webhook/palavra-chave).
- **Lista** → `POST /campaigns` (multi-unidade: um `entityConfig` por unidade selecionada, mesma lista; canal fixo só na unidade atual, as outras resolvem automático; agenda `WEEKLY` com os dias marcados, `interval 1`, `endCondition` `DATE` ou `NEVER`, 1 faixa de horário, `version 2.0`). Toasts: **Campanha criada com sucesso!** (ou **Campanhas criadas com sucesso!**) e **Campanha criada! Inicie o disparo quando quiser.** Vai para `/campaigns/dashboard?entityId={unidade}`. A campanha nasce como rascunho; iniciar é na lista (**Iniciar campanha**) ou no detalhe (**Iniciar**).
- **Webhook** → `POST /campaigns/webhook` (`executionMode` `IMMEDIATE` ou `EXECUTION_WINDOW_ONLY` + `executionWindow` com dias e faixa). Toast **Campanha webhook criada com sucesso!** e abre o modal **Conecte seu sistema** (abaixo). Ao fechar, vai para a lista.
- **Palavra-chave** → `POST /campaigns/inbound` (`inboundConfig`: operador, padrões, maiúsculas, tag, cor, só na primeira). Toasts **Campanha inbound criada com sucesso!** e **Campanha ativa — escutando as palavras-chave.** Vai para a lista.
- Erros de criação: toast com a mensagem do backend ou **Erro ao criar campanhas** / **Erro ao criar campanha webhook** / **Erro ao criar campanha inbound**.

### Modal **Conecte seu sistema** (campanha webhook criada)
Componente `create/WebhookCreatedModal.vue`. Kicker **campanha criada · webhook**; título **Conecte seu sistema**; texto **Envie um POST para esta URL a cada novo contato. Ele entra automaticamente na campanha.**
- **url do webhook**: URL devolvida pelo backend + botão **copiar** (vira **copiado** por 1,6 s).
- **token secreto**: oculto (`•••••`) com botões **revelar** / **ocultar** e **copiar**.
- **exemplo de payload**:
```
{
  "contactData": {
    "name": "Maria Souza",
    "phone": "5511998877665"
  },
  "contextData": {
    "valor_carrinho": 289.90,
    "itens_carrinho": "Tênis Aurora, Meia kit"
  }
}
```
  Nota: **contactData.phone é obrigatório; campos extras viram dados do contato, usáveis pelo Tino e no valor por conversão.**
- Botão **Ir para a campanha →** (na prática leva a `/campaigns/dashboard?entityId={unidade}`, não ao detalhe). O URL e o token ficam disponíveis depois na aba **Detalhes** da campanha.

### Regras e limites do assistente
- Nome: obrigatório, máx. 120. Nome do agente: máx. 30 (opcional na lista; webhook/palavra-chave usam **Agente** se vazio). Tag: máx. 100.
- Follow-ups: máx. 4; opções fixas 4h/24h/48h/72h/168h; ordenados por horas; `sequenceNumber` 1..n.
- Janela: pelo menos um dia; início < fim; padrão seg–sex 09:00–18:00 ou a disponibilidade da unidade.
- Lista: só CSV por vírgula; contatos válidos precisam de nome e telefone; não há validação de formato de telefone no front.
- Modo processo exige processo; **Dados coletados** exige ao menos um campo; **Transferência qualificada** sem setor = fila geral.
- Canal obrigatório; WABA exige template de abertura aprovado; canais listados só da unidade atual.
- Replicação para outras unidades só na criação e só para listas.
- Estimativas do rodapé são locais e aproximadas (3 créditos por contato; 300 contatos por dia).

### Perguntas prováveis (criação)
- "Meu CSV com ponto e vírgula não carrega" → o leitor usa vírgula como separador; use o modelo **Baixar modelo de planilha ↓**.
- "Coluna com valor para a conversão?" → qualquer coluna extra vira dado do contato e pode ser escolhida em **valor por conversão › Coluna da lista**.
- "Não aparece nenhum canal" → só canais WhatsApp (WABA/ROOKIE) conectados (`open`) da unidade atual; conecte em **Conectar canal**.
- "Preciso de template?" → só em canal oficial (WABA): abertura sempre; follow-ups a partir de 24h.
- "Perdi o que estava preenchendo" → na criação o rascunho fica no navegador por unidade (**Rascunho recuperado de onde você parou.**); **Descartar rascunho** apaga.
- "Posso editar a lista depois?" → não pelo assistente; a edição avisa que a lista é acompanhada no detalhe.

### Incertezas (criação)
- O assistente não valida a presença dos templates de follow-up WABA (só mostra o aviso); se o backend rejeita a criação sem eles, não está no front.
- Formato/validação do telefone e deduplicação de contatos: no backend.
- O que acontece ao "adicionar novos lotes de contatos depois" (texto da tela) — não há tela para isso no front.
- Se `startCampaign` é necessário para campanhas de lista com data de início futura (a tela diz **Inicie o disparo quando quiser**).

---

## Editar campanha (`/campaigns/edit/:id`)
Arquivo: `pages/campaigns/edit/[id].vue` + o mesmo assistente (`CampaignsCreateWizard` com `editCampaignId`).

- **Como chegar:** detalhe da campanha > botão **Editar**; links de "editar" da procedência de mensagens no Inbox (`editPath` vindo do backend). `?legacy=1` abre o editor antigo.
- **Para que serve:** ajustar missão, definição de sucesso, canal, janela, follow-ups, diretrizes, perfil do público e palavras-chave de uma campanha existente.
- **Quem vê:** gestor+ (menu). A unidade usada é a da campanha (não a da sessão), para listar os canais certos.
- **Plano, créditos e bloqueios:** feature `campaigns`. Enquanto carrega: **Carregando campanha…**. Falha: toast **Não foi possível carregar a campanha para edição.**
- **O que há na tela:** o mesmo assistente com selo **editando**, título fixo da campanha carregado no campo do nome, e diferenças:
  - Origem dos contatos bloqueada (**A origem dos contatos não muda depois da campanha criada.**); lista de contatos não editável; sem seção **Replicar para outras unidades**.
  - Rodapé: **Alterações valem para os próximos disparos e turnos da conversa.**; botão **Salvar alterações** / **Salvando…**.
  - Diretrizes: só as ativas são carregadas (concatenadas); a primeira ativa mantém o `id` para a API atualizar em vez de criar; se a campanha já teve execuções, aparece o aviso **Esta campanha já conduziu conversas…** (texto completo acima).
  - Modo/processo carregados de `initialProcessId`; definição de sucesso, valor, canal, palavras-chave, janela, follow-ups (horas) e perfil vêm da campanha. Templates de abertura/follow-up NÃO são recarregados no assistente (ver Incertezas).
  - Modal de saída **Sair sem salvar?**.
- **Fluxos:** **Salvar alterações** → lista: `PUT /campaigns` (toast **Campanhas atualizadas com sucesso!**); webhook: `PUT /campaigns/webhook/:id` (**Campanha webhook atualizada com sucesso!**); palavra-chave: `PUT /campaigns/inbound/:id` (**Campanha inbound atualizada com sucesso!**); depois toast **Campanha atualizada.** e volta a `/campaigns/{id}`. Trocar para missão livre limpa o vínculo de processo (`processGroupId`/`initialProcessId` = null).
- **Regras e limites:** as mesmas validações da criação, exceto a exigência de CSV. Em lista, o canal escolhido é enviado como canal fixo da campanha (`entityChannels`).
- **Perguntas prováveis:** "Posso trocar de lista para webhook?" → não. "As mudanças valem para quem já está conversando?" → sim, no próximo turno (texto da tela). "Posso trocar o template?" → o assistente em modo edição só exige o template WABA de abertura se o canal for WABA; ver Incertezas.
- **Incertezas:** `loadForEdit` não carrega `templateAssignments` existentes; em canal WABA, a validação **Selecione um template de abertura aprovado — o canal oficial exige.** pode obrigar a escolher o template de novo ao editar; como o backend trata `templateAssignments` ausentes no `PUT` não está no front. Edição de campanha replicada em várias unidades: o assistente novo envia `associatedCampaigns` só com a campanha atual.

---

## Detalhe da campanha (`/campaigns/:id`)
Arquivos: `pages/campaigns/[id].vue` (carrega `GET /campaigns/:id`), `components/campaigns/CampaignResults.vue` (cabeçalho e abas) e as abas `CampaignDetailsTab.vue`, `CampaignMetricsTab.vue`, `CampaignScheduleTab.vue` (+ `CampaignScheduleView.vue`, `CampaignScheduleStats.vue`, `CampaignJobsTable.vue`), `CampaignTestTab.vue` (+ `CampaignConversationThread.vue`, `useCampaignTestConversation.ts`), `CampaignScenariosTab.vue` (+ `ScenarioEditor.vue`). Usa o layout `default` (sem o submenu de Campanhas).

- **Como chegar:** clicar numa campanha na lista (`?fromDashboard=1`); cartão de campanha na Home; ficha do contato no Inbox (**Abrir campanha**, só gestor+); ação de uma prioridade do Panorama; após salvar a edição. A aba pode ser fixada na URL com `?tab=details|metrics|schedule|test|scenarios`.
- **Para que serve:** acompanhar uma campanha: configuração, resultados, contatos/execuções, testar a conversa da IA sem enviar nada e manter uma suíte de cenários.
- **Quem vê:** gestor+ (backend recorta). Atendente não tem link.
- **Plano, créditos e bloqueios:** feature `campaigns`. Testes e cenários consomem IA (créditos) — a aba Cenários exibe a estimativa.
- **Estados da página:** carregando (spinner); erro **Erro ao carregar campanha** + **Erro ao carregar os dados da campanha** (ou **ID da campanha não fornecido**) + botão **Voltar**; toast **Erro ao buscar os detalhes da campanha.**
- **Voltar** (seta, tooltip **Voltar**): volta para `/campaigns/entity/{fromEntity}` (que redireciona para a lista filtrada), para a lista preservando `companyId/classId/level/dateFrom/dateTo/status` da URL quando `fromDashboard=true`, ou para `/campaigns/dashboard`.

### Cabeçalho
- Título (ou **Campanha {categoria}** se sem título) + selo de status (**Não Iniciada** / **Ativa** / **Pausada** / **Finalizada** / **Arquivada**).
- Chips: origem **Agendada** / **Webhook** / **Inbound**; nome do processo preferencial (resolvido por `GET /processes/:id`) ou **missão livre**; **sucesso: {Processo concluído | Transferência qualificada | Dados coletados | Marcação manual}**.
- Botões: **Editar** (tooltip **Editar campanha**; vai para `/campaigns/edit/{id}` com `?entityId=` quando veio de uma unidade); **Iniciar** (tooltip **Iniciar campanha**; só campanha **Agendada**, **Não Iniciada** e sem jobs agendados `hasScheduledJobs`); **Pausar** (tooltip **Pausar campanha**; status Ativa); **Retomar** (tooltip **Retomar campanha**; status Pausada). Toasts iguais aos da lista.
- Abas: **Detalhes**, **Métricas**, **Fila de Eventos** (webhook) ou **Execuções** (lista e palavra-chave), **Testar**, **Cenários**.

### Aba **Detalhes** (`CampaignDetailsTab.vue`)
- Cartão **Informações da Campanha**: **Título**, **Categoria** (**Vendas**, **Cobrança**, **Qualificação de Leads**, **Reativação**, **Nutrição**, **Pós-venda**; campanhas do assistente novo têm categoria `GENERAL`, exibida como `GENERAL`), **Status**, **Contatos** (`_count.audienceContacts`), **Execuções** (`_count.campaignExecutions`), **Criada em**.
- Campanha de lista — cartão **Configuração do Agendamento**: **Data de Início**, **Data de Fim** (se houver), **Tipo de Execução** (**Uma única vez** / **Diariamente** / **Semanalmente** / **Mensalmente** / **Datas personalizadas** / **Não definido**), **Detalhes** (**Todos os dias no período especificado**; **Todos os {Segunda-feira, Terça-feira…}**; **Todo dia {1, 15} do mês**; **Nas datas: {datas}**; **Execução única na data de início**; ou **Nenhum dia da semana selecionado** / **Nenhum dia do mês selecionado** / **Nenhuma data personalizada definida** / **Detalhes não disponíveis**), seção **Horários de Execução** › **Horários** (**09:00 às 18:00**, ou **Nenhum horário definido**). Vazio: **Nenhuma configuração de agendamento encontrada**.
- Campanha de palavra-chave — cartão **Configuração do Trigger Inbound**: **Operador** (**Contém** / **Igual a** / **Começa com** / **Termina com** / **Expressão Regular**), **Palavras-chave** (chips), **Case Sensitive** (**Sim**/**Não**), **Apenas na primeira mensagem** (**Sim**/**Não**), seção **Tag Aplicada** com a etiqueta colorida. Vazio: **Nenhuma configuração inbound encontrada**.
- Campanha de webhook — cartão **URL do Webhook**: **URL do Endpoint** (montada no front: `{CAMPAIGN_WEBHOOK_URL ou https://api.pypsystem.com}/v1/webhooks/campaign/{id}/{token}`) + **Copiar** (tooltip **Copiar URL**; toast **URL copiado!**); **Secret Token** oculto com botão **Mostrar**/**Ocultar** e **Copiar** (tooltip **Copiar token**; toast **Token copiado!**; erro **Erro ao copiar**); **Exemplo de Payload** com botão **Ver exemplo de payload** / **Ocultar exemplo** (busca `{URL}/schema`, exibe o JSON gerado pelo backend a partir do mapeamento de variáveis, com **Copiar** → **Exemplo copiado!** e notas em lista; **Carregando exemplo...**; erro **Não foi possível carregar o exemplo de payload.**); botão **Regenerar Token** (**Regenerando...**) que abre o modal **Confirmar** com **Tem certeza que deseja regenerar o token? A URL antiga deixará de funcionar imediatamente. Atualize a URL em todos os sistemas que utilizam este webhook.** e botões **Não** / **Sim** (`POST /campaigns/webhook/:id/regenerate-token`; toast **Token regenerado com sucesso!** ou **Erro ao regenerar token**); aviso **Ao regenerar o token, a URL antiga deixará de funcionar imediatamente. Atualize a URL em todos os sistemas que utilizam este webhook.**; seção **Configuração de Execução** › **Modo de Execução** (**Imediato (24/7)** ou **Horário Específico**); seção **Janela de Execução** (se houver) com **Dias da Semana** (**Segunda, Terça…**), **Horários** (**09:00 - 18:00**) e a nota **Eventos recebidos fora da janela de execução são automaticamente enfileirados e processados no próximo horário disponível.** Vazio: **Nenhuma configuração de webhook encontrada**.
- Cartão **Objetivo da Campanha**: **Nome do Agente** (ou **-**) e **Objetivo** (ou **Nenhum objetivo definido**).
- Cartão **Processo & Resultado**: **Processo preferencial** (nome + link **ver processo ↗**, ou **Missão livre — sem processo vinculado**); **Definição de sucesso** (rótulo, ou **Não definida — campanha anterior ao modelo de conversões**) e detalhe: **Destino: {setor | fila geral}** · **Campos exigidos: a, b** · **Valor por conversão: R$ {valor}** · **Valor por conversão: coluna "{coluna}"**.
- Cartão **Template de Início da Conversa** (se houver): selo **Aprovado** / **Em revisão** / **Rejeitado** / **Novo**, **Marketing · pt_BR** ou **Utilidade · pt_BR** e a prévia da mensagem. O status é atualizado em tempo real via socket (`template:status_changed`) com toasts **Template "{nome}" foi aprovado pelo Meta!** / **Template "{nome}" foi rejeitado pelo Meta.**
- Cartão **Follow-ups** (contador): cada item **{n}h após não resposta**, selo **Inativo** quando desativado, instrução ou **Sem instrução específica**, e prévia do template de follow-up (≥24h) com selo de status.
- Cartão **Diretrizes da Campanha**: título, selo **Inativa** para versões antigas, **Prioridade {n}**, texto; vazio **Nenhuma diretriz configurada**.

### Aba **Métricas** (`CampaignMetricsTab.vue`)
Dados: `GET campaign-metrics/:id`, `/quick-stats`, `/abandon-summary`, `/abandon-details`, `GET /campaigns/:id/executions`, `PATCH /campaigns/:id/executions/:execId/conversion`.
- Estados: **Carregando métricas da campanha...**; erro **Erro ao Carregar Métricas** + mensagem + **Tentar Novamente** (toasts **Erro ao obter métricas da campanha.**, **Erro ao obter estatísticas rápidas da campanha.**, **Erro ao obter resumo de abandonos da campanha.**).
- Sub-abas: **Visão Geral**, **Conversas**, **Conversões**, **Abandonos**.
- **Visão Geral**: cartões **Conversas Iniciadas** (`totalConversationsStarted`), **Taxa de Resposta** (`responseRate`, 1 casa decimal), **Taxa de Escalação** (`escalationRate`), **Mensagens Totais** (`totalMessagesExchanged`), **Taxa de Abandono** (`abandonRate` e **({abandonados}/{transferidos})**). Bloco **Distribuição por Status** com barras **Ativo**, **Concluído**, **Aguardando Resposta**, **Transferido**, **Falhou** (largura = quantidade ÷ conversas iniciadas). Bloco **Métricas de Performance**: **Conversas com Respostas** (barra = taxa de resposta), **Conversas Transferidas** (barra = taxa de escalação), **Média de Interações por Conversa**, **Média até Transferência**. Todas as taxas vêm prontas do backend.
- **Conversas**: faixa **Total**, **Com Resposta**, **Transferidas**, **Média Interações**; tabela **Detalhes das Conversas** — **Histórico completo de todas as conversas da campanha**; filtro **Todos os atendentes** / **Sem atendente (IA)** / nome de cada atendente; colunas **Contato** (nome + telefone), **Interações** (total + **{n} IA · {n} usr**), **Status** (**Ativo**, **Concluído**, **Falhou**, **Pausado**, **Aguardando Resposta**, **Aguardando Atendente**), **Atendente** (nome ou **IA apenas**), **Transferido** (**Sim** ou **—**), **Iniciado em**. 20 por página; **Mostrando {a} até {b} de {n} resultados**. Vazio: **Nenhuma conversa encontrada** / **As conversas aparecerão aqui quando contatos interagirem com a campanha.**
- **Conversões**: rótulo **definição de sucesso** + chip (ou **Sem definição de sucesso (campanha anterior ao modelo)**); filtro **Somente convertidas** (padrão) / **Todos os contatos**; cartões **Conversões** (total), **Taxa de conversão** (**sobre conversas iniciadas**), **Valor somado** (R$ ou **—**) com chips por origem **Processo concluído · n**, **Transferência qualificada · n**, **Dados coletados · n**, **Manual · n**, **Sinal externo · n**. Lista de execuções (carregada ao abrir a sub-aba): nome do contato (ou **Contato**), **Convertida em {data} · {origem}** ou o status traduzido, valor, botão **Marcar conversão** / **Remover conversão** (toasts **Conversão registrada.** / **Conversão removida.** / **Erro ao atualizar conversão.**; a origem passa a **Manual**; sem valor informado o backend usa o `goalConfig`). Vazios: **Nenhuma conversão registrada** ou **Nenhum contato nesta campanha ainda** com **Quando Tino cumprir a definição de sucesso — ou você marcar manualmente — as conversões aparecem aqui.** ou **Esta campanha não tem definição de sucesso; você ainda pode marcar conversões manualmente na lista completa.**
- **Abandonos**: cartões **Total Transferido**, **Total Abandonado**, **Taxa de Abandono** (verde <30%, amarelo 30–49%, vermelho ≥50%); tabela **Detalhes dos Abandonos** — **Lista de conversas que foram transferidas e posteriormente abandonadas** com colunas **Contato**, **Transferido em**, **Alerta Enviado em**, **Status Atual**, **Última Interação** (ou **Sem interação**); vazio **Nenhum abandono encontrado** / **Não há conversas abandonadas para esta campanha.**; carregando **Carregando detalhes dos abandonos...**

### Aba **Execuções** (lista) — `CampaignScheduleView.vue`
Dados: `GET /campaigns/:id/schedule-status` (jobs da fila de agendamento).
- Cartões **Agendados**, **Ativos**, **Completados**, **Falhados**; bloco **Próxima Execução** com data/hora e tempo restante (**{d}d {h}h**, **{h}h {m}m**, **{m}m** ou **Executando agora**).
- Tabela **Jobs Agendados**: busca **Buscar contato...** (nome ou telefone); filtro **Todos** / **Agendados** / **Ativos** / **Completos** / **Falhados**; botão **Atualizar**; colunas ordenáveis **Contato**, **Status** (**Agendado** / **Ativo** / **Completo** / **Falhou**), **Agendado Para**, **Tempo Restante** (**Vencido** em vermelho quando passou; **Executando** para ativos; **-** para completos/falhos), **Tentativas** (**{n}x**). 20 por página. Vazio: **Nenhum job encontrado**.
- Rodapé: **Dados carregados em: {data}** e **Clique em "Atualizar" para obter dados mais recentes**. Estados: **Carregando agendamentos...**; erro **Erro ao carregar agendamentos** + **Tentar novamente** (toast **Erro ao buscar status dos agendamentos.**); vazio **Nenhum agendamento encontrado** / **Esta campanha ainda não possui jobs agendados.**
- Tipos de job (`jobType`): `execute-contact`, `reminder`, `follow-up` (não exibidos na tabela).

### Aba **Execuções** (palavra-chave) — `CampaignScheduleTab.vue`
- Cartão **Execuções Inbound** com **Atualizar**; tabela **Status** (**Pendente** / **Processando** / **Ativa** / **Concluída** / **Falhou** / **Cancelada** / **Pausada**), **Contato** (nome/`remoteJid`), **Iniciada em**, **Última atualização**. Vazio: **Nenhuma execução encontrada** / **Quando um contato enviar uma mensagem que corresponda aos padrões configurados, a execução aparecerá aqui**. Nota: **Cada execução representa um contato que enviou uma mensagem correspondente aos padrões configurados nesta campanha. Tino inicia automaticamente a conversa com o contexto da campanha.**

### Aba **Fila de Eventos** (webhook) — `CampaignScheduleTab.vue`
Dados: `GET /campaigns/webhook/:id/queue`.
- Cartão **Fila de Eventos Webhook** com **Atualizar** (**Carregando...**); tabela **Status** (**Pendente**, **Processando**, **Concluída**, **Falhou**, **Cancelada**), **Contato** (nome + telefone do payload), **Agendado para**, **Processado em** (ou **-**), **Tentativas**. Vazio: **Nenhum evento na fila** / **Eventos recebidos fora do horário de execução aparecerão aqui**. Nota: **Quando um evento webhook chega fora da janela de execução configurada, ele é enfileirado e processado automaticamente no próximo horário disponível. Eventos com status "Pendente" serão processados em breve.** Não há botão de cancelar evento.

### Aba **Testar** (`CampaignTestTab.vue`)
Dados: `GET /campaigns/:id/dry-run/sample` (payload sugerido do último disparo real) e `POST /campaigns/:id/dry-run`.
- Painel **Disparo simulado** — **Nada é enviado e nada é gravado: sem conversa, sem execução e sem mexer no processo do contato.** Campos: **Etapa da abordagem** (select com **{etapa} · {descrição}**, só quando o processo tem campo seletor; nota **É o que o disparo manda no campo {campo}. Trocar aqui é como se compara um roteiro com outro.**), **Nome do contato** (padrão **Contato de teste** ou o nome do último disparo), **Dados do evento ({n})** com **Campos que a integração manda junto do disparo, carregados do último envio real.** ou **Esta campanha ainda não teve disparo real, então não há campos de referência para carregar.**; cada campo com rótulo humanizado, valor (texto ou JSON), **Remover {campo}**; **Adicionar campo** (placeholder **nome do campo (ex.: valor)** / **valor**). Botão **Iniciar conversa de teste** (**Rodando...**). Depois de iniciar: **Ocultar** / **Mostrar** o painel e a nota **Conversa em andamento. Para trocar a etapa ou os dados, recomece o teste.**
- Painel **Conversa**: vazio **Inicie a conversa para ver a primeira abordagem. Depois responda como o cliente e acompanhe se Tino segue o roteiro ao longo dos turnos.**; fio com turnos **TINO** (chip da etapa selecionada; **escrevendo…**) e **VOCÊ, COMO O CLIENTE**; avisos **Etapa sem texto escrito — Tino redigiu por conta própria.** e **Você pediu {etapa}, mas o código selecionou {outra}.** / **Nenhuma etapa selecionada, mesmo com {etapa} no disparo. Tino recebeu o catálogo inteiro e escreveu por conta própria.**; botão **Por que ele disse isso** abre a procedência: grupos **Conformidade**, **Roteamento**, **Diretrizes** (links para editar cada instrução), **O que da sua configuração entrou** (seções expansíveis) ou **Nada de configuração da empresa entrou neste turno.** Caixa **Responda como o cliente responderia — ex.: já paguei ontem** (Enter envia) e botão **Recomeçar**. Erro: toast **Erro ao testar a campanha** (ou mensagem do backend). Se a IA devolver vazio: **(vazio)**.
- O cursor do processo volta em cada resposta e é reenviado no turno seguinte (a conversa segue o roteiro em vez de re-triar).

### Aba **Cenários** (`CampaignScenariosTab.vue` + `ScenarioEditor.vue`)
Dados: `GET/POST /campaigns/:id/scenarios`, `/scenarios/suggest`, `/scenarios/cost`, `/scenarios/run-all`, `PUT/DELETE /campaigns/scenarios/:id`, `POST /campaigns/scenarios/:id/run`, `GET /campaigns/scenarios/runs/:runId`, `PATCH .../taken-over`; turnos chegam pelo socket `campaignScenarioSimulation`.
- Painel **Cenários** — **Clientes difíceis que a campanha precisa dar conta. Um cenário só passa se todos os critérios passarem.** Vazio: **Nenhum cenário ainda. A IA pode propor a partir do objetivo da campanha, do roteiro e das conversas que já aconteceram.** Lista com veredito: **Ainda não rodou**, **Exploração** (assumida), **Rodando**, **Passou**, **Erro**, **{n} critério(s) falharam** ou **Não passou**.
  - Propostas da IA: bloco **Propostos ({n}) — nada salvo ainda** com **Revisar** e descartar.
  - Botões: **Rodar todos os cenários** (só com 2+), **Propor cenários com IA** (**Propondo...**; pede 4 rascunhos), **Escrever um cenário**.
  - Custo: **Rodar todos deve consumir cerca de {x} créditos, pela média das rodadas anteriores.** ou **Rodar todos consome até {n} chamadas de IA, debitadas do seu crédito. Depois da primeira rodada esta estimativa passa a sair em créditos.**
- Painel da conversa: vazio **Escolha um cenário para ler a conversa inteira — o que Tino disse e como o cliente reagiu.**; nome e premissa; botões **Rodar**, **Assumir** (só com transcrição e antes de assumir), **Editar**, remover (lixeira, tooltip **Remover cenário**; sem confirmação; toast **Cenário removido**). Aviso quando assumida: **Alguém assumiu esta conversa no meio. Ela deixou de ser reproduzível, então não conta como cenário aprovado.** Bloco **Critérios** com ✓/✗ e detalhe; erro **A simulação não terminou: {erro}**; transcrição com **CLIENTE SIMULADO** e **TINO** (chips da etapa e **transferiu** / **encerrou**); **Rode o cenário para ver a conversa.**; **escrevendo…**. Após assumir: fio com **VOCÊ, CONDUZINDO** e caixa **Responda como o cliente responderia**.
  - Modal ao assumir: **Confirmar** — **Assumir a conversa descarta o veredito desta execução: ela deixa de ser reproduzível e passa a contar como exploração. Para ter o veredito de volta, rode o cenário de novo.** (**Não** / **Sim**).
- Modal do editor (**Novo cenário** / **Editar cenário** / **Revisar cenário proposto**): **Um cliente difícil e o que se espera do Tino diante dele. Todos os critérios precisam passar.** (+ **Proposto pela IA a partir do objetivo da campanha, do roteiro e das conversas reais. Nada é salvo até você revisar.**). Campos: **Nome** (placeholder **Termina em: pagamento prometido**; dica **Nomeie pelo desfecho esperado — assim a lista vira mapa de cobertura.**), **Premissa** (**Cliente que já pagou e vai contestar a cobrança**; **Aparece no topo da transcrição. Sem ela, quem lê não sabe o que o cliente estava tentando fazer.**), **Persona** (**Como este cliente escreve, o que ele quer, onde ele insiste...**; **Cliente cooperativo passa em tudo. O valor está no chato.**), **O que é verdade sobre ele** (pares **campo**/**valor**, botão **Campo**; **Valores, datas e documentos. É o que Tino enxerga — sem isso a conversa trava quando ela precisar de um dado, e o cliente simulado inventaria o resto.**), **Critérios de aprovação** (botão **Critério**; tipos **Desfecho** — Como a conversa termina (**Transferida para humano** / **Encerrada pelo Tino** / **Segue em aberto**), **Etapa** — Tino seguiu a etapa esperada (select **Escolha a etapa**), **Roteiro** — Tino enviou o texto escrito na etapa, **Conformidade** — Nenhuma regra foi violada (select **Escolha a regra** com as regras de conformidade da empresa), **Dado** — Um campo foi coletado (placeholder **chave do campo (ex.: data_pagamento)**), **Comportamento** — Expectativa em texto livre (placeholder **Não pedir CPF ou CNPJ de quem já está identificado**)), **Teto de turnos** (padrão 8; 2 a 20). Botões **Cancelar** / **Salvar cenário** (**Salvando...**). Salvar exige nome, persona e ao menos um critério preenchido. Toasts **Cenário criado** / **Cenário salvo** / **Erro ao criar cenário** / **Erro ao salvar cenário** / **Erro ao sugerir cenários** / **Erro ao rodar o cenário** / **Erro ao rodar os cenários**.
- **Regras:** um cenário passa só se todos os critérios passam; assumir a conversa marca a execução como exploração; a saúde da suíte aparece na lista de campanhas (**cenários ok** / **{n} cenário(s) falhando** / **{n} cenário(s) sem rodar**).

### Perguntas prováveis (detalhe)
- "Onde vejo as conversas da campanha?" → **Métricas › Conversas** (tabela) e no Inbox (conversas com chip **Campanha**).
- "Como marco uma venda?" → **Métricas › Conversões › Marcar conversão** (fica como origem **Manual**).
- "O botão Iniciar não aparece" → só para campanha **Agendada** em **Não Iniciada** sem jobs; webhook/palavra-chave nascem ativas.
- "A URL do webhook parou" → o token foi regenerado (**Regenerar Token**); atualize nos sistemas.
- "Quanto custa rodar os cenários?" → o texto de custo no painel **Cenários**.

### Incertezas (detalhe)
- Fórmulas de `responseRate`, `escalationRate`, `abandonRate`, `conversions.rate` (backend).
- Como o backend produz o `examplePayload`/`notes` do `/schema`.
- Status `CANCELLED` de campanha aparece nos mapas de cor, mas não existe no tipo `CampaignStatus`.
- O que dispara `hasScheduledJobs` e se **Iniciar** reaparece após pausar/retomar uma agendada.

---

## Configuração inicial — Bem-vindo às Campanhas (`/campaigns/setup`)
Arquivos: `pages/campaigns/setup.vue` + `components/campaigns/BrainContextChat.vue` (`POST /brain/chat`). Layout `default`.

- **Como chegar:** nenhuma tela, menu ou redirecionamento leva a esta rota (grep sem resultados); só por URL. Tratar como tela órfã/legada.
- **Para que serve:** conversa guiada com o **Consultor Empresarial** para o Cérebro entender o negócio antes de criar campanhas.
- **O que há na tela:** ícone de megafone; **Bem-vindo às Campanhas!**; **Para criarmos campanhas verdadeiramente eficazes e personalizadas para sua empresa, nosso Consultor Empresarial precisa entender melhor seu contexto de negócio, produtos, serviços e objetivos estratégicos.**; caixa **Esta é uma etapa única e essencial que permitirá que as IAs criem campanhas alinhadas com sua identidade empresarial.**; botões **Configurar contexto empresarial** (abre o chat) e **Pular por agora** (vai para `/campaigns/dashboard`).
- **Modal do chat** (`BrainContextChat`): cabeçalho **Consultor Empresarial** / **Mapeamento de Conhecimento para Campanhas**; tela inicial **Preparação para Campanhas** — **Antes de criarmos suas campanhas, é essencial que o nosso Consultor Empresarial entenda profundamente o contexto da sua empresa. Esta conversa permitirá que os agentes de IA criem campanhas mais eficazes e alinhadas com seus objetivos de negócio.** + **Compartilhe informações sobre seus produtos, serviços, público-alvo, valores e objetivos estratégicos.** + botão **Iniciar Conversa** (envia "Olá" ao Cérebro). Chat com efeito de digitação; caixa **Conte sobre sua empresa, produtos, público-alvo, objetivos...** (Enter envia; Shift+Enter quebra linha). Erro: **Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.** Quando o backend devolve `isSummaryCompleted`, tela **Excelente!** / **Seu Cérebro Empresarial está Pronto!** / **Nosso cérebro foi treinado especificamente para sua empresa. Ele agora compreende profundamente seu negócio, seus produtos, seu público e seus objetivos estratégicos.** / **A partir de agora, toda campanha criada utilizará essa base de conhecimento como fundação. Além disso, nossa IA continuará aprendendo e se aperfeiçoando conforme suas campanhas forem executadas, tornando-se cada vez mais inteligente e eficaz.** / botão **Criar primeiras campanhas** (vai para `/campaigns/dashboard`). Não há botão para fechar o modal no meio da conversa (o botão **Pular** está comentado no código).
- **Incertezas:** se o produto ainda usa essa etapa (nada aponta para ela); o que o backend faz com o resumo.

---

## Contatos de Campanha (`/settings/campaign-integrations`)
Arquivo: `pages/settings/campaign-integrations.vue` (layout `settings`). Dados: `GET /company/integration-status`, `GET /integrations/varejo-online/config/status`, `POST /integrations/varejo-online/config`.

- **Como chegar:** menu principal **Configurações** > seção **Integrações** > tile **Contatos de Campanha** — **Configure Varejo Online, SAN e outras integrações para campanhas WhatsApp.**
- **Para que serve:** guardar a chave da API do Varejo Online (e ver o status da integração SAN) para importar clientes como contatos de campanha.
- **Quem vê:** só Admin da Empresa / `SYSTEM_ADMIN` (tile some e a rota redireciona para `/home`).
- **Plano, créditos e bloqueios:** feature `campaigns` (wall). **PlatformGate**: sem `san.available`, o conteúdo fica desfocado com **Integrações de campanha não disponível no seu plano atual**.
- **O que há na tela:** título **Contatos de Campanha**; subtítulo **Configure as integrações externas para campanhas WhatsApp.**
  - Cartão **Varejo Online** — **Importe clientes do seu sistema de gestão para campanhas**; selo **Ativa** (chave válida), **Chave inválida** ou **Não configurada**. Alerta **Chave API Inválida** / **A chave API atual é inválida. Atualize com uma chave válida.** quando inválida. Com chave válida: **Chave API Atual** (mascarada) + botão **Alterar Chave** + **A chave está configurada e funcionando corretamente.** Formulário: **Chave API** ou **Nova Chave API**, campo tipo senha com placeholder **Cole aqui a chave API do Varejo Online** e botão de mostrar/ocultar, botões **Cancelar** (na alteração) e **Salvar Chave** (**Salvando...**), nota **A chave será criptografada e armazenada de forma segura.**
  - Cartão **SAN Internet** (só quando `san.available`) — **Importe clientes do painel SAN para campanhas**; selo **Ativa** / **Não configurada**; texto **Esta integração é configurada via variáveis de ambiente do servidor. Entre em contato com o administrador do sistema para configurar.**
  - Botão **Atualizar Status**.
- **Fluxos:** colar a chave > **Salvar Chave** → toast **Chave API salva com sucesso!** e recarrega o status; chave vazia → **Informe a chave API**; erro → mensagem do backend ou **Erro ao salvar chave API**.
- **Regras:** a chave é validada pelo backend (`isValid`); a SAN não é configurável pela tela.
- **Onde essas integrações são usadas:** apenas no passo **Audiência** do assistente ANTIGO (`?legacy=1`), via `IntegrationsSelector` / `VarejoOnlineIntegration` / `SanIntegration`. O assistente novo só aceita CSV. Ver a seção do assistente antigo.
- **Perguntas prováveis:** "Configurei a chave e não vejo a opção no assistente" → o assistente padrão não oferece importação por integração; só o antigo (`/campaigns/create?legacy=1`).
- **Incertezas:** critério de `san.available`/`san.configured`; se a intenção é reintroduzir a importação no assistente novo.

---

## Templates WhatsApp (`/settings/channels/whatsapp-waba/templates/:channelId`) — o que campanhas usam
Arquivos: `pages/settings/channels/whatsapp-waba/templates/[channelId].vue` + `components/settings/channels/TemplateManagement.vue` (reutiliza o editor e a prévia de campanhas).

- **Como chegar:** **Configurações > Canais** > canal WhatsApp oficial (WABA) > templates (`?name=` traz o nome do canal). Gestor+ em qualquer nível.
- **Para que serve:** criar, sincronizar com a Meta, pré-visualizar, editar e excluir os templates do canal que as campanhas usam na abertura e nos follow-ups.
- **O que há na tela:** título **Templates WhatsApp** / **Gerencie os templates de mensagem deste canal WABA.**; botões **Sincronizar** (`POST /templates/{canal}/sync`; toasts **Sincronizando templates com o Meta...** → **Templates sincronizados!** / **Erro ao sincronizar templates.**) e **Novo Template** (abre o editor de campanhas em modo `CONVERSATION_START`; `POST /templates/{canal}`; toasts **Enviando template para aprovação...** → **Template enviado para aprovação!**). Tabela: **Nome** (+ corpo), **Status** (**Aprovado** / **Em revisão** / **Rejeitado**), **Categoria** (**Marketing** / **Utilidade** / **Autenticação** + idioma), **Campanhas** (**{n} campanha(s)** ou **—**), **Ações** (**Prévia**, **Editar**, **Excluir**). Vazio: **Nenhum template encontrado** / **Crie um novo template ou sincronize com o Meta para importar templates existentes.**
- **Vínculo com campanhas:** template usado por campanha ativa não pode ser editado (tooltip **Campanha ativa - não pode editar**); template usado por qualquer campanha não pode ser excluído (tooltip **Em uso por campanha(s)**). Editar abre a confirmação **Ao salvar, o template passará por uma nova aprovação do Meta e não poderá ser editado novamente nas próximas 24 horas. Deseja continuar?** (toast **Template atualizado! Aguardando re-aprovação.**). Excluir: **Tem certeza que deseja excluir o template '{nome}'? Esta ação remove o template do Meta e não pode ser desfeita.** (toast **Template excluído com sucesso.**).
- **Regras:** só templates **Aprovado** podem ser escolhidos no assistente; templates criados fora da plataforma com variáveis posicionais aparecem como **Não suportado** na campanha; status muda em tempo real via socket.
- **Incertezas:** tempo de aprovação da Meta e o que acontece com a campanha se o template for rejeitado depois de criada (o front só muda o selo).

---
