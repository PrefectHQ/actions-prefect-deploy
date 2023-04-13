# prefect-project-deploy
## Details
A Github Action to deploy one or more of your Prefect flow deployments via [Prefect Projects](https://docs.prefect.io/latest/concepts/projects/#projects)

## Requirements
- Access to a [Prefect Cloud Account](https://docs.prefect.io/latest/ui/cloud/#welcome-to-prefect-cloud)
- [Checkout](https://github.com/actions/checkout), [Setup Python](https://github.com/actions/setup-python), & [Docker Login](https://github.com/marketplace/actions/docker-login)/Cloud Docker Registry Login (If building and pushing a Docker artifact)

## Inputs
- prefect-api-key _(Required)_ A Prefect Cloud API Key
- prefect-workspace _(Required)_ Full handle of workspace, in format '<account_handle>/<workspace_handle>' 
- name _(Required)_ A name to give the deployment
- requirements-file-path _(Required)_ Path to requirements files to correctly install dependencies for your Prefect flow(s).  Defaults to the GH Workspace/requirements.txt
- work-pool _(Required)_ The work pool that will handle this deployment's runs
- work-queue _(Required)_ The work queue that will handle this deployment's runs (Defaults to `default`)
- entrypoint _(Not Required)_ The path to a flow entrypoint within a project, in the form of `./path/to/file.py:flow_func_name` (Required unless the `--flow` argument is specified in place of the entrypoint.)
- additional-args _(Not Required)_ Any additional arguments to pass to the Prefect Deploy command. Available additional arguments are listed below

## Example Usage (Docker based Prefect Deploy)
```yaml
name: Build and Deploy a Prefect Deployment
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
      - name: 
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Run Prefect Deploy
        uses: PrefectHQ/prefect-project-deploy@v1
        with:
          prefect-api-key: ${{ secrets.PREFECT_API_KEY }}
          prefect-workspace: 387d3401-z2e0-aa50-5a24-a67790f9c3f4/workspace/c87baf1f-y9ad-48ec-9e43-b3ed8d576164
          name: test-docker-deployment
          requirements-file: ./flows/requirements.txt
          work-pool: docker-work-pool
          work-queue: default
          entrypoint: ./example/flows/flow.py:call_api
          additional-args: --var foo=bar --cron "30 19 * * 0"
```

## Additional Arguments
| Arg Name      | Description                                                                                                             |
|---------------|-------------------------------------------------------------------------------------------------------------------------|
| --flow        | The name of a registered flow to create a deployment for. (Use in place of an entrypoint)                               |
| --description | The description to give the deployment. If not provided, the description will be populated from the flow's description. |
| --version     | A version to give the deployment.                                                                                       |
| --tag         | One or more optional tags to apply to the deployment. Note: tags are used only for organizational purposes.             |
| --variable    | One or more job variable overrides for the work pool provided in the format of key=value                                |
| --cron        | A cron string that will be used to set a CronSchedule on the deployment.                                                |
| --interval    | An integer specifying an interval (in seconds) that will be used to set an IntervalSchedule on the deployment.          |
| --anchor-date | The anchor date for an interval schedule                                                                                |
| --rrule       | An RRule that will be used to set an RRuleSchedule on the deployment.                                                   |
| --timezone    | Deployment schedule timezone string e.g. 'America/New_York'                                                             |
| --param       | An optional parameter override, values are parsed as JSON strings e.g. --param question=ultimate --param answer=42      |
| --params      | An optional parameter override in a JSON string format e.g. --params='{"question": "ultimate", "answer": 42}'           |
