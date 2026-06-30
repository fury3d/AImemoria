#!/bin/bash
# Navega para o diretorio onde este script está localizado
cd "$(dirname "$0")"

# Executa o python sem alocar um terminal (detached)
python3 memoria_delta_gui.py &
