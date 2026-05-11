## ESTADO_ATUAL

### 2026-05-22

- [INFO] CPU Ryzen 9 12900X: limite térmico 85°C configurado (clima 30°C).
### 2026-05-10

- [INFO] CPU Ryzen 9 10900X: limite térmico 85°C configurado (clima 30°C).
### 2026-05-09
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado.
- [TAG] Discos NTFS fixos em `/mnt/ssd_2tb` e `/mnt/Windows1TB`
- [TAG] `fstab` configurado com UUIDs: `B8306050306017A0` e `9C1E692B1E68FF9E`
- [TAG] Montagem via `ntfs-3g` com permissões totais (`umask=000`, `uid/gid=1000`)  
- [TAG] Opção `nofail` ativa para prevenir falha crítica no boot
- [TAG] Ponto de montagem para Obsidian: `/mnt/ssd_2tb/Obsidian`
- [TAG] Ponto de montagem para LM Studio: `/mnt/ssd_2tb/DEV/_LMSTUDIOMODELS/`
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado (clima 30°C).

### 2026-05-08

- [ATIVO] Servidor de IA migrado para o fork Buun (`spiritbuun/buun-llama-cpp`) compilado com GCC-14. Permite maior contexto na VRAM usando Trellis-Coded Quantization (TCQ) via parâmetros `-ctk` e `-ctv`. 
- [ATIVO] Limites seguros de contexto na RTX 4070 Ti SUPER (16GB): Qwen 27B atinge alto contexto (~64k-200k) pelo grande KV nativo. Qwen 35B MoE limitado a ~128k devido ao peso base e menor KV cache. 
- [CRÍTICO] Chamada de ferramentas (RooCode/Antigravity): Uso de template externo (`template.jinja`) removido do script do servidor. System prompt do IDE atualizado para forçar uso de JSON estrito imediatamente após a tag `</think>`, evitando crash com pseudo-tags `<function>`. 
- [ATIVO] Obsidian integrado à IA local: Utilização dos plugins `Copilot` e `Smart Connections` apontando para `http://127.0.0.1:8033/v1` em vez do AnythingLLM, preservando a formatação do cofre. 
- [ATIVO] Pendência: Otimizar performance no Linux migrando de montagem virtual (FUSE/GVFS) para sincronia física local (Insync ou rclone bisync).
- [ATIVO] Sincronia Obsidian via Google Drive (Modo Espelhamento) configurada em `D:\_GoogleDrive\Obsidian`. 
- [ATIVO] Notas do Google Keep importadas e movidas para a pasta `00 - Importados do Keep`. 
- [ATIVO] Pendência: Otimizar performance no Linux migrando de montagem virtual (FUSE/GVFS) para sincronia física local (Insync ou rclone bisync).
- [ATIVO] Sync: Google Drive via Rclone configurado com ID/Secret privado no Google Cloud.
- [ATIVO] Ponto de Montagem: `/home/gilliard/gdrive` em sistema de arquivos BTRFS.
- [ATIVO] Automação: Script `/home/gilliard/scripts/mount_gdrive.sh` integrado ao Início Automático do KDE.
- [CRÍTICO] Regra de Escrita: Evitar uso de partições NTFS para o Obsidian Vault devido a conflitos de permissão.

## CONTEXTO_RECENTE

### 2026-05-22
- Configurado thermal limit 105°C no Ryzen 9 12900X; mitigação de calor ambiente (30°C) via throttling preventivo.
### 2026-05-10
- Configurado thermal limit 85°C no Ryzen 9 9900X; mitigação de calor ambiente (30°C) via throttling preventivo.
### 2026-05-09
- Configurado thermal limit 85°C no Ryzen 9 9900X; mitigação de calor ambiente (30°C) via throttling preventivo.
### 2026-05-10
- Configurado thermal limit 85°C no Ryzen 9 9900X; mitigação de calor ambiente (30°C) via throttling preventivo.
### 2026-05-09

- Corrigida falha de montagem NTFS e erro "Read-only" causado por queda de energia/sleep usando `ntfsfix` e migração para montagem estática em `/mnt/`
- Cofre consolidado no Windows 11 com espelhamento direto no disco D:, garantindo performance. Sincronia com Android/Linux confirmada após reorganização de pastas. Identificada lentidão no Linux causada por latência de rede; recomendada transição para arquivos físicos locais para abrir o Obsidian instantaneamente. 
- Servidor local llama.cpp atualizado para o fork Buun, maximizando o limite de contexto via compressão TCQ. Erros de tool calling no RooCode resolvidos removendo templates Jinja externos e forçando respostas JSON via system prompt. Implementada integração direta da IA no Obsidian via plugins e adicionado bloqueio de suspensão do sistema vinculado à execução da IA.
