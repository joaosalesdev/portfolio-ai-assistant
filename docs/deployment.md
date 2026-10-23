# Deployment Workflow

O workflow em `.github/workflows/deploy.yml` implanta o ambiente **dev**, usando
o backend S3 existente. O mantenedor confirmou em 12/10/2026 que o deploy está
funcionando e que as Lambdas foram testadas na AWS, retornando mensagens fixas.
Ainda não há um ambiente de produção separado nem um pipeline RAG funcional.
Terraform base continua sendo aplicado localmente quando seus recursos mudam.

## Preparação antes do primeiro push

1. Revise e aplique a base:

   ```bash
   terraform -chdir=terraform/base plan
   terraform -chdir=terraform/base apply
   ```

   Isso atualiza a confiança OIDC para os jobs da main e do ambiente dev,
   configura acesso de leitura das imagens pela Lambda e permissões de deploy.
   Nenhuma imagem precisa existir para aplicar a base.

2. No GitHub, abra **Settings → Environments → New environment** e crie `dev`.
   Configure **Required reviewers** e **Deployment branches and tags** para
   permitir somente a branch `main`.
   A confiança OIDC de jobs com environment usa o nome do ambiente, em vez da
   branch; por isso a restrição de branches no environment é necessária.
   Confira a disponibilidade dessas proteções no plano do GitHub utilizado.

   **Sem required reviewers, o job apply não espera aprovação.** A declaração
   `environment: dev` no YAML, sozinha, não configura a proteção.
   Se você for o único revisor, habilitar `Prevent self-review` impede que aprove
   seus próprios deploys.

3. Faça commit dos arquivos e push na main. O workflow também pode ser iniciado
   por **Actions → Deploy Lambda containers → Run workflow**, selecionando main.

Cadastre em **Settings → Secrets and variables → Actions → Repository secrets**:

- `OPENAI_API_KEY`
- `DATABASE_URL`

O job `plan` não utiliza o environment `dev`, portanto secrets cadastrados apenas
nesse environment não ficam disponíveis para ele. O workflow verifica a presença
dos dois secrets antes do build e passa seus valores para `TF_VAR_openai_api_key`
e `TF_VAR_database_url` somente na etapa de plan. O apply utiliza o plano salvo,
sem precisar receber os valores novamente. Não cadastre esses valores como Variables
públicas e não os inclua no YAML ou em arquivos versionados.

O Terraform configura ambas as Lambdas com `OPENAI_API_KEY` e `DATABASE_URL`.
O indexing já as utiliza; retrieval recebe a configuração para implementação futura.
O `.env` local não é lido pelo Terraform nem pelo GitHub Actions.

Para plan local, com as variáveis da aplicação já exportadas no terminal:

```bash
export TF_VAR_openai_api_key="$OPENAI_API_KEY"
export TF_VAR_database_url="$DATABASE_URL"
terraform -chdir=terraform/app plan
```

As variáveis são `sensitive`, o que oculta os valores na saída usual do Terraform.
Porém os valores permanecem no estado e no plano binário salvo, inclusive no
artifact de plan usado pelo workflow. Restrinja acesso ao backend e aos artifacts;
o artifact atual tem retenção de um dia. Esta implementação usa env vars diretas,
sem integrar Secrets Manager. Uma futura integração pode evitar incluir os valores
no estado Terraform.

Não é necessário cadastrar access keys AWS. O ARN da role, a região, a conta AWS e
os nomes dos repositórios estão explícitos no workflow e não são secrets.

## Etapas

O job `plan` configura Python 3.14, instala `requirements.txt` e executa
`python -m pytest -v`. Os testes unitários usam clientes simulados e não acessam
a AWS. Se algum teste falhar, o job para antes do build, publicação e deploy.
Alterações em `tests/` ou `pytest.ini` também disparam o workflow na main.

Depois, valida o Terraform, constrói as duas imagens linux/amd64 e invoca
seus handlers localmente. Este teste verifica o empacotamento: retrieval retorna HTTP 400 para um evento vazio e indexing
rejeita esse evento com ValueError, sem chamadas à OpenAI, ao banco ou à AWS. Não valida a leitura
S3 nem um pipeline RAG.

Depois, assume a role via OIDC, publica as imagens e consulta seus digests.
As tags incluem commit, execução e tentativa, evitando colisões com as tags
imutáveis do ECR ao repetir o workflow.

As URIs completas são fornecidas via `TF_VAR_indexing_image_uri` e
`TF_VAR_retrieval_image_uri`. O workflow salva o plano e o lock dos providers
em um artifact com retenção de um dia e mostra o plano no resumo da execução.

O job `apply` usa o environment dev. Após a aprovação configurada no GitHub,
baixa o artifact da mesma execução e aplica exatamente o plano salvo.
A base não é aplicada pelo workflow.

As execuções são serializadas e o estado usa bloqueio no S3. Se outro processo
alterar o estado durante a espera, o plano pode ficar obsoleto: execute novamente
o workflow completo e revise o novo plano. Faça o mesmo se o artifact expirar ou
precisar repetir um job; use **Re-run all jobs**.

## Verificação

Após o apply, confira as funções no console AWS e seus grupos
`/aws/lambda/portfolio-ai-assistant-indexing` e
`/aws/lambda/portfolio-ai-assistant-retrieval`, com retenção de 30 dias.
O Terraform cria uma Function URL pública para retrieval com CORS do portfólio. A notificação S3 para indexing
está definida em `terraform/app/events.tf`; o fluxo de upload até a Lambda foi confirmado pelo mantenedor com um log real. A invocação dos handlers anteriores, com mensagens fixas, foi testada na AWS.
O código local de indexing agora lê documentos no S3; seu deploy e a leitura
real ainda precisam ser validados.

Rollback automatizado e verificação automatizada das funções na AWS após o
deploy ainda não foram implementados. A invocação das funções implantadas já
foi validada pelo mantenedor. Para rollback, será necessário gerar e revisar um novo plano
com os digests anteriores.

Referências: [environments e aprovação no GitHub](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
e [autenticação OIDC na AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).

## Publicar o endpoint do portfólio

Esta alteração requer aplicar a base antes do workflow de app: a role GitHub
Actions precisa de Create/Get/Update/DeleteFunctionUrlConfig, concedidos apenas
para retrieval. As permissões de AddPermission/RemovePermission já existem.
O workflow não aplica base automaticamente.

```bash
terraform -chdir=terraform/base plan
terraform -chdir=terraform/base apply
```

Depois faça push das mudanças de app na main (ou execute o workflow manualmente).
O provider AWS 6.67.0 cria a URL e adiciona automaticamente duas permissões
públicas: InvokeFunctionUrl com auth NONE e InvokeFunction restrita a chamadas
via Function URL. Não há recursos aws_lambda_permission adicionais para a URL,
evitando alterações concorrentes na política durante sua criação. Indexing continua
sem endpoint público. Nenhum apply foi executado pelo agente nesta alteração.

Obtenha a URL pelo output do job apply ou, com acesso ao estado:

```bash
terraform -chdir=terraform/app output -raw retrieval_function_url
```

No terminal, substitua o exemplo pela URL real e confira o preflight, sem chamar
embeddings ou geração:

```bash
CHAT_URL='https://SUBSTITUA.lambda-url.us-east-1.on.aws/'
curl -i -X OPTIONS "$CHAT_URL" \
  -H 'Origin: https://joaosalesdev.github.io' \
  -H 'Access-Control-Request-Method: POST' \
  -H 'Access-Control-Request-Headers: content-type'
```

Esperado: status 2xx e cabeçalhos de CORS permitindo a origem, POST e content-type.
A AWS responde ao preflight. Não é necessário adicionar OPTIONS ao parser da aplicação.
Repetir com uma origem diferente não deve conceder acesso CORS a essa origem.

Para testar a pergunta real (chamadas pagas à OpenAI e leitura do banco):

```bash
curl -i "$CHAT_URL" \
  -H 'Origin: https://joaosalesdev.github.io' \
  -H 'Content-Type: application/json' \
  --data '{"question":"Quais oportunidades profissionais João Paulo procura?"}'
```

Esperado: JSON com `answer`, e cabeçalho Access-Control-Allow-Origin para o portfólio.
HTTP 403 pode indicar ausência de uma das duas permissões públicas. 502/503 são
tratados pelo handler para falhas de geração/embedding ou banco; conferir os logs.

Para integrar o frontend, use a URL retornada e envie somente o JSON da pergunta.
Não envie OPENAI_API_KEY ou DATABASE_URL ao navegador. O CORS vale para toda a
origem joaosalesdev.github.io, sem restrição por caminho. Ele não bloqueia curl,
bots ou outras chamadas diretas; não há autenticação ou rate limiting nesta etapa.

### Conflito durante criação da Function URL

O provider AWS 6.67.0 adiciona as permissões públicas ao criar uma URL com auth
NONE. Recursos separados para essas mesmas permissões podem executar alterações
concorrentes na política e causar ResourceConflictException. A configuração atual
usa apenas a criação automática do provider para as permissões públicas da URL.
A permissão S3 de indexing permanece como recurso separado.

Após um apply parcial, execute novamente o workflow completo (Re-run all jobs)
para produzir e revisar um plano atualizado. Não reaplique o plano antigo. O
Terraform deve reconciliar recursos já gravados no estado; recursos tainted podem
ser recriados, o que pode alterar o endereço da URL.

Se o novo erro disser explicitamente que a configuração da URL já existe e ela
não estiver no estado, avalie importar a URL existente. Não exclua a URL ou o estado
sem conferir o erro e o plan. As permissões criadas automaticamente pelo provider
não são removidas automaticamente quando a URL é excluída; conferir a política
em uma futura desativação do endpoint.

## Notificações opcionais da Melita

Para ativar após o deploy, cadastre também os Repository Secrets:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

O workflow passa os valores apenas à etapa de plan. O Terraform os configura
somente no environment da Lambda retrieval; indexing não recebe essas credenciais.
Não é necessário aplicar base para esta integração. Os dois valores devem estar
preenchidos juntos ou ambos vazios. Localmente, correspondem a
`TF_VAR_telegram_bot_token` e `TF_VAR_telegram_chat_id` no Terraform; variáveis do
processo `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` para executar Python.

Confirme o chat de destino e inicie a conversa com o bot antes do teste. Depois
do deploy, faça uma pergunta pelo portfólio: a resposta deve chegar ao chat e ao
Telegram. Falhas de envio não interrompem o RAG; verificar avisos de notificação
nos logs, sem imprimir secrets. Perguntas e respostas passam a ser encaminhadas
para um serviço externo e ao mantenedor; comunicar esse uso no chat do portfólio.

A entrega real não foi testada pelo agente. Não há dependência Python nova nem
alteração da API pública de resposta. Secrets continuam presentes no plano e no
estado Terraform; restringir acesso a esses arquivos.
