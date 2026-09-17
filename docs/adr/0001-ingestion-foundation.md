# ADR 0001 — Base da indexação e separação das Lambdas

Status: adotado para a estrutura inicial. Integrações ainda não implementadas.

## Contexto

Indexação e consulta permanecerão no mesmo repositório, mas serão implantadas
em Lambdas diferentes. A Lambda de consulta terá Function URL; a indexação será
administrativa, sem endpoint público. Imagens Docker serão preparadas na etapa
de implantação, com entradas e permissões distintas.

## Decisão

Usar uma separação pequena inspirada em Ports and Adapters:

- **Service Layer:** `PrepareDocument` coordena o primeiro caso de uso.
- **Port:** `DocumentLoader`, definido com `typing.Protocol`, descreve a leitura.
- **Dependency Injection:** o loader é recebido no construtor; não há container
  de injeção, singleton ou cliente global criado durante importação.
- **Objetos de dados imutáveis:** dataclasses representam fonte e documento preparado.
- **Adapter:** a próxima etapa implementará um loader Markdown local; futuramente
  outros adapters poderão ler S3 sem modificar o serviço.

O serviço não importa AWS, PostgreSQL, pytest nem SDK de embeddings. Testes usam
um stub em memória. Isso permite verificar regras sem rede ou credenciais.

Fluxo futuro: handler da Lambda → composição das dependências → serviço → adapters.
O handler ficará limitado a traduzir evento e resultado. Não haverá handler que
retorne sucesso fingindo ter indexado documentos.

O Repository para pgvector e o contrato do cliente de embeddings serão introduzidos
quando implementarmos essas integrações, com operações específicas. Não haverá
repository genérico, factory abstrata ou hierarquia de classes por antecipação.

## O que existe agora

Validação de metadata e aprovação explícita, contrato de leitura, normalização
conservadora de quebras de linha, SHA-256 e testes unitários. Ainda não existem
loader real, chunking, embeddings, persistência, handlers ou imagens Lambda.

A flag de aprovação é uma regra do caso de uso, não autenticação nem detecção de
secrets. Ela deverá vir de um manifesto controlado pelo administrador, nunca de
um campo aceito de visitantes do portfólio. Não inserir conteúdo privado no Git.

## Testes e organização

Pacote em `src/`, instalação editável e pytest com `--import-mode=importlib`.
As dependências de desenvolvimento ficam no extra `dev` do `pyproject.toml`.
Testes de integração serão adicionados quando houver banco, separados dos unitários.
Um lock de dependências deverá ser introduzido antes de builds de implantação.

Referências: [pytest](https://pytest.org/en/stable/explanation/goodpractices.html)
e [Python Packaging](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/).

## Consequências

Mais alguns arquivos que um script único, em troca de testes independentes da
infraestrutura. Novas abstrações só entram quando houver uma dependência concreta.
Hashes atuais representam conteúdo normalizado; decisões de reindexação também
precisarão considerar modelo, dimensionalidade e configuração de chunking.
