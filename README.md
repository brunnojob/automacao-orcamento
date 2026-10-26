# RF Soluções — Automação de Orçamentos

Lê solicitações e fotos por e-mail, pesquisa fornecedores e prepara uma prévia de orçamento para revisão humana.

- Gmail e Hostinger via IMAP, restritos às duas contas configuradas no código.
- Identificação visual e pesquisa de preços com fontes pela API OpenAI.
- CA consultado no Supabase por MCP, sem inventar certificados.
- Precificação: `(custo / 0.80) * 2`.
- JSON, opções de fornecedores e fotos recebidas salvos na pasta **orçamentos** da Hostinger.
- Sem envio ao cliente ou compra automática.

[Configuração e limitações](SETUP.md). Todos os resultados precisam de revisão; o fluxo real ainda depende de credenciais e validação integrada.

Desenvolvido por [brunnodev.store](https://brunnodev.store).
