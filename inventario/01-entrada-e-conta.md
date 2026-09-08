# Inventário de telas: Entrada, primeiro acesso e conta pessoal

Fonte: clone da `main` do `tartini-web` (03/09/2026). Só o front foi lido; o que depende do backend (validade de tokens, regras de senha além de 6 caracteres, expiração real de convites) está marcado como incerteza.

Convenções deste arquivo:

- Textos entre aspas são transcrições exatas do código (rótulos, placeholders, toasts). Travessões e reticências dentro das aspas são do próprio produto.
- "Papéis" seguem `utils/roleLabel.ts`: **Administrador** (ADMIN na Empresa), **Gestor da Empresa** (MANAGER na Empresa), **Gestor de Área** (MANAGER na Área), **Gestor de Unidade** (MANAGER na Unidade), **Atendente** (ATTENDANT na Unidade). **Dono da conta** é quem tem `isSubscriptionAdmin = true` (helper `canAccessBilling`). SYSTEM_ADMIN (equipe SAN) passa por todos os gates.
- Helpers de papel usados pelo código: `isCompanyAdmin` (Administrador ou SYSTEM_ADMIN), `isCompanyManagerWide` (Administrador ou Gestor da Empresa), `isClassManagerWide` (nível Área ou acima), `canAccess('MANAGER')` (gestor em qualquer nível: Empresa, Área ou Unidade), `canManageUsers`.
- Toasts: `toast.success` (verde), `toast.error` (vermelho), `toast.warning` (amarelo), `toast.info`.

Arquivos-chave: `middleware/auth.global.ts`, `stores/auth.store.ts`, `stores/dashboard.store.ts`, `components/auth/AuthContainer.vue`, `components/auth/AuthLayout.vue`, `components/auth/StepIndicator.vue`, `components/auth/RegisterStepOne|Two|Three.vue`, `pages/*` listadas abaixo, `components/shared/Sidebar.vue`, `components/shared/ProfileMenu.vue`, `components/shared/EntitySelectModal.vue`, `components/shared/SubscriptionBanner.vue`, `components/shared/CreditGateBanner.vue`, `components/billing/PlanUpgradeWall.vue`, `components/shared/OnboardingWidget.vue`, `components/onboarding/OnboardingBlockModal.vue`, `components/home/*`, `components/settings/security/*`, `components/user/EditUser.vue`, `layouts/auth.vue`, `layouts/default.vue`, `layouts/settings.vue`, `composables/useSettingsMenu.ts`, `plugins/axiosConfig.ts`, `plugins/socket.client.ts`, `docs/visibilidade-por-papel.md`.

---

## Menu principal (sidebar esquerda)

Arquivo: `components/shared/Sidebar.vue`. Renderizada só com sessão ativa e em telas `>= 1024px` (`layouts/default.vue`, `layouts/settings.vue` e demais layouts). Abaixo de 1024px o menu principal some e entra a barra inferior `InboxMobileMenu` (ver "Menu mobile").

Comportamento geral:

- Estado colapsado (48px, só ícones) e expandido (252px). Expande ao passar o mouse; o botão de alfinete no topo fixa/solta (title `"Fixar sidebar"` / `"Soltar sidebar"`). A preferência fica em `localStorage` (`sidebar-expanded`), então sobrevive a fechar o navegador.
- Ícone `fill` (preenchido) marca o item ativo; os demais ficam `regular`. Família de ícones: Phosphor.
- Logotipo (símbolo da marca) no topo leva a `/home`.
- Abaixo do logo, quando expandida, há o botão de contexto **Área / Unidade** (tooltip `"Trocar classe/unidade"`): mostra o nome da Área (linha pequena) e o nome da Unidade atual (ou `"—"`) e abre o modal **Trocar Unidade**. Se houver novos atendimentos em outras unidades, aparece um contador preto (`9+` acima de 9; tooltip `"Novos atendimentos em outras unidades"`).

### Itens da seção principal, na ordem exata

| # | Rótulo (tooltip igual) | Ícone | Rota | Quem vê |
|---|---|---|---|---|
| 1 | `Página Inicial` | `PhHouse` | `/home` | Todos |
| 2 | `Inbox` | `TrayPlainIcon` (ícone próprio, `components/icons/TrayPlainIcon.vue`) | `/inbox` | Todos. Mostra contador de não lidas (`totalUnread`; colapsada mostra `9+` acima de 9) |
| 3 | `Métricas` | `PhChartBar` | `/metrics/overview` | `requires: 'manager'` → gestor em qualquer nível (Administrador, Gestor da Empresa, de Área ou de Unidade). Atendente não vê |
| 4 | `Central de Conversas` | `PhChats` | `/conversations/overview` | Todos (o backend recorta os dados: Atendente vê só as conversas dele) |
| 5 | `Cérebro` | `PhBrain` | `/identity/overview` | `requires: 'companyManager'` → só Administrador ou Gestor da Empresa |
| 6 | `Scout` | `PhCompass` | `/scout` | Todos |
| 7 | `Campanhas` | `PhMegaphone` | `/campaigns` | `requires: 'manager'` + `requiresFeature: campaigns`. O item **não é escondido** pelo plano: quem não tem a feature vê o item e, ao abrir, recebe o `PlanUpgradeWall` |

Seções `performance` e `config` existem no tipo, mas não há itens nelas (só `main`).

### Rodapé da sidebar (mesma ordem)

| Rótulo | Ícone | Ação | Quem vê |
|---|---|---|---|
| `Configurações` | `PhGear` | `/settings` | Todos |
| `Feedback` | `PhChatTeardropText` | Abre o modal **Enviar Feedback** (não é rota) | Todos com assinatura ativa (o modal some em modo somente leitura) |
| Bloco do perfil (avatar com bolinha de presença, nome e e-mail; colapsada só o avatar) | `SharedAvatar` | Ao passar o mouse abre o **Menu do perfil** | Todos |

Bolinha de presença no avatar: title `"Online"`, `"Ausente"` ou `"Offline"`.

### Menu do perfil (`components/shared/ProfileMenu.vue`)

Menu flutuante ao lado do bloco do perfil (abre no hover, fecha ao sair ou clicar fora). Itens na ordem:

1. Nome do usuário (ícone `PhUser`) → `/settings/user` (perfil). Se não houver nome, mostra `"Usuário"`.
2. `Unidade` (ícone `PhBuildings`), com o nome da unidade atual à direita → abre o modal **Trocar Unidade**.
3. `Página de Status` (`PhCellSignalFull`) → link externo `https://san.statuspage.io/` (nova aba).
4. `Documentação` (`PhBookOpen`) → `https://talk-docs.saninternet.com` (nova aba).
5. `Políticas e Termos` (`PhClipboardText`) → `https://www.saninternet.com/contratos` (nova aba).
6. `Tema escuro` / `Tema claro` (`PhMoon` / `PhSun`) → alterna o tema; preferência em cookie `ds-theme` (1 ano).
7. `Sair` (`PhSignOut`, em vermelho) → encerra a sessão (ver fluxo "Sair" na tela Segurança/Perfil).

### Modal "Trocar Unidade" (`components/shared/EntitySelectModal.vue`)

- Título `"Trocar Unidade"`, subtítulo `"Selecione a unidade que deseja acessar"`, botão X.
- Carregando: `"Carregando unidades..."`.
- Vazio: `"Nenhuma unidade encontrada"` / `"Você não possui acesso a outras unidades"`.
- Lista (`GET` via `getUserEntities`): unidade atual marcada com check; badge preto com contagem de novidades por unidade (`9+`).
- Rodapé: `"Atual: {nome da unidade}"`.
- Ao escolher: `POST /auth/switch-entity` (troca client-side, sem recarregar); atualiza empresa/área/unidade, papéis, assinatura, plano; zera o estado da Página Inicial (`dashboard.store.$reset`) e recarrega a rota atual. Erro: toast `"Erro ao trocar de unidade."`.
- O mesmo modal é aberto pelo botão de contexto no topo da sidebar, pelo item `Unidade` do menu do perfil e pelo botão de contexto no cabeçalho da Página Inicial do atendente.

### Menu mobile (`components/inbox/MobileMenu.vue`, abaixo de 1024px)

Barra inferior fixa (some dentro de uma conversa do Inbox). Itens: `Início` (`/home`), `Inbox` (`/inbox`, contador `9+`), `Unidade` (abre painel `"Selecionar Entidade"` com a lista de unidades) e `Config` (`/settings`). Observação: no mobile a troca de unidade **não** chama `/auth/switch-entity`; ela altera o cookie da unidade diretamente e vai para `/home`. Em telas menores que 1024px, dentro de `/settings`, há um cabeçalho `"Configurações"` com botão de menu que abre a sidebar de configurações como gaveta.

### Modal "Enviar Feedback" (`components/shared/FeedbackWidget.vue`)

- Cabeçalho: `"Enviar Feedback"` / `"Sua opinião nos ajuda a melhorar"`.
- `"O que deseja nos contar?"`: quatro tipos `Sugestão`, `Bug`, `Dúvida`, `Elogio`.
- `"Mensagem"` com contador `"{n}/10 min"` (mínimo 10 caracteres; fica vermelho abaixo disso). Placeholders: sem tipo `"Selecione um tipo acima para começar..."`; Sugestão `"Descreva sua sugestão de melhoria..."`; Bug `"Descreva o problema encontrado e como reproduzi-lo..."`; Dúvida `"Qual é a sua dúvida?"`; Elogio `"O que você gostou? Conte-nos!"`. O campo fica desabilitado até escolher o tipo.
- `"Anexos"`: `"Capturar tela"` (usa captura de tela do navegador; mostra `"Capturando..."`) e `"Anexar imagem"` (jpeg, png, webp). Pré-visualizações com rótulo `"Screenshot"` e `"Anexo"`, removíveis.
- Rodapé: `"Cancelar"` e `"Enviar feedback"` / `"Enviando..."` (habilita com tipo + 10 caracteres). Envia rota atual, navegador, resolução e horário como metadados.

---

## Banners e avisos globais

### Faixa de assinatura inativa (`components/shared/SubscriptionBanner.vue`, `composables/useSubscription.ts`, `plugins/subscriptionReadonly.client.ts`)

- Aparece no topo (fixa no desktop) quando `subscriptionStatus` não é `ACTIVE` nem `COMPLETED`. SYSTEM_ADMIN nunca vê. Texto: `"Sua assinatura não está ativa. Acesso em modo somente leitura."`
- Efeito: o `body` recebe a classe `subscription-readonly`, que desabilita botões, inputs, textareas e selects dentro do conteúdo (`article`) e botões flutuantes. Navegação continua funcionando.
- O status é reavaliado ao montar o layout (`GET /subscription/status`) e a cada refresh de sessão. Se o backend responder `403 SubscriptionInactive`, o front faz um refresh e, se continuar inativa, mostra toast `"Sua assinatura não está ativa. Ação bloqueada."`.
- Rótulos de status (usados em outras telas): `PENDING` "Pendente", `SUSPENDED` "Suspensa", `TERMINATED` "Encerrada", `CANCELLED` "Cancelada", `FRAUD` "Fraude", `ACTIVE` "Ativa", `COMPLETED` "Completa".
- O modal de Feedback fica oculto em modo somente leitura.

### Faixa de créditos (`components/shared/CreditGateBanner.vue`, `composables/useCreditGate.ts`)

- Fonte: `GET /subscription/credit-gate` (refeito a cada troca de rota e ao logar). Conta gratuita e "dark-launch" nunca disparam (backend responde OK).
- `BURST` (faixa amarela, ícone `PhWarning`): `"Créditos do mês esgotados - contrate mais para evitar interrupções"`.
- `BLOCKED` (faixa vermelha, ícone `PhWarningOctagon`): `"Sem créditos disponíveis, incluindo a margem extra - contrate agora para evitar a parada"`.
- Clicar leva a `/settings/billing/credits`. Não aparece na própria tela de Créditos. Empilha abaixo da faixa de assinatura.
- Complemento no interceptor (`plugins/axiosConfig.ts`): resposta `402 CreditsExhausted` em ações do usuário (POST/PUT/PATCH/DELETE) mostra toast `"Créditos de IA esgotados. Recarregue para retomar os recursos de IA."`; leituras de fundo falham em silêncio. Só a IA pausa; inbox, canais e métricas seguem.
- Observação: `/settings/billing/credits` exige Administrador no middleware; um Gestor que clicar na faixa é devolvido a `/home`.

### Wall de upgrade de plano (`components/billing/PlanUpgradeWall.vue`, `composables/usePlanGate.ts`, `utils/entitlements.ts`)

- Overlay com blur que cobre o conteúdo (menus continuam clicáveis) quando a rota atual exige uma feature que o plano não libera, ou quando alguma tela chama `promptUpgrade('entities')` (limite de unidades).
- Título: `"{recurso} não está no seu plano"` ou `"Limite de unidades atingido"`. Texto: `"Disponível a partir do plano Scale. Faça upgrade para liberar este recurso."` ou `"Você atingiu o limite de unidades do seu plano. Faça upgrade para cadastrar mais."`. Botão `"Fazer upgrade de plano"` → registra a intenção (`POST /subscription/upgrade-intent`) e vai para `/settings/billing/credits?planos=1`. Rodapé `"Plano atual: {planCode}"`.
- Rótulos dos recursos: `ai.autonomous` "Tino no atendimento", `ai.operations` "Operação do Tino", `copilot.active` "Copilot ativo", `campaigns` "Campanhas", `processes` "Processos e aderência", `tools` "Tools do Tino", `connectors` "Conectores (MCP)", `api` "API e webhooks", `entities` "Mais unidades".
- Rotas gateadas no front: `/campaigns*` e `/settings/campaign-integrations` (campaigns); `/settings/connectors*` (connectors); `/settings/webhooks*` e `/settings/channels/api` (api); `/settings/channel-ai` e `/identity/operations*` (ai.operations); `/identity/processes*` e `/scout/processes*` (processes).
- Só o wall manual (limite de unidades) tem botão X para fechar; o wall de rota só fecha navegando pelo menu.
- Fail-open: se a sessão ainda não tem `entitlements` (sessão antiga), tudo é liberado no front e o backend bloqueia. `403 PlanEntitlementRequired` em ações do usuário gera toast `"Este recurso não está disponível no seu plano. Veja as opções de upgrade."`.

### Widget de onboarding (`components/shared/OnboardingWidget.vue`, `utils/onboardingHelp.ts`)

Flutuante no canto inferior esquerdo, montado em `app.vue` (aparece em todas as telas logadas, exceto `/login`, `/setup`, `/accept-invite`, `/reset-password`, `/setup-password`, `/setup-mfa`, `/setup-organization`). Dados de `GET /onboarding/status` (`dashboard.store`).

- **Quem vê:** todo usuário logado enquanto o onboarding da empresa não estiver concluído (não depende do papel). Os botões de ação (CTA) das etapas Canal/Equipe só aparecem para Administrador (`canCompleteOnboarding = isCompanyAdmin`). Após concluir, o widget só continua visível na sessão em que a conclusão aconteceu (até clicar em `"Iniciar trabalho"`).
- **Pílula minimizada:** anel de progresso com `"{n}%"` e texto `"{índice}. {etapa}"` (ex.: `"1. Identidade da Empresa"`) ou `"Tudo pronto — iniciar trabalho"`. Estado minimizado persistido em `localStorage` (`onboarding-widget-minimized`). Clicar fora do card aberto minimiza.
- **Card expandido:** título `"Preparando sua operação"` e subtítulo `"Configure sua operação em {n} etapas"` (ou `"Operação no ar"` / `"Configuração concluída — hora de atender."`). Lista de etapas numeradas `01`, `02`... com risco ao concluir e animação de check.
- **Etapas** (na ordem; Processos some em planos sem `processes`):
  1. `Identidade da Empresa` (sub-etapas `companyProperty`, `personality`, `operations`; rota `/identity/properties`). Mostra `"{n}%"` enquanto incompleta. Ajuda: `"A Identidade da Empresa é o cérebro da sua IA: tudo o que ela sabe sobre o seu negócio e como deve atender. "` (a expressão "Identidade da Empresa" vira link para `/identity`). Checklist clicável: `Propriedades` com contador `"{x}/3"` (ou `"mínimo 3"` quando atingido) e barra até 10; `Comunicação`, `Diretrizes`, `Conformidade`; e, só com a feature `ai.operations`: `Esclarecimentos`, `Roteamento`, `Disponibilidade`. Não tem CTA (os itens levam à tela correspondente).
  2. `Processos` (feature `processes`; rota `/identity/processes`). Ajuda: `"Processos são a base da inteligência da plataforma: mostram como sua operação funciona de verdade e fazem o motor de IA trabalhar. A partir deles a IA conduz os atendimentos, o gestor recebe insights e a operação ganha feedbacks — inclusive individuais, para cada atendente."` CTA `"Mapear processos"`.
  3. `Canal de Atendimento` (rota `/settings/channels/whatsapp-rookie`). Ajuda: `"Conecte um canal para sua IA começar a receber e responder mensagens com todo o contexto da Identidade da Empresa."` CTA `"Conectar canal"`.
  4. `Equipe` (rota `/settings/company/users`). Ajuda: `"Traga as pessoas da operação para acompanhar as conversas e refinar a IA com o tempo."` CTA `"Convidar equipe"`.
  - Etapa concluída troca o CTA por `"Revisar etapa"`.
- **Bloqueio:** clicar no CTA de Canal/Equipe (ou Processos) com a Identidade incompleta abre o modal **Conclua a Identidade da Empresa** (abaixo).
- **Conclusão:** bloco verde `"Tudo pronto!"` / `"Você concluiu todas as configurações. Tino já está pronto para começar os atendimentos."` e botão `"Iniciar trabalho"` (vai para `/inbox` e dispensa o widget pela sessão).
- **Abertura automática por rota:** `/home` abre com as etapas recolhidas; `/identity*` abre a etapa Identidade; `/identity/processes*` abre Processos; `/settings/channels*` abre Canal; `/settings/company*` abre Equipe. Entrar em `/identity*` também recarrega o status (se um item obrigatório foi apagado, a etapa volta a ficar pendente).
- Troca de unidade/empresa zera o estado do widget e recarrega.

### Modal "Conclua a Identidade da Empresa" (`components/onboarding/OnboardingBlockModal.vue`)

- Cabeçalho escuro com cadeado: `"Conclua a Identidade da Empresa"` / `"Finalize os itens abaixo para avançar para a próxima etapa."`
- Um card por item faltante: rótulo + badge `"{count}/{required}"` + sugestão + botão `"Cadastrar"` (vai para a rota do item). Sugestões exatas: Propriedades `"Cadastre documentos, perguntas e respostas, sites e políticas — pelo menos 3 itens."`; Comunicação `"Defina ao menos 1 estilo de comunicação (tom de voz)."`; Diretrizes `"Adicione ao menos 1 diretriz de comportamento."`; Conformidade `"Adicione ao menos 1 regra de conformidade."`; Esclarecimentos `"Adicione ao menos 1 esclarecimento."`; Roteamento `"Adicione ao menos 1 critério de roteamento."`; Disponibilidade `"Defina ao menos 1 horário de disponibilidade."`.
- Sem pendências: `"Tudo certo na Identidade!"`. Rodapé: `"Entendi"`.

### Avisos de sessão e acesso (`plugins/socket.client.ts`, `plugins/axiosConfig.ts`)

- Sessão encerrada por outro dispositivo (evento `sessionRevoked`): toast amarelo `"Sua sessão foi encerrada em outro dispositivo."`, limpa a sessão e vai para `/login`.
- Papéis alterados por um administrador (evento `permissionsChanged`): a sessão é atualizada sem novo login; toast `"Seus acessos foram atualizados."`.
- Token expirado: o front tenta `POST /auth/refresh` automaticamente; se falhar (400/401/403), faz logout e vai para `/login`.
- `403 MfaSetupRequired` em qualquer chamada: o front tenta um refresh e, se a pendência for real, marca `mfaSetupRequired` e leva a `/setup-mfa`.
- Loading global: ao trocar de área (primeiro segmento da URL), um spinner cobre o conteúdo por ~500 ms (`middleware/loading.global.ts`).
- 404: `error.vue` redireciona para `/home`.

---

## Regras de redirecionamento (middleware `auth.global.ts`)

Avaliadas a cada navegação, nesta ordem:

| Situação | Vai para |
|---|---|
| Rota pública `/waba-setup` | Sempre acessível |
| Visitante (sem sessão) em rota que não é `/login`, `/register`, `/accept-invite`, `/reset-password`, `/external-login` | `/login` |
| Logado tentando abrir uma das rotas de visitante acima (exceto `/external-login?token=...`) | `/home` |
| Logado com `needsPassword` (veio da área de cliente SAN sem senha) fora de `/setup-password` | `/setup-password` |
| Logado, com senha, empresa exige 2FA e ainda não configurou (`mfaSetupRequired`) fora de `/setup-mfa` | `/setup-mfa` |
| Logado, 2FA em dia, tentando abrir `/setup-mfa` | `/home` |
| Logado, com senha, `isFirstLogin` (onboarding inicial não concluído) fora de `/setup`, `/setup-password`, `/setup-organization`, `/setup-mfa` | `/setup` |
| Logado, onboarding inicial concluído, tentando abrir `/setup`, `/setup-password` ou `/setup-organization` | `/home` |
| `/ai-agents`, `/settings/attendants`, `/settings/channels/api`, `/settings/parameters`, `/settings/company`, `/settings/campaign-integrations`, `/settings/connectors`, `/settings/billing/subscription`, `/settings/billing/credits`, `/settings/billing/messaging`, `/settings/webhooks`, `/settings/webhooks/conversation-finished` sem ser Administrador | `/home` |
| `/settings/csat` e tudo em `/identity*` sem ser Administrador ou Gestor da Empresa | `/home` |
| `/settings/conversation-rules`, `/settings/channel-ai`, `/settings/sla` sem nível Área ou acima | `/home` |
| `/settings/company/users` sem `canManageUsers` | `/home` |
| `/settings/channels*` sem ser gestor em algum nível | `/home` |
| `/campaigns/dashboard`, `/metrics/overview`, `/metrics/ai`, `/metrics/service` sem ser gestor em algum nível | `/home` |

Depois disso, se a sessão não tem `entitlements` (plano), eles são buscados em segundo plano (`GET /subscription/entitlements`).

Sequência do primeiro acesso, combinando a ordem acima: senha (`/setup-password`, só quem veio sem senha) → 2FA obrigatório (`/setup-mfa`, só se a empresa exige) → nome da empresa (`/setup`) → estrutura (`/setup-organization`) → `/home`.

---

## Entrar (`/login`)

Arquivos: `pages/login.vue` → `components/auth/AuthContainer.vue` (modo `login`), layout `auth`.

- **Como chegar:** URL direta; qualquer rota protegida sem sessão redireciona para cá; `Sair` no menu do perfil; link `"Entrar"` nas telas de convite/redefinição.
- **Para que serve:** entrar com e-mail e senha (e código de 2FA quando ativo). A mesma tela abriga "Esqueci minha senha" e, no desktop, o painel para criar conta.
- **Quem vê:** visitantes. Usuário logado que abre `/login` é mandado para `/home`.
- **Plano, créditos e bloqueios:** nenhum gate; a resposta do login traz `subscriptionStatus`, `planCode` e `entitlements`, que alimentam as faixas e o wall depois de entrar.
- **O que há na tela:**
  - Card de duas colunas (980px). Coluna do formulário à esquerda; painel com gradiente à direita com o símbolo da marca, título `"Novo por aqui?"`, texto `"Crie sua conta e comece a atender com sua equipe e IA — no mesmo lugar, sem perder o fio."`, botão `"Criar conta"` e rodapé `"TARTINI"`. Abaixo de 768px o painel some e aparece o link inferior `"Não tem uma conta? Criar conta"`.
  - Título `"Entrar"`; subtítulo `"Acesse com suas credenciais para continuar."`.
  - Campo `"E-mail"` (tipo e-mail, placeholder `"voce@empresa.com.br"`, obrigatório).
  - Campo `"Senha"` (placeholder `"Sua senha"`, obrigatório, botão olho para mostrar/ocultar).
  - Link `"Esqueci minha senha"` (à direita, acima do botão).
  - Botão `"Entrar"` (com seta); durante o envio `"Entrando..."`. O botão fica em loading até o redirecionamento terminar.
  - **Etapa 2FA** (mesma rota, aparece quando a senha confere e a conta tem 2FA): botão de voltar (caret, `aria-label="Voltar ao login"`), título `"Autenticação em dois fatores"`, texto `"Digite o código de 6 dígitos do seu app autenticador."`; campo `"Código"` (placeholder `"000000"`, teclado numérico, `autocomplete="one-time-code"`); botão `"Verificar"` / `"Verificando..."`; link `"Usar um código de recuperação"`. Ao alternar: texto `"Digite um dos seus códigos de recuperação. Cada um vale uma única vez."`, campo `"Código de recuperação"` (placeholder `"xxxxx-xxxxx"`), link `"Usar o app autenticador"`.
  - **Esqueci minha senha** (mesma rota): botão de voltar (caret), título `"Recuperar senha"`, texto `"Informe seu e-mail e enviaremos instruções para redefinir sua senha."`, campo `"E-mail"` (placeholder `"voce@empresa.com.br"`, obrigatório), botão `"Enviar instruções"` / `"Enviando..."`. Estado enviado: ícone de check verde, `"E-mail enviado!"`, texto `"Se o e-mail **{e-mail digitado}** estiver cadastrado, você receberá as instruções para redefinir sua senha."`, botão `"Voltar ao login"`.
- **Fluxos:**
  - *Entrar:* `POST /auth/login {login, password}`. Sucesso: grava cookies (usuário, empresa/área/unidade atual, papéis, `isFirstLogin`, `mfaSetupRequired`, assinatura, plano, `sessionId`), entra na sala de socket da sessão e navega: `mfaSetupRequired` → `/setup-mfa`; senão `isFirstLogin` → `/setup`; senão `/home`. Falha (status ≠ 200): toast vermelho com a mensagem do backend ou `"Erro ao tentar logar."`; o formulário permanece preenchido.
  - *Entrar com 2FA:* se o backend responder `mfaRequired`, o token do desafio fica só em memória (recarregar a página volta ao formulário de senha). `POST /auth/login/mfa {mfaToken, code}`. Código errado: toast com a mensagem do backend ou `"Código inválido."` e o usuário pode tentar de novo. Se o backend devolver `error: 'MfaChallengeExpired'` (desafio expirado ou tentativas esgotadas), o front volta para o formulário de senha e limpa o campo de senha. O botão de voltar cancela o desafio e limpa a senha.
  - *Esqueci minha senha:* `POST /auth/forgot-password {email}`; qualquer erro é silenciado e o toast é sempre `"Se o e-mail estiver cadastrado, você receberá as instruções de recuperação."` (não revela se o e-mail existe). O e-mail leva a `/reset-password?token=...`.
- **Regras e limites:** validação nativa do navegador (e-mail válido, campos obrigatórios). Não há bloqueio de tentativas no front. Número de tentativas e validade do desafio de 2FA são do backend.
- **Nomes e termos:** "credenciais" = e-mail + senha; "app autenticador" = aplicativo TOTP (Google Authenticator, Authy, 1Password); "código de recuperação" = código de uso único gerado ao ativar o 2FA.
- **Perguntas prováveis:**
  - *Digitei o e-mail e não recebi nada.* O sistema responde igual para e-mail cadastrado ou não; verifique spam e se o e-mail é o mesmo do cadastro.
  - *Perdi o celular com o app autenticador.* Na etapa do código, clique em `"Usar um código de recuperação"` e use um dos códigos guardados na ativação (cada um vale uma vez).
  - *Depois de entrar caí numa tela de senha/2FA/empresa.* É o fluxo de primeiro acesso ou exigência da empresa (ver tabela de redirecionamento).
- **Incertezas:** validade do desafio de 2FA e número máximo de tentativas (backend). Existem componentes antigos `components/auth/Login.vue`, `ForgotPassword.vue` e `RegisterForm.vue` (com textos como `"Bem-vindo de volta"`, `"seu@email.com"`) que **não** são usados por nenhuma página; os textos válidos são os do `AuthContainer`.

---

## Criar conta (`/register`)

Arquivos: `pages/register.vue` → `AuthContainer.vue` (modo `register`) + `RegisterStepOne.vue`, `RegisterStepTwo.vue`, `RegisterStepThree.vue`, `StepIndicator.vue`.

- **Como chegar:** botão `"Criar conta"` no painel da tela de login (desktop) ou link `"Não tem uma conta? Criar conta"` (mobile); URL direta.
- **Para que serve:** criar uma conta nova (usuário + empresa + estrutura) em três passos e entrar automaticamente.
- **Quem vê:** visitantes. Logado é mandado para `/home`.
- **Plano, créditos e bloqueios:** nenhum no front. O plano da conta criada vem do backend (incerteza: qual plano padrão).
- **O que há na tela:**
  - Título `"Criar conta"` e indicador de passos com rótulos `Dados`, `Organização`, `Resumo` (círculos numerados; concluídos viram check).
  - Painel do desktop (lado esquerdo): `"Bem-vindo de volta!"`, `"Já tem uma conta? Entre com suas credenciais e continue de onde parou."`, botão `"Entrar"`. Mobile: link `"Já tem uma conta? Entrar"` no rodapé.
  - **Passo 1 (Dados):** `"Nome completo"` (placeholder `"Seu nome"`); `"Nome da empresa"` (`"Ex: Minha Empresa LTDA"`); `"E-mail"` (`"voce@empresa.com.br"`); `"Senha"` (`"Mínimo 6 caracteres"`, olho); `"Confirmar senha"` (`"Repita a senha"`, olho). Erros inline (aparecem ao sair do campo ou ao tentar avançar): `"Nome é obrigatório"`, `"Nome da empresa é obrigatório"`, `"E-mail é obrigatório"`, `"E-mail inválido"`, `"Senha é obrigatória"`, `"Mínimo de 6 caracteres"`, `"As senhas não coincidem"`.
  - **Passo 2 (Organização):** três cards: `Simples` / `Uma única unidade`; `Múltiplas unidades` / `Várias lojas ou filiais`; `Áreas e unidades` / `Divisões com unidades`.
    - Múltiplas unidades: cabeçalho `"Suas unidades"` com contador `"{n} adicionada"`/`"{n} adicionadas"`, dica `"Informe o nome de cada loja, filial ou unidade da sua empresa."`, linhas numeradas com placeholder rotativo `"Ex: Loja Centro"`, `"Ex: Filial Shopping"`, `"Ex: Unidade Norte"`, `"Ex: Matriz"`, `"Ex: Loja Sul"`, check verde ao preencher, botão X (title `"Remover unidade"`, só com mais de uma linha), botão `"Adicionar unidade"`.
    - Áreas e unidades: cabeçalho `"Suas áreas"` com `"{n} área"`/`"{n} áreas"`, dica `"Crie as divisões da sua empresa e adicione unidades dentro de cada uma."`; bloco por área com placeholder rotativo `"Ex: Vendas"`, `"Ex: Suporte"`, `"Ex: Administrativo"`, `"Ex: Marketing"`, `"Ex: Operações"`, X `"Remover área"` (só com mais de uma), subtítulo `"Unidades desta área"` com contador `"{preenchidas}/{total}"`, linhas com placeholder `"Nome da unidade"` e X `"Remover unidade"`, botão pequeno `"Unidade"` (adiciona unidade na área) e botão `"Adicionar área"`.
  - **Passo 3 (Resumo):** cards `"Dados pessoais"` (`Nome`, `E-mail`), `"Empresa"` (`Nome da empresa`, `Tipo de organização`: `Simples`, `Múltiplas unidades` ou `Áreas e unidades`), `"Unidades"` (badge com a contagem e etiquetas) ou `"Estrutura"` (badge `"{n} área(s)"`, cada área com suas unidades). Texto legal: `"Ao continuar, você concorda com o nosso Contrato Geral, Termos de Uso e Políticas."` (os dois links apontam para `https://www.saninternet.com/contratos`).
  - Rodapé: `"Voltar"` (a partir do passo 2), `"Próximo"` (desabilitado até o passo ser válido), `"Criar conta"` / `"Criando..."` no passo 3.
- **Fluxos:**
  1. Preencher os dados → `"Próximo"` (só habilita com nome, empresa, e-mail válido, senha ≥ 6 e confirmação igual).
  2. Escolher a estrutura → `"Próximo"`. Regras: Simples sempre válido; Múltiplas unidades exige ao menos uma unidade preenchida; Áreas e unidades exige que **todas** as áreas tenham nome **e** ao menos uma unidade preenchida (linhas vazias são descartadas no envio).
  3. Revisar e `"Criar conta"` → `POST /auth/register {name, companyName, email, password, organizationType, units?|areas?}`. Com 200/201, o front chama o login com o e-mail e a senha informados e segue o fluxo de entrada normal (→ `/setup-mfa`, `/setup` ou `/home` conforme a resposta). Outro status: toast com a mensagem do backend ou `"Erro ao criar conta. Tente novamente."`. Falha de rede: `"Erro ao criar conta. Verifique sua conexão e tente novamente."`.
- **Regras e limites:** senha mínima de 6 caracteres (não há outra regra no front); e-mail validado por expressão regular simples; sem limite de unidades/áreas no formulário (limite de unidades do plano é aplicado depois pelo backend/wall).
- **Nomes e termos:** "Unidade" = loja/filial/local de atendimento; "Área" = divisão/departamento que agrupa unidades; "Simples" = uma única unidade.
- **Perguntas prováveis:**
  - *O botão Próximo não habilita.* Algum campo está inválido (a mensagem aparece em vermelho abaixo do campo ao sair dele).
  - *Posso mudar a estrutura depois?* O código não afirma isso nesta tela (o setup de primeiro acesso diz "Pode alterar depois"; a edição fica em `Configurações > Empresa > Áreas & Unidades`, fora deste inventário).
- **Incertezas:** se a conta criada aqui passa pelo `/setup` (depende de `isFirstLogin` na resposta do backend; como nome e estrutura já foram enviados, provavelmente não). Regras adicionais de senha, unicidade de e-mail e mensagens específicas vêm do backend.

---

## Ativar conta por convite (`/accept-invite?token=...`)

Arquivo: `pages/accept-invite/index.vue`, layout `auth`, service `services/auth.service.ts` (`verifyInviteToken`, `acceptInvite`).

- **Como chegar:** link do e-mail de convite enviado por um gestor/administrador em `Configurações > Empresa > Usuários` (`POST /auth/send-invite`).
- **Para que serve:** o convidado define nome e senha e ativa a conta.
- **Quem vê:** visitantes com token. Se já houver sessão, o middleware manda para `/home` (rota de visitante) e a página não verifica o token.
- **Plano, créditos e bloqueios:** nenhum no front.
- **O que há na tela:**
  - Painel: `"Estamos felizes em tê-lo!"` / `"Ative sua conta e comece a atender com sua equipe e IA — no mesmo lugar, sem perder o fio."`.
  - Título `"Bem-vindo ao time!"`; texto `"Preencha seus dados para ativar sua conta."`.
  - `"Nome"` (placeholder `"Insira o seu nome"`, obrigatório; vem pré-preenchido se o convite trouxer `name`).
  - `"Senha"` (placeholder `"Crie uma senha"`, obrigatório, olho; erro inline `"Mínimo de 6 caracteres"`).
  - `"Confirmar senha"` (placeholder `"Repita a senha"`, obrigatório, olho; erro inline `"As senhas não coincidem"`).
  - Botão `"Ativar conta"` / `"Ativando..."`.
  - Rodapé `"Já tem uma conta? Entrar"` (→ `/login`).
- **Fluxos:**
  1. Ao abrir: sem token → toast `"Token inválido ou expirado."` e vai para `/login`. Com token → `POST /auth/verify-invite {token}`; inválido → toast `"Token de convite inválido ou expirado."` e vai para `/login`; válido → guarda o e-mail do convite e o nome (se vier).
  2. `"Ativar conta"`: validações em toast, nesta ordem: `"Preencha todos os campos."`, `"A senha deve ter no mínimo 6 caracteres."`, `"As senhas não coincidem."`. Depois `POST /auth/accept-invite {name, password, token}` → toast `"Convite aceito com sucesso!"`. Se o e-mail do convite é conhecido, o front faz login automático e vai para `/inbox` (o middleware ainda pode desviar para `/setup-password`, `/setup-mfa` ou `/setup` se a resposta pedir). Se o e-mail não veio na resposta, vai para `/login` para entrar manualmente.
  3. Erros: `"Erro ao aceitar convite. {mensagem do backend}"` seguido de `"Erro ao ativar conta."`.
  - No primeiro acesso ao Inbox, gestores e atendentes (sem papel ADMIN) recebem o tour guiado do Inbox (`composables/useInboxOnboarding.ts`; concluído uma vez por usuário e navegador). Administradores não recebem.
- **Regras e limites:** senha mínima de 6; nome obrigatório. **Expiração:** a tela de Usuários marca o convite como `"Expirado"` 24 horas após `invitedAt` (`CompanyUsersTable.vue`, regra só de exibição); o backend decide a validade real ao verificar o token. Reenvio: `POST /auth/resend-invite` a partir da tela de Usuários.
- **Nomes e termos:** "convite" = e-mail com token; "ativar conta" = criar senha para um usuário pré-cadastrado pelo gestor.
- **Perguntas prováveis:**
  - *O link diz que o token é inválido ou expirado.* Peça ao gestor para reenviar o convite em Configurações > Empresa > Usuários (o front considera expirado após 24 h).
  - *Já tenho conta e cliquei no convite.* Com sessão aberta a página redireciona para `/home`; saia da conta antes de abrir o link.
- **Incertezas:** validade real do token no backend; se o convite pode ser aceito mais de uma vez; se o e-mail pode ser alterado (a tela não mostra o e-mail).

---

## Redefinir senha (`/reset-password?token=...`)

Arquivo: `pages/reset-password/index.vue`, layout `auth`.

- **Como chegar:** link do e-mail de recuperação ("Esqueci minha senha").
- **Para que serve:** definir uma nova senha a partir do token recebido.
- **Quem vê:** visitantes com token válido. Logado é mandado para `/home`.
- **Plano, créditos e bloqueios:** nenhum.
- **O que há na tela:**
  - Link de voltar (caret, `aria-label="Voltar para o login"`).
  - Painel: `"Nova senha"` / `"Escolha uma senha segura para proteger sua conta. Recomendamos usar letras, números e caracteres especiais."`.
  - Título `"Redefinir senha"`; texto `"Digite e confirme sua nova senha para redefinir seu acesso."`.
  - `"Nova senha"` (placeholder `"Mínimo 6 caracteres"`, obrigatório, olho; inline `"Mínimo de 6 caracteres"`).
  - `"Confirme a nova senha"` (placeholder `"Repita a senha"`, obrigatório, olho; inline `"As senhas não coincidem"`).
  - Botão `"Redefinir senha"` / `"Redefinindo..."`.
  - Rodapé `"Lembrou sua senha? Entrar"`.
- **Fluxos:**
  1. Ao abrir: sem token → toast `"Token não encontrado."` → `/login`. Com token → `POST /auth/verify-reset-token`; inválido → toast `"Token inválido ou expirado."` → `/login` (a tela nem renderiza).
  2. Enviar: toasts de validação `"Preencha todos os campos."`, `"A senha deve ter pelo menos 6 caracteres."`, `"As senhas não coincidem."`. Depois `POST /auth/reset-password {token, password}` → toast `"Senha redefinida!"` → `/login`. Erro: `"Erro ao redefinir senha. Token inválido ou expirado."`.
- **Regras e limites:** só o mínimo de 6 caracteres é validado no front; "letras, números e caracteres especiais" é recomendação, não regra.
- **Perguntas prováveis:** *O link expirou.* Peça um novo em `Entrar > Esqueci minha senha`.
- **Incertezas:** validade do token e se o reset encerra as outras sessões (backend).

---

## Autenticando... (`/external-login?token=...`)

Arquivo: `pages/external-login.vue` (sem layout).

- **Como chegar:** link de acesso vindo de fora da plataforma (a tela de senha do primeiro acesso cita a "área de cliente SAN", `https://painel.saninternet.com`).
- **Para que serve:** entrar sem senha usando um token de acesso externo.
- **Quem vê:** qualquer um com o link; funciona mesmo com sessão aberta (a sessão anterior é limpa antes).
- **O que há na tela:** card centralizado com spinner e o texto `"Autenticando..."`.
- **Fluxos:** sem token → `/login`. Com token → `POST /auth/external-login {token}` (o mesmo token não é reenviado na mesma aba, controle por `sessionStorage`). Falha → toast com a mensagem do backend ou `"Token inválido ou expirado."` → `/login`. Sucesso → grava a sessão e navega: `needsPassword` → `/setup-password`; `mfaSetupRequired` → `/setup-mfa`; sem nome de empresa → `/setup`; senão `/home`.
- **Regras e limites:** o token é de uso do backend; o front não o valida.
- **Incertezas:** origem exata do link (SAN/painel do cliente) e validade do token.

---

## Bem-vindo! Crie sua senha (`/setup-password`)

Arquivo: `pages/setup-password.vue`, layout `auth`.

- **Como chegar:** automático. Quem entra por `/external-login` sem senha (`needsPassword`) é preso nesta tela pelo middleware até definir a senha.
- **Para que serve:** criar a senha da conta provisionada externamente (passo 1 de 3 do primeiro acesso).
- **Quem vê:** o usuário com `needsPassword = true` (na prática o dono/administrador provisionado). Quem já tem senha e abre a URL é mandado para `/home` (ou `/setup` se ainda estiver no primeiro acesso).
- **O que há na tela:**
  - Painel: `"Configure sua conta"` / `"Crie uma senha segura para acessar sua conta na plataforma a qualquer momento."`.
  - Título `"Bem-vindo! Crie sua senha"`; texto `"Com uma senha, você pode acessar a plataforma diretamente. Você também pode acessar pela área de cliente SAN"` (link externo `https://painel.saninternet.com`, nova aba, ícone de seta).
  - Indicador de passos 1/3 com rótulos `Senha`, `Empresa`, `Organização`.
  - `"Senha"` (placeholder `"Mínimo 6 caracteres"`, autofoco, olho); `"Confirme a senha"` (placeholder `"Repita a senha"`, olho).
  - Erro inline em vermelho: `"A senha deve ter pelo menos 6 caracteres."` ou `"As senhas não coincidem."`.
  - Botão `"Continuar"` / `"Salvando..."` (desabilitado até os dois campos terem algo).
- **Fluxos:** `"Continuar"` → `POST /auth/setup-password {password}` → `needsPassword = false` → `/setup`. Se a empresa exige 2FA, o middleware intercepta e leva primeiro a `/setup-mfa`. Erro: toast com a mensagem do backend ou `"Erro ao salvar a senha."`.
- **Regras e limites:** mínimo 6 caracteres; não dá para pular (qualquer rota volta para cá). Não há botão de sair nesta tela.
- **Incertezas:** se a senha criada aqui também vale para a área de cliente SAN (o texto sugere que são acessos distintos).

---

## Proteja sua conta (`/setup-mfa`)

Arquivos: `pages/setup-mfa.vue` (layout `auth`) + `components/settings/security/MfaSetupWizard.vue` + `MfaRecoveryCodes.vue`, service `services/mfa.service.ts`.

- **Como chegar:** automático. Quando a empresa exige 2FA e o usuário ainda não configurou, o login (ou o refresh de sessão, ou um `403 MfaSetupRequired`) traz o usuário para cá; nenhuma outra rota abre enquanto isso. Vem depois da senha e antes do onboarding.
- **Para que serve:** ativar o app autenticador obrigatório.
- **Quem vê:** qualquer papel, quando `mfaSetupRequired = true`. Quem já está com 2FA em dia e abre a URL é mandado para `/home`.
- **Plano, créditos e bloqueios:** a sessão fica restrita: o backend responde 403 a tudo fora das rotas de 2FA, e o front nem inicializa notificações/presença/sockets até concluir.
- **O que há na tela:**
  - Painel: `"Autenticação em dois fatores"` / `"Um código do seu celular a cada login. Mesmo que alguém descubra sua senha, não entra sem ele."`.
  - Título `"Proteja sua conta"`; texto `"Sua empresa exige autenticação em dois fatores. Configure um app autenticador para continuar."`.
  - Assistente com indicador de passos `Senha`, `App`, `Recuperação` (detalhado abaixo).
  - Link `"Sair da conta"` (faz logout).
- **Assistente de 2FA (`MfaSetupWizard`, usado aqui e em Segurança):**
  - *Passo 1 (Senha):* texto `"Confirme sua senha para começar."`; campo `"Senha atual"` (autofoco, olho, obrigatório); botão `"Continuar"` / `"Verificando..."`. Chama `POST /auth/mfa/setup {password}`; erro: toast com a mensagem do backend ou `"Erro ao iniciar a configuração."`. (Na variante "trocar app", usada em Segurança, o texto é `"Confirme sua senha e um código do app atual (ou de recuperação). O app atual continua valendo até você confirmar o novo."` e há o campo extra `"Código do app atual ou de recuperação"`, placeholder `"000000"`.)
  - *Passo 2 (App):* texto `"Abra seu app autenticador (Google Authenticator, Authy, 1Password…) e escaneie o código."` (na troca: `"Escaneie o código com o NOVO app autenticador."`); imagem do QR (alt `"QR code para o app autenticador"`); `"Não consegue escanear?"` / `"Digite esta chave manualmente no app:"` com a chave em texto e botão de copiar (`aria-label="Copiar chave"`, vira check por 2 s); campo `"Código de 6 dígitos do app"` (na troca `"Código de 6 dígitos do novo app"`; placeholder `"000000"`, teclado numérico, máximo 7 caracteres); botão `"Ativar"` (na troca `"Confirmar troca"`) / `"Confirmando..."`. Chama `POST /auth/mfa/confirm {code}`; erro: mensagem do backend ou `"Código inválido."`.
  - *Passo 3 (Recuperação):* caixa verde `"Autenticação em dois fatores ativada"` (na troca `"App autenticador trocado"`) com o texto `"Guarde os códigos abaixo em um lugar seguro. Se perder o acesso ao app autenticador, cada um deles entra no lugar do código uma única vez. Eles não serão exibidos novamente."` (na troca, precedido de `"Os códigos de recuperação anteriores deixaram de valer. "`); grade com os códigos; botões `"Copiar"` (vira `"Copiado"`) e `"Baixar .txt"` (arquivo `tartini-codigos-de-recuperacao.txt` com cabeçalho `"Códigos de recuperação — Tartini"` / `"Cada código vale uma única vez."`); checkbox `"Guardei meus códigos de recuperação em um lugar seguro."`; botão `"Concluir"` (só habilita com o checkbox marcado).
- **Fluxos:** ao concluir, a página faz `POST /auth/refresh` para liberar a sessão; então `mfaSetupRequired = false` e navega para `/setup` (se `isFirstLogin`) ou `/home`. Se o refresh falhar: toast `"Não foi possível atualizar a sessão. Entre novamente para continuar."` e logout (a configuração já foi salva; basta entrar de novo, agora informando o código).
- **Regras e limites:** exigência vem da empresa (`requiredByCompany`); enquanto exigido, o 2FA não pode ser desativado em Segurança. Quantidade de códigos de recuperação: definida pelo backend.
- **Nomes e termos:** "2FA"/"autenticação em dois fatores"; "app autenticador"; "chave" = segredo em base32 para digitar manualmente; "códigos de recuperação".
- **Perguntas prováveis:**
  - *Não consigo escanear o QR.* Digite a chave manualmente no app (botão de copiar ao lado).
  - *Fechei sem guardar os códigos.* Eles não são exibidos de novo; gere novos em `Configurações > Pessoal > Segurança > Novos códigos`.
  - *Por que não consigo sair desta tela?* A empresa exige 2FA; conclua a configuração ou use `"Sair da conta"`.
- **Incertezas:** quantidade de códigos e tolerância de tempo do código TOTP (backend).

---

## Como se chama sua empresa? (`/setup`)

Arquivo: `pages/setup.vue`, layout `auth`.

- **Como chegar:** automático no primeiro acesso do dono/administrador (`isFirstLogin = true`), após senha e 2FA. Também via botão `"Voltar"` de `/setup-organization`.
- **Para que serve:** passo 2 de 3: nomear a empresa.
- **Quem vê:** usuário com `isFirstLogin = true` (o dono provisionado). Quem já concluiu é mandado para `/home`.
- **O que há na tela:**
  - Painel: `"Identifique sua empresa"` / `"O nome da sua empresa será usado para identificar sua operação em toda a plataforma."`.
  - Título `"Como se chama sua empresa?"`; texto `"Esse nome vai identificar sua operação na plataforma. Você pode alterar depois."`.
  - Indicador 2/3 (`Senha`, `Empresa`, `Organização`).
  - Campo `"Nome da empresa"` (placeholder `"Ex: Apple"`, autofoco, máximo 100 caracteres; pré-preenchido com o nome atual, se houver).
  - Botão `"Continuar"` / `"Salvando..."` (desabilitado com o campo vazio).
- **Fluxos:** `"Continuar"` → `PUT /onboarding/company-name {name}` → atualiza o nome na sessão → `/setup-organization`. Erro: toast `"Erro ao salvar o nome da empresa."`.
- **Regras e limites:** nome obrigatório, até 100 caracteres, espaços nas pontas removidos. Alteração posterior em `Configurações > Empresa > Informações` (fora deste inventário). Quem entra na Página Inicial ainda sem nome de empresa vê o mesmo formulário lá (ver Página Inicial).
- **Incertezas:** nenhuma relevante.

---

## Como sua empresa é organizada? (`/setup-organization`)

Arquivo: `pages/setup-organization.vue`, layout `auth`.

- **Como chegar:** automático após `/setup`.
- **Para que serve:** passo 3 de 3: definir a estrutura (unidades e áreas) e concluir o primeiro acesso.
- **Quem vê:** usuário com `isFirstLogin = true`.
- **O que há na tela:**
  - Painel (muda com a seleção): padrão `"Estruture seu negócio"` / `"Escolha como sua organização está estruturada para configurarmos tudo da melhor forma."`; Simples `"Operação simples"` / `"Ideal para quem tem uma loja, escritório ou operação centralizada em um único local."`; Múltiplas `"Múltiplas unidades"` / `"Perfeito para empresas com várias filiais ou lojas sob a mesma marca."`; Áreas `"Áreas e unidades"` / `"Para empresas com departamentos ou divisões, cada um com suas próprias unidades."`.
  - Título `"Como sua empresa é organizada?"`; texto `"Isso define como você vai gerenciar atendimentos e equipe. Pode alterar depois."`; indicador 3/3.
  - Cards: `Simples` / `Uma única unidade`; `Múltiplas unidades` / `Várias lojas ou filiais`; `Áreas e unidades` / `Divisões com unidades`.
  - Múltiplas unidades: `"Suas unidades"`, contador `"{n} adicionada(s)"`, linhas numeradas com placeholder `"Unidade 1"`, `"Unidade 2"`... (máx. 100 caracteres), X para remover (só com mais de uma), botão `"Adicionar unidade"`.
  - Áreas e unidades: `"Suas áreas"`, contador `"{n} área(s)"`, bloco por área com placeholder `"Área 1 (ex: Vendas)"` (máx. 100), X para remover (só com mais de uma), linhas de unidade `"Unidade 1"`..., botão pequeno `"Unidade"`, botão `"Adicionar área"`.
  - Rodapé fixo: `"Voltar"` (→ `/setup`) e `"Continuar"` / `"Salvando..."`.
- **Fluxos:** `"Continuar"` habilita quando: Simples selecionado; ou Múltiplas com ao menos uma unidade preenchida; ou Áreas com **ao menos uma** área que tenha nome e uma unidade preenchida (diferente do cadastro público, que exige todas). No envio, áreas sem nome ou sem unidade são descartadas. `POST /onboarding/organization {type, unitNames?|areas?}` → `isFirstLogin = false` → `/home`. Erro: toast `"Erro ao salvar a estrutura organizacional."`.
- **Regras e limites:** nomes até 100 caracteres. O limite de unidades do plano (`entitlements.limits.entities`) não é checado nesta tela (incerteza: se o backend rejeita acima do limite).
- **Nomes e termos:** iguais ao cadastro (Unidade, Área, Simples).
- **Perguntas prováveis:** *Escolhi errado; dá para mudar?* O texto da tela diz que sim ("Pode alterar depois"); a edição fica em `Configurações > Empresa > Áreas & Unidades` (Administrador).
- **Incertezas:** o que o backend cria no caso "Simples" (provavelmente uma unidade com o nome da empresa); comportamento acima do limite de unidades do plano.

---

## Página Inicial (`/home`; `/` renderiza a mesma tela)

Arquivos: `pages/home.vue` e `pages/index.vue` → `components/home/OnboardingHome.vue` (+ `OnboardingPending.vue`, `GestorDashboard.vue`, `AtendenteDashboard.vue`, widgets `DashboardHero`, `MyQueueCards`, `PerformanceCards`, `SatisfactionScoreCard`), `stores/dashboard.store.ts`, `composables/useHomeDashboard.ts`, `useOnboarding.ts`, `useOnboardingProgress.ts`. Layout `default`.

- **Como chegar:** menu `Página Inicial`; logo da sidebar; destino padrão após login/setup; destino de qualquer redirecionamento por falta de permissão e de 404.
- **Para que serve:** enquanto a empresa está sendo configurada, é o checklist de onboarding (Administrador) ou a tela de espera (demais papéis). Depois, é o painel do dia: cockpit da operação para gestores e "minhas conversas" para atendentes.
- **Quem vê:** todos. O que muda:
  - Checklist e formulário de nome da empresa: só Administrador (`canCompleteOnboarding = isCompanyAdmin`).
  - Tela de espera (`OnboardingPending`): qualquer outro papel enquanto o onboarding não está completo.
  - Painel de gestor: quem tem `canAccess('MANAGER')` (Administrador, Gestor da Empresa, de Área ou de Unidade). O backend recorta as unidades acessíveis.
  - Painel de atendente: Atendente.
  - Bloco "créditos de ia" no painel de gestor: `canViewCost = canAccess('MANAGER')` (todo gestor), mas o link `"ver consumo →"` leva a `/settings/billing/credits`, rota de Administrador (gestores não administradores voltam para `/home`).
- **Plano, créditos e bloqueios:** a etapa `Processos` (checklist e widget) só aparece com a feature `processes`; no checklist da Identidade, Esclarecimentos/Roteamento/Disponibilidade só contam com `ai.operations`. O bloco de campanhas do painel só consulta a API com a feature `campaigns`. Faixas de assinatura/créditos e wall aparecem como em qualquer tela.
- **Estados gerais:**
  - Carregando: spinner (`SharedLoading`). O store tenta `GET /onboarding/status` até 5 vezes (esperas de 1 s, 2 s, 4 s, 6 s).
  - Erro: ícone de alerta, `"Não foi possível carregar"`, `"Ocorreu um erro ao buscar os dados. Tente novamente."`, botão `"Tentar novamente"`.
- **O que há na tela (Administrador com onboarding pendente):**
  - Cabeçalho: nome da empresa (ou `"Sua empresa"`) e título `"{primeiro nome}, sua operação está no ar"`.
  - Se a empresa ainda não tem nome: card `"Como se chama sua empresa?"` / `"Esse nome vai identificar sua operação na plataforma. Você pode alterar depois."`, campo com placeholder `"Ex: Loja do Mario"` (máx. 100) e botão `"Salvar"` / `"Salvando..."` (`PUT /onboarding/company-name`; erro `"Erro ao salvar o nome da empresa."`).
  - Bloco `"Preparando sua operação"` com `"{concluídas} de {total}"` e barra de progresso.
  - Lista de etapas (acordeão; a primeira incompleta abre sozinha). Numeração `01`, `02`... recalculada pelo plano:
    1. `Identidade da Empresa`: `"Ensine o Tino sobre o negócio"` / `"Cadastre as propriedades, defina a personalidade e as operações. A partir desses cadastros Tino gera sugestões para você revisar e aceitar."` Botão `"Configurar identidade"` → `/identity/properties`.
    2. `Processos` (feature `processes`): `"A base da inteligência da sua operação"` / `"Processos mostram como sua operação funciona de verdade — e é a partir deles que o motor de IA trabalha. Cada processo mapeado alimenta os atendimentos do Tino, os insights para o gestor e os feedbacks da operação, inclusive individuais para cada atendente. Mapeie ao menos 1 processo para concluir esta fase."` Botão `"Mapear processos"` → `/identity/processes`.
    3. `Canal de atendimento`: `"Conecte um canal e comece a operar"` / `"WhatsApp, chat — conecte e Tino começa a receber e responder mensagens com contexto."` Botão `"Conectar canal"` → `/settings/channels/whatsapp-rookie`.
    4. `Equipe`: `"Traga seu time para a plataforma"` / `"Convide quem faz parte da operação. Mais gente acompanhando e refinando significa evolução mais rápida."` Botão `"Convidar equipe"` → `/settings/company/users`.
  - Badges: `"Pronto"` (etapa concluída; título riscado e botão vira `"Revisar etapa"`) e `"Conclua a Identidade"` (etapa travada). Processos, Canal e Equipe ficam travadas até a Identidade estar 100%; clicar nelas abre o modal **Conclua a Identidade da Empresa**.
  - Critério de "Identidade completa": Propriedades ≥ 3, Comunicação ≥ 1, Diretrizes ≥ 1, Conformidade ≥ 1 e, com `ai.operations`, Esclarecimentos ≥ 1, Roteamento ≥ 1, Disponibilidade ≥ 1 (contadores de `onboarding.identity`). As demais etapas usam os booleanos `processes`, `channel`, `teamMembers` do backend. "Tudo completo" = `onboarding.isComplete` do backend ou todas as etapas visíveis concluídas.
- **O que há na tela (não administrador com onboarding pendente, `OnboardingPending`):** ícone de relógio; título `"{primeiro nome}, sua empresa está sendo configurada"`; texto `"O administrador está finalizando a configuração inicial da plataforma. Assim que estiver pronto, você poderá começar a atender."`; bloco `"Progresso da configuração"` com `"{x} de {y}"` e barra; lista somente leitura das etapas com check nas concluídas.
- **O que há na tela (onboarding completo, gestor: `GestorDashboard`):**
  - Cabeçalho: kicker clicável `"equipe/{escopo} · {data}"` (escopo = nome da unidade filtrada, `"todas as unidades ({n})"` ou o contexto atual), que abre o popover `"unidades ({n})"` com `"Todas as unidades · agregado"` e a lista de unidades (marcador `"atual"`). É um filtro local dos números, não troca o contexto do app. Título `"Bom dia|Boa tarde|Boa noite, {primeiro nome}"` (antes das 12 h, antes das 18 h, depois). Badge `"{n} online"` e botão `"Abrir atendimento →"` (→ `/inbox`).
  - Seção **agora · tempo real** (cockpit escuro): `na fila` (sub `"espera média {n} min"` ou `"sem espera"`; > 5 fica laranja; → `/inbox?filter=AWAITING`), `em andamento` (`"sendo atendidas agora"` / `"nada aberto agora"`; → `/inbox?filter=IN_PROGRESS`), `resolvidas por ia` (`"hoje, sem transferir"` / `"agente sem conversas hoje"`; → `/inbox?filter=FINISHED`), `equipe online` (`"de {n} atendente(s)"` ou `"só você"`).
  - Painel **precisa de você**: lista de alertas com link em minúsculas (`"ver canais →"`, `"ver conversas →"`, `"ver dashboard →"`, `"ver fila →"`). Mensagens: `"{n} de {t} canal está offline"` / `"canais estão offline"`; `"{n} conversa(s) em aberto com SLA estourado — parada há {tempo}"` / `"a mais antiga parada há {tempo}"`; `"Tempo médio de espera acima de 15 min ({n} min)"`; `"{n} clientes aguardando na fila"` (acima de 10). Vazio: `"Tudo em dia ✓"` / `"Nenhuma conversa esperando ação sua. A operação segue no ritmo."` / `"abrir atendimento →"`.
  - Seção **hoje** (`"comparado a ontem até este horário"`): `conversas` (delta `"▲ {x}% vs ontem"` / `"▼ ..."`, só com 5 ou mais em um dos dias; → `/inbox?filter=ALL`), `resolvidas pela ia` (barra de participação; → `/inbox?filter=FINISHED`), `concluídas`, `satisfação` (nota com vírgula ou `"—"`, sub `"{n} resposta(s)"`; → `/scout/satisfaction`).
  - Seção **operação** (`"pico do dia e quem atende"`):
    - Card `"Pico de atendimento"` / `"hoje · conversas por hora"`, total com rótulo `"hoje"`, barras por hora (título ao passar o mouse `"{hh}h · {n} conversa(s) ({x} ia · {y} equipe)"`), legenda `"pico {horas} · {n} conversa(s)[ cada][ · ia | equipe | ia + equipe]"` e link `"ver detalhes por hora →"` (→ `/metrics/service`). Vazio: `"Sem conversas hoje"` / `"O movimento do dia aparece aqui, hora a hora, com o pico de atendimento marcado."`.
    - Card `"Tino em ação"` (badge `"ia/agente"`): barras `ia/agente`, `equipe/atendimento`, `campanhas` com `"{n} · {x}%"`; texto `"Tino resolveu {x}% das conversas de hoje sem precisar da equipe."` ou `"Tino ainda não conduz conversas."` + link `"ativar agente →"` (→ `/settings/channel-ai`). Sem dados: `"Tino ainda não conduz conversas"` / `"Ative o agente para Tino assumir o primeiro atendimento e passar para a equipe quando precisar."` / botão `"Ativar agente ⇄"`. Rodapé (gestor com resumo de uso): `"créditos de ia · {mês}"`, valor + `"créditos"`, link `"ver consumo →"` (→ `/settings/billing/credits`). Cliente só vê créditos, nunca tokens ou dólares.
    - Card `"Equipe hoje"` (badge `"{x} de {y} online"`, link `"ver desempenho →"` → `/metrics/service`): tabela com colunas `atendente`, `status` (`online`/`offline`), `total`, `em andamento`, `concluídas`, `1ª resposta`; clicar na linha (title `"Ver atendimentos de {nome} na central de conversas"`) → `/conversations?attendantId=...`. Vazio: `"Só você por aqui"` / `"Convide a equipe para dividir as filas e acompanhar quem atende o quê em tempo real."` / botão `"Convidar atendentes"` (→ `/settings/company/users`).
  - Erro do painel: `"Não foi possível carregar os dados"` / `"Verifique sua conexão e tente novamente"` / `"Tentar novamente"`.
- **O que há na tela (onboarding completo, atendente: `AtendenteDashboard`):**
  - Cabeçalho (`DashboardHero`): botão de contexto `"{unidade|área|empresa}"` (ou `"Sua operação"`) que abre o modal **Trocar Unidade**; título `"Bom dia|Boa tarde|Boa noite, {primeiro nome}"`; data `"{Dia da semana}, {d} de {Mês}"`; badges `"{n} não lida(s)"` e `"{n} pendente(s)"` (laranja).
  - Seção `"Minhas conversas"`: card de satisfação (`"{nota}/10"` com estrelas e selo `"Excelente"` ≥ 8, `"Bom"` ≥ 7, `"Regular"` ≥ 5, `"Precisa melhorar"`; sem nota `"--"` e `"Sem avaliação"`; subtítulo `"Nota média de avaliação"`), card `"Pendentes"` (`"Aguardando resposta"`, link `"Abrir inbox"`; fundo laranja quando > 0) e card `"Em andamento"` (`"Conversas ativas agora"`, `"Abrir inbox"`). Contagens: conversas do próprio usuário em `AWAITING` e `IN_PROGRESS`.
  - Seção `"Meu desempenho"` (badge `"14 dias"`): `Clientes atendidos`, `Tempo médio` (min), `Primeira resposta` (min), gráfico `"Evolução diária"` ou `"Sem dados de evolução"`.
  - Erro: `"Não foi possível carregar os dados"` / `"Verifique sua conexão e tente novamente"` / `"Tentar novamente"`.
- **Fluxos:** clique nas etapas (acordeão) → botão de ação → tela correspondente; ao voltar, o status é rebuscado no mount. Troca de unidade zera e recarrega tudo. O widget de onboarding flutuante acompanha a mesma origem de dados.
- **Regras e limites:** cumprimentos por hora local; comparativos "vs ontem" só com 5 ou mais ocorrências; anomalias: canal offline, SLA estourado em aberto, espera média > 15 min, fila > 10.
- **Nomes e termos:** "Tino" = agente de IA; "ia/agente" = conversas conduzidas pela IA; "equipe/atendimento" = conduzidas por pessoas; "Identidade da Empresa" = Cérebro (propriedades, personalidade, operações); "Propriedades" = fontes de conhecimento.
- **Perguntas prováveis:**
  - *Sou gestor e a home mostra "sua empresa está sendo configurada".* Só o Administrador conclui o onboarding; a tela de espera aparece para todos os outros papéis até lá.
  - *A etapa Canal está travada.* Complete a Identidade (3 propriedades, 1 comunicação, 1 diretriz, 1 conformidade e, no plano com operações, 1 esclarecimento, 1 roteamento, 1 disponibilidade).
  - *Não vejo a etapa Processos.* Ela só existe em planos com a feature `processes`.
  - *Os números da home consideram qual unidade?* Por padrão todas as unidades acessíveis; o kicker filtra uma unidade sem trocar o contexto.
- **Incertezas:** `components/shared/OnboardingCelebration.vue` (modal `"Etapa concluída!"` / `"Tudo pronto!"` com `"Fazer depois"`, `"Continuar"`, `"Começar a operar"`) existe mas não é montado em nenhum layout ou página; considere não exibido. `QuickActions` é preparado no painel do atendente mas não é renderizado. Os widgets `AnomalyAlerts`, `CampaignsSection`, `ChannelStatusSection`, `MetricsGrid`, `TeamGrid`, `SystemHealthCard`, `QualitativeFeedbackCard`, `HeroMetricCard`, `ConversationBreakdownChart`, `ConversationTrendChart` e `MaturityModal` não são usados (o anel de maturidade do `DashboardHero` só renderiza para `role="gestor"`, e o gestor não usa esse cabeçalho). `components/shared/Header.vue` (faixa "VERSÃO BETA") e `ReportBugButton.vue` (WhatsApp) não são renderizados.

---

## Configurações: Início (`/settings`)

Arquivos: `pages/settings/index.vue`, `layouts/settings.vue`, `components/settings/Sidebar.vue`, `composables/useSettingsMenu.ts`. Incluído aqui só como caminho para as telas pessoais; o detalhamento das demais seções pertence a outras áreas do inventário.

- **Como chegar:** sidebar principal > `Configurações` (ou `Config` no mobile).
- **O que há na tela:** título `"Início"`; legenda `IA` / `Humano` / `Conectado`; cards agrupados por seção com contador (`01`, `02`...). Sidebar secundária `"Configurações"` com `Início` e as seções (acordeão): `Empresa`, `Canais`, `Atendimento`, `Cobrança`, `Análises`, `Integrações`, `Pessoal`. No fim da página, seção `"Conta"` com o card `"Sair da conta"` / `"Encerre sua sessão atual."` (faz logout).
- **Seção `Pessoal` (visível para todos):** `Configurações de usuário` (ícone `PhUser`, `"Gerencie suas informações pessoais."`, `/settings/user`) e `Segurança` (ícone `PhShieldCheck`, `"Autenticação em dois fatores e dispositivos conectados à sua conta."`, `/settings/security`).
- **Quem vê o resto:** seções `Empresa`, `Cobrança`, `Análises`, `Integrações` exigem gestor (`isAdmin = canAccess('MANAGER')`) e seus itens de conta exigem Administrador; `Canais` exige gestor em algum nível; `Usuários` aparece para quem tem `canManageUsers`; `Regras de Conversa`, `IA por canal`, `SLA` exigem nível Área ou acima; `Pesquisa de Satisfação` exige nível Empresa. Itens de feature de plano continuam visíveis e abrem o wall.
- Botão de menu (`SharedSidebarToggleButton`, tooltip `"Abrir menu"` / `"Fechar menu"`) recolhe a sidebar de configurações no desktop.

---

## Configurações de usuário (`/settings/user`)

Arquivos: `pages/settings/user/index.vue` → `components/user/EditUser.vue`; services `users.service.ts` (`getLoggedUser`, `updateWithPassword`); composables `useUnifiedNotifications.ts`, `useSystemNotifications.ts`.

- **Como chegar:** `Configurações > Pessoal > Configurações de usuário`; ou clicar no próprio nome no menu do perfil da sidebar.
- **Para que serve:** editar nome, nome de atendimento e senha; ligar/desligar notificações.
- **Quem vê:** todos os papéis (só os próprios dados).
- **Plano, créditos e bloqueios:** nenhum gate de papel/plano. Em assinatura inativa (modo somente leitura) os campos e o botão ficam desabilitados pela classe global.
- **O que há na tela:**
  - Título `"Configurações de usuário"`; subtítulo `"Gerencie suas informações pessoais."`.
  - Banner com avatar de iniciais (primeira + última), nome (ou `"Usuário"`) e e-mail.
  - Card `"Informações Pessoais"` / `"Atualize seus dados de identificação e como você aparece no sistema."`: campo `"Nome completo *"` (placeholder `"João Silva"`); campo `"Nome de atendimento"` (placeholder `"João"`) com ícone de informação e tooltip `"Esse é o nome que irá aparecer para o cliente como assinatura no momento em que você enviar uma mensagem."`.
  - Card `"Segurança"` / `"Para alterar sua senha, preencha os três campos abaixo. Deixe em branco para manter a senha atual."`: `"Senha atual"` (o asterisco aparece quando algum campo de senha é preenchido), `"Nova senha"` (erro inline `"Mínimo de 6 caracteres"`), `"Confirmar nova senha"` (erro inline `"As senhas não coincidem"`); todos com olho e placeholder `"••••••••"`.
  - Toggles (cards com selo `"Ativo"` / `"Inativo"`), aplicados na hora, sem depender do botão salvar:
    - `"Receber notificações de todas as entidades"` / `"Mesmo atuando em uma entidade, receba avisos de novos atendimentos das demais entidades a que você tem acesso. A alteração é aplicada imediatamente."` (padrão desligado; guardado no navegador).
    - `"Notificações do sistema"` / `"Além do aviso dentro do Tartini, mostre uma notificação do sistema operacional (central de notificações do Windows, banner do macOS) quando chegar mensagem nos seus atendimentos e você não estiver na aba do navegador."` (padrão ligado; guardado no navegador; ligar pede a permissão do navegador).
    - Avisos abaixo dos toggles: `"O navegador está bloqueando as notificações deste site, então elas não aparecerão mesmo com a opção ligada. Libere em Configurações do site → Notificações (no cadeado da barra de endereço) e recarregue a página."` ou `"Este navegador não suporta notificações do sistema."`. Toasts ao ligar: `"O navegador está bloqueando as notificações deste site. Libere nas permissões do navegador."` / `"Este navegador não suporta notificações do sistema."`.
  - Botão `"Salvar Alterações"` / `"Salvando..."`.
- **Fluxos:**
  - *Editar perfil:* alterar nome e/ou nome de atendimento → `"Salvar Alterações"` → `PUT /user/updateWithPassword/{id}` com `name`, `email` (o e-mail atual, não editável na tela), `attendanceName`, `password`, `newPass` → recarrega os dados, atualiza nome e nome de atendimento na sidebar → toast `"Dados atualizados com sucesso!"`.
  - *Trocar senha:* preencher `"Senha atual"`, `"Nova senha"`, `"Confirmar nova senha"` e salvar. Validações (toast amarelo, nesta ordem): `"Nome não pode estar vazio!"`, `"Senha atual é obrigatória para alterar a senha."`, `"A nova senha deve ter no mínimo 6 caracteres."`, `"Nova senha e confirmação não coincidem!"`. Erro do backend (ex.: senha atual errada): toast com a mensagem do backend ou `"Erro ao atualizar com senha."`.
  - *Notificações:* alternar o toggle aplica imediatamente (entra/sai das salas de socket das outras entidades; pede permissão de notificação ao navegador). A permissão é revalidada ao voltar para a aba.
- **Regras e limites:** nome obrigatório; nova senha ≥ 6; e-mail não editável aqui; preferências de notificação são por navegador (`localStorage`), não por conta.
- **Nomes e termos:** "Nome de atendimento" = assinatura exibida ao cliente nas mensagens; "entidades" = unidades.
- **Perguntas prováveis:**
  - *Como troco meu e-mail?* Não há campo para isso nesta tela (incerteza: se um administrador pode alterar em Usuários).
  - *Liguei as notificações do sistema e nada aparece.* O navegador precisa permitir notificações para o site; veja o aviso abaixo do toggle.
  - *As notificações de outras unidades funcionam em outro computador?* Não; a preferência fica no navegador em que foi ligada.
- **Incertezas:** se o backend valida a senha atual quando só o nome é alterado (o front envia `password: ''`); se há upload de avatar (o campo `avatar` existe no tipo, mas a tela não permite alterar).

---

## Segurança (`/settings/security`)

Arquivos: `pages/settings/security/index.vue`, `components/settings/security/MfaCard.vue`, `MfaSetupWizard.vue`, `MfaRecoveryCodes.vue`, `SessionList.vue`, `SessionCard.vue`; services `mfa.service.ts`, `sessions.service.ts`; tipos `types/mfa.ts`, `types/sessions.ts`.

- **Como chegar:** `Configurações > Pessoal > Segurança`.
- **Para que serve:** ativar, trocar ou desativar o 2FA, gerar novos códigos de recuperação e encerrar sessões (dispositivos) da própria conta.
- **Quem vê:** todos os papéis (só a própria conta).
- **Plano, créditos e bloqueios:** nenhum gate de plano. Se a empresa exige 2FA (`requiredByCompany`), o botão `"Desativar"` não aparece. Modo somente leitura desabilita os botões.
- **O que há na tela:**
  - Título `"Segurança"`; subtítulo `"Autenticação em dois fatores e dispositivos conectados à sua conta."`.
  - **Card 2FA:** ícone de escudo (verde e preenchido quando ativo), `"Autenticação em dois fatores"` com selo `"Ativa"` / `"Inativa"`; texto `"Além da senha, um código do seu app autenticador a cada login. Mesmo que alguém descubra sua senha, não entra sem o seu celular."`; quando ativa: `"Ativa desde {d de mmm. de aaaa} · {n} código(s) de recuperação restante(s)"`; quando exigida: `"Sua empresa exige autenticação em dois fatores."`. Botões: inativa → `"Ativar"`; ativa → `"Trocar app"`, `"Novos códigos"` e `"Desativar"` (este só se a empresa não exigir). Falha ao carregar: `"Não foi possível carregar a autenticação em dois fatores."` + `"Tentar novamente"` (toast: mensagem do backend ou `"Erro ao consultar a autenticação em dois fatores."`).
  - **Modal Ativar / Trocar app:** título `"Ativar autenticação em dois fatores"` ou `"Trocar app autenticador"`, botão `"Fechar"`, e o assistente de 3 passos descrito em `/setup-mfa` (na troca, o passo 1 pede também `"Código do app atual ou de recuperação"`).
  - **Modal Desativar:** `"Desativar autenticação em dois fatores"`; `"Sua conta ficará protegida apenas pela senha. Confirme com a senha e um código do app (ou de recuperação)."`; campos `"Senha atual"` e `"Código"` (placeholder `"000000"`); botões `"Cancelar"` e `"Desativar"` / `"Desativando..."`. Sucesso: toast `"Autenticação em dois fatores desativada."`. Erro: mensagem do backend ou `"Erro ao desativar a autenticação em dois fatores."`.
  - **Modal Novos códigos:** `"Novos códigos de recuperação"`; `"Os códigos atuais deixam de valer. Confirme com a senha e um código do app autenticador (ou de recuperação)."`; campos `"Senha atual"` e `"Código"`; botões `"Cancelar"` e `"Gerar"` / `"Gerando..."`. Depois: `"Guarde em um lugar seguro — eles não serão exibidos novamente."`, grade de códigos, `"Copiar"` / `"Copiado"`, `"Baixar .txt"`, botão `"Concluir"`. Erro: mensagem do backend ou `"Erro ao gerar novos códigos."`.
  - **Sessões ativas:** título `"Sessões ativas"`; texto `"Encerre sessões que você não reconhece."`. Carregando: spinner. Vazio: `"Nenhuma sessão ativa encontrada."`. Card verde `"Sessão atual"` com ícone de desktop ou celular, dispositivo (`"{navegador} - {sistema}"`, ou nome/tipo do dispositivo), local (`"{cidade}, {região}, {país}"` ou `"Localização desconhecida"`), `"Última atividade {agora mesmo | há n minuto(s) | há n hora(s) | há n dia(s) | há n mês/meses}"` e `"Criada em {d de mmm. de aaaa, hh:mm}"`. Depois `"Outras sessões ({n})"` com botão `"Encerrar todas"` e um card por sessão com botão `"Encerrar"`. Sem outras: `"Nenhuma outra sessão ativa. Apenas este dispositivo está conectado."`.
  - **Modal Encerrar sessão:** `"Encerrar sessão"`; `"Tem certeza que deseja encerrar esta sessão? O dispositivo será desconectado imediatamente."`; `"Cancelar"` / `"Encerrar"`.
  - **Modal Encerrar todas:** `"Encerrar todas as outras sessões"`; `"Tem certeza que deseja encerrar todas as outras sessões? Você permanecerá conectado apenas neste dispositivo."`; `"Cancelar"` / `"Encerrar todas"`.
- **Fluxos:**
  - *Ativar 2FA:* `"Ativar"` → senha → QR/código → códigos de recuperação → checkbox → `"Concluir"` → o card recarrega (`GET /auth/mfa`) e mostra `"Ativa"`. A partir daí, o login pede o código (ver `/login`).
  - *Trocar app:* `"Trocar app"` → senha + código do app atual (ou de recuperação) → QR no novo app → `"Confirmar troca"` → novos códigos de recuperação (os antigos deixam de valer). O app antigo continua válido até a confirmação.
  - *Desativar:* `"Desativar"` → senha + código → `POST /auth/mfa/disable`. Indisponível quando a empresa exige.
  - *Novos códigos:* `"Novos códigos"` → senha + código → `POST /auth/mfa/recovery-codes` → códigos novos (invalida os anteriores).
  - *Encerrar uma sessão:* `"Encerrar"` no card → confirmar → `DELETE /auth/sessions/{id}` → toast `"Sessão encerrada com sucesso!"` → lista recarregada. No outro dispositivo, o socket recebe `sessionRevoked` e mostra `"Sua sessão foi encerrada em outro dispositivo."` antes de ir para `/login`.
  - *Encerrar todas as outras:* `"Encerrar todas"` → confirmar → `DELETE /auth/sessions` → toast `"Todas as outras sessões foram encerradas."`.
  - *Sair desta sessão (logout):* menu do perfil > `Sair`, ou `Configurações > Conta > Sair da conta`, ou `"Sair da conta"` em `/setup-mfa`. O front chama `POST /auth/logout` (ignora falha), apaga todos os cookies de sessão, limpa caches, rascunhos e assinaturas salvos no navegador, sai das salas de socket e vai para `/login`. Toasts de erro ficam silenciados por 1 s durante o encerramento.
  - Erros de sessões: `"Erro ao buscar sessões."`, `"Erro ao encerrar sessão."`, `"Erro ao encerrar sessões."` (ou a mensagem do backend).
- **Regras e limites:** a sessão atual não tem botão de encerrar (use `Sair`). Tipos de dispositivo: `WEB`, `MOBILE`, `DESKTOP` (só `MOBILE` muda o ícone). O endereço IP existe no dado, mas não é exibido.
- **Nomes e termos:** "sessão" = login ativo em um navegador/dispositivo; "sessão atual" = este navegador; "app autenticador"; "códigos de recuperação".
- **Perguntas prováveis:**
  - *Não aparece o botão Desativar.* A empresa exige 2FA (`"Sua empresa exige autenticação em dois fatores."`).
  - *Vejo uma sessão que não reconheço.* Clique em `"Encerrar"` naquela sessão (ou `"Encerrar todas"`) e troque a senha em Configurações de usuário.
  - *Quantos códigos de recuperação tenho?* O card mostra `"{n} códigos de recuperação restantes"`.
- **Incertezas:** duração da sessão e do refresh token; se encerrar sessões também invalida tokens de API; quantidade de códigos de recuperação gerados.

---

## Glossário transversal

- **Empresa > Área > Unidade:** hierarquia de acesso. "Classe" no código = Área. "Entidade" = Unidade.
- **Papéis:** Administrador (ADMIN na Empresa), Gestor da Empresa, Gestor de Área, Gestor de Unidade, Atendente. Dono da conta = quem responde pela assinatura (`isSubscriptionAdmin`).
- **Primeiro acesso / onboarding inicial:** `isFirstLogin` (senha, nome da empresa, estrutura). **Onboarding da operação:** checklist da Página Inicial/widget (Identidade, Processos, Canal, Equipe).
- **Tino:** o agente de IA. **Cérebro / Identidade da Empresa:** base de conhecimento, personalidade e operações.
- **Plano / entitlements:** features liberadas (`campaigns`, `processes`, `ai.operations`, `api`, `connectors`...). **Créditos:** franquia mensal de IA; `BURST` = usando a margem extra; `BLOCKED` = IA pausada.
- **Modo somente leitura:** assinatura fora de `ACTIVE`/`COMPLETED`.

---

## Incertezas consolidadas

1. Backend: validade de tokens (convite, reset, external-login), regras de senha além de 6 caracteres, limite de tentativas e validade do desafio de 2FA, quantidade de códigos de recuperação, duração de sessão.
2. Expiração de convite: o front rotula `"Expirado"` após 24 h de `invitedAt`; a regra real de aceite é do backend.
3. Fluxo pós-cadastro público: se `/auth/register` devolve `isFirstLogin` (levando a `/setup`) ou vai direto a `/home`.
4. O que o backend cria na estrutura "Simples" e o que acontece se a estrutura ultrapassar o limite de unidades do plano.
5. Componentes presentes mas não renderizados: `OnboardingCelebration.vue`, `Header.vue` (faixa "VERSÃO BETA"), `ReportBugButton.vue`, `Login.vue`, `ForgotPassword.vue`, `RegisterForm.vue`, `QuickActions` na home do atendente e vários widgets de `components/home/widgets`. Se alguma central antiga citar "Bem-vindo de volta" ou "seu@email.com", é texto desses componentes legados.
6. Links com gate: `"ver consumo →"` (home do gestor) e a faixa de créditos levam a `/settings/billing/credits`, rota só de Administrador; gestores não administradores são devolvidos a `/home`.
7. Impersonação (`impersonation` na resposta de login) não tem nenhuma UI no front.
8. Alteração de e-mail e de avatar do próprio usuário: não há campo nas telas pessoais.
