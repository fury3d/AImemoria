#!/usr/bin/env python3
"""Teste rapido do padronizador de deltas."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path

import memoria_delta_gui as m

# Conteudo real do arquivo do usuario (JSON puro sem backticks)
test_content = (
    "{\n"
    '  "data": "2026-05-09",\n'
    '  "ADD": [\n'
    "    {\n"
    '      "tag": "INFO",\n'
    '      "text": "CPU Ryzen 9 9900X: limite termico 85C configurado (clima 30C)."\n'
    "    }\n"
    "  ],\n"
    '  "UPDATE": {},\n'
    '  "REMOVE": [],\n'
    '  "CONTEXTO_RECENTE": "Configurado thermal limit 85C no Ryzen 9 9900X."\n'
    "}\n"
    "\n"
    "{\n"
    '  "data": "2026-05-10",\n'
    '  "ADD": [\n'
    "    {\n"
    '      "tag": "INFO",\n'
    '      "text": "CPU Ryzen 9 10900X: limite termico 85C configurado (clima 30C)."\n'
    "    }\n"
    "  ],\n"
    '  "UPDATE": {},\n'
    '  "REMOVE": [],\n'
    '  "CONTEXTO_RECENTE": "Configurado thermal limit 85C no Ryzen 9 9900X again."\n'
    "}\n"
    "\n"
    "## ESTADO_ATUAL\n"
    "\n"
    "### 2026-05-09\n"
    "- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado.\n"
)

# Escreve arquivo de teste
test_file = Path("/tmp/test_memoria.md")
test_file.write_text(test_content, encoding="utf-8")

# Debug: test extração crua primeiro
dc_debug = m.DeltaCollector(test_file)
blocks = dc_debug._find_json_blocks(test_content)
print(f"Blocos JSON encontrados: {len(blocks)}")
for i, b in enumerate(blocks):
    print(f"  Bloco {i + 1} (len={len(b)}): {b[:80]}...")

# Extrai deltas
dc = m.DeltaCollector(test_file)
deltas = dc.extract_pending_deltas()
print(f"Deltas extraidos: {len(deltas)}")
print(f"Parse errors: {dc.parse_errors}")
if deltas:
    for i, d in enumerate(deltas):
        print(
            f"  [{i + 1}] data={d.get('data')}, ADD={len(d.get('ADD', []))}, UPDATE={len(d.get('UPDATE', {}))}, REMOVE={len(d.get('REMOVE', []))}"
        )
else:
    print("ERRO: Nenhum delta extraido!")
    sys.exit(1)

# Testa limpeza
cleaned = m.DeltaCollector.clean_pending_deltas(test_content)
has_json = '{"data"' in cleaned or '"ADD"' in cleaned
print(f"Limpeza OK: JSON removido = {not has_json}")
print(f"Estado atual permanece: {'## ESTADO_ATUAL' in cleaned}")

# Remove arquivo de teste
test_file.unlink()
print("\nTestes passaram!")
