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
   ````
   ```json
   { "data": "2026-05-10", "ADD": [...] }
   ```
   ````

2. **Sem backticks (JSON puro):**
   ```
   {
     "data": "2026-05-10",
     "ADD": [...]
   }
   ```

3. **Misto:**
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

O separador `---` indica o início da zona de deltas
</think>

<tool_call>
<function=edit_file>
<parameter=display_description>
Create detailed implementation plan for incremental JSON-delta collector/standardizereltas JSON do agente diretamente no arquivo de memória (`.md`), 
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
   ````
   ```json
   { "data": "2026-05-10", "ADD": [...] }
   ```
   ````

2. **Sem backticks (JSON puro):**
   ```
   {
     "data": "2026-05-10",
     "ADD": [...]
   }
   ```

3. **Misto:**
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

O separador `---` indica o início da zona de deltas