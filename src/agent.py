"""
agent.py — Cerveau de l'Agent Nova (IZEN IT Support)
LangChain + Groq + ChromaDB (RAG) + Système de tickets IT
VERSION MULTIMÉDIA : supporte MD, PDF, Images, Vidéos, DOCX, PPTX
"""

import os
import re
import smtplib
import random
import string
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from media_enricher import enrich_response_with_media

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate

from kb_loader import load_all_documents, save_kb_index, get_kb_stats

# ============================================================
# CONFIGURATION IZEN
# ============================================================

BASE_DIR = Path(__file__).parent.parent
KB_DIR   = BASE_DIR / "knowledge_base" / "it_support"
DB_DIR   = BASE_DIR / "data" / "chroma_db"
IDX_PATH = BASE_DIR / "data" / "kb_index.json"

AVATAR_NAME = "Nova"

# MailHog — pas besoin de mot de passe
SMTP_CONFIG = {
    "host":      "localhost",
    "port":      1025,
    "user":      "",
    "password":  "",
    "from_name": "Agent Nova — IT Support",
    "it_email":  "support@izen.tn",
    "it_phone":  "Poste 101",
}

TICKET_CATEGORIES = {
    "password": {"label": "Mot de passe / Compte bloqué",  "severity": "NORMALE",  "sla": "2h"},
    "vpn":      {"label": "VPN / Réseau",                  "severity": "HAUTE",    "sla": "1h"},
    "software": {"label": "Logiciel / Application",        "severity": "NORMALE",  "sla": "4h"},
    "hardware": {"label": "Matériel / PC",                 "severity": "HAUTE",    "sla": "2h"},
    "security": {"label": "Sécurité / Incident",           "severity": "CRITIQUE", "sla": "15min"},
    "other":    {"label": "Autre demande IT",              "severity": "NORMALE",  "sla": "8h"},
}

CATEGORY_KEYWORDS = {
    "password": ["mot de passe", "password", "compte bloqué", "login", "connexion",
                 "identifiant", "accès refusé", "réinitialiser", "verrouillé"],
    "vpn":      ["vpn", "cisco", "anyconnect", "réseau", "internet", "wifi",
                 "connexion réseau", "hors ligne", "télétravail", "distant"],
    "software": ["office", "word", "excel", "outlook", "teams", "logiciel",
                 "application", "crash", "plante", "erreur", "installation"],
    "hardware": ["pc", "ordinateur", "lent", "imprimante", "écran", "clavier",
                 "souris", "matériel", "disque", "mémoire"],
    "security": ["virus", "malware", "phishing", "hacking", "pirate", "arnaque",
                 "suspect", "email frauduleux", "ransomware", "crypté"],
}

AVATAR_PERSONA = f"""Tu es {AVATAR_NAME}, l'agent IA de support IT d'IZEN (entreprise de services IT à Tunis, 200 employés).
Tu traites les incidents IT des employés de manière autonome et active.

Ton rôle :
- Analyser l'intention de l'employé (panne, blocage, demande)
- Rechercher la solution dans la base de connaissances IT (textes, PDFs, captures d'écran, vidéos)
- Guider l'employé étape par étape

Règles de comportement :
- Réponds TOUJOURS en français
- Sois concis et direct (3-5 étapes maximum)
- Guide pas à pas avec des étapes numérotées
- Si la solution est dans la KB, donne-la directement
- Ton contact IT : support@izen.tn | Poste 101 | Resp. Mehdi Bouaziz

Tu t'appelles {AVATAR_NAME} et tu es l'agent IA de support IT d'IZEN."""


# ============================================================
# GÉNÉRATION DE TICKETS
# ============================================================

def generate_ticket_id() -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"IZN-{suffix}"


def detect_category(question: str) -> str:
    question_lower = question.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in question_lower for kw in keywords):
            return category
    return "other"


def create_ticket(question: str, employee_email: str = None, answer: str = "") -> dict:
    ticket_id  = generate_ticket_id()
    category   = detect_category(question)
    cat_info   = TICKET_CATEGORIES.get(category, TICKET_CATEGORIES["other"])
    created_at = datetime.now().strftime("%d/%m/%Y à %H:%M")

    ticket = {
        "ticket_id":      ticket_id,
        "category":       cat_info["label"],
        "severity":       cat_info["severity"],
        "sla":            cat_info["sla"],
        "question":       question,
        "created_at":     created_at,
        "employee_email": employee_email or "Non renseigné",
        "email_sent":     False,
    }

    # Toujours envoyer via MailHog (sans authentification)
    ticket["email_sent"] = send_ticket_email(ticket, answer)

    return ticket


def send_ticket_email(ticket: dict, nova_answer: str = "") -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[{ticket['severity']}] Ticket {ticket['ticket_id']} — {ticket['category']}"
        msg["From"]    = f"{SMTP_CONFIG['from_name']} <nova@izen.tn>"
        msg["To"]      = SMTP_CONFIG["it_email"]

        sev_color = {"CRITIQUE": "#e74c3c", "HAUTE": "#f39c12"}.get(ticket["severity"], "#27ae60")

        html_body = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:600px;">
        <div style="background:#1a1a2e;color:white;padding:20px;border-radius:8px 8px 0 0;">
            <h2>🤖 Agent Nova — Nouveau Ticket IT</h2>
        </div>
        <div style="border:1px solid #ddd;padding:20px;border-radius:0 0 8px 8px;">
            <table style="width:100%;border-collapse:collapse;">
                <tr><td style="padding:8px;font-weight:bold;color:#555;">Ticket ID</td>
                    <td style="padding:8px;"><b style="color:#e74c3c;">{ticket['ticket_id']}</b></td></tr>
                <tr style="background:#f9f9f9;">
                    <td style="padding:8px;font-weight:bold;color:#555;">Catégorie</td>
                    <td style="padding:8px;">{ticket['category']}</td></tr>
                <tr><td style="padding:8px;font-weight:bold;color:#555;">Sévérité</td>
                    <td style="padding:8px;"><span style="background:{sev_color};color:white;padding:2px 8px;border-radius:4px;">{ticket['severity']}</span></td></tr>
                <tr style="background:#f9f9f9;">
                    <td style="padding:8px;font-weight:bold;color:#555;">SLA</td>
                    <td style="padding:8px;">⏱️ {ticket['sla']}</td></tr>
                <tr><td style="padding:8px;font-weight:bold;color:#555;">Employé</td>
                    <td style="padding:8px;">{ticket['employee_email']}</td></tr>
                <tr style="background:#f9f9f9;">
                    <td style="padding:8px;font-weight:bold;color:#555;">Date</td>
                    <td style="padding:8px;">{ticket['created_at']}</td></tr>
            </table>
            <div style="margin-top:16px;padding:12px;background:#fff3cd;border-radius:6px;">
                <b>📝 Problème signalé :</b><br><i>"{ticket['question']}"</i>
            </div>
            {'<div style="margin-top:12px;padding:12px;background:#d4edda;border-radius:6px;"><b>💬 Réponse tentée par Nova :</b><br>' + nova_answer[:500] + '...</div>' if nova_answer else ''}
            <div style="margin-top:16px;color:#888;font-size:12px;">
                Ce ticket a été créé via l'agent IA Nova — IZEN Support IT
            </div>
        </div></body></html>"""

        msg.attach(MIMEText(html_body, "html"))

        # MailHog : connexion simple sans authentification
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.sendmail("nova@izen.tn", SMTP_CONFIG["it_email"], msg.as_string())

        print(f"✅ Email ticket {ticket['ticket_id']} envoyé à {SMTP_CONFIG['it_email']}")
        return True
    except Exception as e:
        print(f"⚠️  Échec envoi email ticket: {e}")
        return False


# ============================================================
# CHARGEMENT ET INDEXATION MULTIMÉDIA
# ============================================================

def load_documents():
    print("📚 Chargement de la base de connaissances IT (multimédia)...")
    stats = get_kb_stats(KB_DIR)
    print("📁 Contenu détecté :")
    emoji_map = {"text": "📝", "pdf": "📄", "image": "🖼️", "video": "🎬", "office": "📊", "unsupported": "❌"}
    for ftype, count in stats.items():
        if ftype != "unsupported" and count > 0:
            print(f"  {emoji_map.get(ftype, '📁')} {ftype.upper()} : {count} fichier(s)")

    docs = load_all_documents(KB_DIR, use_vision=True)
    print(f"✅ {len(docs)} documents chargés au total")
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ {len(chunks)} chunks créés")
    return chunks


def build_vector_store(chunks):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )

    if DB_DIR.exists() and any(DB_DIR.iterdir()):
        print("📂 Chargement base vectorielle existante...")
        vectorstore = Chroma(
            persist_directory=str(DB_DIR),
            embedding_function=embeddings
        )
    else:
        print("🔨 Création de la base vectorielle IT (multimédia)...")
        DB_DIR.mkdir(parents=True, exist_ok=True)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=str(DB_DIR)
        )
        vectorstore.persist()
        print("✅ Base vectorielle IT créée")

    return vectorstore


# ============================================================
# CRÉATION DE L'AGENT RAG
# ============================================================

def create_agent():
    docs      = load_documents()
    chunks    = split_documents(docs)
    save_kb_index(docs, IDX_PATH)
    vectorstore = build_vector_store(chunks)

    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=500
    )

    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
        k=5
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    prompt_template = PromptTemplate(
        input_variables=["context", "question", "chat_history"],
        template=f"""{AVATAR_PERSONA}

Historique de la conversation :
{{chat_history}}

Informations trouvées dans la base de connaissances IT IZEN
(textes, PDFs, captures d'écran, transcriptions vidéo) :
{{context}}

Problème signalé par l'employé : {{question}}

Réponse de {AVATAR_NAME} (guide étape par étape, max 5 étapes) :"""
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt_template},
        verbose=False
    )

    print(f"✅ Agent {AVATAR_NAME} — IT Support IZEN prêt !")
    return chain


# ============================================================
# LOGIQUE : PAS DE TICKET AUTOMATIQUE
# L'utilisateur décide via le bouton dans l'interface
# ============================================================

def should_create_ticket(answer: str, sources: list) -> bool:
    return False  # Ticket uniquement à la demande de l'utilisateur


def ask_agent(chain, question: str, employee_email: str = None) -> dict:
    result = chain.invoke({"question": question})

    sources = []
    if "source_documents" in result:
        for doc in result["source_documents"]:
            source   = doc.metadata.get("source", "")
            doc_type = doc.metadata.get("type", "")
            if source and source not in sources:
                label      = Path(source).parent.name + "/" + Path(source).name
                type_emoji = {"pdf": "📄", "image": "🖼️", "video": "🎬", "docx": "📝", "pptx": "📊"}.get(doc_type, "📁")
                sources.append(f"{type_emoji} {label}")

    answer = result["answer"]
    if hasattr(answer, "content"):
        answer = answer.content

    # Aucun ticket automatique
    ticket = None

    # Enrichissement multimédia (schéma SVG + vidéo YouTube)
    category = detect_category(question)
    media    = enrich_response_with_media(category, question, answer)

    return {
        "answer":  answer,
        "sources": sources,
        "ticket":  ticket,
        "media":   media,
    }


def rebuild_knowledge_base():
    import shutil
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)
        print("🗑️  Ancienne base supprimée")
    docs   = load_documents()
    chunks = split_documents(docs)
    build_vector_store(chunks)
    print("✅ Base de connaissances IT reconstruite !")


# ============================================================
# TEST RAPIDE
# ============================================================

if __name__ == "__main__":
    print("=== TEST AGENT NOVA — IT SUPPORT IZEN ===\n")
    agent = create_agent()

    questions_test = [
        "Mon mot de passe Windows est expiré, comment le changer ?",
        "Je n'arrive pas à me connecter au VPN depuis chez moi",
        "Outlook ne reçoit plus mes emails depuis ce matin",
        "J'ai reçu un email bizarre qui me demande mes identifiants",
        "Mon PC est très lent depuis hier",
    ]

    for q in questions_test:
        print(f"\n❓ {q}")
        result = ask_agent(agent, q)
        print(f"💬 Nova: {result['answer'][:300]}...")
        if result.get("sources"):
            print(f"📚 Sources: {', '.join(result['sources'][:2])}")
        if result.get("media"):
            media = result["media"]
            if media.get("image"):
                print(f"🖼️  Image: {media['image'].get('description', 'N/A')} ({media['image'].get('source')})")

        print("-" * 50)