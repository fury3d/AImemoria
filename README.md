# Aplicador de Delta de Memória

Ferramenta gráfica segura para aplicar atualizações de memória geradas por agentes de IA.
Previne alucinações, duplicatas e mantém histórico consistente.

## 🚀 Instalação

**Linux (Arch/Ubuntu):**
```bash
# Instalar tkinter se não tiver
sudo pacman -S python-tk  # Arch
# ou
sudo apt install python3-tk  # Ubuntu/Debian

# Torna o script executável
chmod +x scripts/run_linux.sh
```

**Windows:**
- Certifique-se de ter o Python instalado (https://python.org)
- Marque "Add Python to PATH" na instalação
- O `.vbs` já cuida de rodar sem terminal

## ▶️ Como Usar

### Linux
1. Clique no ícone `Aplicador de Memória` no menu ou na área de trabalho.
2. Ou rode via terminal (se preferir): `./scripts/run_linux.sh`

### Windows
1. Dê duplo clique em `run_windows.vbs`
2. A janela abrirá instantaneamente, sem terminal.

---

## 🔄 Fluxo de Operação

### 1. Cole o Delta
- Puxe o output do agente (ex: `--- MEMORIA_DELTA...`)
- Cole na caixa de texto principal.

### 2. Gerencie Arquivos
- Clique em `➕ Adicionar` e selecione seu arquivo `.md`.
- A lista **persiste** entre usos (guarda no `~/.config/memoria_delta/`).

### 3. Validação (Opcional mas Recomendado)
- Clique em `🔍 Validar Delta`.
- O script verifica formato, IDs e limites antes de qualquer coisa.
- ❌ Rejeita deltas malformados ou com IDs inexistente.

### 4. Preview Diff
- Selecione o arquivo da lista.
- Clique em `👁️ Preview Diff`.
- Aparece uma janela colorida mostrando:
  - `-` em vermelho (será removido)
  - `+` em verde (será adicionado)

### 5. Aplicar
- Se o diff estiver correto, clique em `💾 Aplicar`.
- O script:
  1. Cria `.backup` do arquivo original (instantâneo).
  2. Escreve as mudanças.
  3. Confirma sucesso.

---

## 🛡️ Segurança & Anti-Alucinação

| Recurso | O que faz |
|---------|-----------|
| **Parsing Determinista** | Só aceita `--- MEMORIA_DELTA` exato. |
| **Validação de IDs** | Se o agente inventar `#99` que não existe, o script ignora. |
| **Limites Duros** | Máximo 5 ADDs, 3 UPDATES, 3 REMOVES por delta. |
| **Backup Automático** | `Memoria.backup` criado milissegundos antes da escrita. |
| **Diff Preview** | Você vê exatamente o que vai mudar antes de confirmar. |

---

## 🔧 Solução de Problemas

**Janela não abre?**
- *Linux:* Verifique se `python3-tk` está instalado.
- *Windows:* O Python está no PATH? Tente abrir `cmd` e digitar `pythonw`.

**Arquivo não aparece na lista?**
- Use `➕ Adicionar` e navegue até o `.md`. Ele salva no `~/.config/memoria_delta/`.

**Delta foi rejeitado?**
- Verifique se o agente usou o formato correto do prompt `v5_unified`.
- IDs de UPDATE/REMOVE devem existir no arquivo original.

---

## 📂 Estrutura de Arquivos

```
scripts/
├── memoria_delta_gui.py      ← Código principal
├── run_windows.vbs            ← Launcher Windows (sem console)
├── run_linux.sh               ← Launcher Linux
└── run_linux.desktop          ← Ícone de desktop Linux
```

## 🧠 Dicas
- Use o `Preview Diff` sempre. É sua última linha de defesa contra alucinações.
- O app guarda seus arquivos favoritos. Não precisa selecionar toda hora.
- Se errar feio, basta renomear `Memoria.backup` pra `Memoria.md`.

---
🚀 Como Usar

### Linux
```bash
# 1. Instalar dependencia
sudo pacman -S python-tk   # Arch
# ou
sudo apt install python3-tk # Debian/Ubuntu

# 2. Tornar executavel
chmod +x scripts/run_linux.sh

# 3. Rodar (3 opcoes)
./scripts/run_linux.sh              # Terminal quick
python3 scripts/memoria_delta_gui.py # Direto
# Ou crie atalho .desktop na area de trabalho
```

Para o ícone `.desktop` funcionar, edite o arquivo e coloque o caminho absoluto:
```ini
Exec=python3 /home/gilliard/Cofre_Obsidian/Obsidian/Memória/AIChat/scripts/memoria_delta_gui.py
```

Depois copie pro seu menu:
```bash
cp scripts/run_linux.desktop ~/.local/share/applications/
```

### Windows
1. Instale Python (marque "Add to PATH")
2. Dê duplo clique em `run_windows.vbs`
3. Janela abre sem terminal

---

## ✅ Fluxo Final

```
1. Agente gera /memoria → Delta aparece
2. Abre Aplicador de Memória
3. Cola o delta
4. Clica "Validar" → Checa formato/IDs
5. Clica "Preview Diff" → Vê o que muda (verde/vermelho)
6. Clica "Aplicar" → Backup + Escreve + Confirma
```

---

## 🛡️ Proteções Anti-Alucinação

| Camada | O que faz |
|---|---|
| **Parsing Determinista** | Só aceita `--- MEMORIA_DELTA` |
| **Validação de IDs** | UPDATE/REMOVE só funcionam se ID existir |
| **Limites Duros** | Máx 5 ADD, 3 UPDATE, 3 REMOVE |
| **Backup Automático** | `.backup` criado antes de escrever |
| **Diff Preview** | Você vê exatamente o que muda
