# RF Soluções — Supabase e MCP

Python 3.11+: instale `pip install -r requirements.txt` e execute `python quotation.py`.

## Projeto conectado

Projeto Supabase: `cdkbobyevlwxofvcoxcc`.
Catálogo: `public.rf_products`, separado das tabelas do PlantForge.
Campos: id, sku, description, unit_cost, ca, photo_url, active, updated_at.
Cadastre produtos reais no Table Editor. Não há produtos de demonstração.
CA desconhecido deve ficar nulo. Use URLs HTTPS de imagens acessíveis ao serviço.

A busca usa descrição exata, inclusive maiúsculas e minúsculas no filtro do banco.
Pedidos sem correspondência única são bloqueados para conferência.
Não há correspondência semântica nem sugestão automática de substitutos.

## Ambiente do serviço

- SUPABASE_SERVICE_ROLE_KEY: chave secreta do projeto, somente no ambiente do servidor.
- GMAIL_APP_PASSWORD: senha de aplicativo de rfcomercialnovo@gmail.com.
- HOSTINGER_APP_PASSWORD: credencial IMAP de suportetec@rf-offshore.com.
- OPENAI_API_KEY e OPENAI_MODEL: extração estruturada.
- PHOTO_ALLOWED_HOSTS: hosts HTTPS confiáveis, separados por vírgula.

O processo inicia `catalog_mcp.py` como subprocesso MCP stdio e chama somente
`search_products`. O adaptador consulta o Supabase REST, sem aceitar SQL.
Não é necessário CATALOG_MCP_URL/TOKEN/TOOL.
A chave service_role tem privilégios elevados: nunca a publique nem a coloque no mcp.json.
A tabela tem RLS e nenhum acesso para anon/authenticated; ausência de políticas é intencional.
A conexão OAuth do VS Code é independente das credenciais do processo Python.

## Operação

Somente as duas caixas fixas são lidas. Assunto/corpo deve conter Cotação, Orçamento ou Oceânica.
Preço = (custo / 0.80) * 2, arredondado em centavos; subtotal usa o preço arredondado.
Fotos e JSON são anexados à mensagem salva por IMAP APPEND na pasta orçamentos da Hostinger.
Sem SMTP ou envio ao cliente. CA vem do catálogo ou N/A.
Foto indisponível e catálogo ambíguo bloqueiam a geração.

Execute uma única instância. Não apague as mensagens geradas, usadas para deduplicação.
O ciclo lê todo o histórico da INBOX; uma falha interrompe o ciclo e tenta novamente após 60 segundos.
Anexos de solicitações recebidas ainda não são extraídos.
Credenciais, LLM, fotos e fluxo IMAP precisam de validação real antes da ativação.

Testes: `python -m unittest -v`.

Autoria: [brunnodev.store](https://brunnodev.store).
