# Configuração

Python 3.11 ou superior. Na pasta do projeto:

```powershell
git pull
python -m pip install -r requirements.txt
python quotation.py
```

Crie um arquivo .env na mesma pasta de quotation.py, usando .env.example como referência.
O programa carrega esse arquivo sem sobrescrever variáveis já definidas no terminal.
Nunca publique credenciais. O .gitignore exclui .env.

## Variáveis

- GMAIL_APP_PASSWORD: senha de aplicativo de rfcomercialnovo@gmail.com.
- HOSTINGER_APP_PASSWORD: senha IMAP de suportetec@rf-offshore.com.
- SUPABASE_SERVICE_ROLE_KEY: chave secreta do projeto cdkbobyevlwxofvcoxcc.
- OPENAI_API_KEY: chave da API com créditos.
- OPENAI_MODEL: modelo disponível na conta com visão e saída estruturada.
- OPENAI_SEARCH_MODEL: modelo com suporte a web_search; opcional, usa OPENAI_MODEL quando ausente.

PHOTO_ALLOWED_HOSTS não é usado. As imagens são anexos do e-mail recebido.
A busca web gera custos de API adicionais. Confirme suporte dos modelos na sua conta.

## Fluxo

1. Lê somente as duas caixas fixas via IMAP e filtra assunto/corpo por Cotação, Orçamento ou Oceânica.
2. Extrai descrição, quantidade explícita e dúvidas usando corpo e imagens JPEG, PNG ou WebP, inclusive imagens inline.
3. Pesquisa fornecedores brasileiros para cada item, com preço em BRL, unidade, evidências, fonte e horário da consulta.
4. Consulta o catálogo Supabase via MCP para enriquecer o CA quando há correspondência exata.
5. Aplica (custo / 0.80) * 2 em cada opção pesquisada elegível e calcula subtotal com preço arredondado.
6. Salva a prévia, fontes, observações e fotos originais na pasta orçamentos da Hostinger por IMAP APPEND.

Nunca envia ao cliente, não compra produtos e não contata fornecedores.
Todos os resultados ficam pendentes de revisão humana. Preços extraídos da web por LLM são candidatos, não confirmações de compra.
Confira preço, embalagem, tamanho/modelo, frete, impostos, estoque e disponibilidade.
Só aceita URLs retornadas pela pesquisa como fontes. Isso não prova que o preço foi extraído corretamente.
Quantidade ausente ou preço incerto impede cálculo daquela opção. Não soma fornecedores alternativos em um total único.
CA não é inferido da imagem nem da busca: vem do catálogo exato ou N/A, para conferência.

## Supabase

O catálogo public.rf_products tem id, sku, description, unit_cost, ca, photo_url, active e updated_at.
RLS ativo; anon e authenticated sem acesso. Acesso feito pelo adaptador MCP stdio catalog_mcp.py com chave de servidor.
A configuração de desenvolvimento .vscode/mcp.json usa acesso somente leitura.
Os resultados pesquisados ficam no e-mail; não são inseridos automaticamente como produtos confirmados no banco.

## Limites

Uma única instância. Até 8 imagens por mensagem, 5 MB por imagem, 12 MB somados; saída até 20 MB.
PDF, planilhas e documentos recebidos ainda não são extraídos.
Imagens inline, como assinaturas, também são analisadas; confira a identificação.
O ciclo examina o histórico inteiro da INBOX. Erros de serviço interrompem o ciclo e são tentados novamente após 60 segundos.
Mensagens geradas registram deduplicação: não as apague sem avaliar reprocessamento.
Fotos e texto são enviados à API OpenAI para análise; a busca recebe a descrição do produto.
Credenciais reais, pesquisa ao vivo e salvamento IMAP ainda precisam de teste integrado no ambiente de execução.

Testes: python -m unittest -v.
