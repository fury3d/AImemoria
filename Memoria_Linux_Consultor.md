## ESTADO_ATUAL




### 2026-05-09
- [INFO] Discos NTFS fixos em `/mnt/ssd_2tb` e `/mnt/Windows1TB` #sistema #linux
- [INFO] `fstab` configurado com UUIDs: `B8306050306017A0` e `9C1E692B1E68FF9E` #sistema #linux
- [INFO] Montagem via `ntfs-3g` com permissões totais (`umask=000`, `uid/gid=1000`)  #sistema #linux
- [INFO] Opção `nofail` ativa para prevenir falha crítica no boot #sistema #linux
- [INFO] Pasta vault Obsidian: `/home/gilliard/Cofre_Obsidian/Obsidian/` #obsidian 
- [INFO] Ponto de montagem para LM Studio: `/mnt/ssd_2tb/DEV/_LMSTUDIOMODELS/` #ia #llamacpp #llm #lmstudio 
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado (clima 30°C). #sistema #hardware

### 2026-05-08

- [ATIVO] Servidor de IA migrado para o fork Buun (`spiritbuun/buun-llama-cpp`) compilado com GCC-14. Permite maior contexto na VRAM usando Trellis-Coded Quantization (TCQ) via parâmetros `-ctk` e `-ctv`.   #ia #llamacpp #llm #bunn #qwen 
- [ATIVO] Para Qwen35B TQ3_4S estou usando fork turbo tan https://github.com/turbo-tan/llama.cpp-tq3/ local: /home/gilliard/IA_Local/motor-tq3-novo/ (precisa fazer compilação ao atualizar) #ia #llamacpp #llm #turboquant #qwen  
- [ATIVO] Limites seguros de contexto na RTX 4070 Ti SUPER (16GB): Qwen 27B IQ3M atinge alto contexto (200k) pelo KV cache com o fork Bunn llama.cpp. Configuração -ctk turbo3_tcq -ctv turbo2_tcq. #ia #llamacpp #llm #bunn #qwen #turboquant
- [ATIVO] Qwen 35B MoE não teve muita diferença de contexto com o fork llama.cpp do bunn devido ao peso base e menor KV cache. Mas ainda assim está sendo usado este fork devido ao possível ganho de precisão. #ia #llamacpp #llm #bunn #qwen 
- [CRÍTICO] Regra de Escrita: Evitar uso de partições NTFS para o Obsidian Vault devido a conflitos de permissão. #sistema #linux #obsidian 

## CONTEXTO_RECENTE

### 2026-05-10
- Configurado thermal limit 85°C no Ryzen 9 9900X; mitigação de calor ambiente (30°C) via throttling preventivo. #sistema #hardware
### 2026-05-09

- Corrigida falha de montagem NTFS e erro "Read-only" causado por queda de energia/sleep usando `ntfsfix` e migração para montagem estática em `/mnt/` COnsiderar que existem outros discos ao fazer a montagem para não sobrescrever e acabar ocultando um outro disco configurado previamente.  #sistema #linux
