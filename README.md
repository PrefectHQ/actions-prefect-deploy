# actions-prefect-deploy

## Details

A Github Action to deploy a Prefect flow via [Prefect Projects](https://docs.prefect.io/latest/concepts/projects/#projects)

## Requirements

- Access to a [Prefect Cloud Account](https://docs.prefect.io/latest/ui/cloud/#welcome-to-prefect-cloud)
- [Checkout](https://github.com/actions/checkout) - to clone the repo
- [Setup Python](https://github.com/actions/setup-python) - to install prefect & other requirements
- (optional) [Docker Login](https://github.com/marketplace/actions/docker-login) / Cloud Docker Registry Login if building and pushing a Docker artifact

## Inputs

| Input | Desription | Required | Default |
|-------|------------|----------|---------|
| additional-args | Any additional arguments to pass to the Prefect Deploy command. Available additional arguments are listed below. | false | |
| entrypoint | The path to a flow entrypoint within a project, in format: `./path/to/file.py:flow_func_name`. | true | |
| name | The name to give the deployment. | true | |
| prefect-api-key | API Key to authenticate with Prefect. | true | |
| prefect-workspace | Full handle of workspace, in format `<account_handle>/<workspace_handle>`. | true | |
| requirements-file-path | Path to requirements files to correctly install dependencies for your Prefect flow. | false | `./requirements.txt` |
| work-pool | The work pool that will handle this deployment's runs. | true | |

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
  deploy-flow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: checkout@v3

      - name: Setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}
          name: simple-deployment
          requirements-file-path: ./examples/simple/requirements.txt
          work-pool: simple-pool
          entrypoint: ./examples/simple/flow.py:call_api
          additional-args: --cron "30 19 * * 0"
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
  deploy-flow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: checkout@v3

      - name: Setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}
          name: basic-docker-auth-deployment
          requirements-file-path: ./examples/docker/requirements.txt
          work-pool: docker-pool
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron "30 19 * * 0"
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
  deploy-flow:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: checkout@v3

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v1
        with:
          workload_identity_provider: projects/<project_id>/locations/global/workloadIdentityPools/<pool-name>/providers/<provider-name>
          service_account: <gcp_service_account>@<project_id>.iam.gserviceaccount.com

      - name: Configure Google Cloud credential helper
        run: gcloud auth configure-docker --quiet us-docker.pkg.dev

      - name: Setup python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Run Prefect Deploy
        uses: PrefectHQ/actions-prefect-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: ${{ secrets.PREFECT_WORKSPACE }}
          name: gcp-workload-identity-auth-deployment
          requirements-file-path: ./examples/docker/requirements.txt
          work-pool: docker-pool
          entrypoint: ./examples/docker/flow.py:call_api
          additional-args: --cron "30 19 * * 0"
```
## Additional Arguments

| Arg Name | Description | Example |
|----------|-------------|---------|
| --anchor-date | The anchor date for an interval schedule. | |
| --cron | A cron string that will be used to set a CronSchedule on the deployment. | `--cron "30 19 * * 0" `|
| --description | The description to give the deployment. If not provided, the description will be populated from the flow's description. | |
| --interval | An integer specifying an interval (in seconds) that will be used to set an IntervalSchedule on the deployment. | `--interval 60` |
| --param | An optional parameter override, values are parsed as JSON strings | `--param question=ultimate --param answer=42` |
| --params | An optional parameter override in a JSON string format. | `--params='{"question": "ultimate", "answer": 42}'` |
| --rrule | An RRule that will be used to set an RRuleSchedule on the deployment. | |
| --tag | One or more optional tags to apply to the deployment - Note: tags are used only for organizational purposes. | |
| --timezone | Deployment schedule timezone string. | `--timezone 'America/New_York'` |
| --variable | One or more job variable overrides for the work pool. | `--variable foo=bar` |
| --version | A version to give the deployment. | |
| --work-queue | The work queue that will handle this deployment's runs. It will be created if it doesn't already exist. | `--work-queue test` |
