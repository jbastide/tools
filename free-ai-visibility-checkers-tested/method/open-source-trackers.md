# Open-source trackers: what an install needs (read from each README, October 21, 2026)

| Tracker | Repo | License | Collects answers from | Needs before a first result |
| --- | --- | --- | --- | --- |
| Elmo | github.com/elmohq/elmo | MIT | Scraping providers for consumer surfaces (ChatGPT, Google AI Mode/Overviews, Gemini, Perplexity, Copilot) and model APIs (OpenAI, Anthropic, Mistral, OpenRouter) | Docker Compose via `npm install -g @elmohq/cli`, `elmo init`, `elmo compose up -d`; API key for at least one AI provider or scraper, plus a TypeSafe key for Jev (mention/sentiment judge, about $0.15–0.35 per 1,000 answers). Dashboard at localhost:1515. |
| OneGlanse | github.com/oneglanse/oneglanse | MIT | The AI products' own websites (ChatGPT, Perplexity, Gemini, Claude, Google AI Overview) in a Camoufox browser with your saved logins | Node 20+, pnpm 10+, Docker; an OpenAI or Anthropic key for the analysis model; accounts for each AI product. `pnpm local`, localhost:3000. |
| Gego | github.com/AI2HU/gego | GPL-3.0 (not MIT) | Model APIs (OpenAI, Anthropic, Google, Perplexity Sonar, Ollama) | Go 1.25+, PostgreSQL, MongoDB, etcd; API keys for the LLM providers. Dashboard at localhost:8989. |

Not installed in this round: all three need paid API keys or AI product accounts, and the agent does not enter
real API keys or sign in to accounts. OneGlanse and Elmo's scraping providers drive the consumer chat sites,
whose terms may restrict automated access; that is the user's risk to weigh.
