# LangGraph Introduction & LangChain vs LangGraph — Revision Notes

Based on the video transcript. I corrected a few points for accuracy and condensed everything into interview/revision-friendly notes. 

---

## 1. Why LangGraph Exists?

### Problem with LangChain

LangChain is excellent for:

* Simple chatbots
* RAG applications
* Sequential workflows
* Content generation pipelines
* Basic tool-calling agents

But it becomes difficult when workflows contain:

* Conditional branching (`if/else`)
* Loops
* Returning to previous steps
* Complex state management
* Multi-step agent workflows

This is where **LangGraph** comes in.

---

## 2. What is LangChain?

**LangChain = Framework for building LLM-powered applications using reusable components.**

### Main Components

#### Models

Unified interface for:

* OpenAI
* Anthropic
* Ollama
* Hugging Face
* Other LLM providers

#### Prompts

Used to create and manage prompts.

#### Retrievers

Fetch relevant documents from:

* Vector databases
* Knowledge bases

Used heavily in RAG systems.

#### Chains

Connect multiple components together.

Example:

```
Prompt → LLM → Output Parser
```

Output of one step becomes input to the next.

---

## 3. What Can You Build With LangChain?

### Simple Chatbots

```
User Input → LLM → Response
```

### Multi-Step Workflows

Example:

```
Topic
 ↓
Generate Report
 ↓
Generate Summary
```

### RAG Applications

```
Question
 ↓
Retriever
 ↓
Relevant Context
 ↓
LLM
 ↓
Answer
```

### Basic Tool Calling

Example:

```
User asks weather
 ↓
LLM calls Weather API
 ↓
Tool returns data
 ↓
LLM formats response
```

---

## 4. Workflow vs Agent (Important Interview Question)

### Workflow

Developer defines the execution path beforehand.

Example:

```
Step A → Step B → Step C
```

Flow is fixed.

### Agent

LLM decides:

* What to do next
* Which tool to use
* In what order

Flow is dynamic.

### Easy Definition

**Workflow = Developer-controlled execution**

**Agent = LLM-controlled execution**

---

## 5. Automated Hiring Example

Video uses an automated hiring workflow:

```
Hiring Request
   ↓
Generate JD
   ↓
Human Approval
   ↓
Post Job
   ↓
Wait for Applications
   ↓
Screen Resumes
   ↓
Schedule Interviews
   ↓
Interview Results
   ↓
Offer Letter
   ↓
Onboarding
```

This workflow contains:

* Branching
* Loops
* Human approvals
* Multiple tools
* Long-running processes

---

## 6. Why Complex Workflows Are Hard in LangChain?

### Challenge 1: Control Flow Complexity

LangChain chains are primarily sequential.

Complex workflows require:

### Conditional Branching

```
If approved → Post JD

Else → Regenerate JD
```

### Loops

```
Create JD
 ↓
Approve?
 ↓
No
 ↓
Create JD Again
```

### Jumps

Moving backward or forward in workflow.

To implement these in LangChain:

* Write custom Python code
* Use while loops
* Use if-else statements

This extra code is called:

### Glue Code

Glue code = Custom Python code written outside LangChain to manage workflow logic.

Problem:

* Harder maintenance
* Harder debugging
* More complexity

---

## 7. How LangGraph Solves It

LangGraph models the workflow as a **Graph**.

### Graph Structure

#### Nodes

Represent tasks.

Examples:

* Create JD
* Approve JD
* Post JD

#### Edges

Represent execution paths.

Example:

```
Create JD
    ↓
Approve JD
```

#### Conditional Edges

Example:

```
Approve JD
   ├── Yes → Post JD
   └── No  → Create JD
```

#### Loops

Naturally supported through graph connections.

---

## 8. State Management (Most Important Concept)

### What is State?

State = Shared data that moves through the workflow.

Examples:

```python
{
    "jd": "...",
    "jd_approved": True,
    "applications_count": 25,
    "shortlisted_candidates": [...],
    "offer_status": "pending"
}
```

---

## 9. State in LangChain

LangChain does not provide strong workflow state management.

Usually developers:

* Use dictionaries
* Pass variables manually
* Maintain state themselves

This becomes difficult in large workflows.

---

## 10. State in LangGraph

LangGraph is **stateful by design**.

You create a State object.

Every node:

### Receives

```python
state
```

### Reads

```python
state["applications_count"]
```

### Updates

```python
state["jd_approved"] = True
```

### Returns

Updated state.

This makes data sharing across workflow steps very easy.

---

# LangChain vs LangGraph (Final Comparison)

| Feature                | LangChain    | LangGraph         |
| ---------------------- | ------------ | ----------------- |
| Simple Chatbots        | ✅            | ✅                 |
| RAG Applications       | ✅            | ✅                 |
| Sequential Workflows   | ✅ Excellent  | ✅                 |
| Conditional Logic      | ⚠️ Manual    | ✅ Native          |
| Loops                  | ⚠️ Manual    | ✅ Native          |
| State Management       | ⚠️ Limited   | ✅ Built-in        |
| Multi-Agent Systems    | ⚠️ Difficult | ✅ Excellent       |
| Long-running Workflows | ⚠️ Difficult | ✅ Excellent       |
| Complex Agentic AI     | ⚠️ Not Ideal | ✅ Designed For It |

---

# When to Use What?

### Use LangChain When:

* Simple RAG chatbot
* Portfolio chatbot
* Content generation
* Summarization
* Sequential workflow
* Minimal branching

### Use LangGraph When:

* Agentic AI systems
* Multi-agent systems
* Complex workflows
* Conditional execution
* Human-in-the-loop approvals
* Iterative/revision workflows
* Long-running business processes

---

### LangChain

* Best for **simple and sequential workflows**.
* Uses components like:

  * Models
  * Prompts
  * Retrievers
  * Chains
* Great for:

  * Chatbots
  * RAG applications
  * Summarization
  * Content generation
  * Basic tool calling

### Problem with LangChain

For complex workflows, you need a lot of **custom Python (glue code)** to handle:

* Conditional branching (`if/else`)
* Loops
* Jumps between steps
* State management

This makes applications harder to:

* Build
* Maintain
* Debug

### LangGraph

* Built specifically for **complex, stateful, agentic workflows**.
* Represents workflows as a **Graph**:

  * **Nodes** = Tasks
  * **Edges** = Flow between tasks
* Supports:

  * Conditional edges
  * Loops
  * Non-linear execution
  * Shared state

### State in LangGraph

* Every node can:

  * Read state
  * Update state
  * Pass updated state to next node
* Built-in state management is a major advantage over LangChain.

### Workflow vs Agent

* **Workflow:** Developer decides the execution path.
* **Agent:** LLM dynamically decides what actions to take and which tools to use.

### Interview Answer

> **Use LangChain for simple sequential workflows like RAG chatbots and content generation. Use LangGraph when the application requires branching, loops, state management, human approvals, or complex agentic behavior.** 

### Easy Rule to Remember

**Sequential Flow → LangChain**
**State + Branching + Loops + Agents → LangGraph** 🚀

