# Arquitetura inicial

Status: estrutura de arquivos; pipelines ainda não implementados.

- `src/`: lógica RAG organizada por responsabilidade.
- `infrastructure/indexing/`: entrada e imagem da Lambda administrativa.
- `infrastructure/retrieval/`: entrada e imagem da Lambda de consulta via Function URL.
- `terraform/`: recursos AWS declarados como infraestrutura como código.

O handler de consulta orquestrará embeddings, retrieval e geração. O handler de
indexação orquestrará leitura, chunking, embeddings e persistência.
Os handlers traduzirão eventos; regras de processamento ficarão em `src/`.

Começaremos com funções e módulos simples e injeção explícita dos clientes externos
quando necessários. Esta estrutura não exige Clean Architecture, classes base ou
um framework de agentes. `persistence/vector_repository.py` concentrará SQL quando
houver banco. Os arquivos atuais são pontos de implementação, não integrações prontas.

Cada Dockerfile usará a raiz do repositório como contexto de build. A imagem deverá
copiar `src/` para um diretório importável e somente o handler da respectiva Lambda.
A origem dos documentos e o mecanismo de aprovação ainda precisam ser implementados.
