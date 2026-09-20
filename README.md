# Portfolio AI Assistant

RAG para consultar experiência profissional e projetos a partir de fontes públicas
selecionadas, com respostas fundamentadas e indicação das fontes.

**Status: estrutura inicial.** Os pipelines, testes de comportamento, imagens Docker
e recursos AWS ainda não estão implementados. Não há deploy ou métricas de produção.

## Estrutura

```text
portfolio-ai-assistant/
├── src/
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── http/
│   │   │   ├── __init__.py
│   │   │   └── lambda_handler.py
│   │   └── events/
│   │       ├── __init__.py
│   │       └── s3_handler.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── chunker.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── embedding_service.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── retriever.py
│   ├── generation/
│   │   ├── __init__.py
│   │   └── generator.py
│   └── persistence/
│       ├── __init__.py
│       └── vector_repository.py
├── tests/
│   ├── unit/
│   │   ├── ingestion/
│   │   ├── embeddings/
│   │   ├── retrieval/
│   │   ├── generation/
│   │   └── persistence/
│   └── events/
│       ├── indexing/
│       │   └── s3_object_created.json
│       └── retrieval/
│           └── post_question.json
├── scripts/
│   ├── invoke_indexing.py
│   └── invoke_retrieval.py
├── docker/
│   ├── indexing.Dockerfile
│   └── retrieval.Dockerfile
├── terraform/
│   ├── versions.tf
│   ├── providers.tf
│   ├── variables.tf
│   ├── locals.tf
│   ├── outputs.tf
│   ├── s3.tf
│   ├── ecr.tf
│   ├── lambda.tf
│   ├── iam.tf
│   ├── events.tf
│   └── terraform.tfvars.example
├── docs/
│   ├── architecture/
│   └── diagrams/
├── .env.example
├── .gitignore
├── .dockerignore
├── requirements.txt
├── pytest.ini
├── Makefile
└── README.md
```

Pastas de testes ainda vazias possuem `.gitkeep` para serem preservadas no Git.

## Responsabilidades

| Pasta | Responsabilidade |
| --- | --- |
| `src/interfaces/` | Traduzir eventos HTTP e S3 para os serviços |
| `src/ingestion/` | Leitura de fontes aprovadas e chunking |
| `src/embeddings/` | Embeddings de documentos e perguntas |
| `src/retrieval/` | Busca, filtros e seleção de contexto |
| `src/generation/` | Respostas fundamentadas e citações |
| `src/persistence/` | Operações PostgreSQL + pgvector |
| `tests/unit/` | Testes de cada módulo sem serviços externos |
| `tests/events/` | Dados fictícios para testes e invocação local |
| `scripts/` | Ferramentas de invocação |
| `docker/` | Empacotamento das duas Lambdas |
| `terraform/` | Recursos AWS definidos como código |
| `docs/` | Arquitetura e diagramas |

Módulos simples por responsabilidade. Os handlers serão finos; clientes externos
serão recebidos explicitamente pelos serviços quando necessário para permitir
testes sem AWS ou chamadas pagas. Não há framework de agentes ou camadas adicionais.

## Lambdas e eventos

| Lambda | Entrada Python | Exemplo |
| --- | --- | --- |
| `portfolio-ai-assistant-indexing` | `interfaces.events.s3_handler.handler` | `tests/events/indexing/s3_object_created.json` |
| `portfolio-ai-assistant-retrieval` | `interfaces.http.lambda_handler.handler` | `tests/events/retrieval/post_question.json` |

A indexação receberá notificações S3 e não terá URL pública. A consulta usará
Function URL e coordenará embedding da pergunta, retrieval e geração.

O evento S3 referencia um Markdown fictício. O prefixo `approved/` no exemplo
não implementa aprovação de documentos. O evento HTTP contém o envelope entregue
pela Lambda; o navegador enviará apenas o JSON da pergunta presente em `body`.

Os exemplos não chamam AWS nem comprovam que os pipelines funcionam.
Os handlers levantam `NotImplementedError` e os scripts encerram informando que
a invocação está pendente.

## Desenvolvimento

```bash
python3 -m venv .venv
source .venv/bin/activate
make install-dev
```

O alvo instala `requirements.txt` e pytest na venv ativa. Dependências de runtime
serão adicionadas conforme cada integração for implementada.

`pytest.ini` configura imports de `src/`. Quando houver testes, executar
`make test` ou `python -m pytest`. Atualmente não há testes coletáveis:
o pytest retornará código 5. Os eventos JSON são fixtures, não testes executáveis.

## Docker e Terraform

Os Dockerfiles ainda contêm apenas orientações e não são buildáveis. Usarão a
raiz do repositório como contexto e copiarão o conteúdo de `src/` para um
diretório importável. As entradas estão indicadas na tabela das Lambdas.

Terraform contém variáveis, nomes e arquivos reservados para implementação.
Ainda não há configuração capaz de provisionar as Lambdas.

## Configuração e segurança

`.env.example` contém campos vazios ou nomes de exemplo, sem credenciais.
O carregamento de `.env` ainda não foi implementado; autenticação AWS será externa.

Versionar os arquivos Terraform e, quando gerado, `.terraform.lock.hcl`.
O `.gitignore` exclui secrets locais, estado, planos e valores locais de Terraform.
O `.dockerignore` permite somente código, Dockerfiles e dependências no contexto.
Testes e payloads de exemplo ficam fora das imagens.

## Próximos passos

1. Configurar versões do Terraform/provider AWS, região e autenticação.
2. Implementar ECR.
3. Implementar e testar o handler mínimo de indexação e sua imagem.
4. Implementar IAM, logs, Lambda e acionamento S3 com validação das fontes.
5. Construir leitura, chunking, embeddings e persistência por etapas.
6. Implementar consulta e avaliar retrieval e respostas com fontes.
