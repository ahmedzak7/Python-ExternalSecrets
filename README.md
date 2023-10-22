# Python-ExternalSecrets
GKE External Secrets and Secrets migration to Google Secret Manager using Python 
![faa0d8d8-0ba9-4c55-8987-bd0a2a26dc55](https://github.com/ahmedzak7/Python-ExternalSecrets/assets/64443382/54651d37-20dc-4b6b-8f5c-16c2a15075cd)


To migrate a large number of k8s secrets into secret manager I wrote a Python script that imports Kubernetes secrets from a specified namespace into Google Cloud Secret Manager. The script retrieves secrets from the Kubernetes cluster, decodes their values, and stores them securely in Google Cloud Secret Manager. It also creates corresponding ExternalSecret resources in Kubernetes to reference the secrets.

Manually migrating secrets from Kubernetes to Google Cloud Secret Manager can be time-consuming and error-prone. The script automates this process, reducing the manual effort required and minimizing the risk of human errors.


Code Explanation and Documentation
Imports
This section imports the necessary modules for the script, including the Google Cloud Secret Manager, the Kubernetes client library, and other standard Python libraries for encoding/decoding and JSON manipulation.

Load K8s Config
Loads the Kubernetes configuration from the default kubeconfig file or the environment variables.

Initialize K8s Client
Creates an instance of the Kubernetes CoreV1Api client to interact with Kubernetes resources.

Initialize Custom Objects API Client
Creates an instance of the Kubernetes CustomObjectsApi client to interact with custom Kubernetes resources.

Namespace Variable
Defines the variable namespace with the value "cert-manager" to specify the Kubernetes namespace where secrets will be retrieved.

Get Secrets from Namespace
Queries Kubernetes for secrets within the specified namespace using the previously defined namespace.

Initialize Secret Manager Client
Creates an instance of the Google Cloud Secret Manager Service Client to interact with secret management.

Loop through K8s Secrets and Create in Secret Manager
Iterates through the list of secrets retrieved from the Kubernetes namespace. For each secret:

Constructs the parent name for the secret in Google Cloud Secret Manager.

Builds a secret body with replication settings.

Creates the secret in Google Cloud Secret Manager.

Decodes the secret values from base64 and stores them in a dictionary.

Converts the dictionary into a JSON payload.

Adds a secret version to Google Cloud Secret Manager.

Constructs an ExternalSecret resource to reference the secret.

Checks if the ExternalSecret already exists, then either updates or creates it accordingly.

Usage
Update the namespace variable to specify the desired Kubernetes namespace.

Ensure the necessary libraries are installed: google-cloud-secret-manager, kubernetes. 

Refresh Interval 
The refreshInterval specifies how often the ExternalSecrets Operator should sync and refresh the external secrets from the external secret management service.

Frequent syncs can lead to increased API calls and resource consumption in the external secret management service.

We can start with a 1-hour interval and adjust it based on our specific use case, security considerations, and performance requirements.
