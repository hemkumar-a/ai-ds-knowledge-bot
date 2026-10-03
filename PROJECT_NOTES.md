# Project Notes

## Packaging decisions

- The repository uses `sample.py` as the canonical implementation and renames it to `app.py` for clearer Streamlit conventions.
- The older Gradio/NLTK prototype (`project.py`) is intentionally not included in the public repository package because the Streamlit implementation is the current project version.
- `chat_history.txt` is ignored because it is a local runtime artifact.
- No generated model weights or local virtual-environment files are included.

## Publishing notes

Before making the repository public, verify that `knowledge_base.json` contains only information that is appropriate for public release. Do not add private study notes, credentials, or personal data.
