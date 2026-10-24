# Agent research: the instructions each run received

Three separate Claude Opus 5.5 agents (high effort) ran inside a Claude Code session on October 23, 2026,
each in a fresh context with only WebSearch and WebFetch, started at the same time. None was told which
10 firms the test drive uses. This is one AI agent's research, not what ChatGPT, Perplexity, Gemini or the
Claude app would answer a consumer.

Instructions given to each agent, word for word:

> You are acting as an AI assistant answering a consumer in Chicago. Research each of the five questions below on the live web using WebSearch (and WebFetch to read pages when useful), then answer each one the way a careful, helpful assistant would: name the specific law firms you would recommend, in order, with a one-line reason each. Use only WebSearch and WebFetch; do not use any browser tools, do not visit AI visibility checker sites, and do not write any files.
>
> Questions:
> P1. Who are the best personal injury lawyers in Chicago?
> P2. I was hurt in a car crash in Chicago. Which law firm should I call?
> P3. Which Chicago personal injury law firms have the best reviews?
> P4. Recommend three personal injury attorneys in Chicago, Illinois, for a slip-and-fall case.
> P5. Best workers' compensation and injury lawyers in Chicago
>
> Answer each question independently, from your own research. Name between 3 and 10 firms per question (P4: exactly three).
>
> Return ONLY a JSON object [...] with, per question, the full answer text, the ranked firms with a one-line reason, the searches run and the sources relied on.
