# BeeReflect AI — Integration Friction Log

## Developer feedback

### AWS Bedrock setup

- **Region and model access are easy to overlook.** Having valid AWS credentials
  is not enough: the selected region must support the model, and the account
  must be allowed to invoke it. Keep the region explicit and report Bedrock's
  error code/message so setup problems are distinguishable from application
  failures.
- **Credentials should stay outside the app.** A local `.env` file is
  convenient for a hackathon demo, but it must remain untracked. For deployed
  environments, use the platform's AWS role/credential provider rather than
  copying access keys into the UI or source code.
- **Model output needs a boundary.** Asking for JSON alone does not guarantee
  parseable or correctly shaped output. Validate the response before rendering
  it and show a useful error instead of presenting malformed data as a
  successful reflection.
- **Personal audio transcripts deserve care.** Send only the text needed for
  the analysis, avoid logging raw transcripts, and make it clear that this
  prototype offers supportive reflection rather than clinical assessment.

### Bee CLI / wearable handoff

- **Transcript ingestion is the first integration seam.** This prototype uses a
  text area because a portable, stable transcript export contract is needed
  before tying the dashboard to a specific Bee CLI workflow. A CLI adapter
  should pass transcript text (and, optionally, capture time) through a clearly
  documented file or standard-input interface rather than coupling the UI to
  device-specific commands.
- **Ambient capture can produce noisy or fragmented notes.** Keep the original
  transcript visible for correction, and test exported logs with interruptions,
  partial sentences, and background speech before relying on extracted tasks.
- **Task dates are often implicit.** The model is instructed not to invent a
  deadline; when a log gives no time, it should say so. A future CLI handoff
  should preserve timestamps/time zones where available so relative phrases
  such as “after lunch” can be interpreted responsibly.

## Hackathon follow-ups

1. Confirm the target AWS region, model access, and least-privilege invocation
   permissions for the demo account.
2. Agree on a Bee CLI transcript export format and add an adapter with sample
   fixtures.
3. Test representative logs for task extraction quality, JSON validity, and
   sensible handling of uncertain or sensitive language.
