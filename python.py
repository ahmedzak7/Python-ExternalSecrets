# Imports
from google.cloud import secretmanager
from kubernetes import client, config
import base64
import json

# Load K8s config
config.load_kube_config()

# Initialize K8s client
k8s_client = client.CoreV1Api()
# Initialize Custom Objects API client
custom_api = client.CustomObjectsApi()
# Define the namespace variable
namespace = "default"

# Get secrets from namespace
secrets = k8s_client.list_namespaced_secret(namespace).items

# Initialize Secret Manager client
sm_client = secretmanager.SecretManagerServiceClient()

# Loop through K8s secrets and create in Secret Manager
for secret in secrets:
    secret_name = secret.metadata.name
    if secret_name == "yourexcludedsecret":
        print(f"Skipping secret '{secret_name}' as requested.")
        continue
    if secret.type == "helm.sh/release.v1" or secret.type == "kubernetes.io/tls":
        print(f"Skipping secret of type 'helm.sh/release.v1'")
        continue
    # Build parent name
    parent = f"projects/YOURPROJECTNAME"

    # Build secret body
    secret_body = {
        "replication": {
            "automatic": {}
        }
    }

    # Create secret
    secret_id = secret.metadata.name
    response = sm_client.create_secret(
        request={
            "parent": parent,
            "secret_id": secret_id,
            "secret": secret_body
        }
    )

    # Print name
    print(f"Created secret: {response.name}")

    # Create a dictionary to store key-value pairs
    data_dict = {}

    for key, value in secret.data.items():
        # Decode the base64 value
        decoded_value = base64.b64decode(value).decode()

        # Add key-value pair to the dictionary
        data_dict[key] = decoded_value

    # Convert the dictionary to a JSON string
    payload_str = json.dumps(data_dict)

    # Build the resource name of the parent secret.
    parent = f"projects/YOURPROJECTNAME/secrets/{secret_id}"

    # Convert the string payload into bytes
    payload_bytes = payload_str.encode('UTF-8')

    # Add the secret version.
    version_response = sm_client.add_secret_version(parent=parent, payload={'data': payload_bytes})

    # Print the new secret version name.
    print(f'Added secret version: {version_response.name}')
    
    # Create ExternalSecret resource data
    external_secret_data = [
        {
            "secretKey": key,
            "remoteRef": {
                "key": secret_id,
                "property": key
            }
        }
        for key in data_dict
    ]

    # Create ExternalSecret resource
    external_secret = {
        "apiVersion": "external-secrets.io/v1beta1",
        "kind": "ExternalSecret",
        "metadata": {
            "name": f"{secret_id}-external-secret",
            "namespace": namespace
        },
        "spec": {
            "refreshInterval": "1h",
            "secretStoreRef": {
                "kind": "SecretStore",
                "name": "gcp-store"
            },
            "target": {
                "name": f"{secret_id}",
                "creationPolicy": "Owner"
            },
            "data": external_secret_data
        }
    }

    # Check if the ExternalSecret already exists, then create or update accordingly
    external_secret_name = f"{secret_id}-external-secret"
    try:
        custom_api.replace_namespaced_custom_object(
            group="external-secrets.io",
            version="v1beta1",
            namespace=namespace,
            plural="externalsecrets",
            name=external_secret_name,
            body=external_secret,
        )
        print(f"Updated ExternalSecret: {external_secret_name}")
    except client.exceptions.ApiException as e:
        if e.status == 404:
            custom_api.create_namespaced_custom_object(
                group="external-secrets.io",
                version="v1beta1",
                namespace=namespace,
                plural="externalsecrets",
                body=external_secret,
            )
            print(f"Created ExternalSecret: {external_secret_name}")
        else:
            raise e
