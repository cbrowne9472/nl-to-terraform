# NL to Terraform

A multi-agent AI system that turns a plain-English infrastructure request
("highly available web app with auto scaling") into validated,
cost-estimated, deployable Terraform for AWS.

<img width="1239" height="698" alt="image" src="https://github.com/user-attachments/assets/62381d0f-ac28-41f6-ab8e-57049720f3c9" />


Six agents work in sequence — each step is traced in LangSmith so the full
reasoning chain is auditable:

```
User Input (natural language)
        |
        v
Intent Extraction Agent     -- understands what the user wants
        |
        v
Resource Planning Agent     -- decides which AWS resources are needed
        |
        v
Terraform Generation Agent  -- writes the .tf files
        |
        v
Validation Agent            -- runs terraform validate, self-heals errors
        |
        v
Cost Estimation Agent       -- calls the AWS Pricing API
        |
        v
User reviews and approves
        |
        v
Deployment Agent            -- runs terraform apply
        |
        v
Real AWS infrastructure
```

## Running locally with Docker Compose

1. Copy `.env.example` to `.env` and fill in your OpenAI and LangSmith keys.
2. Make sure `~/.aws/credentials` has a working AWS profile (used for the
   Pricing API and for `terraform apply`/`destroy` — the backend container
   mounts it read-only).
3. Start everything:

```bash
docker compose up --build
```

4. Open the frontend at http://localhost:5173. The API is at
   http://localhost:8000.

## Environment variables

See `.env.example` for the full list:

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | GPT-4o access for all agents |
| `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT` | LangSmith tracing |
| `AWS_DEFAULT_REGION` | Region used for pricing lookups and deployments (AWS credentials come from `~/.aws/credentials` or an IAM role, not from `.env`) |
| `BACKEND_URL` | Backend URL the frontend talks to |
| `MAX_TERRAFORM_RESOURCES` | Guardrail: max resources per plan (default 20) |
| `MAX_MONTHLY_COST_USD` | Guardrail: blocks the pipeline if the estimated cost exceeds this (default 500) |
| `TERRAFORM_WORKSPACE_DIR` | Where generated Terraform is written and validated |

## Example prompts

- `simple web server in us-east-1`
- `highly available web app with auto scaling`
- `web app with PostgreSQL database and Redis cache`
- `static website with low latency globally`
- `Redis cache cluster with automatic failover and encryption`
- `web app with RDS PostgreSQL, multi-AZ, and daily backups`

## Guardrails

| Guardrail | Default |
|---|---|
| Max resources per request | 20 |
| Max monthly cost | $500 |
| Max validation self-heal attempts | 3 |
| Terraform timeout | 120s |
| Destroy endpoint | Always available (`/pipeline/destroy`) |

## LangSmith

Every agent call is traced under the `nl-to-terraform` project at
[smith.langchain.com](https://smith.langchain.com). Each pipeline run shows
up as a set of traces — one per agent stage — so you can inspect the exact
prompt and response that produced any piece of generated Terraform.

## Development without Docker

Backend:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```
