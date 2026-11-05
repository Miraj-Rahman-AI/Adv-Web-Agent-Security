# AC-DPI-Pilot Architecture

## 1. Overview

AC-DPI-Pilot investigates Authorization-Conditioned,
Task-Preserving Direct Prompt Injection against
LLM-based Web Agents.

The architecture separates:

1. User task specification.
2. Authorization context.
3. LLM-based action planning.
4. Tool execution.
5. Authorization labeling.
6. Experimental evaluation.
7. Trajectory analysis.

## 2. Architecture

```mermaid
flowchart TD

    A["Legitimate User Task"]
    B["Trusted Authorization Context"]
    C["LLM Agent"]
    D["Direct Prompt Injection"]
    E["Structured Action Plan"]
    F["Synthetic Tool Executor"]
    G["Authorization Evaluator"]
    H["Task Success Evaluator"]
    I["Trajectory Analyzer"]
    J["Experimental Results"]

    A --> C
    B --> C
    D --> C

    C --> E
    E --> F

    F --> G
    F --> H

    G --> I
    H --> I

    I --> J
