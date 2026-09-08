# 06 · Métricas (e indicadores da Página Inicial)

Inventário das telas da área **Métricas** do Tartini (dashboard Nuxt 3 + Vue 3) e dos blocos de indicadores da **Página Inicial**, levantado só a partir do código do clone da `main` de 03/09/2026 (`tartini-web`). Tudo o que está entre aspas ou em negrito é texto da interface transcrito literalmente do código (inclusive caixa baixa, "·", "→", "—" e reticências). Onde o comportamento depende do backend e o front não o define, está marcado como incerteza.

Arquivos lidos: `pages/metrics/{index,overview,service,ai}.vue`, `pages/home.vue`, `pages/index.vue`, `layouts/metrics.vue`, `components/metrics/**`, `components/dashboards/{LiveNowStrip,PeriodEfficiency,PeriodFlow,MetricComparison,MetricDetailPanel,AiLiveStrip,AiComparison,AiCopilot,AiDetailPanel}.vue`, `components/home/**`, `components/shared/{Sidebar,SidebarToggleButton,SubscriptionBanner,CreditGateBanner,Loading}.vue`, `components/inbox/MobileMenu.vue`, `composables/{useMetricsFilters,useMetricsScope,useMetricsSidebar,usePeriodRange,useHomeDashboard,useOnboarding,useOnboardingProgress,usePlanGate,useCreditGate,useSubscription}.ts`, `services/{conversation-metrics,dashboard,token-usage,attendant-feedback,users,company,sector}.service.ts`, `stores/{dashboard,auth}.store.ts`, `types/metrics.ts`, `utils/{metricsGoals,duration,signalGrid,entitlements,onboardingHelp}.ts`, `middleware/auth.global.ts`, `docs/visibilidade-por-papel.md`, `docs/value-ux-proposal.md` (proposta; nada dela foi registrado como implementado), `docs/gtm-plan.md`, `CLAUDE.md`, `DESIGN_SYSTEM.md`.

---

## Base comum da área Métricas (vale para as três telas)

### Como chegar
- Menu lateral principal (desktop, largura ≥ 1024px): item **Métricas** (tooltip "Métricas", ícone de gráfico de barras). Leva a `/metrics/overview`. O item só aparece para gestor+ (`requires: 'manager'` → `auth.canAccess('MANAGER')`).
- `/metrics` (raiz) redireciona para `/metrics/overview`.
- Dentro da área existe uma segunda barra lateral (card flutuante de 288px, cabeçalho **Métricas**) com o submenu, nesta ordem: **Panorama** (`/metrics/overview`), **Operação** (`/metrics/service`), **Tino** (`/metrics/ai`).
- No topo de cada tela há um botão de menu (tooltip **Abrir menu** / **Fechar menu**) que recolhe ou expande essa segunda barra. O estado recolhido/expandido é compartilhado entre as três telas durante a sessão.
- Abaixo de 1024px (tablet/celular): a barra lateral principal não é renderizada e o menu inferior do celular tem só **Início**, **Inbox**, **Unidade** e **Config** (não há entrada "Métricas"). A área aparece com um cabeçalho fixo **Métricas** e um botão de hambúrguer que abre uma gaveta com cabeçalho **Métricas** e os mesmos três itens. Ou seja, no celular só se chega a Métricas por URL direta ou por links de outras telas (ex.: na Página Inicial do gestor, **ver detalhes por hora →**, **ver desempenho →** e a ação **ver dashboard →** do painel "precisa de você", todos para `/metrics/service`).
- Outros atalhos: no Panorama, os cards **Operação** e **Tino** têm o link **acessar →** para `/metrics/service` e `/metrics/ai`.

### Quem vê (papéis)
- Guarda de rota (`middleware/auth.global.ts`, `managerPages`): `/metrics/overview`, `/metrics/ai` e `/metrics/service` exigem `auth.canAccess('MANAGER')` = gestor ou acima em qualquer nível do contexto (Empresa: `ADMIN`/`MANAGER`; Área: `MANAGER`; Unidade: `MANAGER`), por herança; `SYSTEM_ADMIN` sempre passa. Quem não atende (Atendente) é redirecionado para `/home`.
- Matriz oficial (`docs/visibilidade-por-papel.md`): Métricas = ✅ Dono da conta, Admin da Empresa, Gestor da Empresa; 🔒 Gestor de Área e Gestor de Unidade (veem só o escopo deles; o recorte é feito pelo backend); ❌ Atendente.
- Rótulos de papel na UI (`CLAUDE.md`): Administrador · Gestor da Empresa · Gestor de Área · Gestor de Unidade · Atendente. "Dono da conta" (`isSubscriptionAdmin`) não muda nada em Métricas; só importa para Faturamento.
- Raiz do recorte hierárquico (`useMetricsScope.computeRoot`): a trilha "empresa › área › unidade › atendente" começa no maior nível que o usuário administra:
  - `SYSTEM_ADMIN` ou `ADMIN`/`MANAGER` na Empresa → raiz = empresa (nome da empresa; fallback "Empresa"). Vê degraus **empresa** (travado), **área**, **unidade** (+ **atendente** onde existe).
  - `MANAGER` na Área → raiz = área (nome; fallback "Área"). Vê **área** (travado) e **unidade**.
  - `MANAGER` na Unidade → raiz = unidade (nome; fallback "Unidade"). Vê só **unidade** (travado).
  - Só `ATTENDANT` → raiz = o próprio usuário (fallback "Você"); na prática não chega às telas por causa do guard.
  - O degrau travado é exibido como pílula sem seta e sem clique ("mostrá-los travados seria oferecer uma escada sem degraus").
- O front avisa em `docs/visibilidade-por-papel.md` que isso é apresentação, não segurança: os cookies de papel são editáveis e quem protege é a API.

### Plano, créditos e bloqueios
- Nenhuma rota de `/metrics` está em `GATED_ROUTES` (`utils/entitlements.ts`), então não há "wall de upgrade" (PlanUpgradeWall) em Métricas.
- Único gate de plano na área: na tela **Tino**, as seções da IA autônoma só aparecem se `auth.hasFeature('ai.autonomous')` (`FEATURE.AI_AUTONOMOUS`). A seção do Copilot aparece sempre ("o Copilot existe em todos os planos"). Comentário do código: "essential não tem → nem chama, sem 403". O rótulo comercial do plano mínimo para as features gateadas é `UPSELL_MIN_PLAN_LABEL = 'Scale'`.
- `hasFeature` é "fail-open": se os entitlements ainda não foram carregados (sessão antiga), o front libera tudo e o backend é a autoridade; `SYSTEM_ADMIN` sempre passa.
- Faixas do layout (aparecem acima do conteúdo em todas as telas da área):
  - Assinatura inativa (status fora de `ACTIVE`/`COMPLETED`): **Sua assinatura não está ativa. Acesso em modo somente leitura.** (e o CSS global desabilita botões de escrita).
  - Gate de créditos (`GET /subscription/credit-gate`): **Créditos do mês esgotados - contrate mais para evitar interrupções** (estado BURST, amarelo) ou **Sem créditos disponíveis, incluindo a margem extra - contrate agora para evitar a parada** (estado BLOCKED, vermelho). Clicar leva a `/settings/billing/credits`.
- Consultar Métricas não consome créditos (nada no código faz isso).
- Não existe exportação (CSV/PDF) em nenhuma tela de Métricas.

### Barra de escopo (`MetricsScopeBar`, igual nas três telas)
Uma linha com: a **trilha hierárquica** à esquerda, a pílula **refinar** e a pílula **período** à direita; abaixo, quando há filtro ativo, a linha de **chips**.

1. **Trilha hierárquica** (degraus com rótulo em caixa baixa): **empresa** › **área** › **unidade** › **atendente**.
   - Valor exibido: nome escolhido; vazio mostra **todas** (área, unidade) ou **todos** (atendente). Botão com `aria-label` "Escolher {rótulo}".
   - Ao abrir um degrau: lista só daquele nível; campo de busca com placeholder "buscar área…" / "buscar unidade…" / "buscar atendente…" (o campo só aparece com mais de 7 opções ou quando já se digitou algo); primeira opção **Todas as áreas** / **Todas as unidades** (ou **Todas as unidades da área** quando há área escolhida) / **Todos os atendentes**; cada opção traz um subtexto à direita: "área", nome da área (para unidades; fallback "unidade") ou "atendente". Vazio: **Nada encontrado.** ou **Nada encontrado para “{busca}”.**
   - As unidades listadas cascateiam pela área escolhida. Escolher área ou unidade **limpa o atendente** (comentário: manter o nome produziria uma trilha contraditória, "área Financeiro › atendente da Central").
   - Fontes: `GET /company/classes-with-entities` (áreas + unidades), `GET /user/attendants` (atendentes ativos + quem já atendeu, escopado pela subárvore acessível; ordenados por nome; nome vazio vira "Sem nome"), `GET /v1/sectors` (setores).
   - O degrau **atendente** existe no Panorama e na Operação; na tela Tino a barra é montada com `show-attendant=false` (não há esse degrau).
2. **refinar** (ícone de sliders; mostra um contador com o número de recortes ativos). Popover:
   - Cabeçalho **canal** com link **limpar** (quando há recorte). Opções de múltipla escolha: **WhatsApp** (`ROOKIE`), **WhatsApp Business** (`WABA`), **Chat Widget** (`CHAT_WIDGET`). Nota: **nenhum marcado = todos os canais**.
   - Se a empresa tem setores: cabeçalho **setor**, opção **Todos** e a lista de setores (escolha única). Um setor lembrado no navegador que não exista mais é descartado silenciosamente.
3. **período** (a pílula mostra o rótulo do período: **Hoje**, **Esta semana**, "{Mês abreviado} {ano}" ex. "Set 2026", "{ano}" ex. "2026", ou o intervalo "dd/mm/aaaa → dd/mm/aaaa"; fallback **Personalizado**). Popover:
   - **rápido**: botões **Hoje**, **Esta semana**, **Este mês**.
   - **mês / ano específico**: pílula de mês com setas ‹ › e o nome do mês; quando o modo "mês" está ativo aparece um ✕ (title **desmarcar mês**) que deixa só o ano; pílula de ano com setas ‹ ›. Texto de apoio: **Ano inteiro selecionado.** (modo ano) ou **Selecionar um mês fixa o ano; ✕ deixa só o ano.**
   - **Personalizado**: dois campos de data ("→" entre eles) e botão **Aplicar** (desabilitado até as duas datas serem preenchidas). Presets, mês e ano não fecham o popover; só **Aplicar** ou clique fora. Ao entrar em Personalizado, os campos vêm semeados com a janela que já estava na tela.
4. **Chips de filtro ativo**: rótulo **filtros** seguido de chips "área {nome}", "unidade {nome}", "atendente {nome}", "canal {WhatsApp|WhatsApp Business|Chat Widget}", "setor {nome}", cada um com um ✕ (`aria-label`/title "Remover filtro {rótulo} {valor}"). Com mais de um chip aparece **limpar tudo**. O período nunca vira chip ("não existe 'sem período'").

### Cálculo das datas (`useMetricsFilters.dateRange`)
- **Default: Esta semana** (`period = 'week'`), a menos que o navegador tenha uma seleção salva.
- **Hoje**: início = fim = data local de hoje.
- **Esta semana**: do **domingo** da semana corrente (`now.getDate() - now.getDay()`) até hoje.
- **Mês** (Este mês ou mês específico): do dia 1 até hoje (mês corrente) ou até o último dia do mês (mês passado). "Este mês" força ano/mês correntes.
- **Ano**: de 1º de janeiro até hoje (ano corrente) ou até 31/12 (ano passado).
- **Personalizado**: as duas datas escolhidas.
- As datas vão para a API como `startDate`/`endDate` no formato `YYYY-MM-DD`, calculadas no **fuso do navegador**. O **período anterior** (base das variações "vs período anterior") "é calculado no backend (janela imediatamente anterior de mesma duração)"; o front não o calcula.
- Granularidade da série temporal dos gráficos: "ausente = automática (hora até 2 dias, dia acima)" (o front nunca envia `granularity`). Rótulos: "dd/MM" no dia, "HHh" na hora.

### Persistência de filtros
- Período (preset, ano, mês, datas personalizadas), canais e setor: salvos no navegador em `localStorage['tartini:metrics-filters']`, restaurados uma vez por carga de página, e **compartilhados pelas três telas** (é um estado único).
- Escopo da trilha (área/unidade escolhidas): compartilhado entre as três telas durante a sessão, mas **não** é salvo no navegador (some ao recarregar). É zerado automaticamente quando o usuário troca de empresa/unidade no contexto do app.
- Atendente em foco: local de cada tela (Panorama e Operação têm o seu; ao trocar de tela ele se perde).
- Ordenação e busca da tabela de atendentes, e o indicador escolhido no comparativo: locais do componente; voltam ao padrão quando o bloco é remontado.

### Camada de decisão e formatação (comum a todos os indicadores)
- Todo indicador vem num "envelope": valor atual (`current`), valor do período anterior (`previous`), variação % (`changePct`), prazo configurado (`goal`, só existe para a 1ª resposta e vem do prazo de SLA do canal, `sla_config`), `status` (`green`/`yellow`/`red`/`neutral`, só pintado quando há prazo de SLA), `outlier` e `sampleSize`.
- **Não existe "meta" cadastrável no produto.** Comentários do código: os alvos fixos que existiam no backend (15 min, 30 min, 20%, 10%, 90%) "eram invenção do backend e saíram"; "o único limite configurado no produto é o prazo de SLA do canal". A referência de tudo é o **período anterior**.
- Variação: rótulo longo "▲ 12,3% vs período anterior" (faixa de sinais); rótulo curto "▲ 12,3%" (grades densas; zero não mostra nada); nos cards de comparação e na home, "▲ 12%" (sem casas decimais). O sinal é sempre em módulo; a seta diz a direção.
- Cor da variação: melhora = verde (`ok-deep`), piora = âmbar (`atencao`); "nunca usa erro — piora de métrica é atenção, não perigo"; zero/sem base = cinza. Para tempos e taxas de atrito (1ª resposta, espera, atendimento, reaberturas, transferências) a polaridade é invertida (cair é bom). Volume não tem polaridade (cinza).
- Tempos: o valor exibido é a **mediana**, em "horário de atendimento" quando a empresa tem horário configurado (`business`), senão o tempo corrido (`total`). Formato `formatDuration` (minutos → texto): "0s", "45s", "2m 30s", "1h 5m", "1d 1h" (arredonda para o minuto; segundos só abaixo de 1h). Sub-linha "mediana 2m 30s · p90 8m 10s".
- Percentuais: 1 casa decimal com vírgula ("42,0%"); contagens em pt-BR ("1.240"). Nos cards de comparação: inteiro quando exato ("85%"), senão 1 casa.
- Prazo de SLA: pílula "sla ≤ 5m" (ou "sla ≥ 90%"), nunca "meta".
- `outlier` só é usado no veredito do Panorama (exclui o sinal). `sampleSize` só na comparação da IA (vira "N/A").

---

## Métricas (`/metrics`)
- **Como chegar:** menu **Métricas**.
- **Para que serve:** não é uma tela; redireciona (com `replace`) para `/metrics/overview` (Panorama).
- **Quem vê / Plano / O que há na tela / Fluxos / Regras / Termos / Perguntas / Incertezas:** ver Panorama.

---

## Panorama (`/metrics/overview`)
- **Como chegar:** menu **Métricas** > **Panorama** (é a tela de entrada da área). Cabeçalho: kicker "métricas · panorama", título **Panorama**.
- **Para que serve:** retrato executivo do período escolhido, juntando os números-âncora da Operação (equipe) e do Tino (IA), com uma frase-resumo, os pontos forte e de atenção, quatro gráficos e dois cards que são a porta de entrada das outras duas telas.
- **Quem vê:** gestor+ (ver base comum). A trilha começa no nível que o usuário administra; abaixo dele pode descer por área e unidade, e ainda focar um **atendente** (o degrau existe aqui). Gestor de Área/Unidade: recorte pelo backend.
- **Plano, créditos e bloqueios:** sem gate de plano no front. Atenção: o Panorama chama `GET /conversation-metrics/ai-overview` sem checar `ai.autonomous`, dentro de um `Promise.all`; se a API negar, a tela inteira cai no estado de erro (ver incertezas).
- **O que há na tela:**
  - **Barra de escopo** completa (trilha com **atendente**, **refinar**, **período**, chips).
  - Nota que aparece só com atendente em foco: **Recorte por atendente aplica-se à Operação; Tino é autônomo (sem atendente) e permanece no escopo do nível.**
  - **Carregando:** spinner com "Carregando" e a frase **Montando o retrato do período.**
  - **Erro:** **Não foi possível montar o Panorama** / **Houve uma falha ao carregar os números deste recorte. Tente novamente.** / botão **Tentar de novo**.
  - **Veredito do recorte** (uma linha + dois destaques):
    - Frase: `Tino absorveu {X}% da operação e resolveu {N} sozinho; o time conduziu {N} conversas com SLA em {X}%.` (X com 1 decimal, N inteiro).
    - Selo de direção (só quando há alguma comparação com período anterior): **melhorou** (verde), **em queda** (âmbar) ou **estável** (cinza).
    - Ponto forte (▲) e ponto de atenção (▼), cada um na forma **{Rótulo} em {valor}, {X}% acima do período anterior.** ou **... abaixo do período anterior.** Rótulos possíveis: **Absorção do Tino**, **Conclusão via processo**, **Aderência a SLA**, **1ª resposta**, **Tempo de atendimento**, **Reaberturas**, **Transferências**.
  - **Faixa de sinais** (4 cards separados por divisores): **conversas** (contagem; variação em cinza, sem polaridade), **absorvido pela ia** (%, em cobalto), **1ª resposta** (mediana; cair é bom), **aderência a sla** (%). Cada card mostra "▲ 12,3% vs período anterior" quando há base.
  - **Gráficos** (grade de 12 colunas):
    - **absorção do Tino** (8 colunas; gráfico-herói): linha (área em cobalto) da % de conversas absorvidas pela IA por bucket, eixo de 0 a 100%; o número grande no canto é a % do período inteiro (vem do KPI, não da média da série). Tooltip: "{rótulo}\n{X}% absorvido\n{ia} de {total} conversas" ou "{rótulo}\nsem conversas no período". Buckets sem conversa quebram a linha (não são zero). Vazio: **sem conversas no período**.
    - **canais** (4 colunas): barras horizontais em tinta, ordenadas por volume, com rótulos **whatsapp**, **whatsapp business**, **chat widget** (outros: rótulo do backend em caixa baixa) e "{n} · {p}%". Vazio: **sem dados de canal**.
    - **aderência a sla** (6 colunas): barras por bucket, eixo 0–100% (marcas de 25); número grande = aderência do período; linha tracejada de referência **período anterior {X}%** (sem casas decimais); barras abaixo dessa referência ficam âmbar; subtítulo **{n} abaixo do período anterior** (âmbar) ou **todos acima do período anterior** (verde). Tooltip: "{rótulo}\n{X}% de aderência\nabaixo do período anterior" / "acima do período anterior" ou "{rótulo}\nnenhum SLA decidido". Bucket sem SLA decidido não tem barra. Vazio: **nenhum SLA decidido no período**.
    - **quem conduziu** (6 colunas): barras empilhadas por bucket, legenda **equipe** (terracota) e **Tino** (cobalto). Tooltip: "{rótulo}\n{n} equipe\n{n} ia" e, quando o total supera equipe + IA, "\n{n} outras origens" (campanhas etc.). Vazio: **sem conversas no período**.
  - **Cards de área**:
    - **Operação** (link **acessar →** para `/metrics/service`): número grande = **contatos únicos**; mini-stats **espera / fila** (mediana), **atendimento** (mediana), **reaberturas** (%), **transferências** (%).
    - **Tino** (link **acessar →** para `/metrics/ai`): número grande = **resolvidas sozinho**; mini-stats **via processo** (%), **economia estimada** (horas: "12h" a partir de 10, senão "3,5h"), **1ª resposta do Tino** (mediana), **pico simultâneo** (inteiro).
- **Fluxos:**
  - Trocar período/canal/setor/área/unidade: qualquer mudança refaz as quatro chamadas (`service-overview`, `ai-overview`, `metric-series`, `channel-distribution`); durante o carregamento a tela inteira mostra o estado "Montando o retrato do período." Só a última requisição disparada pode escrever na tela (a mais lenta não sobrescreve).
  - Focar um atendente (degrau **atendente** ou chip): os números da Operação, os gráficos e o mix de canais passam a ser desse atendente; a visão da IA (`ai-overview`) continua no escopo do nível (a nota explica). O selo/frase misturam os dois recortes.
  - Descer o nível: escolher **área** e depois **unidade** na trilha; voltar escolhendo **Todas as áreas** / **Todas as unidades** ou removendo o chip. Não há comparação entre filhos aqui (isso fica em Operação e Tino).
  - Ir para as sub-telas: **acessar →** em cada card. O escopo e o período viajam junto (estado compartilhado); o atendente em foco não.
  - Não há exportação.
- **Regras e limites:**
  - Veredito: sinais considerados (com polaridade): absorção do Tino (+), conclusão via processo (+), aderência a SLA (+), 1ª resposta (−), tempo de atendimento (−), reaberturas (−), transferências (−). Volume fica de fora. Movimento favorável = `changePct × (invert ? −1 : 1)`; abaixo de 0,5% é ruído. Direção geral = saldo de sinais que melhoraram vs pioraram. Ponto forte = maior movimento favorável (> 0,5%); ponto de atenção = pior movimento (< −0,5%), nunca o mesmo sinal do ponto forte. Sinais marcados como `outlier` pelo backend ficam de fora.
  - Sem período anterior em nenhum sinal: sem selo e sem destaques.
  - Arredondamentos: contagens inteiras; percentuais 1 casa; horas 1 casa abaixo de 10.
- **Nomes e termos:** "absorvido pela ia" / "absorção do Tino" = % das conversas do período conduzidas pela IA ("{ia} de {total} conversas"); "resolvidas sozinho" = conversas resolvidas pela IA "sem nenhum humano na conversa"; "aderência a sla" = % dos SLAs decididos cumpridos; "1ª resposta" = mediana do tempo até a primeira resposta; "contatos únicos" = pessoas distintas atendidas; "via processo" = % das resolvidas pela IA concluídas do início ao fim por processo; "economia estimada" = horas da equipe poupadas (estimativa); "pico simultâneo" = conversas simultâneas da IA no instante mais movimentado; "Tino" = agente de IA da linha de frente; "equipe"/"time" = atendentes humanos.
- **Perguntas prováveis:**
  - "Por que o selo diz 'em queda' se o volume subiu?" O volume não entra no veredito; só qualidade (absorção, processo, SLA, tempos, reaberturas, transferências).
  - "Por que não vejo comparação?" Não há período anterior (ex.: base sem histórico) ou a variação de todos os sinais ficou abaixo de 0,5%.
  - "Filtrei por atendente e a % do Tino não mudou." Correto: o Tino não tem atendente; a nota da tela explica.
  - "Qual é a meta?" Não há meta cadastrável; só o prazo de SLA do canal, que aparece na Operação.
- **Incertezas:** definição exata no backend de "resolvida sozinho", "absorvido", "via processo", "economia estimada" e "pico simultâneo" (o front só exibe); como o backend interpreta `YYYY-MM-DD` (fuso do servidor vs. do usuário); comportamento em plano sem `ai.autonomous` (a chamada `ai-overview` é feita mesmo assim); definição de "outlier".

---

## Operação (`/metrics/service`)
- **Como chegar:** menu **Métricas** > **Operação**; ou Panorama > card **Operação** > **acessar →**; ou Página Inicial (gestor) > **ver detalhes por hora →** / **ver desempenho →** / alerta **ver dashboard →**. Cabeçalho: kicker "métricas · operação", título **Operação**.
- **Para que serve:** saúde operacional da equipe no período: o que está acontecendo agora, qualidade (SLA e tempos), volume e origem das conversas, e as pessoas (comparação entre áreas/unidades/atendentes e a tabela de atendentes).
- **Quem vê:** gestor+; trilha semeada pelo nível do usuário; degrau **atendente** disponível. Recorte por backend para Gestor de Área/Unidade.
- **Plano, créditos e bloqueios:** nenhum gate de plano no front.
- **O que há na tela** (blocos na ordem):
  1. **Barra de escopo** completa.
  2. **Painel ao vivo** (`DashboardsLiveNowStrip`), só quando o período alcança hoje (`endDate ≥ hoje`): kicker **ao vivo · a cada 30s**; ao lado, quando há SLA pendente, "sla {n} em alerta · {n} estourado"; badge **crítico** quando há SLA estourado. Quatro números do instante (sem recorte de data):
     - **em andamento** (`GET /in-progress-clients`); sub "{n} equipe · {n} ia" (quem conduz, via `owner-breakdown` com `status=IN_PROGRESS`) ou **sendo atendidas agora** / **nada aberto agora**; medidor em duas cores (equipe/ia).
     - **na fila** (`GET /pending-client-responses`); sub **aguardando 1ª resposta** ou **sem espera**; fica âmbar acima de 5; medidor com escala de 6.
     - **ia ativa** (= conversas em andamento conduzidas pela IA, `passiveAttendant`); sub **simultâneas, sem humano**; medidor com escala de 5.
     - **equipe online** ("{online}/{total}", `GET /online-attendants`); sub "{n} offline" ou **todos online**.
     - Saúde interna: "erro" se há SLA estourado (`breached + critical > 0`); "atenção" se há SLA em alerta ou fila > 15; só o badge **crítico** é exibido. Atualiza a cada 30s e a cada mudança de filtro. Respeita canal, área/unidade, atendente e setor.
  3. Seção **qualidade do atendimento** (hint **como estamos atendendo neste período**):
     - Gráfico **aderência a sla** (igual ao do Panorama).
     - Bloco **experiência e eficiência** (hint **mediana e p90, vs. período anterior**), grade de 6 indicadores:
       - **1ª resposta** (tempo; cair é bom). Único com prazo configurável: pílula **sla ≤ {tempo}** colorida pelo status (verde/âmbar/vermelho), medidor pintado pelo status com marcador do prazo (escala = prazo × 1,6; title "prazo de sla do canal: sla ≤ 5m").
       - **espera / fila** (tempo).
       - **até resolução** (tempo).
       - **aderência a SLA** (%).
       - **transferências ia→humano** (%; cair é bom).
       - **reaberturas** (%; cair é bom).
       - Cada um: valor, "▲ X%" curto, medidor (sem prazo: barra do valor atual e traço no período anterior, title **barra: período atual · traço: período anterior**; sem período anterior: trilho tracejado com title **sem período anterior para comparar**), e detalhe: tempos mostram "mediana X · p90 Y"; taxas mostram "período anterior: X%" (1 decimal) ou, sem base, o rótulo do prazo.
  4. Seção **volume e origem** (hint **quanto entrou, por onde e por iniciativa de quem**):
     - Gráfico **quem conduziu** com o total no canto: "{n} conversas".
     - Trio em um card só, dividido por fios: **canais** (igual ao Panorama), **quem começou** e **transferências**.
       - **quem começou** (`initiation` do `service-overview`): número grande "{X}% proativo" (terracota); barra empilhada; linhas **recebidas** ("o cliente procurou"), **iniciadas** ("a equipe procurou"), **iniciadas pela ia**, cada uma com a contagem; variação "▲ X% de proatividade" (title "proatividade vs. período anterior"); "{n} sem origem registrada" quando há conversas anteriores ao rastreio (elas ficam fora da taxa). Vazio: **sem conversas no período**.
       - **transferências** (`GET /transfer-stats`): "{n} no período"; uma barra por setor de destino (nome em caixa baixa) com a contagem. Vazio: **nenhuma transferência no período**.
  5. Seção **pessoas** (hint **quem atendeu — clique numa linha para focar a tela**):
     - **Comparativo entre níveis** (`DashboardsMetricComparison`), exibido só quando há nível abaixo, nenhum atendente em foco e mais de um filho (com um filho só o bloco some: "comparando a área consigo mesma"). Título: **Comparar áreas** / **Comparar unidades** / **Comparar atendentes - {unidade}**. Hint: **Clique numa área para descer o nível** / **Clique numa unidade para descer o nível** / **Clique num atendente para ver o detalhe**. Botão de voltar (`aria-label` **Voltar um nível**) quando não está na raiz. Seletor de indicador (pílulas): **SLA** (padrão), **1ª resposta**, **Atendimento**, **Volume**, **Iniciadas**, **Reaberturas**, **Transferências**. Um card por filho com: iniciais, nome, tipo ("área"/"unidade"/"atendente"), seta → (desce) ou ↗ (folha), valor, "▲ 12%" (0 casas), medidor (proporção contra o maior irmão, ou contra o prazo de SLA quando há), rodapé "antes {valor anterior}" e "#{posição} de {n}". Ranking: menor é melhor para tempos, Reaberturas e Transferências; maior é melhor para SLA, Volume e Iniciadas. Vazio: **Esta subdivisão não tem níveis abaixo para comparar.** Fonte: `GET /metric-matrix` com `groupBy` = nível filho.
     - **Tabela de atendentes** (`MetricsAttendantTable`, `GET /attendant-table`): kicker **atendentes** e "{exibidos} de {total}"; busca com placeholder **buscar atendente…** (rótulo acessível "Buscar atendente pelo nome"). Colunas, nesta ordem: **atendente**, **resolvidas**, **em andamento**, **1ª resposta**, **atendimento**, **csat** (+ coluna de ações sem título). Ordenação clicando no cabeçalho (padrão: resolvidas, decrescente; nome começa A→Z; numéricas começam do maior; `aria-sort` na coluna ativa). Linha: avatar com iniciais e ponto verde se online (title "{nome} está online"), status **online**/**offline**, resolvidas com barra proporcional ao maior da lista, em andamento, tempos como mediana em horário de atendimento (senão corrida) ou "—" sem amostra, CSAT "4,5 (12)" (nota com 1 casa e quantidade de respostas) ou "—". Linha inteira clicável (title **Ver todos os números de {nome}**; Enter/Espaço também) = focar a tela nesse atendente. Botão por linha (`aria-label` **Abrir conversas de {nome}**) abre a Central de Conversas filtrada em nova aba. Vazios: **Nenhum atendente com atividade no período.** ou **Nenhum atendente com “{busca}” neste escopo.** + link **limpar busca**. Com atendente em foco, rodapé: **a tela está focada em um atendente · esta lista segue mostrando todos** + botão **ver todos**. A tabela nunca recebe o filtro de atendente (de propósito: é o caminho de volta).
     - **Painel lateral do atendente** (`DashboardsMetricDetailPanel`, abre ao clicar num card de atendente no comparativo): diálogo (`aria-label` "Métricas de {nome}") com iniciais, nome e a linha de contexto (nomes da trilha do nível mais baixo ao mais alto, separados por " · ", sem a empresa; fallback "atendente"); botão **Fechar**. Destaque **aderência a sla** com valor, variação e legenda: **sem período anterior para comparar** / **estável — mesmo patamar de {X}%** / **acima do período anterior, que foi {X}%** / **abaixo do período anterior, que foi {X}%**. Linhas: **1ª resposta**, **Atendimento**, **Conversas**, **Iniciadas por ele**, **Reaberturas**, **Transferências**, cada uma com valor, "▲ X%", "antes {valor}" e medidor vs. período anterior (ou trilho tracejado). Só a 1ª resposta pode mostrar o rótulo "sla ≤ …". Botão fixo: **Ver as conversas deste atendente** (abre `/conversations?attendantId=…` em nova aba e fecha o painel).
- **Fluxos:**
  - **Filtrar por período**: pílula **período** > preset, mês/ano ou Personalizado > **Aplicar**. Recarrega KPIs, série e canais (`filterKey`), o comparativo, e os blocos que se buscam sozinhos (ao vivo, transferências, tabela). Em período passado o painel ao vivo some.
  - **Descer o nível (empresa > área > unidade > atendente)**: dois caminhos: (a) trilha: escolher **área**, depois **unidade**; (b) comparativo: clicar num card de área desce para ela (o título vira "Comparar unidades"), clicar numa unidade desce para ela ("Comparar atendentes - {unidade}"), clicar num atendente **não** desce: abre o painel lateral. Voltar: botão **Voltar um nível** do comparativo, ou os "Todas as…" da trilha, ou o ✕ do chip.
  - **Focar um atendente**: degrau **atendente** na trilha (busca por nome, sem precisar saber a unidade) ou clique na linha da tabela. Efeito: KPIs, gráficos, ao vivo, transferências e canais passam ao recorte da pessoa; o comparativo é escondido; a tabela segue listando todos com o rodapé explicativo. Sair: **ver todos**, o ✕ do chip "atendente", ou escolher outra área/unidade.
  - **Comparar períodos**: não há seleção de dois períodos; a comparação é sempre contra o período anterior de mesma duração (calculado no backend) e aparece como variação, "antes …", traço no medidor e linha de referência no gráfico de SLA.
  - **Abrir as conversas por trás do número**: ícone na linha da tabela ou botão do painel lateral → Central de Conversas (`/conversations?attendantId=…`) em nova aba; a Central lê esse parâmetro e pré-seleciona o atendente.
  - Não há exportação.
- **Regras e limites:**
  - Painel ao vivo: só com o período alcançando hoje; polling de 30s; snapshot sem data; "na fila" âmbar acima de 5; "crítico" com qualquer SLA estourado.
  - Tempos = mediana em horário de atendimento quando configurado (`business`), senão tempo corrido (`total`); "p90" = 90º percentil. "—" quando não há amostra ("'0s' se leria como atendimento instantâneo").
  - Prazo de SLA: só existe para a **1ª resposta** e vem da configuração do canal (Configurações > SLA); os demais indicadores não têm alvo.
  - Comparativo: some com um filho só ou com atendente em foco; medidor sem prazo é proporcional ao maior irmão; ranking usa a polaridade da métrica.
  - CSAT na tabela: nota média e quantidade de respostas da Pesquisa de Satisfação.
  - "sem origem registrada": conversas anteriores ao rastreio de quem iniciou; ficam fora da taxa de proatividade.
- **Nomes e termos:** "ao vivo" = estado neste instante; "em andamento" = conversas abertas sendo atendidas; "na fila" = aguardando 1ª resposta; "ia ativa" = conversas simultâneas conduzidas pela IA sem humano; "equipe online" = atendentes online / total; "1ª resposta" = tempo até a primeira resposta (mediana); "espera / fila" = tempo em fila; "até resolução"/"atendimento" = tempo até resolver (mediana); "aderência a SLA" = % de SLAs cumpridos; "transferências ia→humano" = % de conversas da IA passadas para a equipe; "transferências" (bloco) = transferências entre setores; "reaberturas" = conversas finalizadas que voltaram; "recebidas" = o cliente procurou; "iniciadas" = a equipe procurou; "iniciadas pela ia"; "proativo" = % de iniciadas sobre o total classificado; "resolvidas" = conversas resolvidas no período por atendente; "csat" = nota de satisfação.
- **Perguntas prováveis:**
  - "Onde vejo o SLA de agora?" No cabeçalho do painel ao vivo ("sla {n} em alerta · {n} estourado" e badge **crítico**); a aderência do período fica em "experiência e eficiência" e no gráfico.
  - "Por que o comparativo sumiu?" Há um atendente em foco, ou o nível atual tem só um filho, ou já se está no nível atendente sem filhos.
  - "Por que a tabela mostra todo mundo se filtrei um atendente?" De propósito; o rodapé avisa e o botão **ver todos** limpa o foco.
  - "Por que o tempo mostrado é diferente do da Página Inicial?" Aqui é a mediana em horário de atendimento (quando existe); na home a coluna "1ª resposta" usa a mediana em tempo corrido.
  - "Como comparo dois meses?" Escolhendo um mês na pílula de período; a variação já é contra o mês anterior.
- **Incertezas:** definições no backend de "resolvida", "reaberta", "transferência ia→humano" (denominador), "SLA decidido", "p90"; se o `sectorId` recorta por setor da conversa ou do atendente; fuso das datas; o que o backend devolve como `previous` quando o período personalizado não tem janela anterior completa; se Gestor de Unidade recebe `entityIds` recortados quando a trilha começa na unidade (o front manda `entityIds=[unidade]`).

---

## Tino (`/metrics/ai`)
- **Como chegar:** menu **Métricas** > **Tino**; ou Panorama > card **Tino** > **acessar →**. Cabeçalho: kicker "métricas · tino", título **Tino**.
- **Para que serve:** mostrar o que a IA (Tino) entregou no período: quanto da operação absorveu, velocidade e capacidade, onde rende mais entre áreas/unidades, e o apoio do Copilot ao time.
- **Quem vê:** gestor+. Trilha semeada pelo nível do usuário, **sem degrau de atendente** (as conversas da IA não têm atendente; filtrar por pessoa "zeraria absorção, velocidade e capacidade por construção"). O uso do Copilot por pessoa é alcançável pelo comparativo no nível atendente.
- **Plano, créditos e bloqueios:** as seções da IA autônoma (ao vivo, "o que Tino entregou", "velocidade e capacidade", "onde Tino rende mais" e o painel lateral) só aparecem com a feature `ai.autonomous`; sem ela as chamadas nem são feitas. A seção **apoio do copilot ao time** e os atalhos aparecem sempre.
- **O que há na tela** (na ordem):
  1. **Barra de escopo** sem atendente.
  2. **IA ao vivo** (`DashboardsAiLiveStrip`, só com feature e período alcançando hoje; `GET /ai-live` com `startDate = endDate = hoje` local, polling 30s): kicker **ia ao vivo · a cada 30s**; selo **fora do horário · ia no ar** (ícone de lua) quando o escopo está fora do horário de atendimento. Três números: **ia atendendo agora** (= respondendo + aguardando cliente; barra em dois tons; sub "{n} respondendo · {n} aguardando cliente"), **resolvidas hoje** (sub **100% pela ia, sem humano**), **passadas p/ humano hoje** (sub **ia → equipe**).
  3. Seção **o que Tino entregou** (hint **quanto da operação saiu das costas da equipe**):
     - Card `MetricsAiValue`: herói **absorvido pelo Tino** "{X}%" (cobalto) + "▲ X%" + **da operação do período**; quatro apoios: **resolvidas sozinho** (contagem; sub **sem nenhum humano na conversa**), **via processo** (contagem; sub "{X}% das resolvidas, do início ao fim"), **fora do horário** (contagem; sub "{X}% das conversas do Tino"), **economia estimada** (horas; sub **horas da equipe · estimativa**; sem variação, "uma seta nela sugeriria uma precisão que o número não tem").
     - Gráfico **absorção do Tino** (igual ao do Panorama).
  4. Seção **velocidade e capacidade** (hint **quão rápido responde e quanto segura ao mesmo tempo**), card `MetricsAiSpeedCapacity`:
     - **1ª resposta do Tino**: mediana; selo **praticamente instantânea** quando a mediana fica entre 0 e 0,5 min (~30s); "▲/▼ X%" (cair é bom); sub "mediana X · p90 Y".
     - **pico simultâneo**: "{n} conversas" + variação; sub **ao mesmo tempo, no instante mais movimentado**.
     - **até resolver**: duas barras, **ia** (cobalto) e **equipe** (terracota), com as medianas do tempo até a resolução; selo **{k}× mais rápido** quando a equipe leva pelo menos 1,1× o tempo da IA (1 casa até 10×, inteiro acima); sub **mediana do tempo até a resolução**.
  5. Seção **onde Tino rende mais** (hint **comparação entre os níveis abaixo**), só com mais de um filho. Card `DashboardsAiComparison` (`GET /ai-matrix`): título **Onde Tino rende mais - áreas** / **- unidades** / **- atendentes - {unidade}**; hints **Clique numa área para descer o nível** / **Clique numa unidade para descer o nível** / **No nível atendente, só o aceite do Copilot rende**; **Voltar um nível**; seletor **comparar por** (só quando o backend devolve mais de um indicador) com rótulos **Resolvidas**, **% absorvido**, **Fora do horário**, **Aceite Copilot**; cards com iniciais (cobalto), nome, tipo, valor ou **N/A** (sem amostra, ex.: métrica de conversa no nível atendente), "▲ X%", medidor proporcional ao maior irmão, "#{posição} de {n}" (maior é melhor em todas). Vazio: **Esta subdivisão não tem níveis abaixo para comparar.**
     - **Painel lateral** (`DashboardsAiDetailPanel`, ao clicar num atendente): nome, "{contexto} · uso do Tino", botão **Fechar**; destaque **aceite do copilot** "{X}%" + "▲ X%" + legenda "{n} aceitas de {n} decisões" ou **sem decisões de Copilot no período**; barra aceitas/dispensadas; linhas **Decisões do Copilot**, **Aceitas**, **- enviadas direto**, **- inseridas no rascunho**, **Dispensadas**, **Correções de conhecimento**; botão **Visualizar todas as conversas deste atendente** (nova aba, `/conversations?attendantId=…`).
  6. Seção **apoio do copilot ao time** (hint **quando a ia sugere e a equipe decide**), card `DashboardsAiCopilot` (`GET /copilot-stats`): **aceite das sugestões** "{X}%" (cobalto) + barra + "{n} aceita(s) · {n} dispensada(s)" + "{n} direto · {n} rascunho"; **correções de conhecimento** (contagem; sub **divergências da base sinalizadas ao time**); **cobertura** "{X}%" (sub "{n} de {n} atendentes com copilot ativo"). Vazio: **Sem atividade de Copilot neste período e escopo.**
  7. Seção **Tino também trabalha aqui** (hint **fora do que esta tela mede**): links **Processos & conteúdos do Tino** ("Tino gera os processos na Identidade") → `/identity/overview` e **Avaliações & feedbacks da IA** ("as avaliações feitas pela IA ficam no Scout") → `/scout/evaluations`.
  - Estados: só esqueletos de carregamento; **não há mensagem de erro** nesta tela (se a API falhar, o card de valor fica com "—" e os demais com zeros).
- **Fluxos:**
  - Filtrar por período/canal/setor/área/unidade: recarrega `ai-overview`, `metric-series`, `ai-matrix` (com feature) e `copilot-stats`.
  - Descer o nível: pela trilha (**área** › **unidade**) ou clicando num card do comparativo; no nível atendente, clicar abre o painel lateral com o uso do Copilot (sem mudar o escopo).
  - Comparar: seletor **comparar por** (os indicadores disponíveis vêm do backend; no nível atendente tende a sobrar só **Aceite Copilot**).
  - Não há exportação.
- **Regras e limites:**
  - "praticamente instantânea" = mediana ≤ 0,5 min (e > 0). "k× mais rápido" só a partir de 1,1×.
  - "N/A" = envelope sem amostra (`sampleSize = 0` e valor 0) ou ausente.
  - O painel ao vivo da IA usa a data local de hoje como início e fim.
  - "fora do horário" depende do horário de atendimento configurado (Cérebro > Operações > Disponibilidade); sem horário configurado, os tempos "business" vêm nulos e a tela usa o tempo corrido.
- **Nomes e termos:** "absorvido pelo Tino" = % das conversas do período conduzidas pela IA; "resolvidas sozinho" = resolvidas sem humano; "via processo" = resolvidas do início ao fim seguindo um processo; "fora do horário" = conversas da IA fora do horário de atendimento; "economia estimada" = horas de equipe poupadas (estimativa); "pico simultâneo" = máximo de conversas simultâneas da IA; "até resolver" = mediana do tempo até a resolução (IA vs equipe); "passadas p/ humano" = handoffs IA → equipe; "Copilot" = sugestões da IA ao atendente; "aceite" = % de sugestões aceitas sobre as decididas (aceitas + dispensadas); "direto" = sugestão enviada como estava; "rascunho" = inserida no campo de resposta para edição; "correções de conhecimento" = divergências da base sinalizadas pelo time; "cobertura" = % de atendentes com Copilot ativo.
- **Perguntas prováveis:**
  - "Só vejo a seção do Copilot." O plano não tem a feature `ai.autonomous` (IA na linha de frente); as demais seções ficam ocultas.
  - "Cadê o filtro de atendente?" Não existe aqui; para ver uma pessoa, desça até o nível atendente no comparativo e clique no card (uso do Copilot).
  - "Por que aparece N/A?" Não há amostra para aquele indicador naquele nível (ex.: conversas da IA não pertencem a atendentes).
  - "Por que a economia não tem seta?" É estimativa; o código evita sugerir precisão.
- **Incertezas:** fórmula da economia estimada, do pico simultâneo, da absorção, de "via processo" e de "fora do horário" (backend); se "cobertura" considera só atendentes ativos; se o Copilot ativo (feature `copilot.active`) afeta os números quando o plano não o tem; ausência de estado de erro (falha silenciosa).

---

## Página Inicial (`/home`) · indicadores

A Página Inicial (`pages/home.vue` e também `pages/index.vue` → `OnboardingHome`) mostra, quando o onboarding está concluído, um painel por papel: **GestorDashboard** para quem tem `canAccess('MANAGER')` e **AtendenteDashboard** para os demais. Enquanto o onboarding não está completo, o Admin vê o checklist (**Preparando sua operação**, "{n} de {m}") e os não-admins veem a tela de espera ("{nome}, sua empresa está sendo configurada"). Estados gerais: carregando (spinner "Carregando"), erro **Não foi possível carregar** / **Ocorreu um erro ao buscar os dados. Tente novamente.** / **Tentar novamente**. Abaixo, só os blocos de indicadores.

### Página Inicial do gestor (`/home`, `GestorDashboard`)
- **Como chegar:** menu **Página Inicial** (ícone de casa) ou após o login. Cabeçalho: botão-kicker "equipe/{escopo} · {data}" e título "{Bom dia|Boa tarde|Boa noite}, {primeiro nome}"; à direita, badge "{n} online" e botão **Abrir atendimento →** (→ `/inbox`).
- **Para que serve:** cockpit do gestor com o "agora", os números de hoje comparados a ontem, o pico do dia, a participação do Tino, os créditos de IA do mês e a equipe de hoje.
- **Quem vê:** gestor+ (por herança). Escopo: por padrão agrega **todas as unidades acessíveis** (`GET` das unidades do usuário; o backend intersecta com o que ele pode ver); sem lista, cai na unidade atual. O bloco de créditos exige `canAccess('MANAGER')` (sempre verdadeiro aqui). A troca de contexto (empresa/unidade) refaz tudo e volta ao agregado.
- **Plano, créditos e bloqueios:** campanhas só são consultadas com a feature `campaigns` (e, mesmo assim, o bloco de campanhas não é renderizado). Sem gate para os indicadores. Faixas de assinatura/créditos como no restante do app.
- **O que há na tela:**
  - **Filtro de escopo** (popover do kicker): cabeçalho "unidades ({n})"; **Todas as unidades · agregado** (só com mais de uma unidade) e a lista de unidades, com o marcador **atual** na escolhida. Rótulo do kicker: "equipe/{unidade em caixa baixa}" ou "equipe/todas as unidades ({n})". Fecha com clique fora ou Esc. Não é persistido.
  - **agora · tempo real** (ponto verde pulsante), quatro números grandes clicáveis:
    - **na fila** (`kpis.awaiting`); sub "espera média {n} min" ou **sem espera**; âmbar acima de 5; → `/inbox?filter=AWAITING`.
    - **em andamento** (`kpis.inProgress`); sub **sendo atendidas agora** / **nada aberto agora**; → `/inbox?filter=IN_PROGRESS`.
    - **resolvidas por ia** (`aiEffectiveness.aiResolvedAlone`, cobalto); sub **hoje, sem transferir** ou **agente sem conversas hoje**; → `/inbox?filter=FINISHED`.
    - **equipe online** (`onlineAttendants.online`, terracota); sub "de {n} atendente(s)" ou **só você**.
  - **precisa de você** (painel de alertas), itens gerados no front (`detectAnomalies`), nesta ordem:
    - Canal offline: "{n} de {m} canal está offline" / "canais estão offline" (crítico) → ação **ver canais →** (`/settings/channels/whatsapp-rookie`).
    - SLA: "{n} conversa em aberto com SLA estourado — parada há {idade}" / "{n} conversas em aberto com SLA estourado — a mais antiga parada há {idade}" (idade em "min", "h" ou "dia(s)", arredondada para baixo; crítico) → **ver conversas →** (`/conversations?slaStatus=BREACHED&openOnly=true&sortBy=lastMessageAt&sortOrder=asc`, que a Central lê).
    - Espera: **Tempo médio de espera acima de 15 min ({n} min)** quando a espera média > 15 (crítico) → **ver dashboard →** (`/metrics/service`).
    - Fila: "{n} clientes aguardando na fila" quando a fila > 10 (aviso) → **ver fila →** (`/inbox`).
    - Vazio: **Tudo em dia ✓** / **Nenhuma conversa esperando ação sua. A operação segue no ritmo.** / **abrir atendimento →**.
  - **hoje** ("comparado a ontem até este horário"), quatro cards:
    - **conversas** (`kpis.conversationsStarted.current`) com "▲ {X}% vs ontem" → `/inbox?filter=ALL`.
    - **resolvidas pela ia** (`aiResolvedAlone`) com barra = resolvidas pela IA ÷ conversas de hoje → `/inbox?filter=FINISHED`.
    - **concluídas** (`kpis.completedAttendances.current`) com "▲ {X}% vs ontem" → `/inbox?filter=FINISHED`.
    - **satisfação** (`averageCsat.average`, 1 casa; "—" sem nota) com "{n} resposta(s)" → `/scout/satisfaction`.
    - Regra do delta: some quando não há base (`changePct` nulo) ou quando atual e anterior são ambos < 5; verde = melhora, âmbar = piora, cinza = zero.
  - **operação** ("pico do dia e quem atende"):
    - Card **Pico de atendimento** ("hoje · conversas por hora"), total do dia + **hoje**. Barras por hora (da menor entre 8h e a primeira hora com dado até a hora atual), rótulos "08h", "09h"…; só o pico é colorido (cobalto = só IA, terracota = só equipe, gradiente = as duas, tinta = campanha/nenhuma); title de cada barra "{HHh} · {n} conversa(s) ({n} ia · {n} equipe)"; legenda "pico {horas} · {n} conversa(s)[ cada][ · ia|equipe|ia + equipe]" (empate no máximo = todas viram pico; se todas empatam, não há pico); link **ver detalhes por hora →** (`/metrics/service`). Vazio: **Sem conversas hoje** / **O movimento do dia aparece aqui, hora a hora, com o pico de atendimento marcado.**
    - Card **Tino em ação** (badge **ia/agente**): linhas **ia/agente**, **equipe/atendimento**, **campanhas** com "{n} · {p}%" (quem conduziu, `ownerBreakdown`); frase "Tino resolveu **{X}%** das conversas de hoje sem precisar da equipe." (X = resolvidas pela IA ÷ conversas de hoje, inteiro) ou **Tino ainda não conduz conversas.** + **ativar agente →** (`/settings/channel-ai`). Sem conversa nenhuma: **Tino ainda não conduz conversas** / **Ative o agente para Tino assumir o primeiro atendimento e passar para a equipe quando precisar.** / botão **Ativar agente ⇄**. Rodapé de custo (quando carregado): **créditos de ia · {mês por extenso}**, valor com 2 casas + **créditos**, link **ver consumo →** (`/settings/billing/credits`). Fonte: `GET /token-usage/summary` (mês corrente, unidades do escopo). "O cliente só enxerga créditos (nunca tokens/USD)".
    - Card **Equipe hoje** (badge "{online} de {total} online"; link **ver desempenho →** → `/metrics/service`). Colunas: **atendente**, **status**, **total**, **em andamento**, **concluídas**, **1ª resposta** (total e 1ª resposta somem no celular). Linha: iniciais, nome, **online**/**offline** (offline com opacidade reduzida), total = em andamento + concluídas, em andamento (ou "—" se offline e sem conversas), concluídas, 1ª resposta ("<1 min", "12 min", "1h 5m", "—"; mediana em tempo corrido). Clique (title "Ver atendimentos de {nome} na central de conversas") → `/conversations?attendantId=…` na mesma aba. Vazio: **Só você por aqui** / **Convide a equipe para dividir as filas e acompanhar quem atende o quê em tempo real.** / botão **Convidar atendentes** (`/settings/company/users`).
  - Erro do painel: **Não foi possível carregar os dados** / **Verifique sua conexão e tente novamente** / **Tentar novamente**.
- **Fluxos:** trocar a unidade no kicker refaz o fetch com `entityIds` da unidade; clicar nos números leva ao Inbox já filtrado (`filter=ALL|AWAITING|IN_PROGRESS|FINISHED`, lido pela barra lateral do Inbox), à Central de Conversas ou a Métricas > Operação; não há filtro de período (é sempre "hoje até agora") nem exportação. Os dados não se atualizam sozinhos (sem polling; só ao recarregar, trocar escopo ou contexto).
- **Regras e limites:** janela = do início do dia local (00:00 no fuso do navegador, enviado em ISO) até agora; o backend compara com a mesma janela de ontem (−24h) num único `GET /conversation-metrics/home-overview`; "em andamento" e "na fila" são snapshots sem data; "equipe online" e o "X de Y" vêm de presença (online real) sobre o time todo; "Equipe hoje" lista só quem atuou hoje (por isso as duas contagens não batem necessariamente); hora local das barras derivada de `hourStart` (UTC).
- **Nomes e termos:** "na fila" = aguardando resposta; "em andamento" = abertas em atendimento; "resolvidas por ia"/"resolvidas pela ia" = resolvidas pelo agente sem transferir; "concluídas" = atendimentos finalizados hoje; "satisfação" = nota média da Pesquisa de Satisfação; "ia/agente", "equipe/atendimento", "campanhas" = quem conduz a conversa; "créditos de ia" = consumo de IA do mês em créditos; "1ª resposta" = mediana do tempo até a primeira resposta.
- **Perguntas prováveis:** "Por que 'vs ontem' não aparece?" volume pequeno (< 5 nos dois dias) ou sem base. "Por que o total da equipe difere de 'equipe online'?" fontes diferentes (presença vs. quem atuou hoje). "Como vejo outro período?" Só em Métricas. "O que é 'agente sem conversas hoje'?" a IA não iniciou nenhuma conversa hoje (`aiStarted = 0`).
- **Incertezas:** definição de "resolvida sem transferir" e de "concluída" no backend; arredondamento do "{X}% vs ontem" (o front imprime o número que recebe); se o backend recorta `entityIds` para Gestor de Área/Unidade; fuso usado pelo servidor quando as datas não são enviadas.

### Página Inicial do atendente (`/home`, `AtendenteDashboard`)
- **Como chegar:** menu **Página Inicial** / após o login (quem não é gestor).
- **Para que serve:** as conversas do próprio atendente e o desempenho dos últimos 14 dias.
- **Quem vê:** quem não passa em `canAccess('MANAGER')` (Atendente).
- **Plano, créditos e bloqueios:** nenhum gate específico.
- **O que há na tela:**
  - Cabeçalho (`DashboardHero`): botão de contexto "{unidade/área/empresa}" (fallback **Sua operação**) que abre a troca de unidade; "{Bom dia|Boa tarde|Boa noite}, {nome}"; data por extenso; badges "{n} não lida(s)" e "{n} pendente(s)".
  - Seção **Minhas conversas**: card de satisfação ("{nota}/10", 5 estrelas, selo **Excelente** ≥ 8, **Bom** ≥ 7, **Regular** ≥ 5, **Precisa melhorar** abaixo, **Sem avaliação** sem nota; legenda **Nota média de avaliação**; fonte `GET /attendant-feedback/my-performance?period=14d`, campo `satisfactionScore` = "correção do gestor quando existe, senão a do Scout"); card **Pendentes** (contagem, **Aguardando resposta**, **Abrir inbox**) e card **Em andamento** (contagem, **Conversas ativas agora**, **Abrir inbox**), ambos → `/inbox`; fontes: contagem de conversas `AWAITING` e `IN_PROGRESS` do próprio atendente.
  - Seção **Meu desempenho** (selo **14 dias**): **Clientes atendidos**, **Tempo médio** (min), **Primeira resposta** (min; "< 1" abaixo de 1 min), e **Evolução diária** (linha dos últimos 14 dias) ou **Sem dados de evolução**. Fontes: `clients-attended-last-14-days`, `average-attendance-time-last-14-days`, `average-first-response-time-last-14-days`, `clients-attended-daily-last-14-days` (tempos em horário de atendimento quando há, senão corridos; aqui são **médias**, não medianas).
  - Erro: **Não foi possível carregar os dados** / **Verifique sua conexão e tente novamente** / **Tentar novamente**.
  - Observação: `QuickActions` ("Acesso rápido") é importado, mas não é renderizado.
- **Incertezas:** definição de "cliente atendido" e da média de tempo no backend.

### Indicador de maturidade ("Operação madura") — existe no código, não é exibido hoje
- `useHomeDashboard.operationalScore`: pontuação 0–100 = (canais online ÷ canais) × 40 (ou 20 fixos se não há canal) + 30 se há horário de operação configurado (algum horário ativo em Disponibilidade) + 30 se há ao menos 1 fonte na base de conhecimento. `systemStatus`: ≥ 80 → **Operação madura** / **Tudo certo**; ≥ 50 → **Requer atenção** / **Verifique configurações**; abaixo → **Requer atenção** / **Ação necessária**.
- `DashboardHero` só renderiza o anel de maturidade e o modal quando `role === 'gestor'` e recebe `systemHealth` + `operationalScore`; mas o painel do gestor não usa o `DashboardHero`, e o do atendente o chama com `role="atendente"`. Resultado: **nenhuma tela mostra o indicador** no código atual.
- Textos que existem para ele (caso volte): rótulos do anel **Madura** / **Em progresso** / **Inicial** (legenda **Maturidade**); modal com **Operação madura** ("Sua operação está otimizada e pronta para atender."), **Em progresso** ("Faltam alguns ajustes para otimizar sua operação."), **Configuração inicial** ("Configure os itens abaixo para começar a atender com eficiência."); itens **Canais de atendimento** (PESO 40%), **Horário de operação** (PESO 30%), **Base de conhecimento** (PESO 30%), com dicas como "Configure ao menos um canal para receber conversas", "Ative os {n} canais offline (+{x}%)", "Configure os horários de expediente para que o agente saiba quando a operação atende (+30%)", "Adicione documentos, Q&A ou websites para que Tino responda com mais precisão (+30%)"; ações **Configurar canais** / **Ver canais**, **Configurar horário** / **Ver configuração**, **Adicionar fontes** / **Gerenciar fontes**; rodapé **Canais ativos (40%) + Horário de operação (30%) + Base de conhecimento (30%)**.
- Também não são renderizados os widgets `AnomalyAlerts`, `MetricsGrid`, `HeroMetricCard`, `SystemHealthCard`, `TeamGrid`, `ConversationTrendChart`, `ConversationBreakdownChart`, `CampaignsSection`, `ChannelStatusSection`, `QualitativeFeedbackCard`, nem os `stats` de `GET /onboarding/status` (`totalConversations`, `activeConversations`, `conversationsToday`, `averageResponseTime`, `knowledgeBaseSources`, `indexedVectors`) guardados no `dashboard.store`.

---

## Glossário curto da área (como as telas chamam cada coisa)
- **Tino**: o agente de IA da linha de frente (cobalto). **equipe / time / atendente**: humanos (terracota). **ia/agente**: a IA conduzindo a conversa. **campanhas**: conversas iniciadas por campanha.
- **empresa › área › unidade › atendente**: a hierarquia do recorte ("descer o nível").
- **período** e **período anterior**: janela escolhida e a janela imediatamente anterior de mesma duração (backend).
- **ao vivo**: estado deste instante, atualizado a cada 30s.
- **mediana / p90**: valor central e 90º percentil dos tempos.
- **horário de atendimento**: disponibilidade configurada no Cérebro; tempos "business" descontam o que caiu fora dele.
- **prazo de sla** ("sla ≤ 5m"): único limite configurado no produto, do canal, aplicado à 1ª resposta. Não há "meta".
- **absorvido / absorção**: % das conversas conduzidas pela IA. **resolvidas sozinho**: sem humano. **via processo**: do início ao fim por processo. **fora do horário**: conversas da IA fora do horário de atendimento. **pico simultâneo**: máximo simultâneo da IA. **economia estimada**: horas poupadas (estimativa).
- **recebidas / iniciadas / iniciadas pela ia / proativo**: quem começou a conversa.
- **transferências ia→humano** (taxa) vs **transferências** (entre setores).
- **reaberturas**: conversas finalizadas que voltaram.
- **Copilot**: sugestões da IA ao atendente; **aceite**, **direto**, **rascunho**, **correções de conhecimento**, **cobertura**.
- **créditos de ia**: unidade de consumo mostrada ao cliente (nunca tokens/USD).

## Incertezas gerais (não confirmáveis no front)
1. Fórmulas do backend para todos os indicadores (absorção, resolvidas sozinho, via processo, fora do horário, economia, pico simultâneo, SLA "decidido", reaberturas, transferências, p90, "resolvida sem transferir", "concluída").
2. Fuso: Métricas envia datas `YYYY-MM-DD` do calendário local; a home envia ISO em UTC do dia local; o servidor pode interpretar no fuso dele ("Sem datas, o servidor assume 'hoje 00:00 até agora' no fuso do servidor").
3. Como o backend recorta para Gestor de Área/Unidade e o que devolve quando o front manda `companyId`/`classId`/`entityIds`.
4. Panorama em plano sem `ai.autonomous`: a chamada `ai-overview` é feita; se der 403, a tela inteira mostra erro.
5. `hasFeature` fail-open com entitlements ausentes: o front pode mostrar seções que a API negará.
6. Definição de `outlier` e de `sampleSize`.
7. `PERIOD_OPTIONS` ('Hoje', 'Semana', 'Mês', 'Personalizado') existe no composable, mas a barra de escopo não o usa; rótulos reais são os listados acima.
8. Arredondamento do "% vs ontem" na home (número cru do backend).
