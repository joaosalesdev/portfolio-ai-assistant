# Arquitetura inicial

Status: estrutura de arquivos; pipelines ainda não implementados.

- `src/`: lógica RAG organizada por responsabilidade.
- `src/interfaces/events/s3_handler.py`: entrada S3 da Lambda de indexação.
- `src/interfaces/http/lambda_handler.py`: entrada HTTP de consulta via Function URL.
- `docker/indexing.Dockerfile` e `docker/retrieval.Dockerfile`: imagens das Lambdas.
- `tests/events/indexing/` e `tests/events/retrieval/`: payloads fictícios de exemplo.
- `tests/unit/`: pastas que espelham os módulos de processamento.
- `terraform/`: recursos AWS declarados como infraestrutura como código.

O handler de consulta orquestrará embeddings, retrieval e geração. O handler de
indexação orquestrará leitura, chunking, embeddings e persistência.
Os handlers traduzirão eventos; regras de processamento ficarão em `src/`.

Começaremos com funções e módulos simples e injeção explícita dos clientes externos
quando necessários. Esta estrutura não exige Clean Architecture, classes base ou
um framework de agentes. `persistence/vector_repository.py` concentrará SQL quando
houver banco. Os arquivos atuais são pontos de implementação, não integrações prontas.

Cada Dockerfile usará a raiz do repositório como contexto de build. A imagem deverá
copiar o conteúdo de `src/` para um diretório importável. As entradas serão
`interfaces.events.s3_handler.handler` e `interfaces.http.lambda_handler.handler`.
Os documentos serão referenciados por eventos S3; leitura, aprovação de fontes e
validações ainda precisam ser implementadas. Os exemplos não disparam chamadas AWS.
