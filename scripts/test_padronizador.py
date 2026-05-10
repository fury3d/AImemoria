#!/usr/bin/env python3
"""Teste rapido do padronizador de deltas."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path

import memoria_delta_gui as m

# Conteudo simulando JSON puro colado no .md (sem backticks)
test_content = (
    "{\n"
    '  "data": "2026-05-09",\n'
    '  "ADD": [{"tag": "INFO", "text": "Entrada 1"}],\n'
    '  "UPDATE": {},\n'
    '  "REMOVE": [],\n'
    '  "CONTEXTO_RECENTE": "Contexto 1."\n'
    "}\n"
    "\n"
    "{\n"
    '  "data": "2026-05-10",\n'
    '  "ADD": [{"tag": "INFO", "text": "Entrada 2"}],\n'
    '  "UPDATE": {},\n'
    '  "REMOVE": [],\n'
    '  "CONTEXTO_RECENTE": "Contexto 2."\n'
    "}\n"
    "\n"
    "## ESTADO_ATUAL\n"
    "\n"
    "### 2026-05-09\n"
    "- [INFO] Entrada existente\n"
)

# Teste 1: Extração de JSON puro (sem backticks)
test_file = Path("/tmp/test_memoria.md")
test_file.write_text(test_content, encoding="utf-8")
dc = m.DeltaCollector(test_file)
deltas = dc.extract_pending_deltas()
assert len(deltas) == 2, f"Esperava 2 deltas, achou {len(deltas)}"
print("[OK] Extração JSON puro: 2 deltas encontrados")

# Teste 2: Limpeza
cleaned = m.DeltaCollector.clean_pending_deltas(test_content)
assert '"ADD"' not in cleaned
assert '"UPDATE"' not in cleaned
assert "## ESTADO_ATUAL" in cleaned
print("[OK] Limpeza: JSON removido, markdown preservado")

# Teste 3: DeltaCollector com backticks (tambem funciona)
bt = chr(96)
content_with_bt = (
    "## ESTADO_ATUAL\n\n"
    f"{bt}{bt}{bt}json\n"
    "{\n"
    '  "data": "2026-05-11",\n'
    '  "ADD": [{"tag": "TESTE", "text": "Via backticks"}],\n'
    '  "UPDATE": {},\n'
    '  "REMOVE": []\n'
    "}\n"
    f"{bt}{bt}{bt}\n"
)
test_file.write_text(content_with_bt, encoding="utf-8")
dc2 = m.DeltaCollector(test_file)
deltas2 = dc2.extract_pending_deltas()
assert len(deltas2) == 1, f"Esperava 1 delta (backticks), achou {len(deltas2)}"
print("[OK] Extração com backticks: 1 delta encontrado")

test_file.unlink()
print("\nTodos os testes passaram!")
