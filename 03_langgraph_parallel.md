# LangGraph Parallel Workflows – Last Minute Revision Notes

Based on your transcription 

---

# 1. What is a Parallel Workflow?

In a **Sequential Workflow**, nodes execute one after another.

```text
A → B → C → D
```

In a **Parallel Workflow**, multiple nodes execute simultaneously.

```text
        → Node A →
Start → Node B → Merge → End
        → Node C →
```

### Use Parallel Workflow When

* Tasks are independent
* One task does not depend on another's output
* Multiple calculations/LLM calls can happen simultaneously

### Benefits

* Faster execution
* Better resource utilization
* Cleaner workflow design

---

# 2. Cricket Example (Non-LLM Parallel Workflow)

### Input

```python
runs
balls
fours
sixes
```

### Calculations

#### 1. Strike Rate

Formula:

Strike\ Rate = \frac{Runs}{Balls}\times100

Example:

```python
100 runs in 50 balls

SR = (100/50)*100 = 200
```

---

#### 2. Boundary Percentage

Percentage of runs scored through boundaries.

Formula:

```python
((fours*4) + (sixes*6)) / runs * 100
```

Example:

```python
6 fours
4 sixes

Boundary runs = 24 + 24 = 48

Boundary % = 48/100 * 100
           = 48%
```

---

#### 3. Balls Per Boundary (BPB)

Formula:

```python
balls / (fours + sixes)
```

Example:

```python
50 balls
10 boundaries

BPB = 50/10
    = 5
```

Meaning:

```text
Batsman hits a boundary every 5 balls.
```

---

# 3. Workflow Structure

```text
                    → Calculate Strike Rate →
Start
                    → Calculate BPB         → Summary → End
                    → Boundary Percentage →
```

Important:

All three calculations are independent.

Therefore they can run in parallel.

---

# 4. State Design

```python
class BatsmanState(TypedDict):
    runs: int
    balls: int
    fours: int
    sixes: int

    strike_rate: float
    bpb: float
    boundary_percent: float

    summary: str
```

---

# 5. Graph Creation

```python
graph = StateGraph(BatsmanState)
```

Add nodes:

```python
graph.add_node(...)
```

Add edges:

```python
graph.add_edge(...)
```

Compile:

```python
workflow = graph.compile()
```

Execute:

```python
workflow.invoke(initial_state)
```

---

# 6. MOST IMPORTANT: Parallel Workflow Error

### Wrong Approach

Returning entire state from every parallel node:

```python
return state
```

Problem:

```text
Node A updates state
Node B updates state
Node C updates state
```

LangGraph thinks all nodes may be modifying same keys.

Result:

```text
InvalidUpdateError
```

---

# 7. Solution → Partial State Updates

Return only the fields updated by that node.

### Correct

```python
return {
    "strike_rate": strike_rate
}
```

```python
return {
    "bpb": bpb
}
```

```python
return {
    "boundary_percent": boundary_percent
}
```

---

### Golden Rule

For Parallel Workflows:

```text
Always return partial updates.
```

Even for sequential workflows this is considered a better practice.

---

# 8. LLM Based Parallel Workflow

## Problem Statement

Build a UPSC Essay Evaluator.

Input:

```text
Essay
```

Evaluate on:

1. Clarity of Thought
2. Depth of Analysis
3. Language Quality

---

# Workflow

```text
                         → Clarity Evaluation →
Start → Essay
                         → Analysis Evaluation → Final Evaluation → End
                         → Language Evaluation →
```

---

# Each LLM Node Returns

### Feedback

```text
Detailed textual feedback
```

### Score

```text
0 - 10
```

Example:

```python
{
   "feedback": "...",
   "score": 8
}
```

---

# 9. Why Structured Output?

Without structured output:

```text
Score: seven
```

or

```text
I would rate this essay 8/10
```

Parsing becomes unreliable.

---

### With Structured Output

Always get:

```python
{
    "feedback": "...",
    "score": 8
}
```

Reliable and machine-readable.

---

# 10. Evaluation Schema (Pydantic)

```python
class EvaluationSchema(BaseModel):

    feedback: str

    score: int = Field(
        ge=0,
        le=10
    )
```

### Benefits

* Fixed format
* Validation
* Reliable outputs

---

# 11. Structured Output Model

```python
structured_model = model.with_structured_output(
    EvaluationSchema
)
```

Invoke:

```python
output = structured_model.invoke(prompt)
```

Access:

```python
output.feedback

output.score
```

---

# 12. UPSC Workflow State

```python
class UPSCState(TypedDict):

    essay: str

    language_feedback: str

    analysis_feedback: str

    clarity_feedback: str

    overall_feedback: str

    individual_scores: list[int]

    average_score: float
```

---

# 13. Reducer Function (VERY IMPORTANT)

## Problem

Three parallel nodes generate scores:

```text
8
7
6
```

All want to update:

```python
individual_scores
```

Simultaneously.

Without reducer:

```text
Overwriting happens.
```

Only one value survives.

---

# 14. Reducer Concept

Reducer tells LangGraph:

```text
How to merge multiple updates
for the same key.
```

---

# 15. Using operator.add

```python
import operator
from typing import Annotated
```

```python
individual_scores:
Annotated[
    list[int],
    operator.add
]
```

---

# What Happens?

Node A:

```python
[8]
```

Node B:

```python
[7]
```

Node C:

```python
[6]
```

Reducer:

```python
[8] + [7] + [6]
```

Final:

```python
[8, 7, 6]
```

---

# 16. Node Return Format

Language Node:

```python
return {
    "language_feedback": output.feedback,
    "individual_scores": [output.score]
}
```

Analysis Node:

```python
return {
    "analysis_feedback": output.feedback,
    "individual_scores": [output.score]
}
```

Clarity Node:

```python
return {
    "clarity_feedback": output.feedback,
    "individual_scores": [output.score]
}
```

---

# 17. Final Evaluation Node

Responsibilities:

### 1. Generate Overall Feedback

Use all feedbacks:

```python
language_feedback
analysis_feedback
clarity_feedback
```

Create summarized feedback using LLM.

---

### 2. Calculate Average Score

```python
average_score = (
    sum(individual_scores)
    /
    len(individual_scores)
)
```

---

Return:

```python
{
    "overall_feedback": overall_feedback,
    "average_score": average_score
}
```

---

# 18. Complete Workflow Architecture

```text
                           → Language Evaluation →
Start → Essay
                           → Analysis Evaluation → Final Evaluation → End
                           → Clarity Evaluation →
```

Final Output:

```python
{
    "overall_feedback": "...",
    "average_score": 7.67
}
```

---

# Interview / Revision One-Liners

### Parallel Workflow

```text
Independent tasks execute simultaneously.
```

### Partial State Update

```text
Return only updated keys, not entire state.
```

### Structured Output

```text
Forces LLM to return a predefined schema.
```

### Reducer Function

```text
Defines how multiple parallel updates are merged.
```

### operator.add

```text
Merges lists by concatenation.
```

### Annotated

```text
Used to attach reducer functions to state fields.
```

### Parallel + Same Key Update

```text
Requires a reducer.
```

### No Reducer + Same Key Update

```text
Conflict / overwrite issues.
```

---

# Mental Model

```text
Sequential Workflow
A → B → C

Parallel Workflow
      → B →
A → → C → Merge
      → D →

Partial Updates
Only return changed fields

Structured Output
LLM → Fixed JSON Schema

Reducer
Multiple Outputs → One State Field

operator.add
[8] + [7] + [6]
      ↓
[8,7,6]
```

This is the complete set of concepts covered in this LangGraph Parallel Workflow lesson: **Parallel Nodes, Partial State Updates, Structured Output, Reducers, Annotated, operator.add, and LLM-based Parallel Evaluation Workflows.** 
