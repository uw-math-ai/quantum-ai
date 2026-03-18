Big picture: Quantum programs are hard to implement. The instructions they operate on are not intuitive, and they are hard to debug since inspection of the state destroys it. The expectation is that LLM agents will be used to generate such quantum programs in the future, but how capable are they today?

To narrow the scope we'll focus on circuits based on stabilizer codes. Specifically on fault tolerant circuits for state preparation and syndrome extraction. These circuits are of critical for the next generation of fault tolerant quantum computers, which depends on quantum error correction codes based on stabilizers to improve the overall fidelities and correctness of the outcomes. This gives us a broad set of circuits to use that have clear semantics and are easy to validate without full simulation.

We’ll test multiple agents/LLMs and create a benchmark to compare. To enable this, we’ll build generic infrastructure that evaluates a prompt and uses an oracle to score it (Christian). 

**RQ1: Can an agent generate circuits reliably? (Mayee)**

* Easy problem, i.e. these circuits can efficiently be generated today based on existing algorithms.
* Need examples of existing programs that provide this (stim, QMT)
* Ask the agent to generate state-preparation (and possibly syndrome-extraction) circuits based on stabilizers
* Metric: % of circuits that are FT

**RQ2: Can an agent generate an FT version of a circuit? (Sylvie)**

* More complicated task. FT helps EC ensure errors are not propagated. Rules exist on how to do this, but they are hard to implement and inefficient.
  * Need to explain the agent how flags work
  * Need to define an FT score
* Metric: median FT score

**RQ3: Can an agent optimize a circuit without breaking FT? (Sarju)**

* Even more complicated task. No easy rules
* Metric: circuit volume

**RQ4: Can metrics be improved by training an LLM? (Sarj)**

* Train a custom LLM and run the same benchmarks.
* Same metrics as RQ[1-3], with a different LLM.

**Plan:**

* Christian to provide a programmatic framework to benchmark LLMs
  - Given a prompt and an oracle function, return a score
    * The prompt should be arbitrary text
    * The oracle should receive a stim circuit and return a score
  - Consider GitHub Copilot SDK and CLI
  - Create a list of benchmarks to use

* Mayee to work on the prompt and oracle for RQ1
  - Iterate on a prompt until it generates the corresponding circuit
  - Start with state preparation
  - The prompt should take a stabilizer as a parameter
  - Leverage existing oracles

* Sylvie to work on the prompt and oracle for RQ2
  - Iterate on a prompt until it generates the corresponding circuit
  - The prompt should expect a stim circuit as a parameter
  - Leverage existing oracles

* Sarju to start on a plan to train and integrate an agent
  * Evaluate CodeLlama and KetGPT; provide a recommendation
  * Identify how to integrate with GitHub Copilot and create a prototype