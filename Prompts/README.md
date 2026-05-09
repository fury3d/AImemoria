# Aplicador de Delta de Memória

Ferramenta gráfica segura para aplicar atualizações de memória geradas por agentes de IA.
Previne alucinações, duplicatas e mantém histórico consistente.

---

## 📦 Formato do Delta (JSON v5)

O agente produz um bloco JSON com esta estrutura:

```json
{
  "data": "2026-05-09",
  "ADD": [
    {
      "tag": "INFO",
      "text": "CPU Ryzen 9 9900X: limite térmico 85°C configurado."
    }
  ],
  "UPDATE": {
    "texto_antigo_exato": { "DEPOIS": "novo texto substituindo" }
  },
  "REMOVE": [
    "texto_exato_para_remover"
  ],
  "CONTEXTO_RECENTE": "Resumo curto da sessao para o contexto recente."
}
```

### O que cada chave faz:

| Chave | Formato | Efeito |
|-------|---------|--------|
| `data` | `"YYYY-MM-DD"` | Data para organizar as entries. Padrão: hoje se omitido. |
| `ADD` | `[{"tag": "...", "text": "..."}]` | Insere `- [TAG] texto` em `## ESTADO_ATUAL ### <data>` |
| `UPDATE` | `{ "texto_antigo": {"DEPOIS": "novo"} }` | Substitui bullets cujo conteúdo contém `texto_antigo` |
| `REMOVE` | `["texto_para_remover"]` | Remove bullets cujo conteúdo match (exato ou tag) |
| `CONTEXTO_RECENTE` | `string` | Adiciona entry em `## CONTEXTO_RECENTE ### <data>` |

### Tags válidas:

| Tag | Uso |
|-----|-----|
| `INFO` | Informações gerais |
| `ATIVO` | Recursos/configurações ativas |
| `TAG` | Tags de sistema/disco |
| `CRÍTICO` | Avisos importantes |
| `PENDENTE` | Itens pendentes |

---

## 🚀 Instalação

**Linux (Arch/Ubuntu):**
```bash
# Instalar tkinter se não tiver
sudo pacman -S python-tk          # Arch/CachyOS
sudo pacman -S tk tcl              # Se tk separada
# ou
sudo apt install python3-tk        # Ubuntu/Debian

# Torna o script executável
chmod +x scripts/run_linux.sh
```

**Windows:**
- Certifique-se de ter o Python instalado (https://python.org)
- Marque "Add Python to PATH" na instalação
- O `.vbs` já cuida de rodar sem terminal

---

## ▶️ Como Usar

### Linux
1. Clique no ícone `Aplicador de Memória` no menu ou na área de trabalho.
2. Ou rode via terminal: `./scripts/run_linux.sh`

### Windows
1. Dê duplo clique em `run_windows.vbs`
2. A janela abrirá instantaneamente, sem terminal.

---

## 🔄 Fluxo de Operação

### 1. Cole o Delta JSON
- Puxe o output JSON do agente.
- Cole na caixa de texto principal.

### 2. Gerencie Arquivos
- Clique em `➕ Adicionar` e selecione seu arquivo `.md`.
- A lista **persiste** entre usos (guarda no `~/.config/memoria_delta/`).

### 3. Validação
- Clique em `🔍 Validar Delta`.
- O script verifica:
  - JSON válido
  - Chaves obrigatórias (`ADD`, `UPDATE`, `REMOVE`)
  - Estrutura dos ADD items (`tag` + `text`)
- ❌ Rejeita deltas malformados.

### 4. Preview Diff
- Selecione o arquivo da lista.
- Clique em `👁️ Preview Diff`.
- Aparece uma janela colorida mostrando:
  - `+` em **verde** (será adicionado)
  - `-` em **vermelho** (será removido)

### 5. Aplicar
- Se o diff estiver correto, clique em `💾 Aplicar (com Backup)`.
- O script:
  1. Cria `.backup` do arquivo original (instantâneo).
  2. Escreve as mudanças.
  3. Confirma sucesso.

---

## 📁 Estrutura da Memória

O arquivo `.md` é organizado assim:

```markdown
## ESTADO_ATUAL

### 2026-05-09
- [TAG] Discos NTFS fixos em /mnt/ssd_2tb
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado.

### 2026-05-08
- [ATIVO] Servidor de IA migrado...

## CONTEXTO_RECENTE

### 2026-05-09
- Corrigida falha de montagem NTFS...
```

- **Seções**: `## ESTADO_ATUAL` e `## CONTEXTO_RECENTE`
- **Datas**: `### YYYY-MM-DD` dentro de cada seção
- **Entries**: `- [TAG] texto` sob cada data

---

## 🛡️ Proteções Anti-Alucinação

| Camada | O que faz |
|--------|-----------|
| **JSON Strict Parsing** | Valida schema JSON antes de aplicar. Sem parse = sem aplicação. |
| **Match de Conteúdo** | UPDATE/REMOVE só funcionam se encontrarem conteúdo existente. |
| **Backup Automático** | `.backup` criado milissegundos antes da escrita. |
| **Diff Preview** | Você vê exatamente o que muda antes de confirmar. |
| **Validação de Tipos** | ADD deve ser lista de objetos, UPDATE deve ser dict, REMOVE deve ser lista. |

---

## 🔧 Solução de Problemas

### Janela de Preview aparece em branco?
- O delta pode estar mal-formado (JSON inválido). Clique em "Validar" primeiro.
- Se validar mas diff for vazio, verifique que `ADD`/`UPDATE`/`REMOVE` têm conteúdo.

### Janela não abre?
- **Linux:** Verifique se `python3-tk`, `tk` e `tcl` estão instalados.
- **Windows:** O Python está no PATH? Tente abrir `cmd` e digitar `pythonw`.

### Arquivo não aparece na lista?
- Use `➕ Adicionar` e navegue até o `.md`. Salva no `~/.config/memoria_delta/files.json`.

### Delta foi rejeitado?
- Verifique se o JSON é válido (pode usar https://jsonlint.com/).
- As chaves `ADD`, `UPDATE`, `REMOVE` são obrigatórias.
- Cada item de `ADD` precisa de `"tag"` e `"text"`.

### Backup igual ao original?
- Isso era um bug do parser antigo (Markdown → IDs). Agora com JSON parsing, o delta é aplicado corretamente.
- Se ainda acontecer, verifique o JSON com "Validar" antes de preview.

---

## 📂 Estrutura de Arquivos

```
AIChat/
├── Memoria_Linux_Consultor.md      ← Arquivo de memória principal
├── Memoria_Linux_Consultor.backup  ← Último backup automático
├── README.md                        ← Este arquivo
├── scripts/
│   ├── memoria_delta_gui.py         ← Código principal (Tkinter)
│   ├── run_windows.vbs              ← Launcher Windows (sem console)
│   ├── run_linux.sh                 ← Launcher Linux
│   └── run_linux.desktop            ← Ícone de desktop Linux
└── Prompts/                         ← Prompts do agente
```

---

## 💡 Dicas

- **Use sempre o Preview Diff** — é sua última linha de defesa contra alucinações.
- **O app guarda seus arquivos** — não precisa selecionar o `.md` toda vez.
- **Se errar feio** — renomeie `Memoria.backup` pra `Memoria.md` para reverter.
- **Mantenha o arquivo pequeno** — use `REMOVE` para limpar entries obsoletas e mantenha abaixo de 200 linhas.
- **Datas automáticas** — se omitir `"data"` no JSON, usa a data de hoje.

---
