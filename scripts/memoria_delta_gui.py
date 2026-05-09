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
        lines = content.splitlines(keepends=False)
        delta = self._parse_delta(delta_raw)
        existing_ids = {
            int(m.group(1)) for l in lines if (m := re.match(r"^\s*(\d+)\.", l))
        }

        # 1. REMOVE
        for rid in delta.get("REMOVE", []):
            if rid in existing_ids:
                lines = [l for l in lines if not re.match(rf"^\s*{rid}\.", l)]

        # 2. UPDATE
        for rid, upd in delta.get("UPDATE", {}).items():
            for i, line in enumerate(lines):
                if re.match(rf"^\s*{rid}\.", line):
                    # Preserva indentacao se houver, mas reescreve a linha
                    lines[i] = re.sub(
                        rf"^\s*{rid}\..*", f"{rid}. {upd.get('DEPOIS', line)}", line
                    )
                    break

        # 3. ADD
        if delta.get("ADD"):
            max_id = max(existing_ids, default=0)
            for idx, item in enumerate(delta["ADD"]):
                new_id = max_id + idx + 1
                lines.append(f"{new_id}. [{item['tag']}] {item['text']}")

        return "\n".join(lines) + "\n"

    def _parse_delta(self, raw):
        delta = {"ADD": [], "UPDATE": {}, "REMOVE": []}
        in_sec = None
        for line in raw.splitlines():
            l = line.strip()
            if not l:
                continue

            if l.startswith("## IDs_NOVO"):
                in_sec = "ADD"
                continue
            elif l.startswith("## IDs_ATUALIZAR"):
                in_sec = "UPDATE"
                continue
            elif l.startswith("## REMOVE"):
                in_sec = "REMOVE"
                continue
            elif l.startswith("---"):
                continue
            elif l.startswith("|"):
                continue  # Tabela de operacoes (ignora, usa conteudo das secoes)

            if in_sec == "ADD":
                m = re.match(r"(\d+)\.\s*\[(.*?)\]\s*(.*)", l)
                if m:
                    delta["ADD"].append(
                        {"id": int(m.group(1)), "tag": m.group(2), "text": m.group(3)}
                    )

            elif in_sec == "UPDATE":
                m = re.match(r"(\d+)\.\s*\[(ANTES|DEPOIS)\]\s*(.*)", l)
                if m:
                    rid = int(m.group(1))
                    delta["UPDATE"].setdefault(rid, {})
                    delta["UPDATE"][rid][m.group(2)] = m.group(3)

            elif in_sec == "REMOVE":
                m = re.match(r"(\d+)", l)
                if m:
                    delta["REMOVE"].append(int(m.group(1)))

        return delta

    def _show_diff_window(self, old, new):
        if hasattr(self, "diff_window") and self.diff_window:
            self.diff_window.destroy()

        self.diff_window = tk.Toplevel(self)
        self.diff_window.title("Preview de Alterações (Diff)")
        self.diff_window.geometry("700x500")

        txt = tk.Text(
            self.diff_window, font=("Consolas", 10), wrap="word", bg="#f4f4f4"
        )
        txt.pack(fill="both", expand=True, padx=10, pady=10)

        diff = difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="")
        diff_text = "".join(diff)

        if not diff_text.strip():
            txt.insert("1.0", "Nenhuma alteração detectada.\n")
        else:
            for line in diff:
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
