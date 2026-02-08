# GraphRAG Configuration Guide

written by *n1ghts4kura*.

## Steps

---

### 1. Install deps

Make sure you have followed the [Installation Guide](./INSTALLATION.md) to set up the environment and install dependencies.

After that, we can proceed to configure GraphRAG.

---

### 2. Initialize GraphRAG

What I design for GraphRAG configuration is a bit different from the original way.

First, run the following command to initialize GraphRAG with default settings:

```bash
$ cd backend && source ./venv/bin/activate
$ cd assets/dataset
```

Now, create a folder named as your desired graph name, e.g., `small1`, which means "small map 1".

This folder will contain all the original data and configuration files for this graph.

Create `input` folder under `small1` to store all the raw data files.

```bash
$ mkdir small1
$ cd small1
$ mkdir input
```

Then, navigate back to the backend's root directory and run the initialization command:

```bash
$ graphrag init --root ./small1
```

You will be asked to enter the *chat model* and *embedding model* you want to use.

You can leave them as default for now by pressing Enter. We will modify them later.

Then, you will see a few things created in the `small1` folder:

- `.env`: The API key storage file.

- `config.yaml`: The main configuration file for GraphRAG.

- `prompts/`: A folder containing prompt templates for various tasks.

---

### 3. Customize GraphRAG 

#### `.env` settings

Open the `.env` file in the `small1` folder.

Edit it as follows:

```env
CHAT_API_BASE=http://localhost:8080/v1
EMBED_API_BASE=http://localhost:8081/v1

CHAT_ONLINE_API_BASE=https://api.deepseek.com/v1 # Choose your online LLM service provider
CHAT_ONLINE_API_KEY=sk-xxxxxxxxxxxxxx # Enter your API key here
CHAT_ONLINE_PROVIDER=deepseek # e.g., deepseek, openai, azure, etc.
CHAT_ONLINE_MODEL=deepseek-chat # e.g., deepseek-chat, gpt-4, gpt-3.5-turbo, etc.
```

The variable `CHAT_API_BASE` and `EMBED_API_BASE` are used to connect to your local LLM and embedding services, which is used for competition showing off.

The variable `CHAT_ONLINE_API_BASE`, `CHAT_ONLINE_API_KEY`, `CHAT_ONLINE_PROVIDER`, and `CHAT_ONLINE_MODEL` are used to connect to your online LLM service provider, which is for wider usage and faster responses.

#### `config.yaml` settings (offline version)

Then, open the `config.yaml` file.

*__Modify__* it as follows:

```yaml
# chat model settings
completion_models:
  default_completion_model:
    model_provider: openai
    auth_method: api_key
    api_base: ${CHAT_API_BASE}
    api_key: sk-xxx
    model: default 
    retry:
      type: exponential_backoff
# embedding model settings
embedding_models:
  default_embedding_model:
    model_provider: openai
    auth_method: api_key
    api_base: ${EMBED_API_BASE}
    api_key: sk-xxx
    model: default
    retry:
      type: exponential_backoff
# **input document settings**
input:
  type: json
```

The field `api_base` is located to the local running LLM/embedding service.

The field `input->type` is set to `json`, which means we will process JSON files in the `input` folder.

#### `config.yaml` settings (online version)

If you want to use the online LLM service provider (chat / embed), modify the `config.yaml` based on this tutorial:

- [Official GraphRAG Configuration Docs](https://microsoft.github.io/graphrag/config/yaml/)

This is more detailed and flexible.

---

### 4. Pre-process data

Before building the graph, we need to process all the input data first.

Here is the basic template of how to structure your input data files in the `input` folder:

```json
{
  "title": "Document Title",
  "creation_date": "2023-10-01T12:00:00CST",
  "metadata": {
    "author": "Author Name",
  },
  "text": "The full text content of the document goes here."
}
```

The arguments shown above means:

- `title`: (*Required*) The title of the document.

- `creation_date`: (*Required*) The creation date of the document in *ISO 8601 format*.

- `metadata`: (*Optional*) Any additional metadata you want to include (e.g., author, tags, etc.). If empty, **do not set it to `{}`**, just remove this field.

- `text`: (*Required*) The main text content of the document. Any content is placed here.

---

### 5. Customize Pipeline Prompts (recommended but not required)

After Step4, actually you can start building the graph directly.

But according to Microsoft's suggestions:

> "Using GraphRAG with your data out of the box may not yield the best possible results. We strongly recommend to fine-tune your prompts following the Prompt Tuning Guide in our documentation."

So you can fine-tune the prompts used in various stages of the pipeline.

Here is the [Prompt Tuning Guide](https://microsoft.github.io/graphrag/prompt_tuning/overview/). My guide will not cover this part in detail.

---

### 6. Build the Graph

After a huge amount of works done, now we can finally build the graph!!!

```bash
$ graphrag index --root ./small1
```

---

### 7. Query the Graph

Now you can try querying the graph to get answers based on your data!

```bash
$ graphrag query --root ./small1
```

Query is also a big topic, so please read the official docs: [Querying GraphRAG](https://microsoft.github.io/graphrag/query/overview/). My guide will not cover this part in detail.