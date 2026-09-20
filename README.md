# Portfolio AI Assistant

RAG para consultar experiência profissional e projetos a partir de fontes públicas
selecionadas, com respostas fundamentadas e indicação das fontes.

**Status: recomeço da estrutura.** Os arquivos definem responsabilidades e pontos
de implementação. Ainda não há pipeline RAG, testes de comportamento nesta nova
estrutura, imagem Docker buildável ou recursos AWS implantados.

## Estrutura

```text
portfolio-ai-assistant/
├── src/
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
├── infrastructure/
│   ├── indexing/
│   │   ├── handler.py
│   │   ├── Dockerfile
│   │   └── requests/event.json
│   └── retrieval/
│       ├── handler.py
│       ├── Dockerfile
│       └── requests/request.json
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
├── tests/unit/
├── scripts/
│   ├── invoke_indexing.py
│   └── invoke_retrieval.py
├── docs/
│   ├── architecture/
│   └── diagrams/
├── .env.example
├── .gitignore
├── .dockerignore
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── Makefile
└── README.md
```

## Responsabilidades

| Pasta | Finalidade |
| --- | --- |
| `src/ingestion/` | Leitura de fontes aprovadas e chunking |
| `src/embeddings/` | Embeddings de documentos e perguntas |
| `src/retrieval/` | Recuperação, filtros e seleção de contexto |
| `src/generation/` | Geração com evidências e citações |
| `src/persistence/` | SQL e armazenamento em PostgreSQL + pgvector |
| `infrastructure/` | Entradas e empacotamento das duas Lambdas |
| `terraform/` | Definição dos recursos AWS |
| `tests/unit/` | Testes sem rede ou chamadas pagas, adicionados com a implementação |
| `scripts/` | Ferramentas de invocação, ainda não implementadas |
| `docs/` | Arquitetura e diagramas |

Módulos simples por responsabilidade, sem a pasta intermediária `portfolio_ai/`.
Quando houver clientes externos, eles serão recebidos explicitamente pelas funções
ou serviços para permitir testes independentes da infraestrutura.

As funções planejadas são **portfolio-ai-assistant-indexing** e
**portfolio-ai-assistant-retrieval**. A primeira será administrativa; a segunda
receberá perguntas pela Function URL e coordenará retrieval e geração.

## Exemplos e limites atuais

- Handlers levantam `NotImplementedError`; não executam indexação nem consulta.
- Dockerfiles contêm orientações; ainda não podem gerar imagens.
- Scripts encerram informando que a invocação não foi implementada.
- Eventos JSON são propostas de contrato, sem recursos reais. `dry_run` ainda não
  é uma funcionalidade implementada. O exemplo de consulta representa um evento
  HTTP da Function URL; o corpo enviado pelo navegador será apenas a pergunta.
- Terraform contém nomes/variáveis e placeholders; ainda não provisiona recursos.
- S3 e acionamento por eventos dependem de decisão posterior; não são obrigatórios
  para iniciar o pipeline.

## Desenvolvimento

Criar um ambiente virtual antes de instalar as dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

O pytest está configurado para importar os módulos de `src/`. Os testes serão
adicionados com o primeiro comportamento real. Até lá, `make test` ou
`python -m pytest` reportará ausência de testes (código de saída 5).
As dependências de runtime serão escolhidas durante a implementação.

Cada Dockerfile usará a raiz do repositório como contexto de build. A imagem deverá
expor os módulos de `src/` no caminho de imports e copiar o handler correspondente.
O empacotamento será validado antes do deploy.

## Configuração e segurança

`.env.example` possui apenas campos de exemplo; não há carregamento automático
de `.env` nesta estrutura. Não incluir credenciais nos arquivos Python, Terraform,
imagens ou eventos de exemplo. Autenticação AWS será configurada externamente.

Versionar `terraform/*.tf` e, quando gerado, `.terraform.lock.hcl`.
Não versionar `.env`, credenciais, estado Terraform, planos salvos ou arquivos
locais `.tfvars`. As regras estão no `.gitignore`; o `.dockerignore` restringe
o contexto de build. Isso não substitui a revisão do conteúdo antes do commit.

## Próximos passos

1. Definir versões do Terraform/provider, região e autenticação AWS.
2. Implementar ECR.
3. Implementar e testar o handler mínimo de indexação e sua imagem.
4. Publicar a imagem e implementar IAM, logs e Lambda via Terraform.
5. Implementar leitura, chunking, embeddings e persistência progressivamente.
6. Implementar consulta e avaliação das respostas com fontes.

Não há métricas ou experiência de operação em produção registradas.
