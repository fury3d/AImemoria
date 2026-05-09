# SISTEMA DE MEMÓRIA PARA AGENTES — v2.0

## COMANDO `/memoria`

Quando o usuário digitar `/memoria` ou qualquer variação abaixo, **INTERROMPA** o comportamento normal e responda **EXCLUSIVAMENTE** com o bloco de memória formatado.

Não dê dicas de terminal. Não explique nada. Não continue o fluxo anterior. **SOMENTE** o bloco.

**Reconhece:** `/memoria` · `/salvar` · `/save` · `/salva` · `memoriza` · `guarda` · `guarda isso` · `salva isso` · `snapshot` · `/memo` · `/m`

---

## 📐 ESTRUTURA DE SAÍDA OBRIGATÓRIA

### 1️⃣ ANTES DE RESPONDER — Validação Interna (não exibir)

Execute este checklist antes de gerar qualquer saída:

- [ ] Este fato ainda é verdade **agora** (não foi desfeito depois)?
- [ ] Já existe no estado atual do documento? (se sim → SKIP)
- [ ] É estado permanente ou debugging passageiro? (se passageiro → SKIP)
- [ ] Sobreviveria a um restart do projeto? (se não → SKIP)

### 2️⃣ BLOCO DE SAÍDA — Formato Único

Responda **SOMENTE** com este formato:

```
## MEMORIA_DELTA
```

### data: YYYY-MM-DD

## ADD
- [CRÍTICO|ATIVO|INFO|PENDENTE] categoria: fato conciso (≤1 linha)

## UPDATE
- [ANTES] texto exato existente
- [DEPOIS] texto novo que substitui

## REMOVE
- texto exato a ser removido

## CONTEXTO_RECENTE
- 1-3 linhas densas sobre o que aconteceu **esta sessão**

````

Se **NADA** relevante: responda apenas `✓ Nada novo para memorizar.`

---

## 🧠 REGRAS DE OURO

### Estado, não episódio

| ❌ Errado | ✅ Certo |
|---|---|
| `decidimos usar FastAPI porque...` | `Stack: FastAPI + PostgreSQL` |
| `testei e o CORS tava quebrado, resolvi com middleware` | nada (correção já está implícita no estado) |
| `o usuário pediu pra mudar a cor pra azul` | `Preferência UI: cor primária = azul` |

### O que memoriza

- **Configurações vigentes** (stack, paths, URLs, credenciais mascaradas)
- **Decisões técnicas atuais** (com trade-off resumido)
- **Problemas conhecidos + soluções permanentes**
- **Pendências e próximos passos** (que ainda não foram feitos)
- **Preferências permanentes do usuário** (estilo, ferramentas, workflows)
- **Pessoas relevantes ao projeto**

### O que NÃO memoriza

- ~~Debugging passageiro~~
- ~~Brainstorming que não virou decisão~~
- ~~Tarefas concluídas~~
- ~~Conversa emocional ou Small Talk~~
- ~~Benchmarks e números que não serão consultados~~
- ~~Senhas, tokens, chaves reais~~
- ~~**Qualquer coisa que JÁ está no documento**~~

---

## 📏 LIMITES E QUALIDADE

| Métrica | Limite |
|---|---|
| Itens em `ADD` | máx 5 por chamada |
| Itens em `UPDATE` | máx 3 por chamada |
| Itens em `REMOVE` | máx 3 por chamada |
| `CONTEXTO_RECENTE` | máx 3 linhas |
| Comprimento por item | máx 120 caracteres |

**Se um item não cabe em 120 caracteres, ele não é atomico o suficiente.** Quebre ou reformule.

---

## 🏷️ TAGS E SEU SIGNIFICADO

| Tag | Uso |
|---|---|
| `[CRÍTICO]` | Quebra o projeto se esquecido (configs, paths, secrets refs) |
| `[ATIVO]` | Em andamento agora (não concluído) |
| `[PENDENTE]` | A fazer (decisão tomada, execução pendente) |
| `[INFO]` | Fato permanente do projeto (stack, preferências, convenções) |
| `[OBSOLETO]` | Deveria sair na próxima consolidação (raramente usado diretamente) |

---

## 🔄 COMANDO `/consolidar`

**Reconhece:** `/consolidar` · `consolida` · `limpa memória` · `compacta` · `resumo geral`

### Instrução

Use o conteúdo de memória disponível no contexto. **reescreva COMPLETO** — SUBSTITUIÇÃO, não acréscimo.

### Regras de Consolidação

1. **ESTADO_ATUAL:** só o que é verdade **AGORA**
2. **CONTEXTO_RECENTE:** últimas 5 sessões que importam
3. **HISTÓRICO_RESUMIDO:** uma linha por fato antigo relevante
4. Itens `[OBSOLETO]` → **removidos**
5. Tarefas concluídas → **removidas**
6. Duplicatas → **versão mais atual**
7. Documento final: **máximo 200 linhas**
8. Se passar, corte `HISTÓRICO_RESUMIDO` primeiro

### Formato de Saída do `/consolidar`

```
## ESTADO_ATUAL

### Por categoria (ex: Infra, Stack, Preferencias, Pendencias)

- [TAG] item consolidado

## CONTEXTO_RECENTE

### Ultimas 5 sessões

- data: resumo denso 1-2 linhas

## HISTÓRICO_RESUMIDO

- data: fato antigo relevante em 1 linha
```

---

## 🗑️ COMANDO `/esquecer [tópico]`

Marque referências relacionadas a `[tópico]` para remoção na próxima consolidação.

**Confirme:** `🗑️ Marcado para remoção: [tópico]`

---

## 📊 COMANDO `/status`

Estime o tamanho atual da memória e avise se a consolidação é recomendada.

```
📊 MEMÓRIA STATUS
  Estado atual: X itens (Y linhas)
  Contexto recente: Z sessões
  Histórico: W entradas
  🟢/🟡/🔥 Recomenda consolidação: sim/não
```

---

## ✅ INTEGRIDADE

| Cenário | Comportamento |
|---|---|
| Memória diz X, usuário diz Y | Avise o conflito + pergunte qual é válido |
| Memórias vazias | Construa contexto gradualmente |
| Nenhuma memória no contexto | Converse normalmente; não finja lembrar |
| Item duplicado detectado | **SKIP** — não adicione novamente |

---

## 💡 DICAS PARA O AGENTE (internas)

1. **Pense em delta, não em dump:** o que MUDOU desde a última memória?
2. **Seja cirúrgico:** cada item deve ser atomico e independente
3. **Valida antes de emitir:** se o usuário já tem isso, silêncio é ouro
4. **Preferencia implícita > explícita:** se o usuário sempre escolhe X, memorize X como preferência
5. **Categorize por utilidade futura:** "eu gostaria de saber isso daqui 6 meses?"