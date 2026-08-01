---
layout: post
title:  "Agents Can Learn Continuously Without Updating Model Weights"
date:   2026-08-01
categories: jekyll update
tags: 
  - AI Agent
  - Continual Learning
  - Agent Harness
lang: en
---

{% include lang-switch.html %}

Continual learning is usually associated with retraining a model, updating its weights, or fine-tuning it on new data.

In practice, however, many companies build products using closed-weight models. Developers can call these models through APIs, but they cannot directly inspect or modify their parameters.

Does that mean an AI system must remain static until its model provider releases a new version?

At the Agentic AI Summit 2026, Michele Catasta, President of Replit, offered another answer in his talk, **Continual Learning for Agents**:

> Even when the underlying model remains unchanged, the system around it can continuously learn from real-world usage.

This learning happens in the agent harness, the collection of tools, instructions, context, infrastructure, and control mechanisms surrounding the model.

## An Agent Is More Than a Model

A production agent is rarely just a large language model.

It usually includes:

* System prompts and task instructions
* Tools and APIs
* Context retrieval
* Execution environments
* Retry and error-handling logic
* Permissions and safety constraints
* Multi-agent orchestration
* Memory and historical information
* Evaluation and monitoring systems

Together, these components determine whether an agent can complete real tasks reliably.

Even if the underlying model remains fixed, changing its tools, workflows, context, and execution logic can significantly improve the behavior of the overall system.

Strictly speaking, this is not continual learning at the level of model parameters. It is continual improvement at the system level. From the user's perspective, however, the result is similar: the agent becomes more reliable as it is used.

## Why Fixed Evaluations Are Not Enough

AI teams commonly rely on benchmarks and evaluations to measure system performance.

The process is clear:

1. Modify the agent harness.
2. Run the evaluation suite.
3. Receive a score.
4. Determine whether the change improved performance or introduced a regression.

Evaluations are essential, but they are narrow by design.

A benchmark may contain dozens or hundreds of test cases, while a production system may process millions of real interactions every day. Users will ask questions that the benchmark designers never anticipated, and they will use the product in unexpected ways.

Fixed evaluations show how an agent behaves in known situations. They are much less effective at exposing rare, unpredictable production failures.

Those long-tail failures are often the most valuable signals because they reveal the real boundaries of the system.

## Production Traces as Learning Signals

Once an AI product reaches meaningful adoption, it begins producing a large volume of execution traces.

A trace may contain:

* The user's request
* The context retrieved by the agent
* The tools the agent selected
* The output of each tool call
* The agent's error-recovery attempts
* Whether the task was completed
* Signals about user satisfaction
* Latency and computational cost

These traces can be used for model training, but they can also improve the agent system directly.

By analyzing production traces, a team can investigate questions such as:

* At which steps does the agent fail most often?
* Which tool descriptions confuse the model?
* Why are users dissatisfied with certain interactions?
* Which unexpected behaviors are recurring?
* Is the failure caused by the model or the infrastructure?
* Which prompts or workflows should be changed?

Michele's central argument is that this analysis should not happen only occasionally. Production traces should feed a continuously operating improvement loop.

## A Continuous Agent Improvement Loop

The process described in the talk can be summarized in six steps.

### 1. Collect Production Traces

The system records how agents behave while completing real user tasks.

When millions of traces are generated each day, manual inspection is not practical.

### 2. Cluster Similar Traces

The first stage applies relatively standard machine-learning techniques to group semantically similar traces.

Most clusters represent expected behavior and do not require deeper analysis.

The most interesting signals are newly emerging clusters and small clusters whose frequency is increasing unexpectedly. These often represent new failure modes.

### 3. Detect Anomalies and Long-Tail Behavior

Individual failures may appear unrelated when inspected separately.

Agents are nondeterministic. When facing the same underlying problem, they may choose different reasoning paths, debugging techniques, and recovery strategies.

Semantic clustering can reveal that a collection of apparently different failures shares the same root cause.

### 4. Use Frontier Models to Analyze Root Causes

After identifying an anomalous cluster, a stronger model can inspect the related traces and determine what went wrong.

Possible causes include:

* An unclear prompt
* An inaccurate tool description
* Missing context
* A change in an API response
* An execution environment that was not ready
* Incorrect retry logic
* A poor recovery decision made by the agent

### 5. Generate a Corrective Pull Request

Once the likely root cause is identified, the system can modify the harness, application code, or infrastructure configuration and automatically create a pull request.

Production failures no longer need to wait for an engineer to discover and manually debug them. They can be transformed into candidate fixes automatically.

### 6. Validate the Change Through A/B Testing

An automatically generated pull request should not be deployed immediately.

The team still needs to test how the change affects different metrics, including:

* Task success rate
* Response latency
* Computational cost
* User satisfaction
* Number of tool calls
* Error-recovery performance

The results are rarely completely positive or completely negative.

A change may improve speed while reducing accuracy. Another may lower costs while making the user experience worse.

A human decision-maker must still determine whether the tradeoff supports the product's broader goals.

## A Failure That Traditional Monitoring Could Miss

Michele shared a concrete example from production.

Their platform starts a large number of virtual machines for users every day. Under normal conditions, both the agent harness and the virtual machine must be ready before the agent can execute code or call tools.

Occasionally, however, the agent harness became ready before the virtual machine had fully booted.

The agent would attempt to execute code and fail.

Because agents are eager to troubleshoot, they did not simply wait. Instead, they tried different debugging strategies:

* Checking whether the command was valid
* Trying alternative tools
* Suspecting a permission issue
* Changing the execution sequence
* Running the code again

The traces looked different because the agent selected a different recovery strategy each time.

An engineer reading a single log entry might not recognize that these failures shared the same cause. The issue was also rare enough that it might not create a visible signal in a standard monitoring dashboard.

After clustering the production traces, however, the system grouped these apparently unrelated failures into the same anomalous cluster.

The analysis identified the common cause: the virtual machine occasionally took longer to boot than the agent harness.

The system then generated a pull request to correct the startup sequencing problem.

This example shows that production traces are more than debugging records. They can become learning signals for continuously improving an agent system.

## Evaluation Should Not Be Only a Release Gate

In a traditional workflow, evaluation is often treated as the final step:

> Finish development, run the tests, and decide whether the change can be released.

Michele proposed a broader view:

> Evaluation should not be only a Boolean release check. It should become an engine for continuously improving the agent.

The new workflow looks more like this:

```text
Production usage
→ Trace collection
→ Anomaly detection
→ Root-cause analysis
→ Automatic change generation
→ A/B testing
→ Human decision
→ Deployment
→ Continued trace collection
```

Within this loop, every real-world failure can become an opportunity to improve the system.

## Humans Still Make the Critical Decisions

Even when anomaly analysis and pull request generation are largely automated, humans remain responsible for several important decisions:

* Defining which metrics matter
* Balancing quality, speed, and cost
* Reviewing high-risk changes
* Deciding which experiments should continue
* Identifying when a local fix is hiding a deeper architectural problem
* Setting the long-term direction of the product

An agent may be able to identify a problem and propose a solution, but it may not know what the organization ultimately wants to optimize.

This is why continual agent improvement still requires a human in the loop.

## From Continual Learning to Omniscient Agents

In a related session, **Omniscient Agents**, Alex Graveley described a broader direction for agent autonomy.

He presented a progression in the scope of work agents are trusted to complete:

```text
Tool call
→ Commit
→ Pull request
→ Multiple pull requests
→ Feature
→ Project
→ Product
```

An agent that can only edit code cannot independently own an entire feature.

To manage a feature or a product, it must also be able to:

* Read real business data
* Observe user feedback
* Run experiments
* Monitor production systems
* Determine whether a feature improves retention or revenue
* Expand a deployment or roll it back

Alex summarized this expansion through two dimensions.

### Insight

Insight describes what information the agent can access and whether it can derive useful conclusions from it.

An agent must progress from understanding a codebase to understanding users, products, experiments, and the wider business.

### Control

Control describes what the agent is allowed to change in the real world.

An agent must progress from making recommendations to modifying code, deploying features, running experiments, and operating production systems.

From this perspective, Michele's continual learning loop is a foundational capability for the Omniscient Agent vision.

An agent cannot autonomously manage a product unless it can observe real outcomes, detect failures, improve its execution process, and continue iterating.

## Conclusion

Future progress in agentic systems may not come only from larger models or additional parameters.

Many improvements may come from outside the model:

* Better tools
* More relevant context
* Richer production traces
* Stronger anomaly detection
* More reliable experimentation
* Clearer boundaries for human decisions

Even when model weights remain unchanged, a well-designed feedback system can allow an agent to improve through every real-world interaction.

The most important question may no longer be only:

> Which model are we using?

It may instead be:

> Have we built an agent system that can continuously learn from the real world?
