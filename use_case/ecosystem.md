# Someone else's ecosystem

Where your application would actually run, inside your actual firm.

> **Week 1 starts this file. Week 9 finishes it.**
> TC1 Step 6 asks eight questions. The full Week 9 checklist has around thirty,
> and the eight are a strict subset — so nothing here gets thrown away.

Describe patterns, not specifics. "On-prem OpenShift, images from an internal
registry, no public egress" is useful to everyone and identifies nobody. Never
put real hostnames, IPs, or architecture diagrams in this file.

---

## Week 1 — the first eight questions

<!-- Answered in TC1 Step 6. Bring these back from a real conversation. -->

**Who did you ask?** (role, not name)

Product owner / product manager on Flexion's TrailSkills 2.0 team. Conversation
requested; until it happens, the rows below come from the project's own
planning documents (the AWS grant draft and the technical-preferences note)
and are marked **from docs**. A row changes to **confirmed** after the
conversation.

| # | Question | Answer |
| :---: | --- | --- |
| 1 | Where do internal apps run? (k8s, ECS, App Service, a VM someone maintains) | **From docs:** nothing runs yet. The planned production shape is serverless on AWS: static front end on S3 behind a CDN, API as Lambda functions behind API Gateway. No Kubernetes, no VMs. A Python container like this one has no obvious home in that plan, which is the first thing to ask about. |
| 2 | Which cloud? AWS, Azure, GCP, on-prem, several? | **From docs:** AWS. The platform is being planned against an AWS Imagine Grant application, and the grant form itself says the client has no AWS account yet. Which account a course prototype may run in, Flexion's or the client's, is the question to ask. |
| 3 | Is there an internal container registry? | **From docs:** none named. If the API runs as a container it would be ECR in whichever account owns the deployment. Unknown until asked. |
| 4 | How do users log in? (Okta, Entra ID, Ping, SAML, homegrown) | **From docs:** Amazon Cognito with role-based access is the planned identity layer for the platform. The Pathfinder gap view is specced as signed-in, while the explorer persona arrives signed out, so this is a product question as much as an infrastructure one. |
| 5 | Can the app reach the internet? Egress proxy? Allowlist? | **From docs:** unknown. Serverless on AWS usually means open egress by default, but the firm's and the client's security posture are not written down anywhere I can find. |
| 6 | Where do secrets come from? (Vault, Secrets Manager, Key Vault) | **From docs:** not stated. AWS Secrets Manager or SSM Parameter Store is the default in that shape; `--env-file` is a laptop-only answer. |
| 7 | Who approves a deployment, and what review does it need? | **From docs:** unknown. The grant names a platform steward role to be created at the client; who signs off on a deployment today is the question to ask. |
| 8 | Is there an approved internal LLM endpoint already? | **From docs:** the grant names Amazon Bedrock as the model provider for the platform. For the course, Flexion's Bifrost gateway is the approved endpoint this app already uses, so swapping to Bedrock later is a config change in `.env`, not a code change. |

**What surprised you?**

<!-- after the conversation -->

**What would you have to change about your app to deploy there?**

**From docs, pending confirmation:** the planned platform is TypeScript on Next.js
with the model behind a provider port, so this Python app would not ship as-is.
It would either run as a small container service behind the API (ECS or App
Runner, which the plan does not have yet) or be ported into the TypeScript
domain as the `ModelProvider` adapter. Either way: vendor the CDN library,
add Cognito in front, read secrets from the account's secret store, and point
`LLM_API_BASE` at Bedrock instead of the course gateway.

---

## Week 1 — what your machine told you

<!--
  Paste the egress probe output from Session 1 here. It is evidence, and it
  frequently disagrees with what people believe about their own network.
-->

Run 2026-10-13 from `helpers.preflight.check_egress()` on a personal Mac on a
home network, not a managed firm laptop. 7/7 reachable, no TLS interception,
no proxy or CA environment variables set.

| Host | Why it matters | DNS | TLS | Issuer |
| --- | --- | :---: | :---: | --- |
| pypi.org | Python packages | ok | ok | GlobalSign |
| files.pythonhosted.org | the actual wheel downloads | ok | ok | GlobalSign |
| api.openai.com | the model API | ok | ok | Google Trust Services |
| cdn.jsdelivr.net | the CDN the Week 1 frontend uses | ok | ok | Sectigo |
| huggingface.co | open weights, Weeks 2 and 8 | ok | ok | Amazon |
| registry-1.docker.io | container images | ok | ok | Amazon |
| github.com | this repository | ok | ok | Sectigo |

**Does this match the table above?** It cannot yet: the table above describes
a planned AWS environment that does not exist, and this probe measured my own
network. The useful comparison is against a Lambda or container in the target
account, which is a Week 9 measurement. The one thing this already says: the
course app's CDN dependency works here and may not work there.


---

## Week 9 — the full checklist

<!--
  TC9 extends this same file. Do not start a new one: the point is that the git
  history shows one continuous piece of work from Week 1 to Week 9.
-->

<!-- Week 9 -->
