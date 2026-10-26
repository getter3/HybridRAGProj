# Learning collaboration rules

- This is a learning project. Explain the idea and tradeoffs before proposing code.
- Keep the learner responsible for most implementation; aim to provide roughly 40%
  complete code and leave meaningful TODOs, exercises, and review checkpoints.
- Prefer small, testable steps. Do not fill in a TODO unless the learner asks.
- The learner owns database provisioning and schema decisions. Do not connect to,
  create, migrate, or modify a database. Explain SQL and options when asked.
- Use Python with `uv`; do not use `pip` or system Python commands.
- Never place real credentials in source control. Use `.env.example` for variable
  names and keep `.env` local.
- Ask before changing core architecture choices such as ranking fusion or embedding
  model/provider.
