
"""q
interface.py — Interface Streamlit : Agent Nova IT Support IZEN
Voix + Avatar + RAG + Tickets automatiques + Médias (SVG + YouTube)
"""

import streamlit as st
import tempfile
import os
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
import base64

# ============================================================
# CONFIGURATION DE LA PAGE
# ============================================================

st.set_page_config(
    page_title="Nova — Agent IT Support IZEN",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .avatar-container {
        display: flex; flex-direction: column; align-items: center;
        padding: 20px;
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        border-radius: 20px; margin-bottom: 16px;
    }
    .avatar-img {
        width: 160px; height: 160px; border-radius: 50%;
        border: 3px solid #7c6ff7; object-fit: cover;
    }
    .avatar-name { color: white; font-size: 22px; font-weight: bold; margin-top: 10px; }
    .avatar-subtitle { color: rgba(255,255,255,0.6); font-size: 12px; margin-top: 2px; }
    .status-badge {
        margin-top: 8px; padding: 4px 14px; border-radius: 20px;
        font-size: 12px; font-weight: 600;
    }
    .status-ready    { background: #27ae60; color: white; }
    .status-thinking { background: #f39c12; color: white; }
    .status-speaking { background: #3498db; color: white; }

    .user-msg {
        background: #e8f4fd; border-radius: 18px 18px 4px 18px;
        padding: 12px 18px; margin: 8px 0; margin-left: 20%; color: #2c3e50;
    }
    .nova-msg {
        background: #f0eeff; border-radius: 18px 18px 18px 4px;
        padding: 12px 18px; margin: 8px 0; margin-right: 20%; color: #2c3e50;
    }
    .ticket-badge {
        background: #fff3cd; border: 1px solid #ffc107;
        border-radius: 8px; padding: 8px 12px;
        font-size: 12px; color: #856404; margin-top: 6px;
    }
    .ticket-critique { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
    .source-badge {
        background: #ecf0f1; border-radius: 10px; padding: 3px 8px;
        font-size: 11px; color: #7f8c8d; display: inline-block;
        margin-top: 4px; margin-right: 4px;
    }
    .stats-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 12px; padding: 12px; color: white; text-align: center;
    }
    footer { visibility: hidden; }
    .stButton > button { border-radius: 25px; padding: 8px 20px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

def init_session_state():
    defaults = {
        "agent":                 None,
        "messages":              [],
        "status":                "ready",
        "tickets_created":       0,
        "resolved_auto":         0,
        "employee_email":        "",
        "last_audio_hash":       None,
        "ticket_form_open":      False,
        "ticket_form_msg_index": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


@st.cache_resource(show_spinner=False)
def load_agent():
    import sys
    sys.path.append(str(Path(__file__).parent))
    from agent import create_agent
    return create_agent()


# ============================================================
# ENVOI TICKET PAR EMAIL
# ============================================================

def send_ticket_email(employee_name: str, employee_email: str,
                      problem_description: str, nova_answer: str):
    """
    Envoie un ticket IT par email à support@izen.tn.
    - Essaie d'abord MailHog (localhost:1025) pour les tests.
    - Fallback : sauvegarde le ticket dans data/tickets/*.txt
    """
    ticket_id = f"TKT-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.now().strftime("%d/%m/%Y à %H:%M")

    subject = f"[Ticket IT {ticket_id}] Problème non résolu — {employee_name}"

    body = f"""
Nouveau ticket IT créé depuis l'interface Nova.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎫 TICKET : {ticket_id}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 Employé       : {employee_name}
📧 Email         : {employee_email or 'Non renseigné'}
🕐 Date          : {now}

📋 PROBLÈME DÉCRIT :
{problem_description}

💬 RÉPONSE NOVA (non satisfaisante) :
{nova_answer[:500]}...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ce ticket a été créé automatiquement via Agent Nova IT IZEN.
    """.strip()

    # ── Tentative via MailHog (localhost:1025) ──────────────
    try:
        msg = MIMEMultipart()
        msg["From"]    = employee_email or "nova@izen.tn"
        msg["To"]      = "support@izen.tn"
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP("localhost", 1025, timeout=3) as server:
            server.sendmail(msg["From"], ["support@izen.tn"], msg.as_string())

        print(f"✅ Ticket {ticket_id} envoyé via MailHog")
        return ticket_id

    except Exception as e:
        print(f"⚠️  MailHog non disponible ({e}) — sauvegarde locale")

    # ── Fallback : sauvegarde dans data/tickets/ ────────────
    try:
        tickets_dir = Path(__file__).parent.parent / "data" / "tickets"
        tickets_dir.mkdir(parents=True, exist_ok=True)
        ticket_file = tickets_dir / f"{ticket_id}.txt"
        ticket_file.write_text(body, encoding="utf-8")
        print(f"📁 Ticket sauvegardé : {ticket_file}")
        return ticket_id
    except Exception as e:
        print(f"❌ Impossible de sauvegarder le ticket : {e}")
        return None


# ============================================================
# UTILITAIRES
# ============================================================

def get_avatar_html(photo_path: Path) -> str:
    if photo_path.exists():
        with open(photo_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        img_src = f"data:image/jpeg;base64,{img_b64}"
    else:
        img_src = "https://ui-avatars.com/api/?name=Nova&size=160&background=302b63&color=7c6ff7&bold=true"

    status_map = {
        "ready":    (" Prête à vous aider",  "status-ready"),
        "thinking": (" Analyse en cours...", "status-thinking"),
        "speaking": ("🔊 Réponse vocale...",  "status-speaking"),
    }
    status_text, status_class = status_map.get(st.session_state.status, ("", "status-ready"))

    return f"""
    <div class="avatar-container">
        <img class="avatar-img" src="{img_src}" alt="Nova"/>
        <div class="avatar-name"> Nova</div>
        <div class="avatar-subtitle">Agent IT Support — IZEN</div>
        <div class="status-badge {status_class}">{status_text}</div>
    </div>
    """


def process_question(question: str):
    if not question.strip():
        return

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.status = "thinking"

    from agent import ask_agent
    result = ask_agent(
        st.session_state.agent,
        question,
        employee_email=st.session_state.employee_email or None
    )

    answer  = result["answer"]
    sources = result["sources"]
    ticket  = result.get("ticket")
    media   = result.get("media")

    if ticket:
        st.session_state.tickets_created += 1
    else:
        st.session_state.resolved_auto += 1

    st.session_state.status = "speaking"
    audio_path = None
    try:
        from text_to_speech import generate_speech
        clean_answer = answer.split("---")[0].strip()
        audio_path = generate_speech(clean_answer)
    except Exception as e:
        print(f"TTS non disponible: {e}")

    st.session_state.messages.append({
        "role":    "nova",
        "content": answer,
        "sources": sources,
        "ticket":  ticket,
        "audio":   audio_path,
        "media":   media,
    })
    st.session_state.status = "ready"


# ============================================================
# INTERFACE PRINCIPALE
# ============================================================

def main():
    init_session_state()

    # ---- SIDEBAR ----
    with st.sidebar:
        st.markdown("##  Panneau Nova")

        if st.button(" Démarrer Nova", type="primary", use_container_width=True):
            with st.spinner("Chargement de l'agent IT..."):
                try:
                    st.session_state.agent = load_agent()
                    st.success("✅ Nova est prête !")
                except Exception as e:
                    st.error(f"❌ Erreur: {e}")
                    st.info("Vérifie ta clé GROQ_API_KEY et que MailHog est lancé.")

        st.markdown("---")
        if st.button(" Effacer la conversation", use_container_width=True):
            st.session_state.messages        = []
            st.session_state.resolved_auto   = 0
            st.session_state.tickets_created = 0
            st.rerun()

        st.markdown("---")
        st.markdown("###  FAQ")
        exemples = [
            "Mon mot de passe est bloqué",
            "Je n'arrive pas à me connecter au VPN",
            "Outlook ne reçoit plus mes emails",
            "Mon PC est très lent",
            "J'ai reçu un email de phishing",
        ]
        for ex in exemples:
            if st.button(f"💬 {ex}", use_container_width=True, key=f"ex_{ex[:15]}"):
                if st.session_state.agent:
                    with st.spinner("Nova analyse..."):
                        process_question(ex)
                    st.rerun()
                else:
                    st.warning("Lance Nova d'abord !")

    # ---- COLONNES PRINCIPALES ----
    col1, col2 = st.columns([1, 2])

    with col1:
        data_dir     = Path(__file__).parent.parent / "data"
        avatar_photo = data_dir / "avatar_photo.jpg"

        if not avatar_photo.exists():
            try:
                from avatar import create_default_avatar
                create_default_avatar()
            except:
                pass

        st.markdown(get_avatar_html(avatar_photo), unsafe_allow_html=True)

        if st.session_state.messages:
            last_nova = next(
                (m for m in reversed(st.session_state.messages) if m["role"] == "nova"), None
            )
            if last_nova and last_nova.get("audio") and os.path.exists(last_nova["audio"]):
                st.markdown("#### 🔊 Réponse audio")
                with open(last_nova["audio"], "rb") as af:
                    st.audio(af.read(), format="audio/wav", autoplay=True)

        st.markdown("""
        <div style="background:#f8f9fa; border-radius:10px; padding:12px; margin-top:12px;">
            <div style="font-weight:bold; color:#495057;"> Contact IT IZEN</div>
            <div style="font-size:13px; margin-top:6px;"> support@izen.tn</div>
            <div style="font-size:13px;">Poste 101</div>
            <div style="font-size:13px;"> Mehdi Bouaziz</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("##  Support IT — Agent Nova")

        if not st.session_state.messages:
            st.info(" Bonjour ! Je suis Nova, votre agent IT IZEN. Décrivez votre problème et je vais vous aider à le résoudre immédiatement.")

        # ── FIX : utiliser enumerate pour garantir des clés uniques ──
        for msg_index, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(
                    f'<div class="user-msg">👤 <b>Vous :</b><br>{msg["content"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                content = msg["content"]
                if "---" in content and "Ticket créé automatiquement" in content:
                    parts   = content.split("---", 1)
                    content = parts[0].strip()

                sources_html = ""
                if msg.get("sources"):
                    badges       = " ".join([f'<span class="source-badge">📖 {s}</span>' for s in msg["sources"]])
                    sources_html = f"<br>{badges}"

                ticket_html = ""
                if msg.get("ticket"):
                    t         = msg["ticket"]
                    css_class = "ticket-critique" if t["severity"] == "CRITIQUE" else "ticket-badge"
                    ticket_html = f"""
                    <div class="{css_class}" style="margin-top:8px;">
                         <b>Ticket {t['ticket_id']}</b> créé — {t['category']}<br>
                        Sévérité : <b>{t['severity']}</b> | SLA : {t['sla']}<br>
                        L'équipe IT a été notifiée.
                    </div>"""

                st.markdown(
                    f'<div class="nova-msg"> <b>Nova :</b><br>{content}{sources_html}{ticket_html}</div>',
                    unsafe_allow_html=True
                )

                # ── Affichage du schéma SVG explicatif ──────────────
                media = msg.get("media")
                if media:
                    image_data = media.get("image")
                    if image_data:
                        if image_data.get("source") == "generated_svg" and image_data.get("svg"):
                            with st.expander(" Schéma explicatif", expanded=True):
                                st.markdown(image_data["svg"], unsafe_allow_html=True)
                                st.caption(image_data.get("description", ""))
                        elif image_data.get("url"):
                            with st.expander(" Illustration", expanded=False):
                                st.image(
                                    image_data["url"],
                                    caption=image_data.get("description", ""),
                                    use_column_width=True
                                )
                                if image_data.get("author"):
                                    st.caption(f"Photo par {image_data['author']} — Unsplash")

                 

                # ── BOUTON CRÉER TICKET MANUEL ───────────────────────
                if not msg.get("ticket") and not msg.get("manual_ticket_sent"):
                    if st.button(
                        "🎫 Mon problème n'est pas résolu — Créer un ticket",
                        key=f"ticket_btn_{msg_index}",   # ← clé unique via enumerate
                        help="Envoie un ticket au département IT : support@izen.tn"
                    ):
                        st.session_state.ticket_form_open      = True
                        st.session_state.ticket_form_msg_index = msg_index
                        st.rerun()

                # ── FORMULAIRE TICKET ────────────────────────────────
                if (
                    st.session_state.get("ticket_form_open")
                    and st.session_state.get("ticket_form_msg_index") == msg_index
                ):
                    with st.container():
                        st.markdown("""
                        <div style="background:#fff8e1; border:1px solid #ffc107;
                                    border-radius:10px; padding:16px; margin:8px 0;">
                            <b>🎫 Créer un ticket IT — support@izen.tn</b>
                        </div>
                        """, unsafe_allow_html=True)

                        name = st.text_input(
                            "👤 Votre nom",
                            key=f"tkt_name_{msg_index}",
                            placeholder="Ex: Ahmed Ben Ali"
                        )
                        email = st.text_input(
                            "📧 Votre email",
                            key=f"tkt_email_{msg_index}",
                            value=st.session_state.employee_email,
                            placeholder="ahmed@izen.tn"
                        )
                        details = st.text_area(
                            "📋 Détails supplémentaires (optionnel)",
                            key=f"tkt_details_{msg_index}",
                            placeholder="Précisez votre problème ou ajoutez des informations...",
                            height=80
                        )

                        col_send, col_cancel = st.columns([1, 1])

                        with col_send:
                            if st.button(
                                "📨 Envoyer le ticket",
                                key=f"tkt_send_{msg_index}",
                                type="primary",
                                use_container_width=True
                            ):
                                if not name.strip():
                                    st.error("⚠️ Veuillez saisir votre nom.")
                                else:
                                    user_question = ""
                                    for m in reversed(st.session_state.messages[:msg_index]):
                                        if m["role"] == "user":
                                            user_question = m["content"]
                                            break

                                    full_problem = user_question
                                    if details.strip():
                                        full_problem += f"\n\nDétails supplémentaires : {details}"

                                    ticket_id = send_ticket_email(
                                        employee_name=name.strip(),
                                        employee_email=email.strip(),
                                        problem_description=full_problem,
                                        nova_answer=content,
                                    )

                                    if ticket_id:
                                        st.success(
                                            f"✅ Ticket **{ticket_id}** envoyé à support@izen.tn !\n\n"
                                            f"L'équipe IT vous contactera à **{email or 'votre email'}**."
                                        )
                                        msg["manual_ticket_sent"] = True
                                        msg["manual_ticket_id"]   = ticket_id
                                        st.session_state.ticket_form_open  = False
                                        st.session_state.tickets_created  += 1
                                        st.rerun()
                                    else:
                                        st.error(
                                            "❌ Erreur lors de l'envoi. "
                                            "Contactez directement support@izen.tn ou appelez le Poste 101."
                                        )

                        with col_cancel:
                            if st.button(
                                "✖️ Annuler",
                                key=f"tkt_cancel_{msg_index}",
                                use_container_width=True
                            ):
                                st.session_state.ticket_form_open = False
                                st.rerun()

                # ── Badge ticket manuel déjà envoyé ─────────────────
                if msg.get("manual_ticket_sent"):
                    st.markdown(
                        f"""<div class="ticket-badge" style="margin-top:6px;">
                            🎫 <b>Ticket {msg.get('manual_ticket_id', '')} envoyé</b>
                            — L'équipe IT a été notifiée à support@izen.tn
                        </div>""",
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # ── Input texte ──────────────────────────────────────────
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            question = st.text_input(
                "question",
                placeholder="Décrivez votre problème IT... (ex: Mon VPN ne fonctionne plus)",
                label_visibility="collapsed",
                key="text_input"
            )
        with col_btn:
            send_btn = st.button("Envoie", use_container_width=True)

        if send_btn and question:
            if not st.session_state.agent:
                st.error("⚠️ Lance Nova d'abord (bouton dans le menu gauche) !")
            else:
                with st.spinner(" Nova analyse votre problème..."):
                    process_question(question)
                st.rerun()

        # ── Input vocal ──────────────────────────────────────────
        st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<h4><i class="fas fa-microphone" style="color:#7c6ff7; margin-right:8px;"></i> Ou parlez directement à Nova</h4>
""", unsafe_allow_html=True)

        mic_col1, mic_col2 = st.columns([3, 1])

        with mic_col1:
            audio_bytes = st.audio_input(
                "Maintenez et parlez...",
                label_visibility="collapsed",
                key="mic_input"
            )

        with mic_col2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.caption("Cliquez sur le micro puis parlez")

        if audio_bytes:
            if not st.session_state.agent:
                st.error("⚠️ Lance Nova d'abord !")
            else:
                audio_hash = hash(audio_bytes.getvalue())
                if st.session_state.get("last_audio_hash") != audio_hash:
                    st.session_state["last_audio_hash"] = audio_hash

                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                        tmp.write(audio_bytes.getvalue())
                        tmp_path = tmp.name

                    try:
                        with st.spinner("🎙️ Transcription en cours..."):
                            from speech_to_text import transcribe_audio_file
                            question_vocal = transcribe_audio_file(tmp_path)

                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)

                        if question_vocal:
                            st.success(f"✅ Vous avez dit : *\"{question_vocal}\"*")
                            process_question(question_vocal)
                            st.rerun()
                        else:
                            st.warning("Aucune parole détectée, réessayez.")
                    except Exception as e:
                        st.error(f"Erreur transcription: {e}")
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)


if __name__ == "__main__":
    main()