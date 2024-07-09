#!/bin/bash

if [[ -z "${CDK_DEFAULT_ACCOUNT}" ]]; then
    echo "CDK_DEFAULT_ACCOUNT is not set. Exiting."
    exit 1
fi

if [[ -z "${CDK_DEFAULT_REGION}" ]]; then
    echo "CDK_DEFAULT_REGION is not set. Exiting."
    exit 1
fi

if [[ -z "${GRIPTAPE_API_KEY}" ]]; then
    echo "GRIPTAPE_API_KEY is not set. Exiting."
    exit 1
fi

if [[ -z "${OPENAI_API_KEY}" ]]; then
    echo "OPENAI_API_KEY is not set. Exiting."
    exit 1
fi

secret_name="griptape-api-key"
command_output=$(aws secretsmanager describe-secret --secret-id $secret_name --region ${CDK_DEFAULT_REGION})
command_exit_code=$?

if [[ "$command_exit_code" -ne 0 ]]; then
    echo "Creating secret $secret_name"
    aws secretsmanager create-secret --name $secret_name --secret-string "${GRIPTAPE_API_KEY}" --region ${CDK_DEFAULT_REGION}

    if [[ "$?" -ne 0 ]]; then
        echo "Failed to create secret $secret_name"
        exit 1
    else
        echo "Successfully created secret $secret_name"
    fi

secret_name="openai-api-key"
command_output=$(aws secretsmanager describe-secret --secret-id $secret_name --region ${CDK_DEFAULT_REGION})
command_exit_code=$?

if [[ "$command_exit_code" -ne 0 ]]; then
    echo "Creating secret $secret_name"
    aws secretsmanager create-secret --name $secret_name --secret-string "${OPENAI_API_KEY}" --region ${CDK_DEFAULT_REGION}

    if [[ "$?" -ne 0 ]]; then
        echo "Failed to create secret $secret_name"
        exit 1
    else
        echo "Successfully created secret $secret_name"
    fi