# Plano: Padronizador de Deltas JSON Incrementais

## 1. Objetivo

Permitir que o usuário cole deltas JSON do agente diretamente no arquivo de memória (`.md`),
incrementalmente (um após o outro, direto no Obsidian), e depois execute o script uma vez
por dia/semana para consolidar tudo em formato padronizado.

**Fluxo ideal:**
```
1. [Obsidian] Abre Memoria_Linux_Consultor.md
2. [Obsidian] Cola output JSON do agente (um novo delta)
3. [Obsidian] Fecha
4. [GUI] Clica "Padronizar" → extrai todos os deltas JSON pendentes → consolida tudo
```

---

## 2. Formato Atual vs. Formato de Entrada

### Formato atual (padronizado, o que já funciona):

```markdown
## ESTADO_ATUAL

### 2026-05-09

- [TAG] Discos NTFS fixos em /mnt/ssd_2tb
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado.

## CONTEXTO_RECENTE

### 2026-05-09

- Corrigida falha de montagem NTFS...
```

### Formato de entrada (o que o usuário cola):

O agente produz JSON:

```json
{
  "data": "2026-05-10",
  "ADD": [
    {
      "tag": "INFO",
      "text": "CPU Ryzen 9 9900X: limite térmico 85°C configurado (clima 30°C)."
    }
  ],
  "UPDATE": {
    "texto_antigo_exato": { "DEPOIS": "novo texto substituindo" }
  },
  "REMOVE": [
    "texto_exato_para_remover"
  ],
  "CONTEXTO_RECENTE": "Configurado thermal limit 85°C..."
}
```

### Formato de entrada realista (no .md):

O JSON pode estar colado de várias formas:

1. **Com backticks:**
   ```
   ```json
   { "data": "2026-05-10", "ADD": [...] }
   ```
   ```

2. **Sem backticks (JSON puro):**
   ```
   {
     "data": "2026-05-10",
     "ADD": [...]
   }
   ```

3. **Misto (texto + JSON):**
   ```
   O agente disse:
   ```json
   { ...delta... }
   ```
   ```

---

## 3. Lógica de Padronização

### 3.1. Extração de Deltas Pendentes

O script escaneia o arquivo e procura por blocos JSON válidos.

**Algoritmo:**
```
1. Leia todo o conteúdo do arquivo
2. Extraia todos os blocos JSON encontrados (com regex)
3. Tente parsear cada bloco com json.loads()
4. Valide se cada JSON é um delta válido (tem ADD, UPDATE, REMOVE)
5. Aplique cada delta em ordem (do primeiro pro último)
6. Limpe os blocos JSON extraídos (remova do arquivo)
7. Escreva o resultado
```

### 3.2. Regex de Detecção de JSON

**Padrão 1: JSON entre backticks**
```regex
```[jJ][sS][oOnN]\n([\s\S]*?)\n```
```

**Padrão 2: JSON puro (sem backticks)**
```regex
(\{[\s\S]*?\})
```

Com validação: o JSON deve conter pelo menos `"ADD"`, `"UPDATE"`, `"REMOVE"`.

### 3.3. Estratégia de Aplicação

Cada delta é aplicado em sequência, usando a lógica já existente (`_apply_delta_to_string`):

```
para cada delta_json em deltas_extraidos:
    conteudo = aplicar_delta(conteudo, delta_json)
```

### 3.4. Deduplicação

Ao extrair deltas, o sistema detecta duplicatas:

- Dois deltas com ADD de mesmo texto → adiciona apenas um
- UPDATE para texto que já não existe → ignora o UPDATE
- REMOVE para texto que já não existe → ignora o REMOVE

### 3.5. Limpeza Pós-Extração

Depois de aplicar os deltas:

1. Remove os blocos JSON extraídos
2. Remove linhas vazias consecutivas (>2)
3. Mantém a estrutura Markdown padronizada

---

## 4. GUI - Nova Interface

### 4.1. Novo Botão

Na barra de ações, adicionar:

```
[🔧 Padronizar] [📊 Extrair Todos] [💾 Aplicar]
```

### 4.2. Painel "Deltas Pendentes"

Ao clicar em "🔧 Padronizar":

1. O script escaneia o arquivo
2. Um painel lateral mostra os deltas encontrados:
   ```
   ╔══════════════════════════════════╗
   ║       DELTAS PENDENTES           ║
   ╠══════════════════════════════════╣
   ║ [1] 2026-05-09 - ADD 1, UPD 0   ║
   ║ [2] 2026-05-10 - ADD 1, REM 1   ║
   ║ [3] 2026-05-11 - ADD 0, UPD 2   ║
   ╚══════════════════════════════════╝
   ```

3. Cada delta pode ser:
   - Visualizado (clicar no número)
   - Excluído (não aplicar)
   - Editado (manualmente)

4. Ao clicar "Aplicar":
   - Todos os deltas válidos são aplicados em sequência
   - Preview diff mostra tudo
   - Backup criado
   - Arquivo atualizado
   - Blocos JSON removidos

### 4.3. Status da Janela

No rodapé:

```
🟢 Nenhum delta pendente  OU  🟡 3 deltas pendentes | Última padronização: 2026-05-10 14:32
```

---

## 5. Estrutura do Arquivo (.md)

O arquivo de memória agora suporta **duas zonas**:

```markdown
## ESTADO_ATUAL

### 2026-05-09

- [TAG] Entrada padronizada

## CONTEXTO_RECENTE

### 2026-05-09

- Resumo da sessão

---
# DELTAS PENDENTES (colar aqui, script padroniza)

```json
{
  "data": "2026-05-10",
  "ADD": [...],
  ...
}
```

```json
{
  "data": "2026-05-11",
  "ADD": [...],
  ...
}
```
```

O separador `---` indica o início da zona de deltas pendentes.

---

## 6. Arquitetura de Código

### 6.1. Nova Classe (ou método) no GUI

```python
class DeltaCollector:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.pending_deltas = []
        self.parse_errors = []

    def extract_pending_deltas(self) -> list[dict]:
        """Extrai todos os blocos JSON válidos do arquivo."""
        content = self.file_path.read_text(encoding="utf-8")

        # Padrão 1: JSON entre backticks (preferencial)
        pattern_backticks = r'```(?:json)?\n(.*?)\n```'
        matches = re.findall(pattern_backticks, content, re.DOTALL)

        deltas = []
        for match in matches:
            try:
                delta = json.loads(match)
                if self._is_valid_delta(delta):
                    deltas.append(delta)
            except json.JSONDecodeError:
                self.parse_errors.append(f"JSON inválido: {match[:50]}...")

        # Padrão 2: JSON puro (fallback)
        if not deltas:
            pattern_raw = r'\{[^{}]+(?:ADD[^{}]*UPDATE[^{}]*REMOVE|ADD[^{}]*REMOVE[^{}]*UPDATE|UPDATE[^{}]*ADD[^{}]*REMOVE)\}'
            matches = re.findall(pattern_raw, content, re.DOTALL)
            for match in matches:
                try:
                    delta = json.loads(match)
                    if self._is_valid_delta(delta):
                        deltas.append(delta)
                except json.JSONDecodeError:
                    self.parse_errors.append(f"JSON inválido: {match[:50]}...")

        return deltas

    def _is_valid_delta(self, delta: dict) -> bool:
        """Valida se o JSON é um delta válido."""
        required_keys = ["ADD", "UPDATE", "REMOVE"]
        return all(key in delta for key in required_keys)

    def apply_all_deltas(self) -> str:
        """Aplica todos os deltas pendentes em sequência."""
        content = self.file_path.read_text(encoding="utf-8")
        deltas = self.extract_pending_deltas()

        for delta in deltas:
            content = self._apply_delta_to_string(content, delta)

        return content

    def clean_pending_deltas(self, content: str) -> str:
        """Remove todos os blocos JSON pendentes do arquivo."""
        # Remove blocos entre backticks
        content = re.sub(r'```(?:json)?\n.*?\n```', '', content, flags=re.DOTALL)
        # Remove blocos JSON puro
        content = re.sub(r'\{[^{}]*(?:ADD|UPDATE|REMOVE)[^{}]*\}', '', content, flags=re.DOTALL)
        # Limpa linhas vazias consecutivas
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        return content.strip() + '\n'
```

### 6.2. Nova GUI Section (Tkinter)

```python
def setup_standardizer_ui(self):
    """Adiciona interface de padronização na GUI."""
    pad = {"padx": 5, "pady": 5}
    self.btn_standardize = ttk.Button(
        act_frame, text="🔧 Padronizar", command=self.standardize_file
    )
    self.btn_standardize.pack(side="left", fill="x", expand=True, padx=5)

    # Painel de deltas pendentes (inicialmente oculto)
    self.pending_panel = tk.Text(self, height=10, font=("Consolas", 10), wrap="word")
    self.pending_panel.pack(fill="both", expand=True, padx=10, pady=5)
    self.pending_panel.config(state="disabled")

    # Lista de deltas pendentes
    self.delta_listbox = tk.Listbox(self, height=5)
    self.delta_listbox.pack(fill="x", padx=10, pady=5)
    self.delta_listbox.pack_forget()  # Oculto até ter deltas

def standardize_file(self):
    """Escaneia e mostra deltas pendentes."""
    target = self.get_selected_file()
    if not target:
        return

    collector = DeltaCollector(target)
    deltas = collector.extract_pending_deltas()

    if not deltas:
        messagebox.showinfo("Padronização", "✅ Nenhum delta pendente encontrado.")
        return

    # Mostra painel com resumo
    self.pending_panel.config(state="normal")
    self.pending_panel.delete("1.0", "end")
    self.pending_panel.insert("1.0", f"📊 {len(deltas)} deltas pendentes encontrados:\n\n")

    for i, delta in enumerate(deltas):
        data = delta.get("data", "sem data")
        add_count = len(delta.get("ADD", []))
        upd_count = len(delta.get("UPDATE", {}))
        rem_count = len(delta.get("REMOVE", []))
        self.pending_panel.insert("end", f"[{i+1}] {data} - ADD {add_count}, UPD {upd_count}, REM {rem_count}\n")

    self.pending_panel.config(state="disabled")
    self.delta_listbox.pack(fill="x", padx=10, pady=5)

    # Habilita botão de aplicar
    self.btn_apply_standardize = ttk.Button(
        self, text="💾 Aplicar Padronização", command=self.apply_standardization
    )
    self.btn_apply_standardize.pack(fill="x", padx=10, pady=5)

def apply_standardization(self):
    """Aplica todos os deltas pendentes e limpa o arquivo."""
    target = self.get_selected_file()
    if not target:
        return

    backup = target.with_suffix(".backup")
    shutil.copy2(target, backup)

    collector = DeltaCollector(target)
    new_content = collector.apply_all_deltas()
    cleaned_content = collector.clean_pending_deltas(new_content)

    target.write_text(cleaned_content, encoding="utf-8")
    messagebox.showinfo("Sucesso", f"✅ Padronização aplicada!\nBackup salvo.")
```

---

## 7. Fluxo Completo de Uso

### 7.1. Primeiro Uso (criando o arquivo):

```markdown
## ESTADO_ATUAL

## CONTEXTO_RECENTE
```

Arquivo vazio, pronto para receber deltas.

### 7.2. Dia 1:

```markdown
## ESTADO_ATUAL

## CONTEXTO_RECENTE

---
# DELTAS PENDENTES

```json
{
  "data": "2026-05-09",
  "ADD": [
    { "tag": "INFO", "text": "CPU Ryzen 9 9900X: thermal 85°C configurado." }
  ],
  "UPDATE": {},
  "REMOVE": [],
  "CONTEXTO_RECENTE": "Configurado thermal limit..."
}
```
```

### 7.3. Dia 2:

```markdown
## ESTADO_ATUAL

## CONTEXTO_RECENTE

---
# DELTAS PENDENTES

```json
{
  "data": "2026-05-09",
  "ADD": [
    { "tag": "INFO", "text": "CPU Ryzen 9 9900X: thermal 85°C configurado." }
  ],
  "UPDATE": {},
  "REMOVE": [],
  "CONTEXTO_RECENTE": "Configurado thermal limit..."
}
```

```json
{
  "data": "2026-05-10",
  "ADD": [
    { "tag": "ATIVO", "text": "Servidor llama.cpp atualizado." }
  ],
  "UPDATE": {},
  "REMOVE": [],
  "CONTEXTO_RECENTE": "Atualizado servidor llama.cpp..."
}
```
```

### 7.4. Depois de "Padronizar":

```markdown
## ESTADO_ATUAL

### 2026-05-09

- [INFO] CPU Ryzen 9 9900X: thermal 85°C configurado.

### 2026-05-10

- [ATIVO] Servidor llama.cpp atualizado.

## CONTEXTO_RECENTE

### 2026-05-09

- Configurado thermal limit...

### 2026-05-10

- Atualizado servidor llama.cpp...
```

Arquivo limpo, pronto para receber novos deltas.

---

## 8. Detalhes Técnicos

### 8.1. Regex de Detecção

```python
# Padrão principal (JSON entre backticks)
BACKTICK_JSON = r'```[jJ][sS][oOnN]\s*\n(.*?)\n```'

# Fallback (JSON puro)
RAW_JSON = r'\{[\s\S]*?"data"\s*:\s*"[0-9-]+"[^{}]*"ADD"[^{}]*"UPDATE"[^{}]*"REMOVE"[^{}]*\}'
```

### 8.2. Validação de Delta

```python
def is_valid_delta(delta: dict) -> bool:
    """Valida se o JSON é um delta válido."""
    required_keys = ["ADD", "UPDATE", "REMOVE"]
    if not all(key in delta for key in required_keys):
        return False

    if not isinstance(delta.get("ADD"), list):
        return False
    if not isinstance(delta.get("UPDATE"), dict):
        return False
    if not isinstance(delta.get("REMOVE"), list):
        return False

    for item in delta.get("ADD", []):
        if not isinstance(item, dict) or "tag" not in item or "text" not in item:
            return False

    return True
```

### 8.3. Estratégia de Deduplicação

```python
def apply_delta_deduplicated(content: str, delta: dict) -> str:
    """Aplica delta com deduplicação."""
    for item in delta.get("ADD", []):
        if item["text"] not in content:
            content = _add_item_to_content(content, item)

    for old_text, new_info in delta.get("UPDATE", {}).items():
        if old_text in content:
            content = content.replace(old_text, new_info.get("DEPOIS", new_info))

    for text_to_remove in delta.get("REMOVE", []):
        content = re.sub(rf'-\s*\[.*?\]\s*{re.escape(text_to_remove)}', '', content)

    return content
```

### 8.4. Limpeza Final

```python
def clean_pending_deltas(content: str) -> str:
    """Remove todos os blocos JSON pendentes."""
    # Remove blocos entre backticks
    content = re.sub(r'```[jJ][sS][oOnN]\s*\n.*?\n```', '', content, flags=re.DOTALL)
    # Remove blocos JSON puro
    content = re.sub(r'\{[^{}]*"data"[^{}]*"ADD"[^{}]*"UPDATE"[^{}]*"REMOVE"[^{}]*\}', '', content, flags=re.DOTALL)
    # Limpa linhas vazias consecutivas
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    return content.strip() + '\n'
```

---

## 9. Riscos e Mitigações

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| JSON inválido colado | Bloco não aplicado | Validação com feedback visual |
| Duplicatas | Entrada repetida | Deduplicação automática |
| UPDATE para texto inexistente | Ignorado | Log de avisos |
| Remove muito agressivo | Dados perdidos | Preview obrigatório |
| Arquivo muito grande | Performance lenta | Limitar a 200 deltas pendentes |
| Conflito de datas | Ordem errada | Ordenar por data antes de aplicar |

---

## 10. Roadmap de Implementação

### Fase 1: Motor de Padronização (Core)
- [x] `DeltaCollector` class com `extract_pending_deltas()`
- [x] Regex de detecção (backticks + JSON puro)
- [x] Validação de delta (`_is_valid_delta()`)
- [x] Aplicação sequencial com deduplicação
- [x] Limpeza pós-extração (`clean_pending_deltas()`)
- [ ] Testes unitários

### Fase 2: Integração GUI
- [x] Novo botão "🔧 Padronizar"
- [x] Painel de deltas pendentes (`pending_panel`)
- [x] Preview diff consolidado (`_show_diff_window`)
- [x] Aplicação com backup (`apply_standardization()`)
- [x] Status "x deltas pendentes" (`status_lbl`)

### Fase 3: Melhorias
- [ ] Log de operações (o que foi aplicado, o que foi ignorado)
- [ ] Modo automático (sem preview)
- [ ] Suporte a múltiplos arquivos
- [ ] Histórico de padronizações

---

## 11. Decisões de Design

| Decisão | Escolha | Alternativa | Razão |
|---------|---------|-------------|-------|
| Onde colar deltas | No próprio .md | Arquivo separado | Mais orgânico |
| Como detectar | Regex + JSON parse | AST | Simplicidade |
| Ordem de aplicação | Sequencial (top→bottom) | Por data | Preserva intenção do usuário |
| Limpeza | Automática pós-aplicação | Manual | Menos fricção |
| Deduplicação | Por texto exato | Por hash | Clareza |

---

## 12. Observações Finais

- **O GUI ainda serve para deltas individuais** (preview diff, validação imediata)
- **Padronização é para quando você quer batch processar vários deltas**
- **O formato padrão (com tags e datas) nunca muda** — é o "canon"
- **O sistema é 100% compatível com o GUI existente** — só adiciona uma via extra de entrada
- **A deduplicação é crucial** — evita que o arquivo fique gigante com entradas repetidas
- **O backup é obrigatório** — nunca se aplica sem backup prévio

---

*Pronto para implementação. Iniciar pela Fase 1 (Motor de Padronização).*