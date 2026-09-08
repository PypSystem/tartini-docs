# Inventário de telas — Inbox, conversas e contatos

Fonte: clone `tartini-web` (main de 03/09/2026), somente leitura do front (Nuxt 3 + Vue 3). Tudo o que o backend faz (recortes de escopo, regras de envio, encerramento) só é descrito quando o front deixa isso explícito em comentários ou contratos; o resto está em **Incertezas**.

## Como ler este inventário

- **Papéis** (rótulos do produto em `utils/roleLabel.ts`): Dono da conta (`isSubscriptionAdmin`), Admin da Empresa (`ADMIN` na Empresa, rótulo "Administrador"), Gestor da Empresa (`MANAGER` na Empresa), Gestor de Área (`MANAGER` na Área), Gestor de Unidade (`MANAGER` na Unidade), Atendente (`ATTENDANT` na Unidade). Um papel num nó cobre tudo abaixo dele (herança). `SYSTEM_ADMIN` (suporte da plataforma) passa em todo gate do front e fica fora deste inventário.
- **Nomes de IA usados na interface**: **Tino** é o agente que fala com o cliente (linha de frente); **Copilot** é o assistente privado do atendente (só ele enxerga); **Scout** é o agente que avalia conversas encerradas (resumo e nota). Glossário em `utils/glossary.ts`.
- **Dono da conversa (`owner`)**: `PASSIVE_ATTENDANT` (Tino atendendo de forma passiva), `CAMPAIGN` (Tino conduzindo uma campanha) ou `ATTENDANT` (humano).
- **Status da conversa**: `AWAITING`, `IN_PROGRESS`, `AWAITING_CSAT`, `FINISHED`, `IMPORTED` (significado por tela mais abaixo).
- **Canais**: `ROOKIE` = WhatsApp via QR Code/pareamento (Whatsmeow), `WABA` = WhatsApp Business API oficial da Meta, `CHAT_WIDGET` = chat embutido no site.
- Textos entre aspas são transcrições exatas do código. Rotas entre crases.

## Mapa rápido de rotas desta área

| Rota | Título na tela | Layout |
|---|---|---|
| `/inbox` | "Inbox" (cabeçalho da coluna de navegação) | `messages` |
| `/inbox/:id` | Conversa aberta (nome do contato no cabeçalho) | `messages` |
| `/inbox/visitors` | "Visitantes online" | `messages` |
| `/inbox/contacts` | "Contatos" | `messages` |
| `/inbox/contacts/:contactId` | Ficha do contato (nome do contato como título) | `messages` |
| `/conversations/overview` | "Panorama" (Central de Conversas) | `conversations` |
| `/conversations` | "Central de conversas" | `conversations` |
| `/redirect/inbox/...` | (tela de carregamento) | próprio |
| `/settings/quick-replies` | "Mensagens Rápidas" | `settings` |

## Navegação até a área

**Menu principal** (`components/shared/Sidebar.vue`, fixado ou expandido no hover): "Página Inicial", "Inbox", "Métricas" (só gestor+), "Central de Conversas" (todos), "Cérebro" (só Admin/Gestor da Empresa), "Scout", "Campanhas" (gestor+ e feature `campaigns`); rodapé: "Configurações", "Feedback", perfil (menu com "Unidade", "Página de Status", "Documentação", "Políticas e Termos", "Sair"). O item "Inbox" mostra um badge com o total de não lidas (colapsado: "9+" acima de 9). No topo da sidebar expandida, o botão da unidade atual (tooltip "Trocar classe/unidade") abre o modal "Trocar Unidade" ("Selecione a unidade que deseja acessar"; vazio: "Nenhuma unidade encontrada" / "Você não possui acesso a outras unidades"); o badge preto nesse botão (tooltip "Novos atendimentos em outras unidades") só aparece com a preferência "Receber notificações de todas as entidades" ligada.

**Mobile** (`components/inbox/MobileMenu.vue`, abaixo de 1024px): barra inferior com "Início", "Inbox" (badge de não lidas, "9+"), "Unidade" (abre "Selecionar Entidade"; trocar leva para `/home`) e "Config". A barra some dentro de uma conversa (`/inbox/:id`).

Faixas fixas no topo em todos os layouts desta área: "Sua assinatura não está ativa. Acesso em modo somente leitura." (assinatura inativa: botões, inputs e textareas ficam desabilitados globalmente) e o aviso de créditos: "Créditos do mês esgotados - contrate mais para evitar interrupções" (amarelo, ainda na margem extra) ou "Sem créditos disponíveis, incluindo a margem extra - contrate agora para evitar a parada" (vermelho, IA parada); clicar leva a `/settings/billing/credits`. Ver "Regras transversais" no fim.

---

## Inbox (`/inbox`)

- **Como chegar:** menu principal > "Inbox". No mobile, barra inferior > "Inbox".
- **Para que serve:** é a caixa de atendimento: lista as conversas de WhatsApp e do Chat Widget da(s) unidade(s) do usuário, com filtros, e abre cada conversa ao lado. Na primeira visita, atendentes e gestores recebem um tour guiado.
- **Quem vê:** qualquer usuário logado (a rota não tem gate de papel em `middleware/auth.global.ts`). O recorte das conversas é do backend: Dono/Admin/Gestor da Empresa veem a empresa toda; Gestor de Área/Unidade e Atendente veem só o escopo deles (`docs/visibilidade-por-papel.md`, linha "Página Inicial / Inbox"). O que muda por papel no front:
  - Chips de unidade ("Todas as unidades" + uma por unidade) só aparecem para quem tem acesso a 2+ unidades: `isCompanyAdmin`, ou 2+ unidades em `/chat/accessible-channels`, ou 2+ vínculos de unidade.
  - A seção "Agentes de IA" do menu só aparece se o plano tem a feature `ai.autonomous`.
  - O filtro "Filtrar por tags" só aparece se o plano tem `campaigns` (tags vivem no módulo de campanhas) e se há tags em uso.
  - O tour de onboarding só aparece para quem tem papel `MANAGER` ou `ATTENDANT` em algum nível e NÃO tem `ADMIN` em lugar nenhum (o Admin da conta nunca recebe), nem é `SYSTEM_ADMIN`, nem está no primeiro login.
- **Plano, créditos e bloqueios:** feature `ai.autonomous` (seção "Agentes de IA"; um deep link `?aiSubFilter=` é neutralizado sem ela); feature `campaigns` (tags); Copilot por usuário (ver conversa aberta). Assinatura inativa bloqueia botões e inputs.
- **O que há na tela (desktop, `components/inbox/Sidebar.vue` + `Placeholder.vue`):**
  - **Coluna de navegação** (título "Inbox", colapsável pelo botão com tooltip "Abrir menu"/"Fechar menu"; recolhe sozinha em telas estreitas quando há conversa aberta):
    - Itens: "Tudo" (todas as conversas, `filter=ALL`), "Sua caixa" (só conversas em que o usuário logado é o atendente, `myInbox=true`), "Não atribuído" (conversas sem atendente, `unassigned=true`), "Contatos" (vai para `/inbox/contacts`).
    - Seção "Agentes de IA" (accordion, só com `ai.autonomous`): "Todas as conversas", "Finalizadas", "Transferidas", "Abandonadas" (conversas conduzidas pela IA; `aiSubFilter=all|finished|transferred|abandoned`). Com um deles ativo, as abas de status somem e aparece a faixa "Filtrando: {nome do item}".
    - Seção "Canais" (accordion): "WhatsApp" (`ROOKIE` e `WABA`), "Chat Widget" (`CHAT_WIDGET`).
    - "Visitantes online" com contador verde de visitantes navegando agora (vai para `/inbox/visitors`).
  - **Coluna da lista** (largura fixa de 320px):
    - Cabeçalho: botão de recolher/abrir a navegação, nome do usuário logado, botão "+" (tooltip "Nova conversa") que abre o modal "Iniciar conversa".
    - Chips de unidade (multiunidade): "Todas as unidades" com total de não lidas e um chip por unidade com ponto colorido e contagem; com uma unidade selecionada aparece a faixa "Filtrando **{unidade}** · N não lidas" com "Limpar".
    - Busca: placeholder "Buscar por nome, telefone ou protocolo..." (parâmetro `search`, busca no backend; ao vivo, o front confere só o nome).
    - Abas de status: "Todos" (`ALL`), "Aguardando" (`AWAITING`), "Andamento" (`IN_PROGRESS`), "Finalizados" (`FINISHED`).
    - "Filtrar por tags" (badge com a quantidade selecionada; expandido mostra chips com "(N)" contatos por tag; recolhido mostra as tags ativas e "Limpar" quando há mais de uma).
    - `components/inbox/Filters.vue`: "Filtrar por atendentes" (caixas de seleção com ponto de presença: "Online", "Ausente", "Offline"; a lista vem de `/user/attendants`: atendentes ativos mais gestores/donos que já atenderam, agregada pelas unidades do chip) e "Filtrar por setor" (opção "Todos" + um setor por vez); "Limpar filtros". Os filtros viajam na URL (`attendant`, `sectorId`, `tags`, `filter`, `channel`, `myInbox`, `unassigned`, `aiSubFilter`, `search`).
    - Faixa vermelha de SLA quando há estouros: "N conversa com SLA excedido" / "N conversas com SLA excedido" (tooltip "Conversas com SLA excedido").
    - Lista agrupada em "Fixados", "Hoje", "Ontem", "Anteriores". No primeiro grupo há o botão de ordenação "Urgência" ou "Recentes" (tooltips: "Ordenação por urgência (quem espera há mais tempo no topo). Clique para ordenar pelas mais recentes." / "Ordenação pelas mensagens mais recentes (estilo WhatsApp). Clique para ordenar por urgência."). A preferência fica no navegador (`localStorage`).
    - Paginação por rolagem infinita (50 por página). Carregando: "Carregando conversas...". Vazio: "Nenhuma conversa".
  - **Linha da conversa** (`components/inbox/Chat.vue`):
    - Avatar com selo: iniciais do atendente (tooltip com o nome) ou selo de IA (tooltip "Tino conversando") enquanto a conversa não está finalizada.
    - Nome (até ~10 caracteres; sem nome mostra o telefone formatado; contatos `@lid` sem nome aparecem como "Contato sem nome"), ícone do canal (tooltip "WhatsApp" ou "Chat Widget"), selo da unidade (multiunidade), até 2 tags (+ "+N"), chip de setor (tooltip "Setor: {nome}").
    - Horário da última mensagem (hoje: HH:MM; "Ontem"; ou dd/mm/aaaa; sem data: "Desconhecido"), ícone de fixado (tooltip "Contato fixado"), ícone de spam (tooltip "Contato SPAM").
    - Prévia: "Rascunho: {texto}" se houver rascunho não enviado; senão "Foto", "Documento", "Áudio", "Reação", "Figurinha", "Mensagem editada" ou o texto (sem formatação do WhatsApp).
    - Badges à direita: relógio de SLA "mm:ss" (tooltips "SLA dentro do limite (limite N min)", "SLA em alerta (limite N min)", "SLA excedido (limite N min)", "SLA crítico (limite N min)", "SLA pausado — fora do horário comercial (limite N min)"; borda esquerda amarela em alerta e vermelha em estouro/crítico; grupos não mostram SLA); chip "Campanha" (tooltip `Conduzida pela campanha "{título}"` ou "Conversa conduzida por campanha (IA)"); chip de pendência com o nome do atendente (tooltip "Transferida para: {nome}" ou "Atendente: {nome}") ou "Pendente" (tooltip "Pendente de atendimento!"); chip "Finalizada" (tooltip "Conversa finalizada pelo atendente"); bolinha verde com o número de não lidas.
    - Menu "Mais opções" (três pontos ao passar o mouse): "Fixar"/"Desfixar" e "Marcar como spam"/"Desmarcar como spam".
  - **Painel direito sem conversa** (`Placeholder.vue`): "Nenhuma conversa selecionada" + "Escolha uma conversa na listagem para começar a enviar mensagens". Sem canal conectado e sem conversas: "Conecte-se com os clientes em todos os canais", "Administre as conversas em uma única inbox e configure seus canais para prestar o melhor suporte ao cliente." e botão "Configurar canais" (vai para `/settings/channels/whatsapp-rookie`).
- **O que há na tela (mobile, `components/inbox/SidebarMobile.vue`):** toggle "IA" (tooltip "Ver conversas dos Agentes de IA", só com `ai.autonomous`), botões redondos: globo (tooltip "Visitantes navegando no site", com contador), pessoas (tooltip "Contatos e fichas", vai a `/inbox/contacts`), "+" (tooltip "Iniciar conversa com contatos salvos", abre o modal "Iniciar conversa" da agenda), funil (tooltip "Exibir filtros", com contador de filtros ativos), busca com placeholder "Buscar", chips de unidade, abas "Todos", "Aguardando", "Andamento", "Finalizado". Vazio: "Não há conversas com os filtros aplicados.". Dentro da view de visitantes há o botão "Conversas" para voltar.
- **Fluxos:**
  - *Abrir uma conversa:* clicar na linha leva a `/inbox/{id}` mantendo os filtros na URL.
  - *Filtrar:* escolher aba, item do menu, chip de unidade, tags, atendentes ou setor; tudo recarrega a lista do servidor. "Limpar filtros" zera atendente e setor; "Limpar" zera tags ou a unidade.
  - *Buscar:* digitar na busca (nome, telefone ou protocolo).
  - *Ordenar:* clicar em "Urgência"/"Recentes".
  - *Fixar/spam:* menu de três pontos na linha. Fixados sobem para o grupo "Fixados".
  - *Iniciar conversa com número novo:* "+" > modal "Iniciar conversa" (abaixo).
  - *Tour de onboarding:* aparece sozinho na primeira visita (passos abaixo); "Pular" pausa e deixa o widget flutuante "Retomar o tour do Inbox" / "Continue de onde parou" (com "x" para "Dispensar" de vez); "Voltar", "Próximo", "Concluir".
- **Regras e limites:**
  - Ordem por "Urgência": conversas sem `conversation` por último; `IMPORTED` por último; dia mais recente primeiro; dentro do dia, finalizadas por último; transferidas pela IA ou interrompidas primeiro; `AWAITING` antes de `IN_PROGRESS`; cliente aguardando resposta (última mensagem recebida) primeiro, quem espera há mais tempo no topo; o resto pela mensagem mais recente. "Recentes" ordena só pela última mensagem.
  - Em qualquer "visão de fila" (aba diferente de "Todos", setor, "Agentes de IA", "Não atribuído", "Sua caixa") as conversas de **grupo** do WhatsApp são excluídas (grupo é só container de histórico).
  - A lista atualiza em tempo real (socket `chatsUpdate`); ao reconectar, o front reconcilia sem recarregar a página.
  - Sem a feature `campaigns`, tags não são buscadas (evita erro "fora do plano").
- **Nomes e termos:** "Sua caixa" = conversas atribuídas a mim; "Não atribuído" = sem atendente; "Pendente" = conversa sob comando humano aguardando atendimento; "Finalizada" (chip) = encerrada por um atendente; "Fixados" = contatos fixados no topo; "Urgência"/"Recentes" = modos de ordenação; "Protocolo" = os 8 primeiros caracteres do id da conversa.
- **Tour "Bem-vindo ao Inbox"** (`pages/inbox/index.vue`, `components/onboarding/InboxTour.vue`), passos (título: texto):
  - "Bem-vindo ao Inbox": "Aqui é onde você atende os clientes. Vamos dar uma volta rápida pelas principais áreas. Leva menos de um minuto."
  - "Barra de navegação": "Na barra em destaque, você encontra as principais opções para visualização do histórico de conversas."
  - "Busca": "Encontre qualquer conversa buscando pelo nome ou telefone do contato."
  - "Filtros": "Filtre a lista pelo status da conversa: Todos, Aguardando, Andamento ou Finalizados."
  - "Uma conversa de exemplo": "Abrimos uma conversa de exemplo para você conhecer a tela de atendimento." (abre um chat simulado com "Cliente Exemplo"; nada é enviado ao servidor)
  - "Cabeçalho da conversa": "No topo você vê o contato e as ações da conversa: transferir o atendimento para outro atendente ou setor e encerrar a conversa."
  - "Campo de mensagem": "Aqui você escreve a resposta para o cliente. Nesta mesma barra também dá para adicionar emojis, anexar fotos e arquivos, gravar um áudio e enviar a mensagem."
  - "Assinatura da mensagem": "Ative \"Assinar como\" para que a mensagem enviada mostre quem respondeu. Assim a equipe sabe quem atendeu o cliente."
  - "Excluir mensagem": "Passe o mouse sobre uma mensagem enviada para abrir o menu de ações, onde é possível responder, editar ou excluir."
  - "Detalhes da conversa": "Neste painel você acompanha os dados do contato e da conversa, como nome, telefone, canal e status do atendimento."
  - "Copilot" (só se o usuário tem acesso ao Copilot): "Esta é a aba Copilot, seu assistente de IA durante o atendimento. Use o chat abaixo para conversar com ele: peça ajuda para responder o cliente, tirar dúvidas ou resumir a conversa. Ele responde com base na sua base de conhecimento."
  - "Tudo pronto": "Você já conhece o essencial do Inbox. Pode começar a atender. Bom trabalho!"
  - Rodapé "Passo N de M"; botões "Pular", "Voltar", "Próximo", "Concluir". Conclusão gravada por usuário no navegador (não reaparece no mesmo dispositivo).
- **Perguntas prováveis:**
  - "Por que não vejo a seção Agentes de IA?" Plano sem `ai.autonomous`.
  - "Por que não aparecem os chips de unidade?" Só quem acessa 2+ unidades os vê.
  - "A lista voltou ao topo sozinha?" Não deveria: reconexões e ações fazem reconciliação silenciosa; trocar aba/filtro/unidade recarrega.
  - "Onde estão as conversas de grupo?" Só em "Tudo"/"Todos" sem outros filtros de fila.
  - "Como recebo alertas?" Ver "Regras transversais: notificações".
- **Incertezas:** o recorte exato por papel (o que um Gestor de Unidade ou Atendente enxerga na lista) é feito no backend e não está no front; o significado exato de "Abandonadas" (`aiSubFilter=abandoned`) é do backend; a busca por "protocolo" depende do backend.

## Modal "Iniciar conversa" (número novo) — `components/inbox/NewContact.vue`

- **Como chegar:** Inbox > botão "+" (tooltip "Nova conversa") no cabeçalho da lista (desktop); também pelo botão "Conversar" de um cartão de contato compartilhado dentro de uma mensagem.
- **Para que serve:** enviar a primeira mensagem para um número que ainda não conversou, pelo WhatsApp conectado da unidade.
- **Quem vê:** todos; o seletor "Enviar pela unidade" só aparece quando há 2+ unidades com canal WhatsApp (gestor+ por herança ou 2+ vínculos).
- **O que há na tela:** kicker "equipe/inbox · nova conversa"; título "Iniciar conversa"; "A mensagem sai pelo WhatsApp conectado da unidade."; campo "Enviar pela unidade" (opções "{unidade} — {número}" ou "sem número"; dica "O contato vê o número dessa unidade."); "Número de telefone" (seletor de país com bandeira + máscara; placeholder é o exemplo do país); para canal `WABA`: aviso "Este é um número de **WhatsApp oficial**. Para falar com quem ainda não escreveu para você, a Meta exige uma mensagem de template aprovada.", "Carregando templates…", ou "Nenhum template aprovado neste canal. Crie um em **Configurações › Canais › Templates** e aguarde a aprovação da Meta.", campo "Template" ("Selecione um template"), "Variáveis" (placeholder "Valor de {nome}" ou "Valor do link do botão"; dica "Todas precisam ser preenchidas — a Meta recusa o envio incompleto."), "Prévia" ("É exatamente isso que o contato vai receber."); para canal não oficial: "Primeira mensagem" (placeholder "Digite a mensagem inicial", dica "Depois de enviar, você vai direto para a conversa."), bloco "Assinar mensagem" ("Prefixa seu nome, igual ao envio em conversas existentes."), "Nome na assinatura" (quando a empresa permite trocar), prévia "Sai como **{Nome}:** {mensagem}". Rodapé: "Cancelar", "Enviar"/"Enviando…". Esc fecha.
- **Fluxos:** informar número > (WABA) escolher template e preencher variáveis / (não oficial) escrever a mensagem e opcionalmente assinar > "Enviar" > o front confere o número (`/chat/check-number`), envia e abre `/inbox/{id}` da conversa criada (se não vier id, recarrega a página e abre o chat pelo número).
- **Regras e limites:** erros mostrados no próprio modal: "Número incompleto para {país}. São {N ou M} dígitos depois de +{DDI}.", "Escolha um template para iniciar a conversa.", "Preencha todas as variáveis do template.", "Digite a primeira mensagem.", "Este número não foi encontrado no WhatsApp. Confira e tente novamente." (+ " Se for celular, confirme o dígito 9 depois do DDD." no BR, " Celulares argentinos precisam do 9 depois do +54." na AR), "Erro ao iniciar conversa. Verifique o número e tente novamente.". Template não recebe assinatura. O código alerta que enviar para número desconhecido pelo canal não oficial pode levar a banimento do número.
- **Incertezas:** a lista de países aceitos está em `utils/countries.ts` (não lida em detalhe); a existência do número só é verificável em canal `ROOKIE`.

## Modal "Iniciar conversa" (agenda do WhatsApp, mobile) — `components/inbox/ContactList.vue`

- **Como chegar:** Inbox mobile > botão "+" (tooltip "Iniciar conversa com contatos salvos").
- **O que há na tela:** título "Iniciar conversa", "Selecione um contato da lista para começar a conversar", busca "Buscar por nome ou telefone", botão de sincronizar (tooltip "Caso não tenha um contato específico, salve ele no seu WhatsApp e clique aqui para sincronizar novamente."), lista de contatos (grupos e `@lid` são omitidos), "Carregando contatos...".
- **Fluxos:** clicar num contato abre `/inbox/{id}`; sincronizar chama `/contact/materialize-wa` e recarrega (erro: "Erro ao sincronizar contatos.").

---

## Conversa aberta (`/inbox/:id`)

- **Como chegar:** Inbox > clicar numa conversa. Também por link direto (`{origem}/inbox/{contactId}`, copiado em "Compartilhar"), pela notificação, pela Central ("abrir no inbox →") ou pela ficha ("Abrir conversa").
- **Para que serve:** atender: ler o histórico, responder (texto, mídia, áudio), assumir uma conversa do Tino, transferir, finalizar e consultar detalhes e Copilot.
- **Quem vê:** qualquer usuário logado com acesso à conversa (recorte do backend). Diferenças por papel no front: recibo de leitura só é enviado se o usuário é `ATTENDANT`+ por herança (e não `SYSTEM_ADMIN`) ou é o atendente atribuído; "Abrir campanha" só para gestor+; o Copilot depende de permissão por usuário (abaixo).
- **Plano, créditos e bloqueios:**
  - **Copilot (acesso):** `GET /copilot/access/me`; é liberado por usuário em Configurações > Empresa > "Usuários" (toggle "Acesso" na coluna Copilot; opt-in, padrão desligado). Sem acesso: a aba "Copilot" não aparece, o botão "Sugerir com Copilot" fica bloqueado (tooltip "Você ainda não possui permissão para usar o copilot, entre em contato com seu Gerente") e nada do Copilot ativo roda.
  - **Copilot ativo (proativo):** feature de plano `copilot.active` (upsell "Scale"). Além dela exige: conversa com `owner = ATTENDANT`, não finalizada e atribuída ao usuário logado. O padrão por empresa fica em Regras de Conversa ("Copilot ativo por padrão em novas conversas") e por usuário no toggle "Copilot ativo" da tela de usuários; cada conversa pode ligar/desligar pelo switch ao lado da aba "Copilot". O Copilot reativo (chat de perguntas) não é gateado por plano.
  - **Créditos:** cada pergunta ao Copilot consome créditos ("Cada pergunta ao Copilot consome créditos de IA. Acompanhe seu consumo em Configurações → Faturamento → Consumo."); a transcrição de áudio chama a IA (Whisper) e o Copilot ativo consome créditos (aviso na tela de Regras de Conversa). Gate de créditos: com a IA bloqueada aparece a faixa vermelha no topo.
  - **Processo ao vivo:** seção "Processo" do painel de detalhes só com a feature `processes`.
  - **Envio bloqueado pelo Tino:** com `owner` `CAMPAIGN` ou `PASSIVE_ATTENDANT` e conversa não finalizada, o campo fica desabilitado até "Interromper".

### Cabeçalho da conversa (`components/inbox/Header.vue`)

- Avatar com selo: IA (tooltip "Tino conversando") ou iniciais do atendente (tooltip com o nome), só com a conversa ativa.
- Nome (ordem: nome vivo da lista, nome do contato, "Visitante do Site" no widget, telefone formatado, "Contato"), ícone do canal (tooltip "WhatsApp"/"Chat Widget"), presença do visitante do widget: "no site" (tooltip "O visitante está com o site aberto") ou "fora do site" (tooltip "O visitante saiu do site. Ele verá sua mensagem quando voltar."), chip do setor (tooltip "Setor: {nome}").
- "Protocolo: #{8 caracteres}" com botão de copiar (tooltips "Copiar protocolo" / "Copiado!"). Com o painel de detalhes fechado, link "toque para ver dados".
- Chip de SLA "SLA mm:ss / MM:00" (tooltips "SLA dentro do limite", "Próximo do limite de SLA", "SLA excedido", "SLA crítico", "SLA pausado fora do horário comercial").
- Ícones: setas (tooltip "Transferir conversa"), check (tooltip "Finalizar atendimento"), X (tooltip "Fechar conversa", volta a `/inbox`), seta para a esquerda (tooltip "Abrir detalhes/copilot").
- Incerteza: o modal "Detalhes do Contato" (`ContactInfoModal`) está importado no cabeçalho desktop mas nada o abre; no mobile abre pelo menu "Detalhes".

### Área de mensagens (`components/inbox/Messages.vue` e `components/inbox/messages/*`)

- Estados: "Carregando mensagens...", "Não há mensagens nessa conversa.", botão "Carregar mais mensagens" ao chegar no topo (paginação), botão flutuante "1 nova mensagem" / "N novas mensagens" quando chegam mensagens com a rolagem longe do fim.
- Cabeçalhos de data: "Hoje", "Ontem", dd/mm/aaaa.
- Divisórias de conversa: "Conversa atual" (tracejada), "Conversa iniciada pelo cliente" / "Conversa iniciada pelo atendente" / "Conversa iniciada", "Conversa encerrada pelo atendente" / "Conversa encerrada automaticamente" / "Conversa encerrada", com horário; abaixo, "Motivo: {motivo}". Conversas de contatos mesclados ganham o botão "Conversa mesclada" que recolhe/expande e mostra "N mensagens ocultas" (barras laterais marcam as mensagens vindas da mesclagem). Conversas `IMPORTED` não geram divisória. Encerramentos chegam ao vivo pelo socket.
- Bolhas: recebidas em papel, do atendente em terracota-claro, do Tino em cobalto-claro (e fonte mono). Em grupo, o nome do participante aparece só na primeira mensagem de uma sequência; em 1:1 nunca (o cabeçalho já diz quem é). Mensagem do Tino sem nome mostra "Tino"; do atendente sem nome, "Atendente"; recebida sem nome, "Cliente".
- Eventos de sistema: caixa centralizada com o texto do evento ("Evento do sistema" se vazio); eventos de transferência/handoff aparecem em pílula com gradiente, seguidos do cartão "Tino · resumo do atendimento" (linhas "cliente" e "resumo", link "ver atendimento completo →" que abre a aba Copilot; só aparece se já existe resumo em `/conversation-summaries/:id`).
- "Mensagem apagada" para mensagens excluídas.
- Conteúdos (`MessageContent.vue`): imagem (clique abre em tela cheia com botão de baixar; "Carregando imagem...", "Mídia indisponível", "Falha ao carregar imagem" + botão de tentar de novo), vídeo (idem; "Carregando video..."), áudio (player com barra, tempo, botão "Transcrever"/"Transcrevendo..." e bloco "Transcrição"; "Carregando audio..."; "!" vermelho se o áudio não toca), figurinha ("Carregando figurinha..." / "Carregando figurinha animada..."), documento (nome, tamanho em MB, botão de baixar; abre em nova aba ao clicar; "Carregando documento..."), texto longo com "Ver mais"/"Ver menos" (8 linhas), localização ("Localizacao compartilhada" com link para o Google Maps), contato compartilhado (nome, telefone ou "Contato compartilhado", botão "Conversar" que abre "Iniciar conversa" com o número), resposta de lista ("📋 {título}"), "Mensagem temporaria", template WABA (texto + botões; registro antigo: "Mensagem de template · {nome}"), "Mensagem sem conteúdo".
- Prévia de mensagem citada (`QuotedMessagePreview.vue`): nome do autor citado, "Você – Status", "Para ver o status postado, utilize seu celular.", "Foto", "Audio", "Video", "Figurinha", nome do documento, "Localizacao", contato ("Salve esse contato para iniciar conversa."), "📋 {título}", ou o texto/"Mensagem". Clicar rola até a mensagem original (carrega páginas anteriores se preciso; "Para abrir mensagens de resposta de status utilize seu celular.").
- Rodapé da bolha (`MessageFooter.vue`): horário, "(editado)" e, nas enviadas, o ícone de entrega: relógio (tooltip "Enviando…"; também usado quando falhou), um check (tooltip "Enviada"), dois checks cinza (tooltip "Entregue"), dois checks azuis (tooltip "Visualizada"). Ao lado da bolha: relógio com tooltip "Aguardando o visitante voltar ao site para ser entregue" (widget com visitante fora do site) ou ícone vermelho de falha (tooltip "{motivo} Toque para reenviar"; motivo padrão "Não foi possível entregar esta mensagem."), que reenvia o texto.
- Reações: chip de emojis abaixo da bolha; reagir de novo com o mesmo emoji remove; uma reação por pessoa.
- Menu de ações da mensagem (`ActionMenu.vue`, seta ao passar o mouse): "Reagir" (seletor de emoji), "Responder" (não no Chat Widget), "Por que ela disse isso" (só mensagens do Tino), "Editar" (só suas mensagens de texto/legenda, até 10 minutos), "Excluir" (só suas mensagens, até 2 h 12 min). Duplo clique na bolha também responde.
- Modal "Editar mensagem": textarea, "Cancelar", "Editar". Erros: "Não foi possível editar esta mensagem.", "Erro ao editar a mensagem.", "Erro ao editar mensagem." (serviço).
- Confirmação de exclusão (`SharedConfirmModal`, título "Confirmar"): "Você tem certeza que deseja excluir essa mensagem?", botões "Não"/"Sim". Erros: "Você não pode excluir esta mensagem (prazo expirado ou não é sua).", "Mensagem invalida.", "Nenhuma mensagem selecionada.", "Erro ao excluir a mensagem.".
- Modal "Por que ela disse isso" (`ProvenanceModal.vue`): kicker "Tino · procedência", "O que guiou esta mensagem, e onde cada instrução se corrige."; blocos "Processo" (nome com link), etapa ("Texto que ela deveria seguir" ou "Esta etapa não tem texto escrito — Tino redigiu a mensagem por conta própria."), "Instruções que entraram no prompt" agrupadas em "Conformidade", "Roteamento", "Diretrizes" (com links para editar) e a frase "Se o comportamento está errado, é numa dessas que a correção precisa ser escrita — escrever em outro lugar perde para a instrução que causou isso."; "Campanha: {título}". Estados: "Não foi possível carregar a procedência desta mensagem." e "Esta mensagem não tem procedência registrada. Só mensagens de campanha enviadas depois desta versão carregam o registro.".
- Caixa do Copilot no fim da conversa (`CopilotBox.vue`, só com Copilot ativo): pílula "copilot", texto sugerido, botões "Usar resposta" (envia direto) e "Editar antes" (coloca no campo de texto).
- Aviso flutuante (`CopilotAlertsToast.vue`, só quando a aba Copilot não está visível): "Copilot detectou uma possível inconsistência", `Sobre "{o que você disse}" — clique em Ver para revisar a correção sugerida.`, botão "Ver" (abre a aba Copilot) e "×" (dispensa localmente).
- Faixa de reconexão (`ReconnectingBanner.vue`): "Reconectando o canal… suas mensagens serão enviadas automaticamente em instantes." (canal em standby sendo acordado; some em até 30 s se nada mais chegar).

### Compositor (`components/inbox/Footer.vue`)

- Avisos acima do campo: "O visitante não está no site. Ele verá sua mensagem quando voltar." (widget); "Mensagem substituída pela sugestão do Copilot." com "Desfazer" (quando uma sugestão substituiu texto que já estava digitado); sobreposição "Enviando áudio..." / "Enviando...".
- "Respondendo a: " com prévia ("Foto"/legenda, "Vídeo"/legenda, "Áudio", nome do "Documento", "Figurinha", texto ou "Mensagem") e X para cancelar.
- Faixa de anexos (miniaturas de imagem/vídeo, ícone de áudio/arquivo com o nome, botão X em cada um; clicar na imagem abre em tela cheia).
- Linha de assinatura: toggle + "Assinar como" + campo (placeholder "Digite sua assinatura"; visível só se a empresa permite trocar a assinatura); "Sugerir com Copilot"; quando o Tino conduz: "Tino ativo" + botão "Interromper" (tooltip "Interromper Tino e assumir controle").
- Campo de texto: placeholder "Digite sua mensagem..." ou "Tino está conversando..." (desabilitado); contador "N / 4096" a partir de 80% do limite (tooltips "Limite máximo: 4096 caracteres." / "Limite excedido — não é possível enviar."; o excesso fica destacado em vermelho e novas teclas são bloqueadas, colar continua permitido); botões de anexo, emoji, microfone (não no Chat Widget) e "Enviar".
- Menu de anexo: "Múltiplos Arquivos" (abre o modal "Enviar Múltiplos Arquivos"), "Arquivo Individual" (aceita `.pdf,.doc,.docx,image/*,audio/*,video/*`, múltiplos enquanto houver vaga) e a dica "Você também pode colar arquivos com Ctrl+V".
- Modal "Enviar Múltiplos Arquivos" (`components/shared/MultipleFileUpload.vue`, desktop: até 10 arquivos, 10 MB cada; mobile "Múltiplas Imagens": até 8, 8 MB): "Arraste seus arquivos aqui", "ou", "Escolher Arquivos", "Máximo de 10 arquivos • Imagens, vídeos, áudios, PDFs • Máximo 10MB cada"; grade com ordem numerada (arrastar reordena), "N arquivo(s) selecionado(s)", "Adicionar mais", "Comprimindo... N%" / "Processando...", "Tentar novamente", "Limpar Tudo", "Enviar N arquivo(s)" / "Processando...". Erros: "Máximo de N imagens permitidas", "{arquivo}: Tamanho máximo NMB", "{arquivo}: Vídeos: tamanho máximo 15MB", "N imagem(ns) falharam no processamento", "Processamento muito lento - tente uma imagem menor", "Imagem muito grande - reduza o tamanho". Ao final: "N arquivo(s) enviado(s) com sucesso!" ou "X de Y imagens enviadas. Z falharam."; falha geral "Erro ao enviar arquivos".
- Gravação de áudio: na primeira vez, modal "Permissão de Microfone" ("Para gravar áudios, é necessário permitir o uso do microfone. Clique em \"Entendi\" e aceite a permissão do navegador quando for solicitado." + "Entendi"); barra "Gravando..." com cronômetro, lixeira (descarta) e botão de parar; prévia com play/pause, forma de onda, "0:00 / 0:12", lixeira e botão de enviar. Erros: "Não foi possível acessar o microfone", "Erro ao gravar áudio.", "Nenhum áudio foi capturado. Tente gravar novamente.", "Falha ao processar o áudio gravado. Tente novamente.", "Erro ao processar o áudio gravado.", "O áudio gravado está vazio. Grave novamente antes de enviar.", "Não foi possível reproduzir a prévia do áudio.", "Erro ao reproduzir a prévia.".
- Menu de mensagens rápidas (`QuickReplyMenu.vue`): abre ao digitar "/" no início do campo; lista "/{atalho}" com prévia (variáveis já resolvidas); "Nenhuma mensagem rápida encontrada"; setas, Enter (insere) e Esc (fecha).
- **Fluxos:**
  - *Responder:* digitar e Enter (Shift+Enter quebra linha) ou "Enviar". A bolha aparece na hora com relógio e vira check quando o servidor confirma; em falha, ícone vermelho com "Toque para reenviar". Se o canal estiver reconectando, o front tenta uma segunda vez após 3 s sem avisar. Erro genérico: "Erro ao enviar mensagem" / "Erro ao enviar a mensagem.".
  - *Assinar mensagem:* ligar "Assinar como"; a mensagem sai como `*Nome:*` na primeira linha + texto. Se a empresa marcou "Assinatura obrigatória" (Regras de Conversa) o toggle fica travado ligado; "Permitir mudança de assinatura" libera editar o nome por conversa (guardado no navegador por 7 dias). O nome padrão é o "nome de atendimento" do usuário, senão o nome do usuário.
  - *Usar mensagem rápida:* digitar "/" + início do atalho, escolher; `{{nome_cliente}}` e `{{nome_atendente}}` são substituídos.
  - *Pedir sugestão ao Copilot:* "Sugerir com Copilot" abre o painel na aba Copilot e envia "Sugira uma resposta para enviar agora" ao chat reativo.
  - *Aceitar sugestão:* na aba Copilot ou na caixa inline, "Enviar direto"/"Usar resposta" envia na hora; "Inserir no rascunho"/"Editar antes" coloca no campo (aviso com "Desfazer" se havia texto). Texto vindo da IA é marcado como `aiAuthored` (o backend não o valida contra a base).
  - *Interromper a IA e assumir:* "Interromper" (widget ou `PASSIVE_ATTENDANT` → `/widget-config/chats/interrupt/:id`; campanha → `/campaigns/interrupt/:contactId`). Sucesso: "Conversa interrompida e transferida ao atendente."; erro: "Erro ao interromper a conversa. Tente novamente.". A lista é reconciliada e o campo libera.
  - *Devolver para a IA:* não existe ação no Inbox (ver Incertezas).
  - *Transferir:* ícone de setas > drawer "Transferir conversa" (abaixo).
  - *Finalizar:* ícone de check > drawer "Finalizar conversa" (abaixo).
  - *Anexar mídia:* clipe > "Arquivo Individual" ou "Múltiplos Arquivos", ou colar (Ctrl+V); a legenda (texto do campo) vai na primeira mídia; imagens são comprimidas no navegador (alvo 800 KB, máximo 1920×1080).
  - *Gravar áudio:* microfone > gravar > parar > ouvir > enviar (aparece como áudio "ptt").
  - *Reagir / responder / editar / excluir:* menu da bolha.
  - *Transcrever áudio:* botão "Transcrever" no player; resultado fica em cache no navegador por 24 h.
- **Regras e limites:** 4096 caracteres por mensagem (teto da WhatsApp Business API); até 4 anexos por envio pelo clipe/colar ("É possível enviar no máximo 4 arquivos por vez."), 1 vídeo por vez ("Só é possível enviar um vídeo por vez."), vídeo até 15 MB ("O tamanho máximo para vídeos é de 15 MB."); editar até 10 min e excluir até 2 h 12 min depois do envio, só mensagens suas; rascunhos por conversa guardados no navegador por 30 dias (mostrados como "Rascunho:" na lista); "digitando…" é enviado ao WhatsApp a cada 3 s enquanto digita (não no widget); mídia com erro 410 aparece como "Mídia indisponível" (expirada); mensagens `sent_*` otimistas são reconciliadas com o eco do servidor.
- **Nomes e termos:** "Tino ativo" = o Tino está conduzindo; "Interromper" = assumir a conversa; "Assinar como" = prefixar o nome; "Sugerir com Copilot"; "Rascunho".
- **Perguntas prováveis:**
  - "Não consigo digitar." O Tino está conduzindo: clique em "Interromper" (toast: "Para enviar mensagens, primeiro interrompa a conversa do Tino utilizando o botão abaixo.").
  - "Por que o botão de microfone sumiu?" Chat Widget não envia áudio.
  - "Por que não consigo editar/excluir?" Prazo (10 min / 2 h 12 min) ou a mensagem não é sua.
  - "Mandei e ficou com relógio." Ainda enviando ou canal reconectando; se virar ícone vermelho, toque para reenviar.
  - "Mensagem para visitante ficou com relógio e não é erro?" Visitante fora do site: entregue quando ele voltar.
- **Incertezas:** não há botão para devolver a conversa ao Tino depois de interromper; não há envio manual de CSAT (a pesquisa é automática, configurada em Configurações > Atendimento > "Pesquisa de Satisfação"); a janela de 24 h do WhatsApp só é tratada na abertura de conversa por template (WABA), nunca dentro da conversa aberta; o limite de tamanho do "Arquivo Individual" (fora vídeo) não é validado no front; o que acontece com anexos de áudio/vídeo no widget depende do backend.

### Painel de detalhes (`components/inbox/DetailsPanel.vue`)

- **Como chegar:** cabeçalho da conversa > seta "Abrir detalhes/copilot" ou "toque para ver dados". Começa sempre recolhido ao carregar. Abaixo de 1400 px vira um drawer sobreposto.
- Abas: "Detalhes" e "Copilot" (esta só com acesso). Ao lado de "Copilot", o switch de Copilot ativo (títulos "Ligar Copilot ativo"/"Desligar Copilot ativo"; só aparece com a feature `copilot.active`, conversa em posse do usuário logado e estado já carregado do backend). Botão de fechar (tooltip "Fechar detalhes/copilot"). Sem conversa: "Selecione uma conversa para ver os detalhes".

#### Aba "Detalhes" (`components/inbox/details/ContactDetails.vue`)

- Cartão: avatar, nome (lápis "Editar contato" > campo + "Salvar"/"Cancelar"; toast "Nome atualizado com sucesso!" / "Erro ao atualizar nome do contato."), subtítulo "Chat Widget", "Grupo · WhatsApp" ou "WhatsApp"; ações "Copiar"/"Copiando..." (copia o texto da conversa; "Conversa copiada!" / "Nenhuma conversa ativa para copiar." / "Erro ao exportar conversa."), "Abrir ficha", "Compartilhar" ("Link copiado para a área de transferência!"), "Mesclar" (só widget; tooltip "Unificar visitantes duplicados do chat widget em um único contato").
- Seção "Ficha do contato" + "Abrir ficha ›": "Carregando…", "Status" (nome com cor ou "Sem status"), até 3 campos preenchidos (spark de IA quando coletado pelo Tino), até 2 notas ("Pedido"/"Informação"), ou "Nada registrado ainda sobre este contato.".
- Seção "Conversa" (recolhível): "Status" (pílula "Aguardando", "Em andamento", "Aguardando CSAT", "Finalizado"), "Campanha" (+ botão "Abrir campanha" para gestor+), "Atendente", "Transferido pelo Tino" → "Sim", "Interrompido por" → nome ou "Atendente", "Telefone", "Atualizado" (data/hora), "ID externo" (tooltip "Identificador do contato no seu sistema (ERP, CRM etc.), enviado no webhook de atendimento"; "Não definido"; edição com placeholder "Ex: ERP-12345"; vazio limpa; toast "ID externo atualizado com sucesso!" / "Erro ao atualizar ID externo do contato.").
- Seção "Processo" (`ProcessLiveContext.vue`, só com feature `processes` e conversa que usou processo): selo "ao vivo", aviso "Chegou até você pelo Tino" + motivo (ou "Tino passou esta conversa para a equipe. Confira o histórico antes de responder."), "Processo", "Status" ("Em andamento", "Concluído", "Encerrado", "Passou para a equipe", "Transferido para a equipe"), barra de etapas com "etapa X de Y · há N min · N trocas" e o nome da etapa ("entregue à equipe"/"encerrado"), último turno ("Tino {resultado} · o sistema {ação}"), links "Diagnóstico do processo →" (`/scout/processes/{id}`) e "Auditoria desta conversa →" (`/scout/evaluations/{id}`, só finalizada).
- Seção "Sessão" com selo "Web" (widget): "IP", "Telefone" (ou "Não preenchido"), "Página" (link).
- Seção "Navegação" (widget): histórico de páginas da sessão com duração ("12s", "3m 4s", "5min", "1h 2min") e "· agora" na página atual; "Ver mais (N)"/"Ver menos" (4 por padrão).
- Seção "Contato vinculado" (widget com WhatsApp vinculado): nome, "WhatsApp", botão "Abrir" (tooltip "Abrir conversa no WhatsApp").
- Seção "Tags" (só com feature `campaigns`): chips coloridos e "Aplicada em {data}". Só leitura aqui.
- Seção "Protocolos": lista "#{8 chars}" + data por conversa do contato, com "Copiar"/"Copiado!"; o protocolo atual em azul.
- Seção "Notas" (notas da conversa, `conversation-note.service.ts`): lista com autor ("Sistema" quando não há atendente), ícone do canal, data, "Expandir"/"Recolher" (acima de 80 caracteres), "Editar", "Excluir" (não em notas de sistema); "Nenhuma nota adicionada"; botão flutuante "Adicionar nota"; folha "Nova nota"/"Editar nota" (placeholder "Adicionar uma nota..."/"Editar nota...", "Cancelar", "Salvar"); confirmação "Deseja realmente excluir esta nota?" ("Não"/"Sim"). Erro em qualquer operação: "Erro ao criar anotação.".
- Modal "Mesclar contatos" (`MergeContactsModal.vue`): "Contato principal" (nome, telefone, "IP: x"), "Selecionar contatos para mesclar", busca "Buscar por nome..." (a partir de 2 letras), listas "Sugestões" (motivos "Mesmo telefone", "Mesmo IP", "Mesmo nome", "N conversa(s)") e "Resultados"; vazio: "Nenhum contato similar encontrado." + "Use a busca para encontrar contatos." ou `Nenhum resultado para "{busca}"` + "Tente outro nome."; "Cancelar", "Mesclar N contato(s)"; confirmação: "As mensagens dos contatos selecionados serão movidas para o chat de {nome} e não aparecerão mais na sidebar. Essa ação não pode ser desfeita." com "Voltar" e "Confirmar"/"Mesclando..."; toast "Contatos mesclados com sucesso!" / "Erro ao mesclar contatos.". Após mesclar, a conversa removida redireciona para a principal.

#### Aba "Copilot" (`components/inbox/details/CopilotChat.vue`)

- **Copilot ativo (proativo):** barra de status com "Copilot", "Contexto: {contato}" e 4 estágios "Lendo contexto", "Detectando intenção", "Consultando base" (ou "Consultando: {documento}"), "Redigindo"; ao terminar: "Sugestão pronta para envio" ou "Correção sugerida". Cartão "Sugestão do Copilot" (texto + ícones "Enviar direto", "Inserir no rascunho", "Copiar", "Dispensar", "Expandir") ou cartão "Correção do Copilot" (`Você disse "{X}", mas a base diz "{Y}".` + texto corrigido + as mesmas ações). Sem nada: "Sem sugestões no momento.". Só o item mais recente fica em tela; o cartão minimiza ao usar o chat. Ao desligar o switch, a tela é limpa na hora; transferir a conversa apaga as sugestões do atendente anterior.
- **Copilot reativo (chat):** vazio: "Como posso ajudar?" + "Eu li o histórico desta conversa e tenho acesso à base de conhecimento. Pergunte qualquer coisa."; cabeçalho "N mensagens" + "Nova conversa" (tooltip "Apagar copilot atual"); respostas com "Copilot", "Fontes:" (documentos; fontes de processo com selo "processo") e ações "Enviar" (insere no campo a parte entre aspas ou tudo), "Copiar" ("Mensagem copiada!" / "Falha ao copiar para a área de transferência."), "Regenerar"; erro na resposta: "Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente.". Campo "Pergunte ao Copilot sobre este atendimento..." (Enter envia), botão "Mensagens prontas" ("Sugira uma resposta para enviar agora", "Faça um resumo deste atendimento", "Vale a pena escalar esse caso?", "Quais artigos da base são relevantes aqui?"), botão "Anexar imagem" (até 5 imagens de 8 MB: "Máximo de 5 imagens por pergunta.", `A imagem "{nome}" excede 8MB.`, `Falha ao ler a imagem "{nome}".`; só imagens envia a pergunta "Analise a(s) imagem(ns) anexada(s) e me ajude."), selo de custo de IA, "Enviar".
- **Regras:** histórico por conversa fica no backend (comentário: Redis, 1 h) e em cache do navegador; ao perder a posse da conversa o cache local é apagado.
- **Incerteza:** o modal "Adicionar contexto da Base de Conhecimento" (`CopilotContextModal.vue`, "Buscar documento...", "Confirmar (N)") não é chamado por nenhuma tela.

### Drawer "Transferir conversa" (`components/inbox/TransferPanel.vue`)

- **Como chegar:** cabeçalho > "Transferir conversa" (mobile: menu > "Transferir").
- **O que há:** abas "Atendente" e "Setor". Atendente: busca "Pesquisar atendente", opção "Nenhum" (remove o atendente), lista da empresa inteira com presença (atendentes e gestores; usuários desativados não aparecem; o Admin da conta fica de fora), botão "Transferir para atendente". Setor: busca "Pesquisar setor", setores da unidade da conversa (nome e descrição), "Nenhum setor encontrado", botão "Transferir para setor".
- **Fluxos e mensagens:** "Atendente transferido!" / "Atendente removido!" / "Erro ao atribuir atendente."; "Conversa transferida para o setor!" / "Erro ao transferir conversa para o setor." / "Selecione um setor para transferir" / "Conversa não encontrada para realizar a transferência.". O botão fica desabilitado enquanto a seleção for igual à atual. O atendente que recebe é avisado ("Nova conversa atribuída a você: {contato} ({setor})").

### Drawer "Finalizar conversa" (`components/inbox/Finish.vue`)

- **Como chegar:** cabeçalho > "Finalizar atendimento" (mobile: menu > "Finalizar").
- **O que há:** textarea com placeholder "Digite o motivo da finalização", dica "Descreva como o atendimento terminou — inclusive se foi resolvido fora do chat.", contador "N/500" (vermelho nos últimos 50), "Limite de 500 caracteres atingido.", botão "Finalizar"/"Finalizando...".
- **Regras:** motivo obrigatório ("Informe o motivo da finalização"), máximo 500 caracteres ("O motivo deve ter no máximo 500 caracteres"); sucesso "Conversa finalizada com sucesso"; erro "Não foi possível finalizar a conversa." ou a mensagem do backend. Ao finalizar, o Scout gera resumo/nota se "Ativar Scout ao finalizar conversa" estiver ligado (Regras de Conversa) e a pesquisa de satisfação pode ser disparada (status "Aguardando CSAT").

### Versão mobile da conversa (`ChatMobile.vue`, `HeaderMobile.vue`, `MessagesMobile.vue`, `FooterMobile.vue`)

- Cabeçalho escuro: "Voltar", nome ou "Contato sem nome", "Protocolo: #…" com "Copiar protocolo"/"Copiado!", chip "SLA mm:ss / MM:00", chip do setor, tags "Transferida pelo Tino" (tooltip "Tino transferiu esta conversa. Você deve seguir a conversa!") e "Interrompida" (tooltip "Conversa interrompida por um atendente."), selo de IA ("Tino conversando"), menu "Mais opções": "Anotações", "Detalhes" (abre "Detalhes do Contato" com nome e telefone; "Carregando informações do contato..."), "Transferir", "Finalizar", "Fechar".
- Mensagens: mesmas bolhas; arrastar a bolha para a direita (mais de 60 px) responde; menu com "Reagir", "Responder", "Editar", "Excluir" (sem "Por que ela disse isso"); transcrição de áudio inline ("Transcrição"); "Recarregando áudio...".
- Compositor: toggle + "Assinar como" (campo "Assinatura"), botão de câmera (aceita imagem, vídeo e PDF), campo "Mensagem", botão de enviar ou de microfone ("● Gravando"), modal "Múltiplas Imagens" (8 arquivos, 8 MB). Erros extras: "Permissão de microfone negada. Verifique as configurações do dispositivo.", "Nenhuma trilha de áudio detectada. Verifique se o microfone está ativo.", "API de áudio não suportada neste navegador.", "Nenhum áudio gravado. Verifique o microfone.", "Não foi possível acessar o microfone. Verifique as permissões e o dispositivo.", "Erro ao enviar áudio", "Erro ao enviar imagens".
- Sem painel de detalhes/Copilot no mobile.
- **Incerteza:** o item "Anotações" abre `InboxNotesModal`, componente que não existe no repositório; no mobile a ação provavelmente não faz nada.

---

## Visitantes online (`/inbox/visitors`)

- **Como chegar:** Inbox > coluna de navegação > "Visitantes online" (mobile: botão do globo).
- **Para que serve:** ver quem está navegando no site com o Chat Widget agora e abordar proativamente.
- **Quem vê:** todos os usuários do Inbox; depende do Chat Widget da unidade atual estar ativo.
- **Plano, créditos e bloqueios:** exige Chat Widget cadastrado e habilitado; sem ele, estado "Chat Widget não configurado".
- **O que há na tela (`components/inbox/Visitors.vue`):** título "Visitantes online", "N navegando agora" (ponto verde pulsando), botão "Atualizar lista", busca "Buscar por nome ou página...", abas "Todos", "Identificados", "Anônimos"; cada visitante: inicial ou globo, nome ou "Visitante anônimo", página atual (título ou caminho, "Navegando"), tempo no site ("45s", "12min", "1h 5min"), "via {origem}" ou "via Acesso direto", ponto verde (tooltip "Visitante online no site"). Vazios: "Nenhum visitante navegando no momento", "Nenhum visitante identificado no momento", "Nenhum visitante anônimo no momento", "Nenhum visitante encontrado"; sem widget: "Chat Widget não configurado" + "Ative e instale o Chat Widget no seu site para acompanhar os visitantes em tempo real." + botão "Configurar Chat Widget" (`/settings/channels/chat-widget`).
- **Painel direito (`VisitorsPlaceholder.vue`):** "Chat Widget não configurado" + "Para acompanhar quem está navegando no seu site em tempo real e iniciar conversas proativas, ative e instale o Chat Widget nas configurações de canais." + "Configurar Chat Widget"; "Nenhum visitante navegando no momento" + "Quando alguém abrir uma página do seu site, ele aparecerá aqui em tempo real e você poderá iniciar uma conversa."; "N visitante(s) online" + "Selecione um visitante na lista para iniciar uma conversa proativamente.".
- **Chat do visitante (`VisitorChat.vue`):** clicar no visitante resolve/cria só o contato (sem criar conversa) e abre a janela completa (mesmo cabeçalho, mensagens, compositor, detalhes/Copilot, transferir e finalizar); no mobile navega para `/inbox/{id}?channel=chat-widget`. Erros: "Não foi possível abrir a conversa." / "Não foi possível abrir a conversa deste visitante.".
- **Fluxos:** *Abordar:* escolher o visitante > escrever no compositor > "Enviar"; a conversa nasce nesse envio. Se o visitante sair do site, o cabeçalho mostra "fora do site" e a mensagem fica pendente até ele voltar.
- **Regras:** o IP do visitante aparece para o atendente (comentário do código pede cobertura na política de privacidade/LGPD); a lista é por unidade atual; uma lista que "zera" só é limpa após reconfirmar no servidor (evita piscar).
- **Incertezas:** o que define "identificado" é o `visitorName` vindo do widget (login/identificação no site); não há detalhe no front.

---

## Contatos (`/inbox/contacts`)

- **Como chegar:** Inbox > "Contatos" (mobile: botão de pessoas, tooltip "Contatos e fichas").
- **Para que serve:** listar e buscar os contatos das unidades acessíveis e abrir a ficha (mini CRM) de cada um.
- **Quem vê:** todos; chips de unidade só para multiunidade (mesmo estado do chip do Inbox). Backend intersecta com as unidades acessíveis.
- **O que há na tela (`components/inbox/contacts/List.vue`):** título "Contatos" com o total, botão de sincronizar (tooltip "Sincronizar contatos do WhatsApp", chama `/contact/materialize-wa`), busca "Nome, telefone ou e-mail" (server-side, com debounce; busca também ID externo e dígitos do telefone), filtros "Status" (lista do catálogo da empresa; vazio: "Nenhum status cadastrado. Crie em Identidade › Operações.") e "Tag" (tags em uso; vazio: "Nenhuma tag em uso nesta unidade."), "Limpar"; chips de unidade; linhas com avatar, nome (ou telefone, ou "Contato sem nome"), data da última mensagem (hora hoje; dd/mm; dd/mm/aaaa), telefone, pílula de status, até 2 tags (+ "+N"), selo da unidade; "Carregando mais…"; vazio "Nenhum contato ainda" ou "Nenhum contato para esta busca" + "Limpar filtros". 30 por página, rolagem infinita; a lista e a posição de rolagem sobrevivem ao abrir/voltar da ficha.
- **Painel direito (`contacts/Placeholder.vue`):** "Nenhum contato aberto" + "Escolha um contato na lista para ver a ficha: status, campos preenchidos, notas registradas pelo Tino e pela equipe e o histórico de conversas.".
- **Fluxos:** buscar/filtrar; clicar no contato abre `/inbox/contacts/{id}` (no mobile em tela cheia).
- **Regras:** excluir um status no catálogo derruba o filtro que apontava para ele e recarrega a lista.
- **Incertezas:** contatos de WhatsApp só entram na lista depois de existirem no banco (sincronizar traz os da agenda); a regra exata é do backend.

## Ficha do contato (`/inbox/contacts/:contactId`)

- **Como chegar:** Contatos > clicar no contato; ou painel de detalhes da conversa > "Abrir ficha"; ou link copiado ("Copiar link da ficha").
- **Para que serve:** a memória do relacionamento: dados, status, campos coletados pelo Tino ou pela equipe, tags, notas e histórico de conversas, com transcrições.
- **Quem vê:** todos com acesso à unidade do contato; "Criar em Identidade › Operações" (status) só para gestor+.
- **O que há na tela (`components/inbox/contacts/Profile.vue`):**
  - Link "Contatos" (volta), avatar, nome editável (tooltip "Editar nome"; Enter salva, Esc cancela; toast "Nome atualizado com sucesso!"), linha "{canal} · {unidade} · {telefone}", "na base desde dd/mm/aaaa", seletor de status (`StatusSelect.vue`: "Sem status" + catálogo; toast `Status alterado para "{nome}".` / "Status removido." / "Erro ao atualizar o status do contato."; vazio: "Nenhum status cadastrado ainda." + "Criar em Identidade › Operações" ou "Peça a um gestor para criar a lista de status."), botão de link (tooltip "Copiar link da ficha"; "Link da ficha copiado!"), botão "Abrir conversa" (`/inbox/{id}`).
  - "Ficha não encontrada" + "O contato pode ter sido mesclado com outro ou pertencer a uma unidade fora do seu acesso." + "Voltar para Contatos".
  - Cartão "Campos do contato" (`ProfileFields.vue`): "N/M" preenchidos; sem catálogo: "Nenhum campo configurado para a empresa. Os campos que Tino coleta na conversa são definidos em Identidade › Operações › Campos do contato."; cada campo com valor ou "— adicionar", ações "Editar", "Limpar campo" (Enter salva, Esc cancela); procedência "Tino · dd/mm/aa" (clicável, tooltip "Ler a conversa em que a IA coletou este dado") ou "equipe · dd/mm/aa"; erro do backend abaixo do campo (validação por tipo) com link "Abrir Identidade › Operações" quando a chave não existe no catálogo.
  - Cartão "Tags" (`ProfileTags.vue`): chips coloridos (ícone de megafone com tooltip "Aplicada por uma campanha" quando veio de campanha), X (tooltip "Remover tag"), botão "Tag" que abre o campo "Nome da tag" com sugestões do catálogo (nome + contagem) e "Criar {nome}" com seletor de cor (tooltip "Cor da nova tag"); vazio: "Nenhuma tag aplicada. Tags são critério de audiência das campanhas.". Erros: "Erro ao aplicar a tag.", "Erro ao remover a tag.".
  - Cartão "Notas" (`ProfileNotes.vue`, notas do contato): textarea "Escrever uma nota sobre este contato…" (até 5000 caracteres), seletor "Pedido"/"Informação", "Salvar nota"/"Salvando…" ("Nota registrada!" / "Erro ao registrar a nota."); linha do tempo com tipo, autor ("Tino", "Sistema" ou nome/"Equipe") e data, "ver conversa" (tooltip "Ler a conversa em que este registro foi feito"), lixeira "Remover nota" só quando `canDelete` (nota da IA nunca é apagável) com confirmação "Remover esta nota? A ação não pode ser desfeita." ("Nota removida." / "Erro ao remover a nota."); vazio: "Nenhuma nota ainda. Tino registra aqui o que promete ao cliente durante a conversa, e a equipe registra o que precisa ficar guardado sobre o contato.".
  - Cartão "Conversas" (`ProfileConversations.vue`): total; "A ficha carrega as N conversas mais recentes; este contato tem M." quando há mais de 50; cada conversa com data/hora de início "→ hora de fim", status ("Aguardando", "Em andamento", "Aguardando CSAT", "Finalizada"), canal · setor · atendente, resumo do Scout, link "Nota do Scout 8,5" / "Avaliação do Scout" (`/scout/evaluations/{id}`), "Ver transcrição"; "Ver mais (N restante(s))" (8 iniciais, +10 por clique); vazio "Nenhuma conversa registrada com este contato ainda.".
  - Cartão "Vínculos": "Mesmo telefone, outro canal" (candidatos a mesclagem, botão "Mesclar contatos") e "Em outras unidades" (links para a ficha em cada unidade com "últ. dd/mm/aa" ou "sem conversa"; "Cada unidade tem a própria ficha, com histórico e status próprios.").
  - Gaveta de transcrição (`ConversationDrawer.vue`): nome do contato ou "Conversa", datas, canal · setor · atendente, ou "Conversa fora das mais recentes listadas na ficha."; bloco "Resumo do Scout"; transcrição somente leitura ("Nenhuma mensagem encontrada"); rodapé "Somente leitura" e link "Avaliação do Scout 8,5". Erro: "Não foi possível carregar a transcrição desta conversa.". Esc fecha.
- **Fluxos:** editar nome; trocar status; preencher/limpar campos; aplicar/remover tag; escrever nota; abrir transcrição; mesclar (mesmo modal "Mesclar contatos" da conversa); ir para a ficha em outra unidade.
- **Regras:** campos validados pelo backend por tipo (e-mail, CPF/CNPJ, data…); salvar vazio equivale a limpar; a tag existente herda a cor do catálogo; a mesma pessoa em outra unidade não é duplicata (só navegação); duplicata é só mesmo telefone em outro canal da mesma unidade.
- **Perguntas prováveis:** "Posso apagar a nota que o Tino escreveu?" Não (é evidência do que foi prometido ao cliente). "Por que a lista mostra 50 conversas?" A ficha carrega no máximo 50; o total real aparece no cabeçalho.
- **Incertezas:** o catálogo de campos e status é configurado em Identidade › Operações (área do Cérebro, fora deste inventário).

---

## Central de Conversas — navegação (`layouts/conversations.vue`, `components/conversations/Sidebar.vue`)

- **Como chegar:** menu principal > "Central de Conversas" (abre em "Panorama").
- Coluna lateral "Central de Conversas" com "Panorama" e "Conversas"; no mobile, cabeçalho "Conversas" com botão de menu.
- **Quem vê:** todos (o item não tem `requires`); o backend recorta os dados pelo papel: Admin/Gestor da Empresa veem a empresa, Gestor de Área/Unidade a subárvore, Atendente só as conversas em que é o atendente (`docs/visibilidade-por-papel.md`, nota ²), em listagem, detalhe, mensagens, CSV e finalização em massa.

## Panorama (`/conversations/overview`)

- **Para que serve:** retrato do inventário de conversas no recorte (o que está na mesa agora), não de desempenho.
- **O que há na tela (`pages/conversations/overview.vue`):** kicker "central · panorama", título "Panorama", link "ver conversas"; barra de escopo (`ScopeBar.vue`): trilha "empresa › área › unidade › atendente" (degraus fixos conforme o papel: raiz é a empresa para Admin/Gestor da Empresa, a área para Gestor de Área, a unidade para Gestor de Unidade; atendente fica na raiz "empresa" mas vê só as próprias conversas), opções "Todas as áreas", "Todas as unidades"/"Todas as unidades da área", "Todos os atendentes", busca "buscar {nível}…", "Nada encontrado."; botão "refinar" (canal: "Todos", "WhatsApp", "WhatsApp Business", "Chat Widget"; setor: "Todos" + setores; "limpar"); seletor "período" (`PeriodBar.vue`: "Hoje", "Esta semana", "Este mês", mês/ano específico com setas e "desmarcar mês", "Personalizado" com "Aplicar"; dicas "Ano inteiro selecionado." / "Selecionar um mês fixa o ano; ✕ deixa só o ano."; padrão: mês atual); chips "filtros" com "limpar tudo".
  - Veredito (clicável, abre a Central com o recorte): "Comece pelas N que estouraram o SLA.", "N conversa(s) está(ão) parada(s) há mais de 7 dias — são as mais antigas da fila.", "N conversa(s) em aberto ainda não tem/têm atendente.", "Fila em dia: nada parado há mais de um dia.", "Nada em aberto neste recorte."; selo "requer ação", "atenção", "em dia", "sem pendências"; contexto "X% do período foi finalizado." (+ " — era Y% no período anterior.").
  - Sinais clicáveis: "em aberto", "sem atendente", "conduzido pelo Tino" (%), "sla estourado", com variação "▲/▼ X%" vs. período anterior.
  - Seção "há quanto tempo estão paradas": "N parada(s) há mais de 7 dias" / "... há mais de 1 dia" / "0 paradas há mais de 1 dia — fila recente"; baldes "menos de 1 hora", "1 a 24 horas", "1 a 7 dias", "mais de 7 dias".
  - Seção "como as conversas se repartem": colunas "Status" (Aguardando, Em andamento, Aguardando CSAT, Finalizada, Importada), "Responsável" (IA passiva, IA de campanha, Humano), "Canal" (WhatsApp, WA Business, Chat Widget), "SLA" (No prazo, Estourado, Sem SLA); dica "N conversas · clique numa linha para vê-las na Central".
  - Estados: "Montando o retrato do recorte.", "Não foi possível montar o Panorama" + "Houve uma falha ao carregar os números deste recorte. Tente novamente." + "Tentar de novo", "Nenhuma conversa neste recorte" + "Troque o período ou limpe os filtros acima.".
- **Fluxos:** ajustar escopo/período/refinar; clicar em qualquer número abre `/conversations` com os mesmos filtros na URL.

## Central de conversas (`/conversations`)

- **Para que serve:** "Busque, audite e exporte qualquer conversa que já passou pela plataforma".
- **O que há na tela (`pages/conversations/index.vue`, `FilterBar.vue`):** título "Central de conversas", botões "Atualizar" e "Exportar CSV"; barra de filtros: busca "Buscar por nome, telefone ou mensagem…" (contato e conteúdo das mensagens), datas de/até, "Canal" (WhatsApp, WA Business, Chat Widget), "Entidade" (unidades), "Atendente", "Status" ("Em aberto" = aguardando + em andamento, "Aguardando", "Em andamento", "Aguardando CSAT", "Finalizada", "Importada"), "Responsável" ("Humano", "IA passiva", "IA de campanha"), "SLA" ("Estourado", "Dentro do SLA", "Sem SLA"), caixa "Somente IA"; chips dos filtros ativos ("Período:", "Canal:", "Entidade:", "Status:", "Responsável:", "Atendente:", "SLA:", "Busca:", "Atendente: Somente IA") com "Limpar tudo", ou "Nenhum filtro aplicado"; "N conversas". Deep links aceitos: `startDate`, `endDate`, `channelType`, `entityId`, `classId`, `sectorId`, `attendantId`, `status`, `owner`, `slaStatus`, `openOnly`, `sortBy`, `sortOrder`, `id` (abre o drawer).
  - Tabela: caixa de seleção (tooltip "Selecionar todas as conversas desta página" / "Selecionar conversa (varre as conversas em aberto deste contato)"), "ID" (#8 chars, copiar: `ID {x} copiado`), "Contato" (nome e telefone), "Canal" (ROOKIE → "WhatsApp"/"ROOKIE", WABA → "WA Business"/"WABA", widget → "Chat Widget"/"WEB"; tooltips "WhatsApp não oficial (Whatsmeow) — conexão via QR Code", "WhatsApp Business API oficial da Meta", "Chat embedável em sites (widget web)"), "Entidade", "Status" (tooltips: "Aguardando resposta do cliente", "Conversa em andamento com troca ativa de mensagens", "Aguardando o cliente responder à pesquisa de satisfação (CSAT)", "Conversa encerrada — sem mais interações esperadas", "Conversa importada de histórico anterior — não houve interação na plataforma"), "Responsável" (nome do atendente + "Atendente"; "IA passiva"/"Sem humano"; "IA de campanha"/"Outbound"; tooltips "Atendente humano: {nome}", "Atendimento conduzido pela IA passiva (sem intervenção humana)", "Conversa iniciada por uma campanha outbound e conduzida pelo Tino"), "Início" (ordenável), "Duração" (verde até 8 min, vermelho a partir de 120 min), "SLA" ("Estourado", "No prazo", "Ativo", "—"), "Última mensagem". Paginação "Mostrando…" / "Exibir" 25, 50, 100. Vazio: "Nenhuma conversa encontrada" + "Tente ajustar os filtros ou ampliar o período de busca." + "Limpar filtros".
  - Barra de seleção: "N conversa(s) selecionada(s)", "Limpar seleção", "Finalizar selecionadas".
  - Modal "Finalizar conversas" (`BulkFinishModal.vue`): "N conversa(s) selecionada(s)", "Todas as conversas **em aberto** dos contatos selecionados serão marcadas como **Finalizadas** — incluindo conversas antigas presas em aberto. Esta ação não pode ser desfeita.", "Motivo (opcional)" (placeholder "Ex.: Limpeza de conversas antigas em aberto", até 500 caracteres, contador), "Cancelar", "Finalizar"/"Finalizando...". Resultado: "N conversa(s) finalizada(s) em M contato(s)." ou "Nenhuma conversa em aberto encontrada para os contatos selecionados."; erro "Erro ao finalizar conversas.".
  - Drawer de detalhe (`DetailDrawer.vue`): cabeçalho com iniciais, nome, telefone, "#id", entidade, link "abrir no inbox →", botão de compartilhar (tooltip "Copiar link de compartilhamento"; toast "Link copiado"; link `/conversations?id=…`), fechar (Esc). Abas "Conversa" (transcrição somente leitura; "Nenhuma mensagem encontrada"), "Resumo & auditoria" ("Resumo gerado pelo Scout" + texto, "Avaliação CSAT" com estrelas e comentário, ou "Nenhuma análise do Scout disponível para esta conversa"; "Consumo de IA" com "Créditos", "Chamadas IA" e por categoria: "Atendimento passivo", "Campanhas", "Scout", "Indexação RAG", "Consulta RAG", "Copilot", "Qualificação", "Scout — Feedback", "Transcrição", "Mapeamento", "Chat"; "Notas internas (N)" ou "Nenhuma nota interna nesta conversa"; "Avaliações (N)"), "Metadados" ("SLA · Estourado/No prazo/Alerta/Ativo" com "Xmin / Ymin" e barra; "Tempos": "Início", "Encerrado", "Duração", "Motivo do encerramento"; "Informações": "ID da conversa", "Status", "Canal", "Entidade", "Setor"; "Responsável": "Atendente humano", "Inteligência artificial" ou "Campanha outbound"). Aviso para importadas: "Conversa importada" — "Esta conversa foi importada do histórico do WhatsApp e não aconteceu dentro do Tartini — por isso não há mensagens, atendente, métricas ou SLA para exibir. Para acompanhar o histórico completo e ter métricas e relatórios precisos, conduza os atendimentos pelo Tartini.". Rodapé "Visualização em **modo auditoria** · somente leitura".
- **Fluxos:** buscar/filtrar; abrir o drawer clicando na linha; "abrir no inbox →" leva a `/inbox/{contactId}`; "Exportar CSV" baixa `conversas-AAAA-MM-DD.csv` com os filtros atuais ("CSV exportado com sucesso." / "Erro ao exportar CSV."); encerrar em massa: marcar linhas > "Finalizar selecionadas" > motivo > "Finalizar".
- **Regras:** a finalização em massa mira o contato de cada conversa selecionada e encerra todas as conversas em aberto dele; "Em aberto" no filtro de status viaja como `openOnly`.
- **Incertezas:** colunas exatas do CSV (backend); regra "Somente IA" vs. "Responsável" (o front manda `aiOnly` e ignora `attendantId` quando marcado).

## Componentes de conversas usados fora desta área

- `components/conversations/Card.vue` (cartão de conversa avaliada: "Tino"/"Passiva"/"Ativa", "atendeu {cliente}", "Seguiu processo"/"Divergência no processo", "Scout: 8.5", "Gestor: 9.0", "Detalhes →", "Descartar avaliação"/"Repor nas médias") e `components/conversations/Messages.vue` (painel "Conversa Completa", "N mensagens", somente leitura) são usados nas telas do Scout (`/scout/evaluations`), fora deste inventário.

---

## Redirecionamento (`/redirect/inbox/...`)

- **Para que serve:** página intermediária que mostra o carregamento por 1,5 a 2,5 s e então leva a `/inbox{resto do caminho}` preservando a query. Usada por links externos/deep links.
- **Quem vê:** exige login (middleware); sem outro gate.
- **Incerteza:** de onde esses links são gerados (e-mails, webhooks) não está no front.

---

## Mensagens Rápidas (`/settings/quick-replies`)

- **Como chegar:** menu principal > "Configurações" > seção "Atendimento" > "Mensagens Rápidas" ("Crie e gerencie suas respostas rápidas para agilizar o atendimento.").
- **Para que serve:** cadastrar atalhos "/atalho" que inserem textos prontos no campo de mensagem do Inbox.
- **Quem vê:** todos os usuários (a rota não tem gate); a matriz de visibilidade marca 🔒 para gestores de área/unidade e atendentes (veem as suas e as da empresa). Só gestor+ (`canAccess('MANAGER')`) pode criar, editar, excluir e reordenar as mensagens "Da empresa"; para os demais elas aparecem como "Somente leitura".
- **O que há na tela (`pages/settings/quick-replies/index.vue`):** título "Mensagens Rápidas", "Configure atalhos de mensagens para agilizar o atendimento. Use `/atalho` no campo de digitação para inserir mensagens pré-definidas.", botão "Nova mensagem"; grupos "Minhas mensagens" ("Atalhos pessoais, visíveis apenas para você.") e "Da empresa" ("Atalhos compartilhados com toda a equipe."); tabela "Atalho" (`/atalho`), "Conteúdo" (até 80 caracteres), "Ações" ("Editar", "Deletar" > "Confirmar"/"Cancelar"); arrastar as linhas reordena dentro do grupo. Vazio: "Nenhuma mensagem rápida cadastrada." + "Criar primeira mensagem".
- **Modal (`components/settings/QuickReplyModal.vue`):** "Nova Mensagem Rápida" / "Editar Mensagem Rápida"; "Visibilidade" ("Pessoal" — "Visível apenas para você." / "Da empresa" — "Compartilhada com toda a equipe."; só ao criar e só para gestor+; padrão "Da empresa" para gestor+, "Pessoal" para os demais; não muda depois de criada); "Atalho" (prefixo "/", placeholder "ex: finalização"; obrigatório; só letras, números, hífen e underscore: "O atalho é obrigatório." / "Use apenas letras, números, hífens ou underscores."); "Conteúdo" (placeholder "Digite o conteúdo da mensagem...", obrigatório); "Variáveis disponíveis": `{{nome_cliente}}` "Nome do cliente", `{{nome_atendente}}` "Nome do atendente" (clicar insere no fim); "Cancelar", "Criar"/"Salvar".
- **Mensagens:** "Mensagem rápida criada com sucesso.", "Mensagem rápida atualizada com sucesso.", "Mensagem rápida removida com sucesso.", "Erro ao carregar mensagens rápidas.", "Erro ao criar mensagem rápida.", "Erro ao atualizar mensagem rápida.", "Erro ao remover mensagem rápida.", "Erro ao reordenar mensagens rápidas.".
- **Fluxos:** criar; editar; excluir com confirmação inline; reordenar por arrastar; usar no Inbox digitando "/".
- **Regras:** o menu no Inbox filtra por prefixo do atalho (sem diferenciar maiúsculas); o cache de mensagens rápidas do Inbox é invalidado ao salvar aqui.
- **Incertezas:** limites de tamanho do conteúdo (não há validação no front); unicidade do atalho (backend).

---

## Regras transversais desta área

### Notificações e alertas (`composables/useNotificationSound.ts`, `useSystemNotifications.ts`, `useUnifiedNotifications.ts`, `useChannelUnpaired.ts`)
- Som (`/sounds/notification.mp3`) em toda mensagem recebida fora da conversa aberta; dentro da conversa aberta só quando a aba está em segundo plano.
- Toast dentro do app fora do Inbox: "Nova mensagem de {contato}" ou "Você recebeu uma mensagem, clique para ver." (máximo 3 toasts; clicar abre a conversa). Conversa atribuída: "Nova conversa atribuída a você: {contato} ({setor})".
- Título da aba: "(N) Tartini" e, em segundo plano, "(N) Nova mensagem!".
- Notificação do sistema operacional (preferência "Notificações do sistema" em Configurações > Pessoal > "Configurações de usuário"; padrão ligada; depende da permissão do navegador, pedida no primeiro clique da sessão): título = nome do contato, corpo = prévia da mensagem (até 120 caracteres) ou "Enviou uma mensagem."; "Conversa atribuída a você" — "{contato} — Setor: {setor}". Avisos na tela de usuário: "O navegador está bloqueando as notificações deste site... Libere em Configurações do site → Notificações..." e "Este navegador não suporta notificações do sistema.".
- "Receber notificações de todas as entidades" (mesma tela): recebe "Novo atendimento em {unidade}: {contato}" das outras unidades (clicar troca de unidade e abre a conversa) e o badge preto no botão de unidade; nada dessas conversas entra na lista da unidade atual.
- Canal deslogado: toast "Canal desconectado" — `O canal "{nome}" foi deslogado do WhatsApp. Clique aqui para refazer o pareamento via QR code.` (30 s; clicar leva a `/settings/channels/whatsapp-rookie`).

### SLA (`composables/useSlaMonitor.ts`)
- Configurado por canal em Configurações > Atendimento > "SLA de Atendimento" (gestor de área+). Estados: `ACTIVE` (dentro do limite), `WARNING` (próximo do limite), `BREACHED` (excedido), `CRITICAL`, `PAUSED` (fora do horário comercial), `RESOLVED` (some da tela). O monitor vive no layout do Inbox: bipe curto ao entrar em alerta e bipe mais grave ao estourar, repetido a cada 30 s enquanto houver estouro (mesmo em aba de fundo); relógio na lista, no cabeçalho e faixa vermelha na lista. Grupos não têm SLA.

### Encerramento automático e IA por canal (referências, fora do escopo)
- Regras de Conversa (Configurações > Atendimento): "Assinatura obrigatória", "Permitir mudança de assinatura", "Encerrar conversa automaticamente" com "Tempo por canal" ("Sem valor definido, o canal usa o padrão de 24 h."), "Ativar Scout ao finalizar conversa", "Copilot ativo por padrão em novas conversas".
- IA por canal: "O cliente para de responder" → follow-up do Tino ("Espera N min sem resposta, até N tentativas."); "A conversa fica parada" → "Tino se despede e encerra o atendimento. Vale só para conversas conduzidas pelo Tino — conversas com a equipe seguem a Finalização Automática, em Regras de Conversa." ("Encerra após N min de inatividade."); "Alguém chama fora do horário" → aviso automático.
- Pesquisa de Satisfação (empresa): "Coletar em", "Regra de disparo" ("Todas as conversas" / "Apenas conversas resolvidas"), "Canais Habilitados", "Tempo limite para resposta (minutos)" (padrão 60). A conversa fica em "Aguardando CSAT" nesse intervalo.

### Papéis: resumo do que muda no Inbox
| Papel | Inbox e conversa | Central | Mensagens rápidas |
|---|---|---|---|
| Dono / Admin da Empresa | tudo da empresa; chips de unidade; sem tour de onboarding (papel `ADMIN`) | empresa inteira | edita as da empresa |
| Gestor da Empresa | tudo da empresa; chips; tour | empresa inteira | edita as da empresa |
| Gestor de Área / de Unidade | escopo da subárvore (backend); chips se 2+ unidades; tour; pode abrir a campanha no painel e ver o link "Criar em Identidade › Operações" | subárvore | edita as da empresa (`canAccess('MANAGER')`) |
| Atendente | escopo próprio (backend); "Sua caixa" = as suas; tour; sem link de campanha; troca o status do contato, mas não cria a lista de status | só as conversas em que é o atendente | só as pessoais; as da empresa em "Somente leitura" |

"Exportar CSV" e "Finalizar selecionadas" na Central aparecem para todos; o backend aplica o mesmo recorte de papel a essas ações.

### Glossário curto
"Tino" (agente de IA da linha de frente), "Copilot" (assistente do atendente; "reativo" = chat de perguntas, "ativo" = sugere sozinho), "Scout" (avaliador de conversas), "Cérebro"/"Identidade" (base de conhecimento e configurações da IA), "Unidade"/"Entidade" (nó operacional; "Área" agrupa unidades), "Setor" (fila dentro da unidade), "Protocolo" (8 primeiros caracteres do id da conversa), "Handoff" (passagem IA → equipe), "Ficha" (mini CRM do contato), "Rookie" (WhatsApp por QR Code), "WABA" (WhatsApp oficial), "Chat Widget" (chat do site), "Importada" (conversa trazida do histórico do WhatsApp, sem interação na plataforma).

### Incertezas gerais
1. Recorte por papel da lista do Inbox e da Central é 100% backend; o front só sabe que existe.
2. Não há ação para devolver ao Tino uma conversa interrompida; nem envio manual de pesquisa CSAT.
3. Janela de 24 h do WhatsApp: tratada apenas na abertura de conversa por template (WABA); o comportamento de envio livre depois de 24 h dentro de uma conversa existente não é tratado no front.
4. `InboxNotesModal` (mobile > "Anotações") não existe no repositório.
5. `ContactInfoModal` no cabeçalho desktop e `CopilotContextModal` não têm gatilho.
6. Limites de tamanho para "Arquivo Individual" (exceto vídeo 15 MB) e para o conteúdo da nota da conversa/mensagem rápida não são validados no front.
7. Significado exato de "Abandonadas" (Agentes de IA) e de "Somente IA" (Central) é do backend.
8. Onde nascem os links `/redirect/inbox/...` não está no front.
