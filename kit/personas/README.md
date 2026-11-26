# Optional persona profiles — reusable ways of working

A persona is a named, reusable operating profile for a particular task. It is not a different model, an autonomous process, a new authority, or a second reviewer. Start with one Claude session; switch profiles only when a concrete task benefits. Use the generic Builder, Researcher, Reviewer or Mentor examples, or create a private profile for a user-defined specialty.

## Contract

- Profile format: JSON, `schema: 1`, lowercase safe ID, display name, purpose, fixed advisory authority, approved skill IDs, requested capabilities, behavior rules and review checklist. See `examples/` and `../tools/persona.py` for the supported format. Unknown fields and unapproved skill bindings are rejected. The validator checks shape, not trustworthiness of prose.
- Shared skills stay in one canonical location, referenced by ID. Do not duplicate them in profiles. Keep skill revision/digest and approval in the private registry; verify current version before binding. Role-specific guidance stays private and concise.
- User approval and actual host permissions bound every action. Effective capabilities are the intersection of requested, user-approved and runtime-available capabilities. Even `write` only means reversible in-scope local writes; it never allows installation, publication, secret access or changes to core governance. A profile cannot approve itself or another profile.
- Use private `.cm-private/personas/` for personalized records and an activation record with ID, exact digest, bound skill revisions, task ID, scope, effective capability set, user approval if required and exit condition. Do not publish real names, private histories, paths, or configuration.
- Selection: match task intent and skill requirements; pick one profile, or use a second explicitly labeled review lens in the same session. Distinct actors require independently verified host identities and actual separate evidence. No fabricated reviewers, parallel workers or tool execution.
- Evolution: propose profile changes from verified friction or explicit preferences; test against representative tasks and preserve version history. Active profile behavior, skill promotion and authority/security changes require explicit approval. Generic notes and evidence remain eligible for ordinary Advanced Evolution.
- Stop: when the assigned task exits, checkpoint, clear the active profile pointer and return to the base workspace rules. A session handover must preserve profile ID/digest and exact outstanding task; resolve any drift before resuming.

## Usage

Ask Claude: "Use the Researcher profile to investigate this error. Then return to Builder for the approved fix." Use `/persona` only after confirming installation and invocation support; otherwise ask in natural language. The optional skill documents list, inspect, propose, activate, review and stop operations. No runtime configuration or background agents are installed by these examples.

## Sources and boundaries

The design is independently written, informed by read-only review of a private modular persona schema and its documentation: separation of persona definitions, shared skill bindings, evidence and authorization. No private schema, source file, persona identity, runtime or private path is distributed. No compatibility claim with those private systems.
