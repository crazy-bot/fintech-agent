# 9fin Senior AI Engineer Technical Challenge

Welcome to the challenge!

When you are ready to go through what you've done, email us back, and we'll review the submission before scheduling a technical interview to discuss your approach. There is no time limit here but please don't spend more than ~2 hours on this task. If you feel stuck for some time or there is an issue with the challenge, please stop and send us a quick email to help you out.

We want to test your analytical mindset and ability to write clean maintainable python code for this AI system using best SE practices. Specifically, we'll look at the following in our code review (NOT ranked by importance):
- Use of docker
- Repo structure, environment and dependency management
- Use of data structures
- Code readability and maintainability
- System scalability to larger dataset
- LLM prompting, configuration and context window management
- Basic but appropriate evaluation script and metrics definitions
- Reproducibility
- Logging/observability
- Data validation

We can always discuss any further plans if there was more time to iterate on this.

Good luck!

## Background 
An intern have been tasked with creating a chat agent POC that can answer questions about financial tables from the 9fin platform. Their internship has now come to an end so they sent you what they came up with in the `agent.py` file along with the following slack message:
```text
Hey, I've sent you my progress so far on the agent POC. I'm not sure how well it's working though and it can only answer one question at the time but you can try it... Also FYI, the product manager said there is 100k+ financial tables in the db (not just per company) and I haven't tested on that scale yet. I've only tested with tables for 3 companies from the `company_financials` postgres table. That table has the following columns: `company_id`, `company`, `currency`, `periods`, `key_financials`, `cash_flow_and_leverage` and `cap_table`. A sample of 3 table rows is in the json file.
```
While the product manager (a key stakeholder on this project) wants to extend the agent beyond company based financial table data soon, they are keen to first try this out feature-flagged internally in production.

## Task
Pick up where the intern left, improve the code/repo to prepare it for production-use at scale and make the agent conversational with source citations (running in terminal is fine). I.e. you should be able to have a multi turn markdown text-only dialogue about 9fin company financials with the agent in the terminal. The agent should be running with docker. Furthermore, initiate creation of an offline evaluation framework for the agent. For now it's okay to use the example questions in `agent.py`.

Commit your files to a **private** github repo and share it with us [@hanneskindbom](https://github.com/hanneskindbom) & [@9jori](https://github.com/9jori) when you're ready!

_NOTE: We don't expect you to set up a db for the data in this takehome task although it would be used in prod. Also, feel free to use any LLM or request an Open AI key from us if needed._


### Example conversation
Below is a brief illustrative terminal chat with the agent for financial tables:

```text
$ docker run --rm -it -e OPENAI_API_KEY=YOUR_KEY ai-agent
User: Show Sales and Adjusted EBITDA for Tronox in 2024.
Agent: Tronox (USD millions), 2024: Sales = 3,074; Adjusted EBITDA = 564. [1](www.9fin.com/company_id/1/key_financials) Compare to 2023?
User: Yes, summarize the YoY change.
Agent: Sales: 2,850 → 3,074 (+7.9%). Adjusted EBITDA: 524 → 564 (+7.6%). [1](www.9fin.com/company_id/1/key_financials)
```


## Questions
We've listed some of the questions that you can think about for the interview:
- How did you approach this task? What were all the things you could have done?
- What would you tell your colleague for the future (in terms of improved collaboration/reduced repeated work)?
- How would you improve evals of the agent if you had more time?
- How can we make this agent answer other questions such as on recent news about companies? web search
- How can we give the agent a memory? state