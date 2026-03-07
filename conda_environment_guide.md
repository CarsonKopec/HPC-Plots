# Conda Environment Export & Import Guide

## Exporting an Environment

```bash
conda env export > environment.yml
```

### Export Options

| Command | Description |
|--------|-------------|
| `conda env export > environment.yml` | Full export with all packages and exact versions |
| `conda env export --no-builds > environment.yml` | Cross-platform (excludes OS-specific build strings) |
| `conda env export --from-history > environment.yml` | Only explicitly installed packages (most portable) |
| `conda env export -n myenv > environment.yml` | Export a specific environment by name |
| `pip freeze > requirements.txt` | Export as a pip requirements file |

> **Tip:** Use `--from-history` when sharing across different operating systems.

---

## Installing / Recreating an Environment

### From `environment.yml`

Create a new environment:
```bash
conda env create -f environment.yml
```

Create with a different name:
```bash
conda env create -f environment.yml -n new_name
```

Update an existing environment:
```bash
conda env update -f environment.yml
```

### From `requirements.txt`

```bash
pip install -r requirements.txt
```

---

## Activating the Environment

```bash
conda activate env_name
```
