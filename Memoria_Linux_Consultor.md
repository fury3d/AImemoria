## ESTADO_ATUAL

### 2026-05-09
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado.
- [INFO] Discos NTFS fixos em `/mnt/ssd_2tb` e `/mnt/Windows1TB`
- [INFO] `fstab` configurado com UUIDs: `B8306050306017A0` e `9C1E692B1E68FF9E`
- [INFO] Montagem via `ntfs-3g` com permissões totais (`umask=000`, `uid/gid=1000`)  
- [INFO] Opção `nofail` ativa para prevenir falha crítica no boot
- [INFO] Pasta vault Obsidian: `/home/gilliard/Cofre_Obsidian/Obsidian/`
- [INFO] Ponto de montagem para LM Studio: `/mnt/ssd_2tb/DEV/_LMSTUDIOMODELS/`
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado (clima 30°C).

### 2026-05-08

- [ATIVO] Servidor de IA migrado para o fork Buun (`spiritbuun/buun-llama-cpp`) compilado com GCC-14. Permite maior contexto na VRAM usando Trellis-Coded Quantization (TCQ) via parâmetros `-ctk` e `-ctv`. 
- [ATIVO] [IA] Limites seguros de contexto na RTX 4070 Ti SUPER (16GB): Qwen 27B IQ3M atinge alto contexto (200k) pelo KV cache com o fork Bunn llama.cpp. Configuração -ctk turbo3_tcq -ctv turbo2_tcq. 
- [ATIVO] [IA] Qwen 35B MoE não teve muita diferença de contexto com o fork llama.cpp do bunn devido ao peso base e menor KV cache. Mas ainda assim está sendo usado este fork devido ao possível ganho de precisão.
- [CRÍTICO] [SYSTEM] Regra de Escrita: Evitar uso de partições NTFS para o Obsidian Vault devido a conflitos de permissão.

## CONTEXTO_RECENTE

### 2026-05-10
- Configurado thermal limit 85°C no Ryzen 9 9900X; mitigação de calor ambiente (30°C) via throttling preventivo.
### 2026-05-09

- Corrigida falha de montagem NTFS e erro "Read-only" causado por queda de energia/sleep usando `ntfsfix` e migração para montagem estática em `/mnt/`
- Cofre consolidado no Windows 11 com espelhamento direto no disco D:, garantindo performance. Sincronia com Android/Linux confirmada após reorganização de pastas. Identificada lentidão no Linux causada por latência de rede; recomendada transição para arquivos físicos locais para abrir o Obsidian instantaneamente. 
- Servidor local llama.cpp atualizado para o fork Buun, maximizando o limite de contexto via compressão TCQ. Erros de tool calling no RooCode resolvidos removendo templates Jinja externos e forçando respostas JSON via system prompt. Implementada integração direta da IA no Obsidian via plugins e adicionado bloqueio de suspensão do sistema vinculado à execução da IA.
