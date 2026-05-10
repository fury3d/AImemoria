#!/usr/bin/env python3
"""
memoria_delta_gui.py - Aplicador Gráfico de Delta de Memória
Cross-platform (Linux/Windows), sem terminal, seguro contra alucinações.
Dependência: python-tk (Linux) ou Python instalado (Windows)
"""

import difflib
import json
import re
import shutil
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Caminho do config (arquivo oculto)
CONFIG_PATH = Path.home() / ".config" / "memoria_delta" / "files.json"


# ---------------------------------------------------------------------------
# Regex patterns for JSON extraction
# ---------------------------------------------------------------------------
# Padrão 1: JSON entre backticks (preferencial)
RE_BACKTICK_JSON = re.compile(r"```(?:json)?\s*\n(.*?)\n```", re.DOTALL)


def _is_valid_delta(delta: dict) -> bool:
    """Valida se o JSON é um delta válido."""
    if not isinstance(delta, dict):
        return False
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


class DeltaCollector:
    """Extrai e aplica deltas JSON pendentes a partir do arquivo .md."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.pending_deltas = []
        self.parse_errors = []

    # ------------------------------------------------------------------ #
    # Extraction
    # ------------------------------------------------------------------ #
    @staticmethod
    def _find_json_blocks(text: str) -> list[str]:
        """Encontra blocos JSON completos usando brace-matching.

        Rastreia profundidade de chaves para lidar com estruturas aninhadas.
        Retorna lista de strings JSON completas.
        """

        def skip_string(text: str, start: int) -> int:
            """Pula uma string JSON (entre aspas) e retorna posicao depois da aspa fechamento."""
            i = start + 1  # pula aspas abertura
            while i < len(text):
                if text[i] == '"':
                    return i + 1  # posicao depois da aspa fechamento
                if text[i] == "\\":
                    i += 2  # pula escape
                else:
                    i += 1
            return i  # fim do texto

        blocks = []
        i = 0
        n = len(text)
        while i < n:
            ch = text[i]
            # Pula strings fora de qualquer chave
            if ch == '"':
                i = skip_string(text, i)
                continue
            if ch == "{":
                start = i
                depth = 1
                i += 1
                while i < n:
                    c = text[i]
                    if c == '"':
                        # Pula conteudo de string dentro do JSON
                        i = skip_string(text, i)
                        continue
                    if c == "{":
                        depth += 1
                    elif c == "}":
                        depth -= 1
                        if depth == 0:
                            blocks.append(text[start : i + 1])
                            i += 1
                            break
                    i += 1
                continue
            i += 1
        return blocks

    def extract_pending_deltas(self) -> list[dict]:
        """Extrai todos os blocos JSON válidos do arquivo."""
        content = self.file_path.read_text(encoding="utf-8")
        deltas = []
        seen_positions = set()  # Evita duplicatas

        # Padrão 1: JSON entre backticks (preferencial)
        for match in RE_BACKTICK_JSON.finditer(content):
            json_str = match.group(1).strip()
            start_pos = match.start()
            if start_pos in seen_positions:
                continue
            try:
                delta = json.loads(json_str)
                if _is_valid_delta(delta):
                    deltas.append(delta)
                    seen_positions.add(start_pos)
            except json.JSONDecodeError:
                self.parse_errors.append(
                    f"JSON inválido (backticks): {json_str[:60]}..."
                )

        # Padrão 2: JSON puro via brace-matching (fallback)
        # Pula blocos ja extraidos (backticks)
        backtick_spans = set()
        for match in RE_BACKTICK_JSON.finditer(content):
            for pos in range(match.start(), match.end()):
                backtick_spans.add(pos)

        all_blocks = self._find_json_blocks(content)
        for block in all_blocks:
            if any(block.startswith(content[pos : pos + 5]) for pos in backtick_spans):
                continue  # Pula ja extraidos
            try:
                delta = json.loads(block)
                if _is_valid_delta(delta):
                    deltas.append(delta)
            except json.JSONDecodeError:
                self.parse_errors.append(f"JSON inválido (raw): {block[:60]}...")

        self.pending_deltas = deltas
        return deltas

    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    def apply_all_deltas(self, app_instance) -> str:
        """Aplica todos os deltas pendentes em sequência sobre o conteúdo."""
        content = self.file_path.read_text(encoding="utf-8")
        deltas = self.extract_pending_deltas()

        for delta in deltas:
            content = app_instance._apply_delta_to_string(content, delta)

        return content

    def apply_all_deltas_from_content(self, content: str, app_instance) -> str:
        """Aplica todos os deltas pendentes em sequência sobre o conteúdo dado."""
        deltas = self.pending_deltas  # already extracted
        for delta in deltas:
            content = app_instance._apply_delta_to_string(
                content, json.dumps(delta, ensure_ascii=False)
            )
        return content

    # ------------------------------------------------------------------ #
    # Cleanup
    # ------------------------------------------------------------------ #
    @staticmethod
    def clean_pending_deltas(content: str) -> str:
        """Remove todos os blocos JSON pendentes do conteúdo."""
        # Remove blocos entre backticks
        content = RE_BACKTICK_JSON.sub("", content)

        # Remove blocos JSON puro via brace-matching
        blocks = DeltaCollector._find_json_blocks(content)
        for block in blocks:
            try:
                delta = json.loads(block)
                if _is_valid_delta(delta):
                    content = content.replace(block, "")
            except json.JSONDecodeError:
                pass

        # Limpa linhas vazias consecutivas (>2)
        content = re.sub(r"(\n\s*){3,}", "\n\n", content)
        return content.strip() + "\n"


# ---------------------------------------------------------------------------
# GUI App
# ---------------------------------------------------------------------------
class MemoriaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Aplicador de Delta de Memória")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Carrega lista de arquivos
        self.config = self._load_config()

        # Variável para armazenar conteudo novo (p/ aplicar)
        self._pending_new_content = None

        self.setup_ui()
        self.update_file_list()

    def _load_config(self):
        if CONFIG_PATH.exists():
            try:
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return []
        return []

    def _save_config(self):
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def setup_ui(self):
        pad = {"padx": 5, "pady": 5}
        self.option_add(
            "*Font", "Segoe 10"
        ) if sys.platform == "win32" else self.option_add("*Font", "Sans 10")

        # HEADER
        hdr = ttk.Label(
            self,
            text="1. Cole o MEMORIA_DELTA do agente abaixo:",
            font=("", 10, "bold"),
        )
        hdr.pack(fill="x", padx=10, pady=(10, 0))

        # INPUT DELTA
        self.delta_text = tk.Text(self, height=15, font=("Consolas", 10), wrap="word")
        self.delta_text.pack(fill="both", expand=False, padx=10, pady=5)

        # FILE SELECTOR
        frm_files = ttk.LabelFrame(
            self, text="2. Escolha o Arquivo de Memória (persistente)", padding=5
        )
        frm_files.pack(fill="x", padx=10, pady=5)

        list_frame = ttk.Frame(frm_files)
        list_frame.pack(fill="both", expand=True)

        self.file_list = tk.Listbox(list_frame, height=4, selectmode=tk.SINGLE)
        self.file_list.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side="right", fill="y", padx=5, pady=5)
        ttk.Button(btn_frame, text="➕ Adicionar", command=self.add_file).pack(
            fill="x", pady=2
        )
        ttk.Button(btn_frame, text="➖ Remover", command=self.remove_file).pack(
            fill="x", pady=2
        )

        # ACTIONS
        act_frame = ttk.Frame(self)
        act_frame.pack(fill="x", padx=10, pady=10)

        self.btn_validate = ttk.Button(
            act_frame, text="🔍 Validar Delta", command=self.validate_delta
        )
        self.btn_validate.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_preview = ttk.Button(
            act_frame,
            text="👁️ Preview Diff",
            command=self.preview_diff,
            state="disabled",
        )
        self.btn_preview.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_apply = ttk.Button(
            act_frame,
            text="💾 Aplicar (com Backup)",
            command=self.apply_delta,
            state="disabled",
        )
        self.btn_apply.pack(side="left", fill="x", expand=True, padx=5)

        # PADRONIZAÇÃO
        std_frame = ttk.LabelFrame(
            self, text="Padronização de Deltas Pendentes", padding=5
        )
        std_frame.pack(fill="x", padx=10, pady=5)

        std_btn_frame = ttk.Frame(std_frame)
        std_btn_frame.pack(fill="x", padx=5, pady=5)

        self.btn_standardize = ttk.Button(
            std_btn_frame, text="🔧 Padronizar", command=self.standardize_file
        )
        self.btn_standardize.pack(side="left", fill="x", expand=True, padx=5)

        self.btn_apply_std = ttk.Button(
            std_btn_frame,
            text="💾 Aplicar Padronização",
            command=self.apply_standardization,
            state="disabled",
        )
        self.btn_apply_std.pack(side="left", fill="x", expand=True, padx=5)

        # Painel de deltas pendentes
        self.pending_panel = tk.Text(
            std_frame, height=6, font=("Consolas", 9), wrap="word", state="disabled"
        )
        self.pending_panel.pack(fill="x", padx=10, pady=5)

        # STATUS
        self.status_lbl = ttk.Label(
            self, text="Aguardando input...", foreground="gray", font=("Segoe UI", 9)
        )
        self.status_lbl.pack(fill="x", padx=10, pady=5, anchor="w")

    def update_file_list(self):
        self.file_list.delete(0, tk.END)
        for f in self.config:
            self.file_list.insert(tk.END, f)

    def add_file(self):
        path = filedialog.askopenfilename(
            title="Adicionar Arquivo de Memória", filetypes=[("Markdown", "*.md")]
        )
        if path and path not in self.config:
            self.config.append(path)
            self._save_config()
            self.update_file_list()

    def remove_file(self):
        sel = self.file_list.curselection()
        if sel:
            if messagebox.askyesno(
                "Remover", f"Remover {Path(self.config[sel[0]]).name} da lista?"
            ):
                self.config.pop(sel[0])
                self._save_config()
                self.update_file_list()

    def get_selected_file(self):
        sel = self.file_list.curselection()
        if not sel:
            messagebox.showwarning(
                "Seleção", "Selecione um arquivo de memória na lista."
            )
            return None
        return Path(self.config[sel[0]])

    # --- LOGICA DE NEGOCIO ---

    def validate_delta(self):
        raw = self.delta_text.get("1.0", "end-1c").strip()
        # Remove markdown backticks if present
        if raw.startswith("```json"):
            raw = raw[7:].split("```")[0].strip()
        elif raw.startswith("```"):
            raw = raw[3:].split("```")[0].strip()

        if not raw.startswith("{"):
            messagebox.showerror(
                "Validação",
                '❌ Formato inválido.\nDeve ser um bloco JSON válido.\n\nExemplo:\n{\n  "ADD": [],\n  "UPDATE": {},\n  "REMOVE": [],\n  "CONTEXTO_RECENTE": "..."\n}',
            )
            return False

        try:
            delta = self._parse_delta(raw)  # Checa se parse JSON não falha
            # Validação estrutural
            if "ADD" not in delta or "UPDATE" not in delta or "REMOVE" not in delta:
                raise ValueError("Chaves obrigatórias faltando (ADD, UPDATE, REMOVE).")

            self.status_lbl.config(
                text="✅ JSON válido estruturalmente. Selecione arquivo e veja o Preview.",
                foreground="green",
            )
            self.btn_preview.config(state="normal")
            self.btn_apply.config(state="disabled")  # Reseta apply
            return True
        except json.JSONDecodeError as e:
            messagebox.showerror("Validação", f"❌ JSON inválido:\n{e}")
            return False
        except Exception as e:
            messagebox.showerror("Validação", f"❌ Erro ao ler delta:\n{e}")
            return False

    def preview_diff(self):
        target = self.get_selected_file()
        if not target:
            return

        if not target.exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{target}")
            return

        raw = self.delta_text.get("1.0", "end-1c").strip()
        try:
            old_content = target.read_text(encoding="utf-8")
            self._pending_new_content = self._apply_delta_to_string(old_content, raw)

            # Abre janela de diff
            self._show_diff_window(old_content, self._pending_new_content)
            self.status_lbl.config(
                text="👁️ Preview gerado. Clique em 'Aplicar' para confirmar.",
                foreground="blue",
            )
            self.btn_apply.config(state="normal")
        except Exception as e:
            messagebox.showerror("Preview", f"Falha ao gerar diff:\n{e}")

    def apply_delta(self):
        target = self.get_selected_file()
        if not target:
            return

        if not self._pending_new_content:
            messagebox.showerror("Erro", "Gere o Preview antes de aplicar.")
            return

        backup = target.with_suffix(".backup")
        try:
            shutil.copy2(target, backup)
            target.write_text(self._pending_new_content, encoding="utf-8")

            messagebox.showinfo(
                "Sucesso",
                f"✅ Delta aplicado com sucesso!\n\nBackup salvo em:\n{backup.name}",
            )
            self.status_lbl.config(
                text=f"✅ Aplicado em {target.name} ({datetime.now().strftime('%H:%M:%S')})",
                foreground="green",
            )
            self.btn_apply.config(state="disabled")
            self.btn_preview.config(state="disabled")
        except Exception as e:
            messagebox.showerror(
                "Erro", f"❌ Falha ao aplicar:\n{e}\nBackup mantido em:\n{backup}"
            )

    # --- PARSING DETERMINISTICO ---

    def _apply_delta_to_string(self, content, delta_raw):
        """
        Aplica delta JSON (v5) sobre o arquivo Markdown de memória.

        Estrutura esperada da memória:
          ## ESTADO_ATUAL
            ### 2026-05-09
            - [TAG] entry
          ## CONTEXTO_RECENTE
            ### 2026-05-09
            - context entry

        delta_raw pode ser um dict já parseado ou uma string JSON.
        """
        lines = content.splitlines(keepends=False)
        # Aceita dict ou string JSON
        if isinstance(delta_raw, dict):
            delta = delta_raw
        else:
            delta = self._parse_delta(delta_raw)
        data = delta.get("data", datetime.today().strftime("%Y-%m-%d"))

        # 1. REMOVE (match de conteúdo nas bullets existentes)
        remove_list = delta.get("REMOVE", [])
        if remove_list:
            new_lines = []
            for l in lines:
                stripped = l.strip()
                if any(
                    rm.strip() == stripped.lstrip("- ") or f"[{rm.strip()}]" in stripped
                    for rm in remove_list
                    if rm.strip()
                ):
                    continue
                new_lines.append(l)
            lines = new_lines

        # 2. UPDATE (substitui texto antigo → novo nas bullets existentes)
        update_map = delta.get("UPDATE", {})
        if update_map:
            new_lines = []
            for l in lines:
                replaced = False
                for old_text, new_info in update_map.items():
                    if old_text.strip() and old_text.strip() in l:
                        if isinstance(new_info, dict):
                            new_after = new_info.get("DEPOIS", "")
                        elif isinstance(new_info, str):
                            new_after = new_info
                        else:
                            continue
                        prefix = re.match(r"^(\s*-\s*)", l)
                        if prefix:
                            new_lines.append(f"{prefix.group(1)}{new_after}")
                        else:
                            new_lines.append(new_after)
                        replaced = True
                        break
                if not replaced:
                    new_lines.append(l)
            lines = new_lines

        # 3. ADD (insere em ## ESTADO_ATUAL ### <data>)
        add_items = delta.get("ADD", [])
        if add_items:
            lines = self._add_items_to_state(lines, add_items, data)

        # 4. CONTEXTO_RECENTE (adiciona em ## CONTEXTO_RECENTE ### <data>)
        contexto = delta.get("CONTEXTO_RECENTE", "")
        if contexto:
            lines = self._update_context_recente(lines, contexto, data)

        return "\n".join(lines) + "\n"

    def _item_already_exists(self, content: str, text: str) -> bool:
        """Verifica se um texto ja' existe em qualquer bullet do conteudo.

        Compara o texto do ADD contra bullets existentes em todo o arquivo
        (nao' so' na data atual), ignorando prefixo [TAG].
        """
        # Extrai partes do texto para comparacao mais flexivel
        text_lower = text.lower().strip()
        if not text_lower:
            return True

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- "):
                continue
            # Remove prefixo "- " e [TAG] para comparacao
            bullet = stripped.lstrip("- ")
            # Pula [TAG] se presente
            tag_end = bullet.find("] ")
            if tag_end != -1:
                bullet = bullet[tag_end + 2 :]
            # Verifica se o texto ja' existe (substring ou igual)
            if text_lower in bullet.lower() or bullet.lower() in text_lower:
                return True
        return False

    def _add_items_to_state(self, lines, items, data):
        """Inserta ADD entries em ## ESTADO_ATUAL ### <data>.

        Deduplica: se o texto ja' existe em qualquer bullet do arquivo, pula.
        """
        content_text = "\n".join(lines)

        # Filtra itens duplicados
        unique_items = [
            it
            for it in items
            if not self._item_already_exists(content_text, it["text"])
        ]

        if not unique_items:
            return lines  # Todos duplicados, nada a fazer

        # Verifica se ## ESTADO_ATUAL existe
        estado_idx = None
        for i, l in enumerate(lines):
            if l.strip().startswith("## ESTADO_ATUAL"):
                estado_idx = i
                break

        if estado_idx is None:
            # Cria a seção se não existir
            lines.extend(
                [
                    "## ESTADO_ATUAL",
                    f"### {data}",
                ]
                + [f"- [{it.get('tag', 'INFO')}] {it['text']}" for it in unique_items]
                + [""]
            )
            return lines

        # Procura ### <data> dentro de ESTADO_ATUAL
        date_idx = None
        for i in range(estado_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("### "):
                if data in stripped:
                    date_idx = i
                    break
                else:
                    # Encontrou outra data → parar busca
                    break

        if date_idx is None:
            # Cria ### <data> antes da próxima seção ou ao final
            insert_at = self._find_next_header(lines, estado_idx + 1, level=2)
            new_block = [f"### {data}", ""]
            for it in unique_items:
                new_block.append(f"- [{it.get('tag', 'INFO')}] {it['text']}")
            lines = lines[:insert_at] + new_block + lines[insert_at:]
        else:
            # Insere bullets após a linha de data (ou após bullets existentes)
            insert_pos = date_idx + 1
            while insert_pos < len(lines) and lines[insert_pos].strip().startswith(
                "- "
            ):
                insert_pos += 1
            for it in reversed(unique_items):
                lines.insert(insert_pos, f"- [{it.get('tag', 'INFO')}] {it['text']}")

        return lines

    def _update_context_recente(self, lines, contexto, data):
        """Atualiza ou adiciona entry em ## CONTEXTO_RECENTE ### <data>."""
        ctx_idx = None
        for i, l in enumerate(lines):
            if l.strip().startswith("## CONTEXTO_RECENTE"):
                ctx_idx = i
                break

        if ctx_idx is None:
            lines.extend(["", "## CONTEXTO_RECENTE", f"### {data}", f"- {contexto}"])
            return lines

        # Procura ### <data>
        date_idx = None
        for i in range(ctx_idx + 1, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("### "):
                if data in stripped:
                    date_idx = i
                    break
                else:
                    break

        if date_idx is None:
            insert_at = self._find_next_header(lines, ctx_idx + 1, level=2)
            lines = (
                lines[:insert_at] + [f"### {data}", f"- {contexto}"] + lines[insert_at:]
            )
        else:
            # Adiciona bullet ao final do dia
            insert_pos = date_idx + 1
            while insert_pos < len(lines) and lines[insert_pos].strip().startswith(
                "- "
            ):
                insert_pos += 1
            lines.insert(insert_pos, f"- {contexto}")

        return lines

    def _find_next_header(self, lines, start, level=2):
        """Encontra o próximo header do mesmo nível ou retorna o final."""
        for i in range(start, len(lines)):
            stripped = lines[i].strip()
            if stripped.startswith("## ") or stripped.startswith("# "):
                return i
            if re.match(r"^#{2,} ", stripped):
                return i
        return len(lines)

    def _parse_delta(self, raw):
        """
        Parse JSON delta format (v5_unified):
        {
          "ADD": [{"tag": "TAG", "text": "..."}],
          "UPDATE": {"old_line": {"DEPOIS": "new_line"}},
          "REMOVE": ["line_to_remove"],
          "CONTEXTO_RECENTE": "..."
        }
        """
        delta = json.loads(raw)

        if not isinstance(delta, dict):
            raise ValueError(
                "Delta JSON deve ser um objeto ({}) com chaves ADD, UPDATE, REMOVE."
            )

        # Valida chaves obrigatorias
        for key in ("ADD", "UPDATE", "REMOVE"):
            if key not in delta:
                raise ValueError(f"Chave obrigatória faltando: '{key}'")

        # Valida tipos
        if not isinstance(delta["ADD"], list):
            raise ValueError("'ADD' deve ser uma lista [].")
        if not isinstance(delta["UPDATE"], dict):
            raise ValueError("'UPDATE' deve ser um objeto {}.")
        if not isinstance(delta["REMOVE"], list):
            raise ValueError("'REMOVE' deve ser uma lista [].")

        # Valida estrutura de ADD
        for idx, item in enumerate(delta["ADD"]):
            if not isinstance(item, dict) or "tag" not in item or "text" not in item:
                raise ValueError(f"ADD[{idx}] deve ter 'tag' e 'text'.")

        return delta

    # ------------------------------------------------------------------ #
    # Padronização de Deltas Pendentes
    # ------------------------------------------------------------------ #

    def standardize_file(self):
        """Escaneia o arquivo selecionado e mostra os deltas pendentes."""
        target = self.get_selected_file()
        if not target:
            return

        if not target.exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{target}")
            return

        collector = DeltaCollector(target)
        deltas = collector.extract_pending_deltas()

        if not deltas:
            self.pending_panel.config(state="normal")
            self.pending_panel.delete("1.0", "end")
            self.pending_panel.insert("1.0", "✅ Nenhum delta pendente encontrado.\n")
            self.pending_panel.config(state="disabled")
            self.btn_apply_std.config(state="disabled")
            self.status_lbl.config(
                text="🟢 Nenhum delta pendente",
                foreground="green",
            )
            return

        # Mostra painel com resumo
        self.pending_panel.config(state="normal")
        self.pending_panel.delete("1.0", "end")
        self.pending_panel.insert("1.0", f"📊 {len(deltas)} delta(s) pendente(s):\n\n")

        for i, delta in enumerate(deltas):
            data = delta.get("data", "sem data")
            add_count = len(delta.get("ADD", []))
            upd_count = len(delta.get("UPDATE", {}))
            rem_count = len(delta.get("REMOVE", []))
            self.pending_panel.insert(
                "end",
                f"[{i + 1}] {data} - ADD {add_count}, UPD {upd_count}, REM {rem_count}\n",
            )

        # Mostra erros de parse se houver
        if collector.parse_errors:
            self.pending_panel.insert("end", "\n⚠️ Erros de parse:\n")
            for err in collector.parse_errors:
                self.pending_panel.insert("end", f"  - {err}\n")

        self.pending_panel.config(state="disabled")

        # Habilita botão de aplicar
        self.btn_apply_std.config(state="normal")
        self.status_lbl.config(
            text=f"🟡 {len(deltas)} delta(s) pendente(s)",
            foreground="#FFA500",
        )

    def apply_standardization(self):
        """Aplica todos os deltas pendentes e limpa o arquivo."""
        target = self.get_selected_file()
        if not target:
            return

        if not target.exists():
            messagebox.showerror("Erro", f"Arquivo não encontrado:\n{target}")
            return

        # Confirmação
        if not messagebox.askyesno(
            "Confirmar",
            "Aplicar todos os deltas pendentes?\n\n"
            "Isso irá:\n"
            "- Aplicar os deltas ao arquivo\n"
            "- Remover os blocos JSON pendentes\n"
            "- Criar backup automático",
        ):
            return

        try:
            backup = target.with_suffix(".backup")
            shutil.copy2(target, backup)

            collector = DeltaCollector(target)
            deltas = collector.extract_pending_deltas()

            if not deltas:
                messagebox.showinfo(
                    "Padronização", "Nenhum delta pendente para aplicar."
                )
                return

            # Aplica deltas
            old_content = target.read_text(encoding="utf-8")
            new_content = self._apply_standardization_to_content(old_content, collector)

            # Gera preview diff
            self._show_diff_window(old_content, new_content)

            # Salva resultado
            target.write_text(new_content, encoding="utf-8")

            messagebox.showinfo(
                "Sucesso",
                f"✅ Padronização aplicada!\n"
                f"{len(deltas)} delta(s) processado(s).\n\n"
                f"Backup salvo:\n{backup.name}",
            )

            # Atualiza painel
            self.pending_panel.config(state="normal")
            self.pending_panel.delete("1.0", "end")
            self.pending_panel.insert(
                "1.0",
                f"✅ Padronização aplicada ({len(deltas)} delta(s))\n"
                f"Backup: {backup.name}\n",
            )
            self.pending_panel.config(state="disabled")
            self.btn_apply_std.config(state="disabled")

            self.status_lbl.config(
                text=f"✅ Padronizado em {target.name} ({datetime.now().strftime('%H:%M:%S')})",
                foreground="green",
            )

        except Exception as e:
            messagebox.showerror("Erro", f"❌ Falha ao padronizar:\n{e}")

    def _apply_standardization_to_content(
        self, content: str, collector: DeltaCollector
    ) -> str:
        """Aplica todos os deltas do collector sobre o conteúdo e limpa."""
        # Aplica cada delta em sequência
        for delta in collector.pending_deltas:
            content = self._apply_delta_to_string(content, delta)

        # Limpa blocos JSON pendentes
        content = DeltaCollector.clean_pending_deltas(content)

        return content

    # ------------------------------------------------------------------ #
    # Diff UI
    # ------------------------------------------------------------------ #
    def _show_diff_window(self, old, new):
        if hasattr(self, "diff_window") and self.diff_window:
            self.diff_window.destroy()

        self.diff_window = tk.Toplevel(self)
        self.diff_window.title("Preview de Alterações (Diff)")
        self.diff_window.geometry("700x500")

        # Scrollbar + Text
        pad_frame = ttk.Frame(self.diff_window)
        pad_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(pad_frame)
        scrollbar.pack(side="right", fill="y")

        txt = tk.Text(
            pad_frame,
            font=("Consolas", 10),
            wrap="word",
            bg="#f4f4f4",
            yscrollcommand=scrollbar.set,
        )
        txt.pack(fill="both", expand=True, side="left")
        scrollbar.config(command=txt.yview)

        # Armazena linhas em lista (generator é esgotavel → bug se iterar 2x)
        diff_lines = list(
            difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="")
        )

        if not any(diff_lines):
            txt.insert("1.0", "Nenhuma alteração detectada.\n")
        else:
            for line in diff_lines:
                if line.startswith("+"):
                    txt.insert("end", line + "\n", ("green",))
                elif line.startswith("-"):
                    txt.insert("end", line + "\n", ("red",))
                else:
                    txt.insert("end", line + "\n")

        txt.tag_config("green", foreground="green")
        txt.tag_config("red", foreground="red")
        txt.config(state="disabled")


if __name__ == "__main__":
    app = MemoriaApp()
    app.mainloop()
