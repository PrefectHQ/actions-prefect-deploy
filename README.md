# actions-prefect-deploy

## Details

A Github Action to deploy one or more Prefect deployments with a [`prefect.yaml` file](https://docs.prefect.io/latest/guides/prefect-deploy/)). Note - all configuration must be defined in your `prefect.yaml` file, which will be inferred at run time. This means you **cannot** pass any additional CLI arguments. For example, your `prefect.yaml` should have the following configuration in place: 
```yaml
deployments:
  - name: Simple
    description: null
    entrypoint: examples/simple/flow.py:call_api
    flow_name: null
    parameters: {}
    schedule: null
    tags: []
    version: null
    work_pool:
      name: simple-pool
```

Additionally, the `prefect deploy` command needs to load your flow in order to gather some information about it. This results in the module that the flow is in being loaded, which can result in errors if not all the dependencies are present (issue [9512](https://github.com/PrefectHQ/prefect/issues/9512)). As a result, this action takes in a comma-seperated list of requirments to pre-load these ahead of running `prefect deploy`. This will **not** result in a generic image being created, but rather used to satisfy a pre-flight check required by the Prefect CLI. If building one or many custom docker images, those will still be isolated and only install the relevant dependencies defined as a part of your Dockerfile.

## Requirements

- Access to a [Prefect Cloud Account](https://docs.prefect.io/latest/ui/cloud/#welcome-to-prefect-cloud)
- [Checkout](https://github.com/actions/checkout) - to clone the repo
- [Setup Python](https://github.com/actions/setup-python) - to install prefect & other requirements
- [Prefect Auth](https://github.com/PrefectHQ/actions-prefect-auth) - to log into Prefect Cloud
- (optional) [Docker Login](https://github.com/marketplace/actions/docker-login) / Cloud Docker Registry Login if building and pushing a Docker artifact

## Inputs

| Input | Desription | Required |
|-------|------------|----------|
| deployment-names | Comma separated list of deployment names defined in the prefect.yaml file. | false |
| requirements-file-paths | Comma sepearated list of paths to requirements files to correctly install dependencies for your Prefect flow(s). | false |
| deployment-file-path | Relative path to your Prefect deployment file. Defaults to `./prefect.yaml` | false |
| all-deployments | If set to "true", all deployments defined in prefect.yaml will be deployed. This will override the deployment-names input. Defaults to "false" | true |

**Note**: When setting the `deployment-file-path` only associate deployment-names that are included in that deployment file.  If you attempt to pass a prefect deployment that is not included in that file, the action will fail.

## Examples

### Simple Prefect Deploy

Deploy a Prefect flow that doesn't have a `push` step defined in the `prefect.yaml`
```yaml
name: Deploy a Prefect flow
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Prefect Auth
        uses: PrefectHQ/actions-prefect-auth@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v3
        with:
          deployment-names: Simple
          requirements-file-paths: ./examples/simple/requirements.txt
          prefect-file: ./examples/simple/prefect.yaml
```

### Multi-Deployment Prefect Deploy

Deploy multiple Prefect deployments that do not have a `push` step defined in the `prefect.yaml`
```yaml
name: Deploy multiple Prefect deployments
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    runs-on: ubuntu-latest
    steps:
      - ...

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v3
        with:
          deployment-names: Simple_Deployment_1,Simple_Deployment_2
          requirements-file-paths: ./examples/multi-deployment/deployment-1/requirements.txt,./examples/multi-deployment/deployment-2/requirements.txt
          prefect-file: ./multi-deployment/prefect.yaml
```

### Multi-Deployment Prefect Deploy of all Deployments defined in `prefect.yaml`

Deploy all Prefect deployments that do not have a `push` step defined in the `prefect.yaml`
```yaml
name: Deploy all Prefect deployments
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    runs-on: ubuntu-latest
    steps:
      - ...

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v3
        with:
          all-deployments: "true"
          requirements-file-paths: ./examples/multi-deployment/deployment-1/requirements.txt,./examples/multi-deployment/deployment-2/requirements.txt
          prefect-file: ./examples/multi-deployment/prefect.yaml
```

### Basic Docker Auth w/ Prefect Deploy

Deploy a Prefect flow and also build a Docker artifact that pushes to a defined repository in the `prefect.yaml` file.
```yaml
name: Build an Image and Deploy a Prefect flow
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Prefect Auth
        uses: PrefectHQ/actions-prefect-auth@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v3
        with:
          deployment-names: Docker
          requirements-file-paths: ./examples/docker/requirements.txt
          prefect-file: ./examples/docker/prefect.yaml
```
### GCP Workload Identity w/ Prefect Deploy

Deploy a Prefect flow and also build a Docker artifact that pushes to a defined repository in the `prefect.yaml` file.
```yaml
name: Build an Image and Deploy a Prefect flow
on:
  push:
    branches:
      - main
jobs:
  deploy_flow:
    permissions:
      # required to obtain Google Cloud service account credentials
      id-token: write
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: projects/<project_id>/locations/global/workloadIdentityPools/<pool-name>/providers/<provider-name>
          service_account: <gcp_service_account>@<project_id>.iam.gserviceaccount.com

      - name: Configure Google Cloud credential helper
        run: gcloud auth configure-docker --quiet us-east1-docker.pkg.dev

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Prefect Auth
        uses: PrefectHQ/actions-prefect-auth@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v3
        with:
          deployment-names: Docker
          requirements-file-paths: ./examples/docker/requirements.txt
          prefect-file: ./examples/docker/prefect.yaml
```

## Terms & Conditions
See here for the Prefect's [Terms and Conditions](https://www.prefect.io/legal/terms/).
