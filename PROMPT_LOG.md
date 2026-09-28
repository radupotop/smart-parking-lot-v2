
Mon, 28 Sep 2026 16:28:43 +0100
> read the documents from specs/; do a short summary; ack
----

Mon, 28 Sep 2026 16:30:49 +0100
> $git-commit
----

Mon, 28 Sep 2026 16:33:00 +0100
> fill in the ERD.md doc according to the PRD & SRS docs
----

Mon, 28 Sep 2026 16:38:10 +0100
> I've moved it to ERD1.md and kept the ERD.md template as-is; git commit and ack;
----

Mon, 28 Sep 2026 16:49:56 +0100
> Create the overarching tasks in the backlog; add implementation details according to the SRS docs.
----

Mon, 28 Sep 2026 16:59:31 +0100
> $prompt-log
----

Mon, 28 Sep 2026 17:01:50 +0100
> Add the required sub-tasks in the backlog. also the ticket about Podman containers seems to be missing;
----

Mon, 28 Sep 2026 17:13:23 +0100
> Add a task-0 for bootstrapping a venv using uv; use `uv venv --seed --clear --no-managed-python`; this should be inside the `src/` dir; and it should also include a `pyproject.toml` file
----

Mon, 28 Sep 2026 19:42:50 +0100
> Start with Task-0 the bootstrap environment; do it in a subagent
----

Mon, 28 Sep 2026 19:49:53 +0100
> OK let's carry on with Task-1, each of the sub-task should run in a sub-agent, with a commit after each; they should run sequentially - not in parallel;
----

Mon, 28 Sep 2026 20:07:44 +0100
> Add Task-1.4: add a compose yaml file which encapsulates the current container infra
----

Mon, 28 Sep 2026 20:48:15 +0100
> add Task-1.5 for updating python to 3.14-slim and django to 6.1
----
