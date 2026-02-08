# GraphRAG Configuration Guide

written by *n1ghts4kura*.

## Steps

### 1. Install deps

Make sure you have followed the [Installation Guide](./INSTALLATION.md) to set up the environment and install dependencies.

After that, we can proceed to configure GraphRAG.

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
$ graphrag init --root ./assets/dataset/small1
```

Then, you will see a few things created in the `small1` folder:

- `.env`: The API key storage file.

- `config.yaml`: The main configuration file for GraphRAG.

- `prompts/`: A folder containing prompt templates for various tasks.
