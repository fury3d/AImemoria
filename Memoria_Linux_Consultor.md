## ESTADO_ATUAL


### 2026-06-12
- [INFO] Dispositivo alvo principal: Samsung S24 Plus.
- [INFO] IP fixo configurado S24+: 192.168.100.100
- [INFO] Conexão remota ADB usa VPN Tailscale.
- [INFO] Configurado Cloudflare tunel para acesso remoto: n8n.iasol.space.
- [INFO] IP Tailscale S24+: 100.111.70.43
- [INFO] Comando adb local: adb connect 192.168.100.100:5555 && scrcpy --turn-screen-off --stay-awake --mouse-bind=++++ --keyboard=uhid --mouse=sdk
- [INFO] Comando adb tailscale: adb connect 100.111.70.43:5555 

### 2026-06-03

- [INFO] Travas de segurança npmrc: ignore-scripts=true e save-exact=true contra ataques de supply chain.
- [INFO] Criado script (~/scripts/n8n-start.sh) e atalho (.desktop) para rodar n8n via Docker usando sintaxe do Fish.
- [CRITICO] Revisar segurança antes de instalar dependencias: checar ps aux | grep -i "token" e pm2 ls.
- [CRITICO] Configurar sempre npm config set min-release-age=3 como trava adicional.

### 2026-05-15
- [CRITICO] Tablet XP-Pen (28bd:0905) desconfigura mapeamento no X11 apos acordar do Sleep.
- [INFO] Corte de energia USB (VBUS) por software/uhubctl nao e suportado pela placa-mae.
- [INFO] Solucao permanente: resetar controladora PCI XHCI (0000:0a:00.0) via unbind/bind.
- [CRITICO] Script systemd /usr/lib/systemd/system-sleep/tablet-pci-fix.sh criado para automatizar reset PCI.

### 2026-05-15
- [INFO] Estrutura de Pastas Padronizada:
Scripts: /home/gilliard/scripts/ (Centraliza automações como mount_gdrive.sh e run_deepsproxy.sh).
Apps (Compilados/Source): /home/gilliard/Apps/ (Local do DeepSeekProxy).
AppImages: /home/gilliard/Applications/.
- [ATIVO] **DeepSeekProxy:** Operacional em `/home/gilliard/Apps/DeepSeekProxy/deepsproxy`.
- [ATIVO] **Automação de Proxy:** Script de inicialização e limpeza de porta configurado em `/home/gilliard/scripts/run_deepsproxy.sh`.

### 2026-05-09
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado.
- [INFO] Discos NTFS fixos em `/mnt/ssd_2tb` e `/mnt/Windows1TB`
- [INFO] `fstab` configurado com UUIDs: `B8306050306017A0` e `9C1E692B1E68FF9E`
- [INFO] Montagem via `ntfs-3g` com permissões totais (`umask=000`, `uid/gid=1000`)  
- [INFO] Opção `nofail` ativa para prevenir falha crítica no boot #sistema #linux
- [INFO] Pasta vault Obsidian: `/home/gilliard/Cofre_Obsidian/Obsidian/` #obsidian 
- [INFO] Ponto de montagem para LM Studio: `/mnt/ssd_2tb/DEV/_LMSTUDIOMODELS/` #ia #llamacpp #llm #lmstudio 
- [INFO] CPU Ryzen 9 9900X: limite térmico 85°C configurado (clima 30°C).

### 2026-05-08
- [ATIVO] Servidor de IA migrado para o fork Buun (`spiritbuun/buun-llama-cpp`) compilado com GCC-14. Permite maior contexto na VRAM usando Trellis-Coded Quantization (TCQ) via parâmetros `-ctk` e `-ctv`.  #ia #llamacpp #llm #bunn #qwen 
- [ATIVO] Limites seguros de contexto na RTX 4070 Ti SUPER (16GB): Qwen 27B IQ3M atinge alto contexto (200k) pelo KV cache com o fork Bunn llama.cpp. Configuração -ctk turbo3_tcq -ctv turbo2_tcq. #ia #llamacpp #llm #bunn #qwen 
- [ATIVO] Qwen 35B MoE não teve muita diferença de contexto com o fork llama.cpp do bunn devido ao peso base e menor KV cache. Mas ainda assim está sendo usado este fork devido ao possível ganho de precisão. #ia #llamacpp #llm #bunn #qwen 
- [CRÍTICO] Regra de Escrita: Evitar uso de partições NTFS para o Obsidian Vault devido a conflitos de permissão. #sistema #linux #obsidian 

## CONTEXTO_RECENTE

### 2026-06-12
- Acesso local via Wifi se mostrou mais rápido e estável (dispositivo longe do computador). Acesso remoto via cloudflare tunel se mostrou eficiente. Opção tailscale ativo. 
### 2026-06-03
- Configuradas travas no .npmrc contra supply chain e fragmentada checagem de segurança para respeitar limite de tokens.
### 2026-05-15
- Tablet XP-Pen perdia mapeamento no sleep. Resolvido automatizando reset da controladora PCI XHCI pós-suspensão.

- **Organização de Diretórios:** Definida a separação clara entre binários AppImage e aplicações que rodam via Node/Source para evitar dispersão de arquivos no sistema.
### 2026-05-10
- Configurado thermal limit 85°C no Ryzen 9 9900X; mitigação de calor ambiente (30°C) via throttling preventivo.
### 2026-05-09

- Corrigida falha de montagem NTFS e erro "Read-only" causado por queda de energia/sleep usando `ntfsfix` e migração para montagem estática em `/mnt/`
- Cofre consolidado no Windows 11 com espelhamento direto no disco D:, garantindo performance. Sincronia com Android/Linux confirmada após reorganização de pastas. Identificada lentidão no Linux causada por latência de rede; recomendada transição para arquivos físicos locais para abrir o Obsidian instantaneamente. 
- Servidor local llama.cpp atualizado para o fork Buun, maximizando o limite de contexto via compressão TCQ. Erros de tool calling no RooCode resolvidos removendo templates Jinja externos e forçando respostas JSON via system prompt. Implementada integração direta da IA no Obsidian via plugins e adicionado bloqueio de suspensão do sistema vinculado à execução da IA.
