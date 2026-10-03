import json
import streamlit as st
from sentence_transformers import SentenceTransformer, util

# ---------------- Configuration ----------------
DATA_FILE = "knowledge_base.json"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
THRESHOLD = 0.65  # minimum similarity to consider direct answer

# ---------------- Dataset Functions ----------------
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------- Embedding Model ----------------
model = SentenceTransformer(MODEL_NAME)

# ---------------- Embedding Model ----------------
@st.cache_resource
def load_model():
    return SentenceTransformer(MODEL_NAME)


model = load_model()


@st.cache_resource
def compute_embeddings(questions):
    embeddings = model.encode(
        list(questions),
        convert_to_tensor=True,
    )
    return embeddings

def find_answer(query, data, embeddings, threshold=THRESHOLD):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarity_scores = util.cos_sim(query_embedding, embeddings)[0]

    # Boost scores if keywords match
    for i, item in enumerate(data):
        for kw in item.get("keywords", []):
            if kw.lower() in query.lower():
                similarity_scores[i] += 0.1  # small boost

    best_idx = int(similarity_scores.argmax())
    best_score = float(similarity_scores[best_idx])

    if best_score >= threshold:
        return best_score, best_idx
    return None, None

def top_similar_questions(query, data, embeddings, top_n=3):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarity_scores = util.cos_sim(query_embedding, embeddings)[0]
    top_indices = similarity_scores.topk(k=top_n).indices.tolist()
    return [(data[i]["question"], float(similarity_scores[i])) for i in top_indices]

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI & DS Knowledge Bot", layout="wide", page_icon="📘")

# Header
st.markdown("<h1 style='text-align:center; color:#4B7BEC;'>📘 AI & DS Knowledge Bot</h1>", unsafe_allow_html=True)
st.markdown("---")

data = load_data()

questions = tuple(
    item["question"]
    for item in data
)

embeddings = compute_embeddings(questions)

# User Query
st.markdown("### Ask a Question")
query = st.text_input("Type your question here...", key="query")

if query:
    best_score, best_idx = find_answer(query, data, embeddings)
    
    if best_idx is not None:
        # Direct Answer Card
        entry = data[best_idx]
        st.markdown("**Answer:**")
        st.write(entry["answer"])        
        if entry.get("examples"):
            st.markdown("**Examples:**")
            st.write(", ".join(entry["examples"]))
        if entry.get("references"):
            st.markdown("**References:**")
            for ref in entry["references"]:
                st.markdown(f"- [{ref}]({ref})")
    else:
        # Fallback suggestions
        st.warning("I don’t have a direct answer. Here are some helpful suggestions:")

        # A. Related Topics
        topics = list(set(item["topic"] for item in data))
        st.markdown(f"**Related Topics:** {', '.join(topics)}")

        # B. Similar Questions
        st.markdown("**Similar Questions from Dataset:**")
        similar_qs = top_similar_questions(query, data, embeddings, top_n=3)
        for q, score in similar_qs:
            st.markdown(f"- {q} (Similarity: {score:.2f})")

        # C. Related References only from similar questions
        st.markdown("**Related References:**")
        displayed_refs = set()
        for q, score in similar_qs:
            idx = next(i for i, item in enumerate(data) if item["question"] == q)
            for ref in data[idx].get("references", []):
                if ref not in displayed_refs:
                    st.markdown(f"- [{ref}]({ref})")
                    displayed_refs.add(ref)

        # D. Ask user to contribute
        st.info("You can add this question to improve the knowledge base below:")

# ---------------- Add New Knowledge ----------------
with st.expander("➕ Add New Knowledge"):
    new_q = st.text_input("New Question:", key="new_q")
    new_a = st.text_area("Answer:", key="new_a")
    new_topic = st.text_input("Topic:", key="new_topic")
    new_keywords = st.text_input("Keywords (comma separated):", key="new_keywords")
    new_examples = st.text_input("Examples (comma separated):", key="new_examples")
    new_references = st.text_input("References (comma separated URLs):", key="new_references")

    if st.button("Add Entry"):
        if new_q and new_a:
            data.append({
                "question": new_q,
                "answer": new_a,
                "topic": new_topic,
                "keywords": [k.strip() for k in new_keywords.split(",") if k.strip()],
                "examples": [e.strip() for e in new_examples.split(",") if e.strip()],
                "references": [r.strip() for r in new_references.split(",") if r.strip()],
                "similar_questions": []
            })
            save_data(data)
            st.success("✅ New entry added!")
        else:
            st.error("Please provide both a question and an answer.")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>© HEM | AI & DS Knowledge Bot | GitHub Link</p>", unsafe_allow_html=True)
