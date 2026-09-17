# Casos de segurança a implementar

Esta lista não significa que os controles já foram implementados ou testados.

- Manifesto: rejeitar fonte não aprovada, caminho externo e escape por symlink.
- Entrada: tamanho excessivo, formatos inválidos e parâmetros inesperados.
- Prompt injection: pergunta manipuladora e instrução inserida em documento fictício.
- Citações: rejeitar identificadores e URLs que não pertençam ao contexto aprovado.
- Logs: não expor credenciais ou conteúdo sensível em falhas.
- Consumo: verificar limites compartilhados e comportamento de concorrência.

Usar somente dados sintéticos. A rejeição de fonte não aprovada já possui teste
unitário em `tests/unit/test_prepare_document.py`.
