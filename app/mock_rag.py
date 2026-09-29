from __future__ import annotations

import time

from .incidents import STATE
from .pii import summarize_text
from .tracing import get_langfuse_client, observe

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, logs identify affected requests, traces localize the root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


@observe(name="retrieve-context", as_type="retriever", capture_input=False, capture_output=False)
def retrieve(message: str) -> list[str]:
    """Retrieve context as a first-class retriever observation in the agent trace."""
    langfuse = get_langfuse_client()
    langfuse.update_current_span(
        input={"query": summarize_text(message, max_len=1_000)},
        metadata={"corpus": "lab-corpus"},
    )
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(2.5)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            langfuse.update_current_span(
                output={"documents": [summarize_text(doc, max_len=1_000) for doc in docs]},
                metadata={"corpus": "lab-corpus", "document_count": len(docs)},
            )
            return docs

    docs = ["No domain document matched. Use general fallback answer."]
    langfuse.update_current_span(
        output={"documents": docs},
        metadata={"corpus": "lab-corpus", "document_count": len(docs)},
    )
    return docs
