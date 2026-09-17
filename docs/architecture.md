# Arquitetura inicial

## Estado atual
Implementado: preparação de documentos com validação de aprovação, contrato de
leitura, normalização e hash; testes unitários. Não há pipeline RAG completo.

## Organização acordada
Um repositório e duas Lambdas com imagens Docker:

- Indexação administrativa: leitura → chunking → embeddings → pgvector.
- Consulta via Function URL: pergunta → retrieval → contexto → geração → fontes.

Handlers, imagens, banco e clientes externos ainda serão implementados.

## Configuração a decidir
- Provedor/modelo de embeddings: [preencher após avaliação]
- Dimensionalidade: [preencher]
- Modelo de geração: [preencher]
- Estratégia de chunking e versão: [preencher]
- Região e banco remoto: [preencher]
- Limites de consumo e latência: [preencher]

## Evidências
[Vincule ADRs, testes e experimentos que sustentam as decisões.]
