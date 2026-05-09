#!/usr/bin/env python3
"""
memoria_delta_gui.py - Aplicador Gráfico de Delta de Memória
Cross-platform (Linux/Windows), sem terminal, seguro contra alucinações.
Dependência: python-tk (Linux) ou Python instalado (Windows)
"""

import difflib
import json
import os
import re
import shutil
import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# Caminho do config (arquivo oculto)
CONFIG_PATH = Path.home() / ".config" / "memoria_delta" / "files.json"


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

        try:
            backup = target.with_suffix(".backup")
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
        """

        def _apply_delta_to_string(self, content, delta_raw):
            """
            Aplica delta JSON (v5) sobre o arquivo Markdown de memória.

            Estrutura da memória:
              ## ESTADO_ATUAL
                ### 2026-05-09
                - [TAG] entry
              ## CONTEXTO_RECENTE
                ### 2026-05-09
                - context entry
            """
            lines = content.splitlines(keepends=False)
            delta = self._parse_delta(delta_raw)
            data = delta.get("data", datetime.today().strftime("%Y-%m-%d"))

            # 1. REMOVE (match de conteúdo nas bullets existentes)
            remove_list = delta.get("REMOVE", [])
            if remove_list:
                new_lines = []
                for l in lines:
                    stripped = l.strip()
                    # Remove se conteúdo (sem prefixo "- [TAG] ") match em alguma entrada REMOVE
                    if any(
                        rm.strip() == stripped.lstrip("- ")
                        or f"[{rm.strip()}]" in stripped
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

    def _add_items_to_state(self, lines, items, data):
        """Inserta ADD entries em ## ESTADO_ATUAL ### <data>."""
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
                + [f"- [{it.get('tag', 'INFO')}] {it['text']}" for it in items]
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
            for it in items:
                new_block.append(f"- [{it.get('tag', 'INFO')}] {it['text']}")
            lines = lines[:insert_at] + new_block + lines[insert_at:]
        else:
            # Insere bullets após a linha de data (ou após bullets existentes)
            insert_pos = date_idx + 1
            while insert_pos < len(lines) and lines[insert_pos].strip().startswith(
                "- "
            ):
                insert_pos += 1
            for it in reversed(items):
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
