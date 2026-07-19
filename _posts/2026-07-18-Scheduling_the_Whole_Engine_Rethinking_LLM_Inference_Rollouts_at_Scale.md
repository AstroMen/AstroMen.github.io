---
layout: post
title:  "Scheduling the Whole Engine: Rethinking LLM Inference Rollouts at Scale"
date:   2026-07-18
categories: jekyll update
tags: 
  - AIOps
  - Kubernetes
  - DevOps
  - System Design
lang: en
---

{% include lang-switch.html %}

*Notes and reflections from OpenAI's infrastructure presentation at AGI Summit 2026*

At AGI Summit 2026 in San Francisco, I attended an OpenAI infrastructure presentation by Dong Meng and Zihan "Gavin" Zheng on a problem that sounds routine but becomes fundamentally different at large scale: updating an inference service.

For a conventional stateless application, a rolling deployment is straightforward:

1. Start a new replica.
2. Wait until it is ready.
3. Remove an old replica.
4. Repeat.

Kubernetes supports this pattern exceptionally well because replicas are usually small, independent, and relatively fast to start.

Large language model inference breaks several of those assumptions.

A production LLM replica may actually be a coordinated engine spanning multiple GPU workers. Those workers must use compatible hardware, fit within the right memory envelope, connect through the required high speed topology, and become operational together.

The scheduler is therefore no longer placing a collection of independent pods. It is proving that one complete serving engine can exist and that introducing it will not destabilize the system around it.

> **Image 1 placement**
>
> Insert the photo titled **"A scheduling request is a stack of constraints"** here.
>
> Suggested caption: *Scheduling a large inference engine requires preserving serving intent, eligibility, hardware shape, topology, and transition safety.*

## The Serving Unit Is the Whole Engine

The most important abstraction shift is simple:

> An LLM engine should be scheduled as one serving unit, not as a pile of unrelated GPU workers.

Kubernetes may see several pods, but the application sees a single engine. If one required worker cannot start, the engine may provide no useful serving capacity at all.

This changes the central scheduling question.

Instead of asking:

> Where can the next worker run?

The system must ask:

> Is there a valid placement for the entire engine?

An engine request may describe:

- GPU type and memory requirements
- Worker groups and their roles
- Required connections between workers
- Placement and failure domain constraints
- Availability and latency objectives
- Warm up, rollback, and transition safety requirements

Individual worker placements can all appear locally valid while still making the complete engine impossible to construct. For example, placing smaller, flexible worker groups first may consume the only connected capacity that a larger, less flexible group requires.

A whole engine request preserves atomic intent across scheduling layers and allows the rarest or most constrained shape to be considered first.

> **Image 2 placement**
>
> Insert the photo titled **"One LLM engine can be a group"** here.
>
> Suggested caption: *A single serving engine may span multiple GPU workers that must fit, connect, and start together.*

## Capacity Is a Shape, Not Just a Number

A cluster may report many idle GPUs and still be unable to start an engine.

Suppose an engine requires four GPUs within one connected NVLink or InfiniBand domain. Four GPUs may be free across the cluster, but if they are divided across multiple incompatible domains, they cannot form the required serving unit.

The useful capacity metric is therefore not simply:

> How many GPUs are free?

It is:

> How many eligible, connected shapes can the fleet currently provide?

This reframes GPU fragmentation as well.

Traditional fragmentation metrics focus on unused devices. For large inference engines, the more important issue is whether the remaining devices can form the next required topology.

A fleet could have 100 GPUs free in total and still be unable to satisfy an 80 GPU request if those devices are divided across clusters or connection domains that cannot be combined.

In this environment, operationally meaningful inventory should track **eligible contiguous shapes**, not only idle GPU counts.

> **Image 3 placement**
>
> Insert the photo titled **"Fragmentation is about usable shape, not leftover GPUs"** here.
>
> Suggested caption: *Total free GPU count can be misleading when the next request requires one eligible, contiguous topology.*

## A Scheduling Request Is a Stack of Constraints

The presentation described scheduling as a layered proof rather than a single placement decision.

A request passes through several categories of constraints:

```text
Serving intent
Tier, latency target, minimum availability
        ↓
Eligibility
Region, provider, policy
        ↓
Hardware shape
GPU SKU, memory, worker roles
        ↓
Local topology
Node, domain, NVLink or InfiniBand connectivity
        ↓
Transition safety
Warm up capacity, rollback room, no unsafe double use
        ↓
Concrete placement plan
or a specific blocked reason
```

These layers answer three different questions.

First, is there an eligible environment for the engine?

Second, can every worker group fit together within that environment?

Third, can the transition occur safely without violating availability or rollback requirements?

This distinction also improves explainability. "No capacity" is often too vague to be operationally useful. A better scheduler should identify whether the request is blocked by region eligibility, hardware shape, topology, cluster health, or the absence of a safe transition path.

Each blocked reason leads to a different response: select another pool, repair a cluster, wait for capacity, reserve a topology, or adjust rollout policy.

## Placement Is Only the Beginning

Even after the scheduler finds a valid location, the engine is not ready.

The startup lifecycle may include:

```text
Request accepted
    ↓
Cluster selected
    ↓
Workers placed
    ↓
Containers launched
    ↓
Model weights loaded
    ↓
Workers connected
    ↓
Warm up and CUDA graph capture
    ↓
Health and correctness checks
    ↓
Ready
```

During much of this period, expensive GPUs are already occupied but are not serving traffic.

That makes startup time a capacity cost, not merely a latency metric. A slower startup means either maintaining overlapping old and new capacity for longer or operating with reduced serving capacity for longer.

Every rollout therefore spends one of two resources:

- **Spare capacity:** Start the replacement before removing the old engine.
- **Temporary availability:** Release old capacity first and accept reduced capacity while the replacement starts.

Keeping a complete spare copy of every engine would be prohibitively expensive. Running with no operational headroom makes deployment and repair slow and fragile. The practical goal is not maximum utilization in isolation, but enough utilization combined with enough room to operate safely.

## Stability Should Be Part of the Objective Function

A mathematically cleaner placement is not always the safest production placement.

Moving a healthy inference engine may require:

- Reloading model weights
- Rebuilding caches
- Repeating warm up
- Reconverging traffic routing
- Temporarily duplicating capacity
- Accepting additional failure risk

For that reason, the scheduling policy presented was stability first:

1. Keep healthy groups where they are.
2. Repair an existing placement when a bounded change is sufficient.
3. Move healthy work only when necessary.

This is an important difference between online inference and many batch training workloads. A training job may wait in a queue, checkpoint, or restart later. A live inference engine has active users behind it.

The scheduler should not ask only whether a new arrangement can fit. It should also ask how much healthy work must be disrupted to create that fit.

## The Impossible Pentagon of Fleet Scheduling

The presentation captured the core tradeoff through five desirable properties:

- High utilization
- Immediate scheduling
- Flexible movement and reshaping
- No rescheduling of existing workloads
- Resilience to maintenance and cluster degradation

When capacity is abundant and engines are small, these goals may appear compatible.

Under capacity pressure, they are not.

High utilization removes spare operational capacity. Immediate placement may require advance reservations. Reservations reduce flexibility and utilization. Refusing to move existing workloads can leave globally useful capacity stranded. Resilience requires headroom that may remain idle during normal operation.

The correct policy depends on the workload, but the tradeoff cannot be eliminated. It must be made explicit.

## Production Capacity and Deployment Gate Capacity Serve Different Goals

One of the most useful distinctions in the presentation was between production serving capacity and deployment gate capacity.

Production capacity is optimized for durable service across a changing fleet. It benefits from flexible contracts, multiple compatible locations, failure domain diversity, and conservative movement.

A deployment gate answers a narrower question:

> Is the next engine image safe enough to continue rolling out?

For this purpose, repeatability may be more important than flexibility. A gate may reserve a known GPU shape so that a candidate engine can be compared with a known good reference under nearly identical conditions.

That reservation can appear inefficient from a pure utilization perspective, but it reduces hardware and topology variation. If the engines behave differently, the new software image is more likely to be the cause.

## Ready Does Not Mean Safe to Release

Kubernetes readiness answers an operational question:

> Can this instance receive traffic?

It does not prove that a new runtime image is correct, stable, or free from performance regressions.

The deploy gate compares two engines:

- A reference running a known good image
- A candidate running the new image

They use the same model, configuration, GPU environment, and shared test load. The test can cover normal traffic, peak load, overload, recovery, and compatibility scenarios.

The gate then compares signals such as:

- Startup and readiness time
- Request success rate
- Crashes and restarts
- Time to first token
- Time between tokens
- Median and tail latency
- Numerical divergence between outputs

When a regression appears, the rollout is held for investigation. A clean result provides evidence to continue, although production monitoring remains necessary because a gate can validate only the behaviors it measures.

> **Image 4 placement**
>
> Insert the photo titled **"How we validate a new engine image"** here.
>
> Suggested caption: *The deployment gate compares a known good reference and a candidate under the same workload and environment.*

## The End to End Workflow

The full workflow can be summarized as follows:

```text
New engine image
        ↓
Define the whole engine contract
        ↓
Filter eligible regions, providers, policies, and hardware
        ↓
Select a compatible cluster
        ↓
Prove the exact connected topology
        ↓
Evaluate warm up, availability, and rollback safety
        ↓
Create an atomic placement plan
        ↓
Launch, load, connect, and warm up the engine
        ↓
Confirm operational readiness
        ↓
Compare reference and candidate in the deploy gate
        ↓
Continue the rollout or hold and investigate
        ↓
Monitor the phased production deployment
```

## Broader Implications

The ideas in this presentation extend beyond LLM inference.

As AI systems become larger and more heterogeneous, infrastructure control planes will increasingly need to reason about **intent, topology, lifecycle state, and disruption**, rather than treating compute as a uniform pool.

This has direct implications for AIOps and autonomous operations. Observability systems should distinguish allocation, assignment, placement, startup, readiness, traffic serving, and release validation instead of collapsing them into a single "healthy" status. Automated remediation should consider the cost of disturbing healthy work, not only whether an alternative configuration is technically feasible.

The same principles can apply to robotics fleets, scientific computing, multimodal serving, safety critical AI, and any distributed system in which a usable service depends on several tightly coordinated components.

The deeper lesson is that scaling AI infrastructure is not only about acquiring more accelerators. It is about preserving the structure required to turn those accelerators into reliable serving capacity.
