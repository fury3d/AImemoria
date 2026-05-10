#!/usr/bin/env python3
"""Teste rapido do padronizador de deltas."""
import json
import sys
import os

# Adiciona o diretorio ao path
sys.path.insert(0, os.path.dirname(__file__))

import memoria_delta_gui as m
from pathlib import Path

BACKTICK = chr(96)  # backtick

test_content = f"""## ESTADO_ATUAL

### 2026-05-09

- [INFO] Entrada existente

## CONTEXTO_RECENTE

---
# DELTAS PENDENTES

{BACKTICK}{BACKTICK}{BACKTICK}json
{{
  "data": "2026-05-10",
  "ADD": [{{"tag": "TESTE", "text": "Nova entrada via delta padronizado."}}],
  "UPDATE": {{}},
  "REMOVE": [],
  "CONTEXTO_RECENTE": "Teste de padronizacao."
}}
{BACKTICK}{BACKTICK}{BACKTICK}
"""

# Escreve arquivo de teste
test_file = Path("/tmp/test_memoria.md")
test_file.write_text(test_content, encoding="utf-8")

# Extrai deltas
dc = m.DeltaCollector(test_file)
deltas = dc.extract_pending_deltas()
print(f"Deltas extraidos: {len(deltas)}")

if deltas:
    print(f"Primeiro delta: {json.dumps(deltas[0], indent=2, ensure_ascii=False)}")
else:
    print("ERRO: Nenhum delta extraido!")
    sys.exit(1)

# Limpeza
cleaned = m.DeltaCollector.clean_pending_deltas(test_content)
backtick_clean = (BACKTICK * 3) not in cleaned
print(f"Limpeza OK (sem
