# Portfolio AI Assistant

Assistente RAG integrado ao [portfólio de João Paulo](https://joaosalesdev.github.io/portfolio/pt)
para consultar experiência profissional, projetos e decisões técnicas com base em
documentos selecionados, recuperando trechos e gerando respostas com referências.

**Em produção e funcionando**, conforme confirmação do mantenedor em 22/10/2026.
O chat já está integrado ao portfólio e usa o fluxo completo de consulta:
pergunta → embedding → busca no pgvector → contexto → resposta OpenAI.
A indexação parte dos uploads no S3 e persiste documentos, chunks e embeddings.
Inserções e atualizações sem duplicação, inclusive com aumento ou redução dos
chunks, já foram validadas pelo mantenedor.

O serviço em uso ainda utiliza os nomes de ambiente `dev` no GitHub Actions e no
estado Terraform; não há ambientes separados de desenvolvimento e produção.
A operação confirmada não encerra a avaliação de qualidade, custos e robustez.
Validação automática das citações foi adiada, e exclusão de documentos no S3 ainda
não remove dados do RAG.

Nesta revisão, os 77 testes pytest passaram localmente com serviços simulados.
O repositório também contém nove testes Terraform de app e um de base. Não foram
executadas chamadas à API paga, consultas ao banco ou mudanças na AWS nesta revisão.

## Problema e objetivo

Informações profissionais estão distribuídas entre portfólio, currículo e
documentação de projetos. O assistente permite que visitantes e recrutadores
encontrem informações específicas sem precisar navegar por todas essas fontes.

Exemplos de perguntas:

- Qual experiência com AWS está documentada?
- Em quais projetos foram utilizadas filas?
- Por que determinada solução arquitetural foi escolhida?
- Qual projeto demonstra integração com LLMs?

O objetivo é construir e operar uma aplicação pequena, avaliar a qualidade da
recuperação e evoluir a partir de resultados medidos. O sistema não deverá inventar
experiência profissional nem executar ações externas em nome do visitante.

## Arquitetura

![Arquitetura alvo do Portfolio AI Assistant: indexação de documentos via S3 e Lambda, consulta pelo portfólio e PostgreSQL com pgvector](docs/diagrams/01-high-level-architecture.png)

[Abrir o diagrama em tamanho original](docs/diagrams/01-high-level-architecture.png).

O diagrama representa os dois fluxos principais implementados. As chamadas às APIs de
embeddings e geração, a Function URL, o ECR e os componentes de operação estão
descritos abaixo, mas não aparecem individualmente nesta visão de alto nível.

### Indexação

```text
Administrador → documentos aprovados em bucket S3 privado
→ evento ObjectCreated → Lambda de indexação
→ leitura e normalização → chunking + metadata
→ API de embeddings → PostgreSQL + pgvector
```

A indexação preserva a origem dos trechos e registra hash, versão e configuração
dos embeddings. Documentos alterados são reprocessados, com substituição atômica
dos chunks por documento após a geração dos novos embeddings. O sequencer S3
é usado na persistência para ignorar eventos repetidos ou mais antigos.

O bucket é privado. Somente conteúdo autorizado para respostas públicas
deverá entrar na base. O mecanismo automático de aprovação ainda será implementado; a revisão e a
seleção dos arquivos enviados ao S3 são manuais.

### Consulta

```text
Visitante → chat do portfólio → HTTPS / Lambda Function URL
→ validação e normalização → embedding da pergunta → busca no pgvector
→ seleção de contexto → API de LLM → resposta com fontes
```

A Lambda de consulta coordena retrieval e geração. Documentos e perguntas usam
a mesma configuração de embeddings. As instruções orientam o modelo a reconhecer
falta de evidência; sem contexto, há uma mensagem fixa de abstenção. Isso não
garante correção factual. Falhas técnicas retornam códigos de erro próprios.

A busca atual é exata, por distância de cosseno. Chunking, Top-K e
eventuais thresholds serão avaliados com perguntas e evidências conhecidas.
Similaridade não será interpretada como garantia de verdade.

### Infraestrutura e componentes

- Duas Lambdas independentes, com imagens Docker armazenadas no Amazon ECR.
- S3 para documentos e notificação de criação de objetos para a indexação.
- Function URL para consultas do portfólio; indexação sem endpoint público.
- PostgreSQL + pgvector, com banco Neon já utilizado pelo mantenedor.
- Terraform para recursos AWS e roles IAM separadas.
- CloudWatch para logs e métricas.
- GitHub Actions implementado para validação, build, publicação e deploy.

Embeddings utilizam OpenAI `text-embedding-3-small`. A geração usa OpenAI `gpt-6-luna` via Responses API, com raciocínio `none`.

## Estado atual do repositório

| Componente | Situação no código |
| --- | --- |
| Terraform | Separado em base/app, com estados distintos no backend S3 |
| Lambdas | Indexing validado na AWS até a persistência; retrieval valida, normaliza, gera embeddings e busca chunks; imagens Docker por digest e arquitetura x86_64 |
| IAM | Roles separadas para Lambda com permissões de escrita nos grupos CloudWatch |
| CloudWatch | Dois grupos de logs com retenção de 30 dias |
| Handlers | Indexing valida eventos S3, prepara documentos, gera embeddings e persiste; retrieval valida, normaliza, gera embeddings e busca chunks; chat integrado ao portfólio e funcionando, conforme o mantenedor |
| Entrada S3 | Validação e extração de bucket, chave decodificada, versão e sequencer implementadas; leitura de .md e .txt em UTF-8 implementada |
| Dockerfiles | Imagens Python 3.14; indexing completo validado na AWS e retrieval com busca, contexto e geração |
| ECR | Dois repositórios definidos em base; criação na AWS confirmada |
| GitHub/AWS | Integração OIDC e permissões para publicação e deploy implementadas; deploy na AWS confirmado pelo mantenedor |
| GitHub Actions | Workflow de build, teste dos containers, publicação, plan e apply implementado; deploy funcionando na AWS; configuração de required reviewers não documentada como validada |
| S3 de documentos e notificação | Fluxo upload → Lambda → leitura → embeddings → banco confirmado pelo mantenedor |
| Function URL | Retrieval público definido com CORS para https://joaosalesdev.github.io; endpoint publicado e chat integrado, conforme o mantenedor |
| Embeddings | OpenAI text-embedding-3-small, 1.536 dimensões e lotes de até 32 chunks |
| Persistência | PostgreSQL + pgvector, transação por documento e comparação de sequencer; inserção e atualização sem duplicação validadas, incluindo aumento/redução dos chunks; rollback e concorrência reais ainda por validar |
| Retrieval e geração | Entrada HTTP, normalização, embedding, busca vetorial e seleção de contexto e geração implementados; validação das citações pendente |
| Testes | Dez testes Terraform com AWS simulado para S3, variáveis e Function URL, além do teste de invocação dos containers; 77 casos pytest de parsing, ingestão, normalização, chunking, embeddings e persistência |
| Scripts de invocação | Indexing e retrieval locais com eventos JSON implementados |

O backend S3 do Terraform armazena **estado da infraestrutura**. Ele é distinto
do bucket de documentos do RAG.

## Organização do código

```text
portfolio-ai-assistant/
├── src/
│   ├── interfaces/
│   │   ├── s3_event_parser.py  # Validação e interpretação do evento S3
│   │   └── lambda_handlers/
│   │       ├── indexing.py
│   │       └── retrieval.py
│   ├── ingestion/          # Leitura, normalização e chunking
│   ├── embeddings/         # Vetorização de documentos e perguntas
│   ├── retrieval/          # Busca e seleção de contexto
│   ├── generation/         # Respostas fundamentadas
│   └── persistence/        # Operações PostgreSQL + pgvector
├── tests/
│   ├── unit/              # Testes unitários por responsabilidade
│   └── events/            # Exemplos S3 e HTTP
├── sql/                   # Criação das tabelas de documentos e chunks
├── scripts/               # Invocação das funções
├── docker/                # Dockerfiles de indexação e consulta
├── terraform/
│   ├── base/              # ECR, OIDC e permissões do GitHub Actions
│   └── app/               # Lambdas e recursos da aplicação
├── docs/                 # Documentação, diagramas e rascunhos pessoais
├── requirements.txt
├── pytest.ini
├── Makefile               # Reservado para testes e tarefas futuras
└── README.md
```

A organização separa interfaces de entrada, processamento e persistência. Os
handlers deverão traduzir eventos e chamar serviços; clientes externos serão
injetados quando necessário para permitir testes sem AWS ou chamadas pagas.

As imagens usam os handlers `interfaces/lambda_handlers/indexing.py` e
`interfaces/lambda_handlers/retrieval.py`. Indexing recebe eventos S3; retrieval
valida a entrada HTTP. O processamento de documentos já está implementado no
indexing; retrieval recupera chunks, prepara o contexto e gera respostas.

### Entrada, leitura e normalização

O handler chama `interfaces/s3_event_parser.py`, que:

- Exige uma lista `Records` não vazia.
- Valida a origem `aws:s3` e eventos `ObjectCreated:*`.
- Extrai bucket, chave decodificada, `versionId` e `sequencer` de cada registro.
- Aceita múltiplos registros e preserva os campos opcionais quando presentes.
- Rejeita eventos inválidos com `ValueError`, registrado e propagado pelo handler.

O retorno contém `statusCode`, uma mensagem em inglês, a lista `objects` e
as contagens `documents_loaded`, `chunks_created`, `embeddings_generated`,
`documents_saved` e `documents_skipped`.
O handler chama `ingestion/loader.py` para cada objeto. O loader aceita `.md`
e `.txt`, solicita o objeto por bucket e chave, usa `VersionId` quando presente,
decodifica o conteúdo em UTF-8 e fecha o corpo da resposta. Documentos vazios,
formatos não suportados e conteúdo inválido causam erro. Falhas de leitura são
registradas pelo handler e propagadas, sem retornar sucesso falso.

O loader retorna texto e identificação da fonte para as próximas etapas. O handler
retorna os objetos e as contagens de processamento, sem expor o conteúdo. O handler normaliza o texto com `ingestion/preprocessor.py`: padroniza quebras
de linha, remove espaços finais sem significado e reduz linhas vazias excessivas
fora de blocos de código. Preserva indentação, blocos de código e quebras de linha
Markdown com dois espaços. Ainda não há mecanismo de aprovação de
conteúdo. O parser pertence a `interfaces/`; a leitura pertence a `ingestion/`.

Os rascunhos pessoais de implementação estão em
[docs/rascunho-indexing.txt](docs/rascunho-indexing.txt) e
[docs/rascunho-retrieval.txt](docs/rascunho-retrieval.txt).

### Chunking inicial

`ingestion/chunker.py` recebe o documento normalizado e retorna chunks com limite
configurável por `max_chars` (padrão: 1.000 caracteres). Prioriza quebras entre
parágrafos, depois espaços em branco; quando necessário, corta no limite.
O handler usa o valor padrão. A estratégia inicial não utiliza sobreposição.

Cada chunk preserva os metadados de origem e acrescenta `chunk_index` (a partir
de zero), `start_char` e `end_char` (exclusivo), relativos ao texto normalizado.
A concatenação dos chunks reproduz o texto integralmente. Texto vazio ou composto
apenas por espaços em branco retorna uma lista vazia; limites inválidos geram erro.

O tamanho é medido em caracteres, não tokens. Títulos e blocos de código podem
ser separados quando ultrapassam o limite; identificação de seções e ajustes de
sobreposição ficam para avaliação posterior. Os chunks recebem embeddings na etapa seguinte e são enviados à persistência. Logs registram contagens,
sem imprimir o conteúdo completo dos documentos.

### Embeddings

`embeddings/embedding_service.py` gera vetores com `text-embedding-3-small` e
1.536 dimensões explícitas, em lotes de até 32 chunks. Valida a quantidade,
os índices e a dimensão das respostas antes de associar cada vetor à sua fonte.
O resultado preserva texto e metadados, acrescentando `embedding`,
`embedding_model` e `embedding_dimensions`.

O handler usa o SDK OpenAI com timeout de 20 segundos por tentativa e até duas
retentativas. Falhas são registradas e propagadas. O retorno inclui apenas a
contagem `embeddings_generated`, sem expor vetores ou texto. Os vetores são enviados ao repositório PostgreSQL após sua geração. Reexecutar um evento repete as chamadas pagas.

A variável `OPENAI_API_KEY` deve estar disponível no processo; `.env` não é
carregado automaticamente. A execução local agora chama a API e pode gerar custos.
Na AWS, o Terraform configura a chave nas Lambdas usando o secret de repositório
`OPENAI_API_KEY` recebido pelo workflow. Não inserir a chave no código ou no Git.
Os timeouts de indexing e retrieval no Terraform são de 120 segundos; lotes de
muitos documentos ainda podem exceder esse limite. Não há orçamento global de
execução nesta versão inicial.

### Persistência PostgreSQL + pgvector

A extensão `vector` e as tabelas já estão em uso no banco do mantenedor.
Para preparar outro ambiente, execute [sql/001_vector_storage.sql](sql/001_vector_storage.sql) no banco
alvo, por exemplo pelo editor SQL do DBeaver. O script cria `portfolio_documents`
e `portfolio_chunks` com `vector(1536)`. Ele não é executado automaticamente pelo
handler. Para tabelas já existentes, revise sua compatibilidade; `IF NOT EXISTS`
não atualiza esquemas antigos.

Configure `DATABASE_URL` no processo e como secret do repositório para o deploy
via Terraform, com os parâmetros
TLS exigidos pelo provedor. A role do banco precisa de leitura/escrita nas tabelas
e acesso à sequência da coluna identity. Não publique a URL com credenciais.

`persistence/vector_repository.py` salva o texto normalizado, hash SHA-256, origem,
versão, sequencer e chunks com vetores e configuração do modelo. Uma transação
por documento bloqueia seu registro, substitui os chunks e atualiza os metadados.
Falhas durante a escrita revertem a transação. Documentos anteriores do mesmo
lote podem já ter sido confirmados se outro documento falhar.

Eventos com sequencer igual ou menor são ignorados na persistência; eventos sem
sequencer não sobrescrevem um documento que já tenha sequência registrada.
Eventos sem sequencer entre si apenas substituem o registro. A comparação ocorre
após os embeddings, portanto reentregas ainda podem consumir API. Exclusões S3
não removem documentos nesta implementação.

O handler retorna `documents_saved` e `documents_skipped`, além das contagens das
etapas anteriores. Os testes usam conexões simuladas: não comprovam execução do
SQL, rollback ou concorrência em um PostgreSQL real. Separadamente, o mantenedor
validou a inserção e a atualização reais sem duplicação, inclusive com aumento
e redução do número de chunks. Rollback, concorrência e descarte de eventos
antigos ainda não têm validação específica registrada.

### Variáveis de ambiente

O RAG exige `OPENAI_API_KEY` e `DATABASE_URL`. As notificações opcionais da
Melita utilizam `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID`, somente no retrieval. Ambas são
configuradas pelo Terraform nas Lambdas. Retrieval utiliza ambas para embeddings,
busca vetorial e geração.

`DOCUMENTS_BUCKET` não é necessário: bucket e chave vêm do evento S3.
`INDEXING_FUNCTION_NAME` e `RETRIEVAL_FUNCTION_NAME` não são consumidos pelo código.
`AWS_REGION` é fornecido pelo ambiente Lambda; localmente, configure a região
no seu perfil AWS ou no ambiente, se necessário. Não tente sobrescrever a variável
reservada `AWS_REGION` no bloco environment da Lambda.

O `.env.example` contém as variáveis obrigatórias e as duas opcionais do Telegram. Ele é uma
referência e não carrega automaticamente um `.env`. O Terraform recebe os valores
por `TF_VAR_openai_api_key` e `TF_VAR_database_url`; o workflow usa GitHub Actions
Repository Secrets com nomes `OPENAI_API_KEY` e `DATABASE_URL`.
Veja [a configuração do deploy](docs/deployment.md).

Os valores são marcados como sensíveis, mas permanecem no estado Terraform e no
plano binário armazenado como artifact. Esses arquivos devem ter acesso restrito.

### Entrada de consulta

`interfaces/question_parser.py` interpreta eventos HTTP de Lambda Function URL:
aceita POST com body JSON contendo `question`, incluindo body codificado em base64.
A pergunta deve ser uma string não vazia de até 2.000 caracteres, após remover
espaços nas extremidades. O corpo decodificado é limitado a 16 KiB.

O handler retorna JSON com HTTP 200 após processar a consulta, 400 para
conteúdo inválido, 405 para método não suportado, 413 para corpo muito grande e
502 para falha no embedding ou na geração e 503 para falha na consulta ao banco. A resposta contém a pergunta normalizada,
o modelo, a dimensão, os chunks recuperados e o contexto com fontes, sem expor o vetor. A resposta gerada é retornada no campo `answer`.
A Function URL e o CORS estão configurados na AWS e são utilizados pelo chat,
conforme confirmação do mantenedor.

Após a validação, `retrieval/query_preprocessor.py` normaliza a pergunta: espaços
repetidos, tabs e quebras de linha tornam-se um único espaço, sem espaços nas
extremidades. Acentos, maiúsculas e pontuação são preservados. O limite de 2.000
caracteres continua sendo verificado antes dessa normalização. Não há remoção
de palavras ou processamento de Markdown nesta etapa.

A função `embed_query` em `embeddings/embedding_service.py` reutiliza a geração
em lote e a validação dos vetores dos documentos, com modelo e dimensão idênticos.
O cliente OpenAI usa timeout de 20 segundos e duas retentativas. Perguntas inválidas
são rejeitadas antes de criar o cliente. O vetor permanece em memória e é usado na busca no pgvector; não é retornado nem salvo.

A invocação local agora exige `OPENAI_API_KEY` e faz uma chamada paga à OpenAI.
Também requer `DATABASE_URL` e consulta o banco em modo somente de leitura.
A busca e a geração reais já funcionam pelo chat, conforme o mantenedor.
Os testes automatizados usam clientes simulados; a qualidade dos resultados
precisa continuar sendo avaliada com perguntas e evidências conhecidas.

Para executar localmente o evento POST de exemplo:

```bash
python scripts/invoke_retrieval.py
```

O fixture usa uma pergunta baseada em `career_goals.md`. Uma requisição HTTP real
leva apenas `{"question": "..."}` no corpo; o envelope do evento é produzido pela AWS.

### Busca vetorial

`retrieval/retriever.py` coordena a consulta implementada em
`persistence/vector_repository.py`. A busca usa distância de cosseno (`<=>`),
filtra pelo mesmo modelo e dimensão da pergunta e retorna os cinco chunks mais
próximos. O argumento `top_k` aceita de 1 a 20, configurável no código; não é
recebido do visitante. A consulta inclui desempate por documento e índice do chunk.

O retorno contém `matches` e `matches_count`. Cada resultado inclui texto,
distância, chave da fonte, versão, identificador do documento, índice e posições
do chunk. Não há filtro mínimo de relevância: resultados próximos podem não
responder à pergunta. Uma lista vazia retorna HTTP 200. A conexão solicita modo
somente de leitura e timeout SQL de 10 segundos, sem gravar dados.

Veja [como validar o retrieval](docs/validacao-retrieval.md), com perguntas de
exemplo, evidências esperadas e verificações SQL. Nenhuma migração adicional é
necessária nesta etapa.

### Seleção de contexto

`retrieval/context_selector.py` organiza os chunks recuperados em blocos `[S1]`,
`[S2]` etc., preservando a ordem da busca. Remove duplicatas do mesmo chunk e
ignora textos vazios. O limite padrão é de 6.000 caracteres, incluindo os rótulos
e separadores, configurável por `max_chars` no código. Chunks que não cabem são
ignorados inteiros, sem truncar; um trecho posterior menor ainda pode ser incluído.

O retorno acrescenta `context`, `sources`, `sources_count` e `has_context`.
Cada fonte mantém texto e metadados de origem, distância e um `id` correspondente
ao rótulo do contexto. Os campos `matches` continuam disponíveis para comparar
resultados recuperados com os efetivamente selecionados. Os logs mostram apenas
contagens e tamanho do contexto, sem imprimir o conteúdo.

O orçamento é de caracteres, não tokens. `has_context` indica somente que há
texto selecionado; não garante evidência suficiente para responder. Os documentos
continuam sendo dados não confiáveis: os identificadores não impedem prompt
injection. A geração separa instruções de conteúdo; a validação automática dos
identificadores das citações ainda não está implementada.
O contexto é enviado ao modelo na etapa seguinte de geração.

### Geração de respostas

`generation/generator.py` recebe a pergunta e o contexto selecionado. Usa
`gpt-6-luna` via Responses API com `reasoning={"effort": "none"}`, `store=False`
e limite de 800 tokens de saída. As instruções ficam separadas dos dados e
orientam respostas no idioma da pergunta, com citações `[S1]`, `[S2]`, sem inventar
informações e reconhecendo quando os documentos não fornecem evidência suficiente.

A chamada de geração tem timeout de 30 segundos e não usa retentativas automáticas.
Sem contexto, retorna uma mensagem fixa em português e pula a geração. O embedding
da pergunta e a consulta ao banco já ocorreram nesse caso.

A resposta inclui `answer`, `generation_model` e `generation_skipped`. Falhas de
API, saída incompleta ou texto vazio retornam HTTP 502. Ainda não há conferência
automática das citações nem garantia de sustentação factual. `sources` contém as
fontes selecionadas, que podem não coincidir com as efetivamente citadas.

A execução de `python scripts/invoke_retrieval.py` agora gera consumo da OpenAI
para embedding e, quando há contexto, geração. Continua usando `OPENAI_API_KEY`
e `DATABASE_URL`; nenhuma dependência adicional é necessária. A geração real foi confirmada pelo mantenedor no chat; nesta revisão, o agente
executou somente testes simulados. O timeout total da Lambda permanece em 120 segundos,
sem um controle global de duração entre as etapas.

Referências: [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
e [geração de texto](https://developers.openai.com/api/docs/guides/text).

### Notificações para Melita no Telegram

Após uma consulta bem-sucedida, retrieval envia a pergunta normalizada e a resposta
para o chat configurado no bot Melita. Isso inclui respostas de falta de contexto;
erros HTTP de entrada, embedding, consulta ou geração não geram notificação.
Não são enviados vetores, documentos completos, IPs ou credenciais.

Configure `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` no processo local ou como
Repository Secrets do GitHub Actions. O Terraform recebe os valores via
`TF_VAR_telegram_bot_token` e `TF_VAR_telegram_chat_id` e os adiciona apenas à Lambda
retrieval. O par é opcional: deixar ambos vazios desativa o envio; preencher somente
um é rejeitado pelo Terraform. O arquivo `.env` não é carregado automaticamente.

`notifications/telegram.py` usa a biblioteca padrão do Python, sem dependências
novas. Envia texto simples, sem interpretar Markdown/HTML e sem prévias de links.
Mensagens longas são divididas em partes conservadoras de até 3.500 unidades UTF-16.
Cada envio tem timeout de dois segundos e não é repetido automaticamente. A chamada
ocorre antes do retorno HTTP, podendo acrescentar latência. Com menos de dez
segundos restantes na Lambda, a notificação é ignorada.

O envio é de melhor esforço: configuração ausente, rejeição ou falha no Telegram
não altera a resposta do chat. Pode haver perda ou entrega parcial; não há fila,
retry ou garantia de entrega única. Os logs não incluem token, texto da conversa
ou URL do bot. Os secrets também permanecem no estado/plano Terraform, como os
outros valores sensíveis.

Antes do teste real, abra a conversa com Melita e envie `/start`; confirme que o
chat ID identifica a conversa desejada e que o bot tem permissão para enviar nela.
Ao executar `scripts/invoke_retrieval.py` com as variáveis presentes, o envio real
também acontece. Os testes automatizados não enviam mensagens. O frontend não
recebe nem deve enviar o token ou chat ID. Informe no portfólio que perguntas e
respostas são encaminhadas ao mantenedor pelo Telegram para acompanhamento.

## Desenvolvimento local

Criar e ativar um ambiente virtual e instalar as dependências declaradas:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

O `requirements.txt` inclui boto3 para acesso ao S3 e pytest para testes, além
das dependências transitivas. O SDK `openai` também está incluído. A conexão PostgreSQL usa `psycopg`; os vetores usam `pgvector`.
O `Makefile` está reservado para testes e outras tarefas futuras; não possui
comandos implementados.

Para executar os testes unitários, instale pytest no ambiente virtual:

```bash
python -m pip install 'pytest>=8.3,<10'
python -m pytest
```

Para executar somente os testes da entrada S3:

```bash
python -m pytest tests/unit/test_s3_event.py -v
```

Os JSONs em `tests/events/` são fixtures; o de indexing reproduz um evento real.

O evento de consulta representa o envelope entregue pela Function URL. Em uma
requisição HTTP real, o cliente enviará apenas o JSON da pergunta presente em
`body`, não o envelope inteiro.

Para invocar o handler de indexing diretamente no Python local:

```bash
python3 scripts/invoke_indexing.py
```

O script usa `tests/events/indexing/s3_object_created.json`; edite esse JSON
para testar outro evento.
O contexto é `None`. Este comando não invoca a Lambda na AWS nem usa Docker;
executa o handler Python atual, que valida o evento e retorna os dados dos
objetos, lê documentos no S3, chama a OpenAI e grava no PostgreSQL. Requer
credenciais AWS, permissão de leitura, `OPENAI_API_KEY` e `DATABASE_URL`.
Essa execução gera consumo da API e altera os registros do banco.

Para depurar no VS Code, selecione o interpretador da `.venv` com
**Python: Select Interpreter**. Na configuração de execução local do
`launch.json`, use `scripts/invoke_indexing.py` como programa. Coloque um
breakpoint no handler e inicie a depuração com **F5**. A configuração do VS Code
é local; a invocação pelo terminal acima também funciona sem ela.

## Terraform e deploy

As configurações em `terraform/base/providers.tf` e
`terraform/app/providers.tf` referenciam o mesmo bucket S3 de estado, com chaves
distintas. Para utilizá-las em outra conta, revisar backend, região,
credenciais externas e nomes antes de inicializar.

### Endpoint do chat

`terraform/app/function_url.tf` define uma URL HTTPS pública apenas para retrieval,
com autenticação `NONE`. O provider AWS 6.67.0 adiciona automaticamente as duas
permissões públicas de invocação exigidas pela AWS.
O CORS permite origem `https://joaosalesdev.github.io`, método POST e cabeçalho
`content-type`. O caminho `/portfolio/pt` não faz parte da origem do navegador.
A Function URL gerencia o preflight CORS; não adicionamos cabeçalhos CORS no handler.

Primeiro aplique `terraform/base` para conceder à role de deploy as permissões de
gerenciamento da URL, restritas à função retrieval. Depois execute o workflow de
app. Consulte o endpoint com `terraform -chdir=terraform/app output -raw
retrieval_function_url` ou no output do apply no Actions.

CORS controla leitura de respostas pelo navegador, não autentica chamadas.
A URL pública pode ser chamada por outros clientes e gerar consumo de API.
Não há rate limiting nesta alteração. Veja os comandos de teste no
[guia de deploy](docs/deployment.md).

### Base de conhecimento

`knowledge_base/` organiza os documentos usados para alimentar o RAG. A pasta local
não é sincronizada automaticamente com o S3. Revisar e enviar somente os documentos
aprovados ao prefixo `documents/` do bucket configurado.

`knowledge_base/README.md` e `knowledge_base/SOURCES.md` são guias de manutenção,
não conteúdo factual a indexar. O loader atual não interpreta nem filtra frontmatter
como `ingest: false` ou `status: draft`: qualquer `.md` ou `.txt` enviado ao prefixo
monitorado pode ser processado. A seleção deve ocorrer antes do upload.

### Retenção de imagens no ECR

O `base` configura uma política de lifecycle em cada repositório (`indexing` e
`retrieval`) para manter somente as três imagens mais recentes por data de push,
incluindo imagens com ou sem tags. Após aplicar a política, o ECR remove as
imagens excedentes automaticamente; a limpeza pode levar até 24 horas.
A retenção considera pushes, não deploys bem-sucedidos: uma imagem em uso pela
Lambda ou necessária para rollback pode ser removida se ficar fora das três
mais recentes.

### Bucket de documentos

O `base` cria o bucket `${project_name}-documents-${account_id}-${aws_region}`,
com bloqueio de acesso público, ACLs desabilitadas, criptografia SSE-S3 e
versionamento. `force_destroy = false` e `prevent_destroy = true` protegem os
documentos contra remoção pelo Terraform.

Execute e revise o `plan` de `base` e aplique-o antes do deploy de `app`.
Isso cria o bucket e atualiza as permissões da role de deploy. Os dois estados
precisam usar os mesmos `project_name`, conta AWS e `aws_region`.
O nome pode ser consultado com `terraform -chdir=terraform/base output documents_bucket_name`.

O `app` gerencia exclusivamente a configuração de notificações do bucket e a
permissão para o S3 invocar a Lambda de indexing. Uploads sob `documents/`
disparam `s3:ObjectCreated:*`, inclusive uploads multipart. O prefixo é
configurável por `documents_prefix`; a role da Lambda só pode ler objetos e
versões sob esse prefixo. Uploads fora dele não disparam indexing.

O handler de indexing processa documentos Markdown e texto até a persistência
dos embeddings. A leitura utiliza a versão indicada no evento, e a persistência
compara o sequencer para ignorar eventos duplicados ou antigos. Isso ainda não
evita chamadas repetidas à API de embeddings. Exclusões não disparam eventos
nesta configuração nem removem dados do banco. Nenhum arquivo é enviado pelo Terraform.

### Deployment Workflow

![Fluxo de deploy: Terraform base prepara ECR e acesso à AWS; GitHub Actions publica imagens e executa Terraform app para criar ou atualizar Lambdas](docs/diagrams/02-deployment-architecture.png)

[Abrir o fluxo de deploy em tamanho original](docs/diagrams/02-deployment-architecture.png).

O diagrama representa o fluxo de deploy implementado:

1. Terraform `base`, executado inicialmente na máquina local, cria o ECR e
   configura o acesso do GitHub à AWS via OIDC. O provider OIDC existente é
   reutilizado. A base volta a ser aplicada quando seus recursos mudam.
2. Um push na branch `main` dispara o GitHub Actions, que executa os
   testes pytest, os testes Terraform e a invocação local dos containers,
   constrói as duas imagens Docker e publica-as no ECR. Falhas nos testes
   interrompem o fluxo antes da publicação e do deploy.
3. No mesmo pipeline, o Actions passa as URIs com os digests das imagens ao
   Terraform `app`, executa o plan e aplica o plano no environment dev. A espera
   por aprovação depende da configuração de required reviewers.
4. Terraform `app` cria ou atualiza as Lambdas com as imagens publicadas e
   gerencia suas roles IAM e grupos de logs.

O digest identifica o conteúdo de uma imagem, permitindo selecionar sua versão
exata. Publicar uma imagem no ECR, sozinho, não atualiza a Lambda.
GitHub Actions coordena o deploy; Terraform gerencia a configuração das funções.

Terraform `app` recebe imagens por digest. O workflow está implementado em
`.github/workflows/deploy.yml` e utiliza o ambiente dev. A aprovação depende da
configuração de required reviewers no GitHub; a declaração do environment no
YAML, sozinha, não exige aprovação.

Veja [como preparar e executar o deploy](docs/deployment.md).
O deploy inicial foi confirmado em 12/10/2026 e o indexing completo em
18/10/2026. Em 22/10/2026, o mantenedor confirmou o assistente em produção,
com endpoint e chat do portfólio funcionando. Rollback operacional e verificação
automatizada após deploy continuam como melhorias pendentes.

## Segurança e operação

Com o chat em produção, continuar revisando e evoluindo:

- Seleção explícita de fontes, sem credenciais ou dados confidenciais.
- Secrets externos ao código, às imagens e ao contexto do modelo.
- Permissões mínimas e distintas para indexação e consulta.
- Limites de entrada, contexto, saída, duração e consumo.
- Tratamento de erros e logs estruturados sem exposição desnecessária de conteúdo.
- Validação das citações e renderização segura no frontend.
- Testes de prompt injection direta e indireta.

Conteúdo recuperado deve ser tratado como dado, não como instrução. Prompts
restritivos e citações não eliminam alucinações ou prompt injection.
As exclusões do Git e do contexto Docker não substituem a revisão dos arquivos
antes de publicá-los.

## Melhorias e validação contínua

1. Ampliar e revisar o conteúdo aprovado, registrando fontes e informações ausentes.
2. Manter perguntas com evidências esperadas, paráfrases e casos sem resposta;
   avaliar a recuperação separadamente da qualidade da resposta gerada.
3. Medir erros, latência, tokens e custos; definir proteção contra abuso e limites
   de consumo. CORS não limita chamadas diretas ao endpoint público.
4. Implementar tratamento de exclusões S3, considerando versionamento, delete
   markers e eventos fora de ordem, para remover documentos e chunks do RAG.
5. Retomar a validação automática das citações quando oportuno; ela foi adiada
   pelo mantenedor e não substitui a avaliação de sustentação factual.
6. Complementar testes reais de reentrega, evento antigo, concorrência e rollback;
   reduzir chamadas repetidas de embeddings quando um evento já foi processado.
7. Documentar rollback operacional, verificar o serviço após deploy e revisar a
   retenção de imagens; considerar ambientes separados conforme a necessidade.

Os diagramas atuais mostram arquitetura e deployment. Detalhes de sequência podem
ser acrescentados para explicar o comportamento já implementado, quando úteis.

A confirmação de operação pelo mantenedor e os testes locais são evidências
distintas. Ainda não há métricas consolidadas de uso, qualidade ou incidentes de
produção documentadas neste repositório.
