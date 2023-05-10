# actions-prefect-deploy

## Details

A Github Action to deploy one or more Prefect deployments via [Prefect Projects](https://docs.prefect.io/latest/concepts/projects/#projects). Note - all configuration must be defined in your `deployment.yaml`, which will be infered at run time; this means you **cannot** pass any additional CLI arguments. For example, your `deployment.yaml` should have the following configuration in place: 
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
| deployment-names | Comma separated list of deployment names defined in the deployment.yaml file. | true |
| requirements-file-paths | Comma sepearated list of paths to requirements files to correctly install dependencies for your Prefect flow(s). | false |

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
      - uses: checkout@v3

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
```
### Multi-Deployment Prefect Deploy

Deploy multiple Prefect deployments that doesn't have a `push` step defined in the `prefect.yaml`
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
      - uses: checkout@v3

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

          requirements-file-paths: ./examples/multi-deployment/deployment-1/requirements.txt,./examples/multi-deployment/deployment-2/requirements.txt
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
      - uses: checkout@v3

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
        uses: PrefectHQ/actions-prefect-deploy@v2
        with:
          requirements-file-path: ./examples/docker/requirements.txt
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron '30 19 * * 0' --pool docker-pool
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
        uses: PrefectHQ/actions-prefect-deploy@v2
        with:
          requirements-file-path: ./examples/docker/requirements.txt
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron '30 19 * * 0' --pool docker-pool
```
## Additional Arguments

| Arg Name | Description | Example |
|----------|-------------|---------|
| --anchor-date | The anchor date for an interval schedule. | |
| --cron | A cron string that will be used to set a CronSchedule on the deployment. | `--cron '30 19 * * 0' `|
| --description | The description to give the deployment. If not provided, the description will be populated from the flow's description. | |
| --interval | An integer specifying an interval (in seconds) that will be used to set an IntervalSchedule on the deployment. | `--interval 60` |
| --name | The name to give the deployment. | `--name 'Test Flow'` |
| --param | An optional parameter override, values are parsed as JSON strings | `--param question=ultimate --param answer=42` |
| --params | An optional parameter override in a JSON string format. | `--params='{"question": "ultimate", "answer": 42}'` |
| --pool | The work pool that will handle this deployment's runs. | `--pool docker-pool` |
| --rrule | An RRule that will be used to set an RRuleSchedule on the deployment. | |
| --tag | One or more optional tags to apply to the deployment - Note: tags are used only for organizational purposes. | |
| --timezone | Deployment schedule timezone string. | `--timezone 'America/New_York'` |
| --variable | One or more job variable overrides for the work pool. | `--variable foo=bar` |
| --version | A version to give the deployment. | |
| --work-queue | The work queue that will handle this deployment's runs. It will be created if it doesn't already exist. | `--work-queue test` |

## Terms & Conditions
See here for the Prefect's [Terms and Conditions](https://www.prefect.io/legal/terms/).
