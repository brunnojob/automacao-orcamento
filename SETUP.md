# RF Soluções — automação de orçamento

Execute Python 3.11 ou superior: `pip install -r requirements.txt`, depois `python quotation.py`.

Configure no ambiente, sem publicar segredos:
- GMAIL_APP_PASSWORD: senha de aplicativo de rfcomercialnovo@gmail.com.
- HOSTINGER_APP_PASSWORD: senha IMAP de suportetec@rf-offshore.com.
- OPENAI_API_KEY e OPENAI_MODEL: extração estruturada.
- CATALOG_MCP_URL, CATALOG_MCP_TOKEN e CATALOG_MCP_TOOL: servidor MCP HTTP autenticado.
- PHOTO_ALLOWED_HOSTS: hosts HTTPS confiáveis das fotos, separados por vírgula.

O MCP deve aceitar {"query":"descrição"} e retornar {"products":[{"id":"sku","description":"produto","unit_cost":"10.00","ca":null,"photo_url":"https://host-confiavel/foto.jpg"}]}. O resultado precisa identificar exatamente um produto. Adapte o contrato ao servidor real antes de ativar. Não configure uma ferramenta de SQL arbitrário: use uma consulta de catálogo restrita e somente leitura.

Apenas as duas contas fixas são lidas. O processo usa IMAP APPEND na pasta orçamentos da Hostinger. Não existe transporte SMTP nem envio ao cliente. Cada mensagem inclui JSON, cálculos e fotos. CA ausente vira N/A; produto ambíguo ou foto indisponível bloqueia o orçamento. A deduplicação usa conta, UIDVALIDITY e UID em cabeçalho persistido no destino.

Execute uma única instância. Não apague mensagens geradas, pois elas registram a deduplicação. Uma interrupção durante APPEND exige conferir o destino antes de reiniciar. Falhas são tentadas novamente no próximo ciclo; a versão inicial interrompe o ciclo ao encontrar erro. Monitora todo o histórico da INBOX; faça primeiro uma validação com caixas controladas. Extração de anexos recebidos, OAuth de Gmail e seleção manual de correspondências ainda não estão implementadas. Quantidades ausentes não são presumidas.

Conexões do editor não são herdadas pelo serviço Python. Esta estrutura não foi ativada em produção. A validação com catálogo, LLM e contas reais continua necessária.

Autoria: [brunnodev.store](https://brunnodev.store).
