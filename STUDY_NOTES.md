# Study Notes: LangChain Text Chunking

## What chunking does

Text splitters break large documents into smaller pieces that can be embedded,
retrieved, and supplied to an LLM. Good chunking tries to keep useful context
together while keeping each chunk small enough for downstream processing.

There are two separate decisions:

1. **Where to split:** at headings, paragraphs, sentences, fixed separators, or
   topic changes.
2. **How to measure chunk size:** by characters or by tokens.

These approaches can be combined. For example, split Markdown by headings first,
then split oversized sections by recursive boundaries while measuring size in
tokens.

LangChain's splitter package is `langchain-text-splitters`, imported in Python as
`langchain_text_splitters`. This project already lists it and `tiktoken` in
[pyproject.toml](./pyproject.toml).

## Common strategies and utilities

| Strategy / utility | Strategy and basic use | Pros | Cons | Best use cases |
|---|---|---|---|---|
| `CharacterTextSplitter` | Splits on a chosen separator, often a blank line. Set `separator`, `chunk_size`, and `chunk_overlap`. | Simple and quick to understand. | Does not recursively find a smaller boundary when a section is too large; character sizes may not match model token limits. | A quick baseline for plain text with consistent paragraph breaks. |
| `RecursiveCharacterTextSplitter` | Tries larger-to-smaller separators, by default paragraphs (`"\n\n"`), lines (`"\n"`), spaces, and then characters. Set `chunk_size` and `chunk_overlap`. | General-purpose; tries to keep larger natural units together. | Default size is characters, and it does not understand document meaning or headings. | Generic prose and a strong first RAG baseline. |
| `TokenTextSplitter` | Splits directly using a tokenizer and a token count. | Useful when a hard token-size limit matters. | Can split through sentences, Markdown structures, or table rows. LangChain also warns that direct token splitting can create malformed Unicode for some writing systems. | Enforcing a tokenizer-specific token cap. |
| `RecursiveCharacterTextSplitter.from_tiktoken_encoder(...)` | Uses recursive separators but measures chunk size with `tiktoken`. | Combines more natural boundaries with token-aware sizing; recursive splitting can keep chunks under the configured size. | Token counts depend on the encoding selected and may not exactly match every embedding provider's tokenizer. | Prose or Markdown when token-aware sizing is desired. |
| `MarkdownHeaderTextSplitter` | Splits at configured Markdown headings such as `#`, `##`, and `###`, recording heading hierarchy in each output `Document`'s metadata. | Preserves section context and enables heading metadata for retrieval. | A section may still be too large and need another splitter. By default, split headings are stripped from chunk text; set `strip_headers=False` to retain them. | Markdown guides, FAQs, and heading-organized documents. |
| Sentence splitters, such as `SpacyTextSplitter` | Finds sentence boundaries, then groups sentences into chunks. | Avoids many mid-sentence cuts. | Adds tokenizer or model setup; sentence boundaries alone do not ensure ideal chunk sizes or preserve document hierarchy. | Text where keeping full sentences together is important. |
| Code splitting with `RecursiveCharacterTextSplitter.from_language(...)` | Uses language-specific separators, such as Python class and function boundaries. | More likely to keep code structures together than generic text splitting. | Uses separators rather than a full language parser; a very large function may still be split. | Source-code files. |
| HTML splitters | `HTMLHeaderTextSplitter` follows heading tags; `HTMLSectionSplitter` follows larger sections; `HTMLSemanticPreservingSplitter` can preserve elements such as lists and tables. | Uses structure still present in raw HTML. | Not useful when the source has already been converted to Markdown or plain text and the HTML structure is gone. | Raw HTML pages. |
| `RecursiveJsonSplitter` | Traverses nested JSON and splits while trying to keep objects together. | Preserves JSON structure better than arbitrarily cutting serialized JSON text. | Designed for JSON; large individual values or lists may need extra handling. | Nested JSON records or API responses. |
| Semantic chunking, often called `SemanticChunker` | Uses embeddings to identify likely topic changes and split near those changes. It is an optional approach, not the basic splitter to start with. | Can help when long prose has weak or missing structural boundaries. | Requires embedding work during chunking, has tuning choices, and produces variable-sized chunks; a separate size limit may still be needed. | A later experiment after establishing a baseline and retrieval tests. |

### Key distinction: token count versus token boundaries

`TokenTextSplitter` cuts at token boundaries to meet its token count. The
`RecursiveCharacterTextSplitter.from_tiktoken_encoder(...)` factory instead
tries recursive text boundaries while using token counts to measure size. This
usually preserves more readable structure.

For code-specific splitting, see the
[LangChain code splitter guide](https://docs.langchain.com/oss/python/integrations/splitters/code_splitter).
For details on token sizing, see the
[token splitting guide](https://docs.langchain.com/oss/python/integrations/splitters/split_by_token).

## What is in this project's `data/` folder

The files in [data/org/](./data/org/) are Markdown, but their contents vary:

- The walkthrough has Markdown headings, a table of contents, navigation text,
  and multiple page files.
- The consumable-items list has headings and fixed-width table content.
- The FAQ includes long plain-text-style sections and records that are not all
  expressed as normal Markdown headings.

Because of this mixture, a single hard token splitter may produce chunks that
are the right size but lose useful section or table context.

## Suggested starting pipeline for these files

1. **Split by Markdown headings** to make sections and retain heading metadata.
2. **Split oversized sections recursively with token-aware sizing.**
3. **Carry source metadata** such as filename and page/part identity through to
   the final chunks.
4. **Inspect table and FAQ chunks.** If rows or records are broken apart, handle
   those structures specially rather than assuming a generic splitter will
   preserve them.
5. **Consider cleaning repeated navigation or boilerplate** before embedding;
   duplicated page menus and navigation may add noise to both vector and
   keyword retrieval.

Illustrative example:

```python
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

headers_to_split_on = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]

header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False,
)
sections = header_splitter.split_text(markdown_text)

# TODO: Add filename and page/part metadata to each section.

size_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    encoding_name="cl100k_base",
    chunk_size=600,      # starting experiment, not a universal best value
    chunk_overlap=80,    # tune after inspecting the resulting chunks
)
chunks = size_splitter.split_documents(sections)
```

`MarkdownHeaderTextSplitter.split_text()` returns LangChain `Document` objects.
The heading values are stored in their metadata. The second splitter's
`split_documents()` carries document metadata forward when it creates smaller
chunks.

The example's `cl100k_base` is a tokenizer encoding choice, not a universal
tokenizer for every embedding model. If the embedding provider has a known
tokenizer, use an appropriate one where supported; otherwise treat this size as
an experiment and inspect actual chunks.

## A small evaluation exercise

Compare the current `TokenTextSplitter` baseline with the two-stage Markdown
approach on:

1. One walkthrough page.
2. One FAQ or item-list file.

For each approach, inspect whether chunks retain headings, complete passages,
and table rows. Then try representative retrieval questions, such as asking for
an item's effect or a walkthrough location. The most useful chunking approach
is the one that improves retrieval on this corpus, not necessarily the most
complex one.

## FastAPI-generated API specification

FastAPI automatically creates an OpenAPI specification from the application's
routes, request parameter types, Pydantic validation constraints, and response
models. The specification is generated from the code; it is not a separate
hand-maintained API definition.

With the development server running on port `8890`, the default URLs are:

- `http://127.0.0.1:8890/docs` — interactive Swagger UI for exploring and
  sending requests to the endpoints.
- `http://127.0.0.1:8890/openapi.json` — the machine-readable OpenAPI JSON
  document.
- `http://127.0.0.1:8890/redoc` — an alternative API documentation view.

For GET endpoints, bind Pydantic request models to query parameters with
`Annotated[RequestModel, Query()]`. This helps FastAPI describe fields such as
`query`, `limit`, and their validation constraints as query parameters in the
generated specification. `response_model` describes the response shape.

To save the running application's generated specification locally:

```bash
curl http://127.0.0.1:8890/openapi.json -o openapi.json
```

Official guide: [FastAPI OpenAPI docs](https://fastapi.tiangolo.com/tutorial/metadata/).

## Official documentation

- [Text splitter overview](https://docs.langchain.com/oss/python/integrations/splitters)
- [Recursive text splitting](https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter)
- [Markdown header splitting](https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter)
- [Splitting by tokens](https://docs.langchain.com/oss/python/integrations/splitters/split_by_token)
- [Splitting by characters](https://docs.langchain.com/oss/python/integrations/splitters/character_text_splitter)
- [HTML splitting](https://docs.langchain.com/oss/python/integrations/splitters/split_html)
- [JSON splitting](https://docs.langchain.com/oss/python/integrations/splitters/recursive_json_splitter)
