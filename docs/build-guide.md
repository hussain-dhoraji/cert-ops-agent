# Building the agent in Copilot Studio

Everything the agent needs is in this repo. This guide wires it together in Copilot Studio. Microsoft moves
menus around often; if a label differs, look for the closest equivalent.

## 0. Prerequisites

- A Microsoft work or school account with Copilot Studio (the free trial works). Personal accounts such as
  Gmail or Outlook.com are not accepted.
- A public HTTPS URL for cert-watcher. For a demo:
  ```bash
  ./demo/run-cert-watcher.sh                   # cert-watcher with known demo data on :8080
  devtunnel host -p 8080 --allow-anonymous     # Microsoft dev tunnels; prints https://<id>-8080.<region>.devtunnels.ms
  ```
  The anonymous tunnel exposes only demo data. Stop it when you are done.

## 1. Create the agent

1. In [Copilot Studio](https://copilotstudio.microsoft.com), create a new agent and skip the conversational setup.
2. Name: **Cert Ops Assistant**. Paste the description and instructions from
   [`agent/instructions.md`](../agent/instructions.md).
3. Settings > Generative AI: turn on **generative orchestration**, so the agent chooses actions and knowledge itself.
4. Turn off general knowledge (the model's own web/world knowledge) so answers stay grounded.

## 2. Add knowledge (grounding)

Upload the three files in [`knowledge/`](../knowledge) as knowledge sources, or put them in a SharePoint
library and add that site. Give each a description, e.g. "Standard certificate renewal procedure and issuing
rules", which the orchestrator uses to pick the right source.

## 3. Add the cert-watcher action

1. Tools (or Actions) > Add > New custom connector > **Import an OpenAPI file**, and choose
   [`connector/cert-watcher.swagger.json`](../connector/cert-watcher.swagger.json).
2. Set **Host** to your tunnel host (without `https://`). Authentication: none for the demo.
3. Create the connector, create a connection, then add the **List certificate status** action to the agent.
4. Keep the action description from the file; it tells the orchestrator when to call it and how to use the
   severity filter.

## 4. Add topics

For each file in [`agent/topics/`](../agent/topics): create a topic from blank, open **Open code editor**, paste
the YAML and save. `conversation-start.yaml` replaces the body of the built-in Conversation Start topic.
If the editor rejects a property, build the same flow on the canvas; the YAML is the specification.

## 5. Test, then publish

1. Use the test pane with a few golden-set questions. Turn on the activity map to confirm the action and the
   right knowledge source are used.
2. Publish. Settings > Channels > **Microsoft Teams** to try it where users would.
3. Settings > Channels > **Mobile app** (with authentication set to "No authentication" in Settings > Security
   for the demo) and copy the **token endpoint**. The eval harness uses it.

## 6. Evaluate

```bash
pip install -r requirements.txt
export COPILOT_TOKEN_ENDPOINT='<token endpoint>'
cd evals && python -m certops_eval.run --label instructions-v1 --out results/v1.json
```

Change the instructions, bump the version in `agent/instructions.md`, publish, run again with `--label
instructions-v2`, and compare:

```bash
python -m certops_eval.compare results/v1.json results/v2.json
```

To run it from GitHub Actions, add the repository secret `COPILOT_TOKEN_ENDPOINT` and the variable
`AGENT_EVAL_ENABLED=true`. The **Agent evaluation** workflow then runs on demand and every Monday.

## 7. Export the solution

So the agent itself is versioned: create a solution in Power Apps (Solutions > New), add the agent and the
custom connector, export it, and commit the zip under `solution/`. With the Power Platform CLI:

```bash
pac solution export --name CertOpsAssistant --path solution/CertOpsAssistant.zip
pac solution unpack --zipfile solution/CertOpsAssistant.zip --folder solution/src
```

## Security notes

- The demo connector has no authentication. Before anything beyond a demo, put cert-watcher behind Azure API
  Management and use OAuth 2.0 with Entra ID (planned for v2).
- Switch the agent back to "Authenticate with Microsoft" before sharing it, and turn off the unauthenticated
  channel once evaluation runs use an authenticated client.
