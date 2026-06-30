## ESTADO_ATUAL

### 2026-06-30

- [INFO] Existe um servidor n8n versão atualizada 2.23.4 rodando no Android Galaxy S20+ com Termux.
- [INFO] Este servidor tem acesso remoto via Cloudflare Tunnel no endereço n8n.iasol.space e está rodando o projeto Viva Praia.
- [INFO] Projeto Viva Praia: bot configurado e funcionando para imagens, texto e voz, apenas para criação de tarefas, previsão de incluir outras funções com outros bancos de dados no Notion como: lista de compras, anexar documentos e arquivos, reclamações/melhorias, Orçamentos, Inventário e HistóricoManutenção. 
- [INFO] Botões do Telegram para aprovação de tarefa que se apagam automaticamente para não poluir chat funcionaram apenas com HTTP Request. Botão com callback data chega dentro de um json.callback_query.data sendo redirecionado pelo switch para diferenciar mensagem e cliques de botão, buscando os dados do cache e concluindo ação. 
- [INFO] Sempre criar um novo código de nó é necessário inserir e revisar o campo de conexões.
