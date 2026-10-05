FROM public.ecr.aws/lambda/python:3.14

COPY requirements.txt ${LAMBDA_TASK_ROOT}/requirements.txt

RUN pip install --no-cache-dir \
    -r ${LAMBDA_TASK_ROOT}/requirements.txt \
    --target ${LAMBDA_TASK_ROOT}

COPY src/ ${LAMBDA_TASK_ROOT}/

CMD ["interfaces.http.retrieval.lambda_function.lambda_handler"]
