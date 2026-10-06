# Deployment Workflow

O workflow em `.github/workflows/deploy.yml` implanta o ambiente **dev**, usando
o backend S3 existente. Ainda não há um ambiente de produção separado.
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

Não é necessário cadastrar access keys. O ARN da role, a região, a conta AWS e
os nomes dos repositórios estão explícitos no workflow e não são secrets.

## Etapas

O job `plan` valida o Terraform, constrói as duas imagens linux/amd64 e invoca
seus handlers localmente. Este teste verifica o empacotamento e a execução dos
handlers mínimos; não valida um pipeline RAG.

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

Após o apply, confira os outputs dos nomes e ARNs das funções e seus grupos
`/aws/lambda/portfolio-ai-assistant-indexing` e
`/aws/lambda/portfolio-ai-assistant-retrieval`, com retenção de 30 dias.
Este primeiro deploy ainda não cria Function URL nem conecta notificações S3.
As imagens continuam usando os handlers mínimos.

Rollback automatizado e verificação da função implantada na AWS ainda não foram
implementados. Para rollback, será necessário gerar e revisar um novo plano
com os digests anteriores.

Referências: [environments e aprovação no GitHub](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments)
e [autenticação OIDC na AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws).
