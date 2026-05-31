# LangGraph Core Concepts – Revision Notes

These notes cover the main concepts from the second LangGraph video. A few explanations have been simplified and organized for quick revision. 

---

# 1. What is LangGraph?

**LangGraph = Orchestration framework for building stateful, multi-step LLM workflows.**

### What does it do?

It converts an LLM workflow into a **Graph**:

* Nodes = Tasks
* Edges = Flow between tasks

Then LangGraph automatically executes the workflow.

### Key Features

✅ Graph-based workflow

✅ State management

✅ Conditional branching

✅ Loops

✅ Parallel execution

✅ Memory support

✅ Resumability

✅ Multi-agent workflows

---

# 2. What is an LLM Workflow?

### Workflow

A sequence of tasks executed to achieve a goal.

Example:

```text
Create JD
 ↓
Post JD
 ↓
Screen Candidates
 ↓
Interview
 ↓
Onboarding
```

### LLM Workflow

A workflow where some tasks involve LLMs.

Examples:

* Prompting
* Reasoning
* Tool Calling
* Memory Access
* Decision Making

---

# 3. Common LLM Workflow Patterns

---

## A. Prompt Chaining

Break a complex task into smaller steps.

### Example

```text
Topic
 ↓
Generate Outline
 ↓
Generate Report
```

Benefits:

* Better quality output
* Easier debugging
* Validation between steps

Use when:

* Large tasks can be broken into smaller tasks.

---

## B. Routing

Choose the best handler for a task.

### Example

Customer Support Bot

```text
User Query
     ↓
   Router
 ┌───┼────┐
Refund Tech Sales
```

The router decides where the request should go.

Use when:

* Different requests need different experts/models.

---

## C. Parallelization

Split work into multiple independent tasks and execute simultaneously.

### Example

Content Moderation

```text
Video
  ↓
 ┌─────┬─────┬─────┐
Policy Misinfo Adult
Check  Check  Check
 └─────┴─────┴─────┘
        ↓
   Aggregator
```

Benefits:

* Faster execution
* Better analysis

Use when:

* Tasks are independent.

---

## D. Orchestrator-Worker Pattern

Similar to Parallelization but tasks are created dynamically.

### Example

Research Assistant

```text
Query
  ↓
Orchestrator
  ↓
Assign Research Tasks
  ↓
Workers
  ↓
Aggregate Results
```

Difference:

### Parallelization

Tasks are predefined.

### Orchestrator-Worker

Tasks are dynamically generated based on input.

---

## E. Evaluator-Optimizer Pattern

Used when output requires multiple revisions.

### Example

```text
Generate Blog
      ↓
Evaluate
      ↓
Feedback
      ↓
Regenerate
      ↓
Evaluate Again
```

Loop continues until quality criteria are satisfied.

Use for:

* Blogs
* Emails
* Stories
* Reports
* Creative writing

---

# 4. Graphs, Nodes and Edges

This is the most important LangGraph concept.

---

## Graph

Entire workflow representation.

---

## Node

Each node represents one task.

### Important

In LangGraph:

```python
Node = Python Function
```

Examples:

* Generate Topic
* Evaluate Essay
* Call LLM
* Call Tool

---

## Edge

Defines execution flow.

Example:

```text
Node A → Node B
```

Edge tells:

> Which node runs next?

---

## Types of Edges

### Sequential Edge

```text
A → B → C
```

### Parallel Edge

```text
     A
   /   \
  B     C
```

### Conditional Edge

```text
      A
    /   \
Success Fail
```

### Loop Edge

```text
A → B → C
↑       ↓
└───────┘
```

---

# 5. State (Most Important Concept)

### Definition

State = Shared data used and updated throughout workflow execution.

### Example

UPSC Essay Evaluator

```python
{
   "topic": "...",
   "essay_text": "...",
   "clarity_score": 4,
   "language_score": 3,
   "depth_score": 5,
   "final_score": 12
}
```

---

## Why State Exists?

Workflow decisions depend on data.

Example:

```text
Essay Score > 10
       ↓
 Pass

Essay Score < 10
       ↓
 Feedback
```

Without state, workflow cannot make decisions.

---

## State Properties

### Shared

All nodes can access it.

### Mutable

Nodes can update it.

### Evolves Over Time

Values change as workflow progresses.

---

## State Creation

Usually created using:

### TypedDict

```python
from typing import TypedDict
```

or

### Pydantic

```python
from pydantic import BaseModel
```

---

# 6. Reducers

Reducer defines:

> How state updates should happen.

---

## Problem

Suppose state contains:

```python
messages = []
```

User says:

```text
Hi
```

State:

```python
["Hi"]
```

Assistant replies:

```text
Hello
```

If state replaces previous value:

```python
["Hello"]
```

Previous message is lost.

Bad for chatbots.

---

## Reducer Solution

Reducer controls update behavior.

### Replace

```python
old_value → new_value
```

Example:

```python
score = 10
score = 15
```

---

### Append

```python
["Hi"]
+
["Hello"]
```

↓

```python
["Hi", "Hello"]
```

Useful for:

* Chat history
* Essay versions
* Logs

---

### Merge

Combine multiple updates.

Useful in:

* Parallel workflows
* Multi-agent systems

---

## Easy Definition

**Reducer = Rules that decide how state updates are applied.**

---

# 7. LangGraph Execution Model

How LangGraph works internally.

---

## Step 1: Graph Definition

Create:

* Nodes
* Edges
* State

---

## Step 2: Compilation

```python
graph.compile()
```

Checks:

* Graph structure
* Missing connections
* Invalid nodes

Similar to validation.

---

## Step 3: Invocation

Start workflow:

```python
graph.invoke(initial_state)
```

---

## Step 4: Node Execution

Node receives state.

```python
state
```

Node performs task.

Updates state.

Returns updated state.

---

## Step 5: Message Passing

Updated state moves through edges.

```text
Node A
   ↓
State
   ↓
Node B
```

This is called:

### Message Passing

---

## Step 6: Supersteps

LangGraph executes workflows in rounds called:

### Supersteps

Example:

```text
      A
    / | \
   B  C  D
```

B, C, D run together.

Entire parallel round = One Superstep.

---

## Execution Stops When

1. No active nodes remain.
2. No messages are being passed.

Workflow ends.

---

# Final Summary (2-Minute Revision)

### LangGraph

* Orchestration framework for LLM workflows.
* Represents workflows as graphs.

### Core Building Blocks

* **Node = Task (Python Function)**
* **Edge = Execution Flow**
* **State = Shared Workflow Data**
* **Reducer = State Update Rule**

### Common Workflow Patterns

1. Prompt Chaining
2. Routing
3. Parallelization
4. Orchestrator-Worker
5. Evaluator-Optimizer

### State

* Shared across all nodes
* Mutable
* Evolves during execution

### Reducers

Control how state updates happen:

* Replace
* Append
* Merge

### Execution Flow

```text
Define Graph
    ↓
Compile
    ↓
Invoke
    ↓
Node Execution
    ↓
Message Passing
    ↓
Supersteps
    ↓
Workflow Ends
```

### Interview Answer

> **LangGraph is a graph-based orchestration framework where workflows are modeled as Nodes and Edges, data is managed through State, updates are controlled by Reducers, and execution happens through message passing and supersteps.** 
