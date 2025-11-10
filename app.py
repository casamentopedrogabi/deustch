import streamlit as st
import random
from datetime import date, timedelta
import pandas as pd
import altair as alt
import os
import json
import locale 
# Importa o cliente do Supabase
from supabase import create_client, Client

# --- App Configuration ---
st.set_page_config(layout="wide", page_title="Verbos com Preposição", page_icon="🧠")

# --- Constants ---
# Logic
NEW_VERB_BATCH_SIZE = 3 
MASTERY_STREAK = 3 
NEW_VERBS_PER_SESSION = 3
REVIEW_VERBS_PER_SESSION = 3

# --- Heineken Colors (para os gráficos) ---
heineken_colors = {
    "dark_green": "#286529",
    "red": "#ca2819",
    "lime_green": "#8ebf48",
    "medium_gray": "#95a49b"
}

# --- Database Setup ---
# Initialize Supabase connection. 
# Ele vai ler as chaves do seu arquivo .streamlit/secrets.toml
try:
    url = st.secrets["connections"]["supabase"]["url"]
    key = st.secrets["connections"]["supabase"]["key"]
    supabase: Client = create_client(url, key)
except Exception as e:
    # Este erro só aparecerá se os secrets estiverem faltando
    st.error(f"Erro ao conectar ao Supabase: {e}")
    st.error("Verifique suas chaves no .streamlit/secrets.toml (local) ou em 'Manage app' (nuvem).")
    st.stop()
# --- END Database Setup ---


# --- Verb Data ---
# (Data list VERB_DATA remains the same as previous)
VERB_DATA = [
    {"id": "v1", "verb": "sich erinnern", "preposition": "an", "case": "Akk", "translation": "lembrar-se de"},
    {"id": "v2", "verb": "denken", "preposition": "an", "case": "Akk", "translation": "pensar em"},
    {"id": "v3", "verb": "glauben", "preposition": "an", "case": "Akk", "translation": "acreditar em"},
    {"id": "v4", "verb": "sich freuen", "preposition": "auf", "case": "Akk", "translation": "estar feliz por algo futuro"},
    {"id": "v5", "verb": "sich freuen", "preposition": "über", "case": "Akk", "translation": "ficar feliz por algo já ocorrido"},
    {"id": "v6", "verb": "warten", "preposition": "auf", "case": "Akk", "translation": "esperar por"},
    {"id": "v7", "verb": "antworten", "preposition": "auf", "case": "Akk", "translation": "responder a"},
    {"id": "v8", "verb": "aufpassen", "preposition": "auf", "case": "Akk", "translation": "tomar conta de"},
    {"id": "v9", "verb": "sich konzentrieren", "preposition": "auf", "case": "Akk", "translation": "concentrar-se em"},
    {"id": "v10", "verb": "sich vorbereiten", "preposition": "auf", "case": "Akk", "translation": "preparar-se para"},
    {"id": "v11", "verb": "hoffen", "preposition": "auf", "case": "Akk", "translation": "esperar (ter esperança)"},
    {"id": "v12", "verb": "sich interessieren", "preposition": "für", "case": "Akk", "translation": "interessar-se por"},
    {"id": "v13", "verb": "danken", "preposition": "für", "case": "Akk", "translation": "agradecer por"},
    {"id": "v14", "verb": "bezahlen", "preposition": "für", "case": "Akk", "translation": "pagar por"},
    {"id": "v15", "verb": "sich entschuldigen", "preposition": "für", "case": "Akk", "translation": "pedir desculpas por"},
    {"id": "v16", "verb": "kämpfen", "preposition": "für", "case": "Akk", "translation": "lutar por"},
    {"id": "v17", "verb": "sorgen", "preposition": "für", "case": "Akk", "translation": "cuidar de"},
    {"id": "v18", "verb": "werben", "preposition": "für", "case": "Akk", "translation": "fazer propaganda para"},
    {"id": "v19", "verb": "sich bewerben", "preposition": "um", "case": "Akk", "translation": "candidatar-se a"},
    {"id": "v20", "verb": "bitten", "preposition": "um", "case": "Akk", "translation": "pedir algo"},
    {"id": "v21", "verb": "es geht", "preposition": "um", "case": "Akk", "translation": "trata-se de"},
    {"id": "v22", "verb": "sich kümmern", "preposition": "um", "case": "Akk", "translation": "cuidar de / tomar conta"},
    {"id": "v23", "verb": "lachen", "preposition": "über", "case": "Akk", "translation": "rir de"},
    {"id": "v24", "verb": "sprechen", "preposition": "über", "case": "Akk", "translation": "falar sobre"},
    {"id": "v25", "verb": "diskutieren", "preposition": "über", "case": "Akk", "translation": "discutir sobre"},
    {"id": "v26", "verb": "sich wundern", "preposition": "über", "case": "Akk", "translation": "surpreender-se com"},
    {"id": "v27", "verb": "sich beschweren", "preposition": "über", "case": "Akk", "translation": "reclamar de"},
    {"id": "v28", "verb": "sich ärgern", "preposition": "über", "case": "Akk", "translation": "ficar irritado com"},
    {"id": "v29", "verb": "denken", "preposition": "über", "case": "Akk", "translation": "refletir sobre"},
    {"id": "v30", "verb": "abhängen", "preposition": "von", "case": "Dat", "translation": "depender de"},
    {"id": "v31", "verb": "erzählen", "preposition": "von", "case": "Dat", "translation": "contar sobre"},
    {"id": "v32", "verb": "träumen", "preposition": "von", "case": "Dat", "translation": "sonhar com"},
    {"id": "v33", "verb": "profitieren", "preposition": "von", "case": "Dat", "translation": "se beneficiar de"},
    {"id": "v34", "verb": "wissen", "preposition": "von", "case": "Dat", "translation": "saber sobre"},
    {"id": "v35", "verb": "sprechen", "preposition": "von", "case": "Dat", "translation": "falar de (referência geral)"},
    {"id": "v36", "verb": "Angst haben", "preposition": "vor", "case": "Dat", "translation": "ter medo de"},
    {"id": "v37", "verb": "schützen", "preposition": "vor", "case": "Dat", "translation": "proteger de"},
    {"id": "v38", "verb": "warnen", "preposition": "vor", "case": "Dat", "translation": "avisar / alertar sobre"},
    {"id": "v39", "verb": "passen", "preposition": "zu", "case": "Dat", "translation": "combinar com"},
    {"id": "v40", "verb": "gratulieren", "preposition": "zu", "case": "Dat", "translation": "parabenizar por"},
    {"id": "v41", "verb": "führen", "preposition": "zu", "case": "Dat", "translation": "levar a"},
    {"id": "v42", "verb": "einladen", "preposition": "zu", "case": "Dat", "translation": "convidar para"},
    {"id": "v43", "verb": "gehören", "preposition": "zu", "case": "Dat", "translation": "pertencer a"},
    {"id": "v44", "verb": "teilnehmen", "preposition": "an", "case": "Dat", "translation": "participar de"},
    {"id": "v45", "verb": "arbeiten", "preposition": "an", "case": "Dat", "translation": "trabalhar em (algo abstrato)"},
    {"id": "v46", "verb": "sterben", "preposition": "an", "case": "Dat", "translation": "morrer de"},
    {"id": "v47", "verb": "leiden", "preposition": "an", "case": "Dat", "translation": "sofrer de (doença)"},
    {"id": "v48", "verb": "zweifeln", "preposition": "an", "case": "Dat", "translation": "duvidar de"},
    {"id": "v49", "verb": "sich beschäftigen", "preposition": "mit", "case": "Dat", "translation": "ocupar-se com / lidar com"},
    {"id": "v50", "verb": "anfangen", "preposition": "mit", "case": "Dat", "translation": "começar com"},
    {"id": "v51", "verb": "aufhören", "preposition": "mit", "case": "Dat", "translation": "parar com"}
]


# --- Distractor Pools (Dynamically generated from new data) ---
PREPOSITION_DISTRACTORS = list(set([v["preposition"] for v in VERB_DATA]))
CASE_DISTRACTORS = ["Acusativo (Akk)", "Dativo (Dat)", "Genitivo (Gen)"]
TRANSLATION_DISTRACTORS = list(set([v["translation"] for v in VERB_DATA]))

# --- Helper Functions ---

def get_verb_by_id(verb_id):
    """Fetches the full verb dictionary given its ID."""
    for verb in VERB_DATA:
        if verb["id"] == verb_id:
            return verb
    return None

# --- Helper function to safely convert list to JSON string ---
def to_json(data):
    """Safely converts Python list to JSON string for DB."""
    return json.dumps(data or [])

# --- Helper function to safely load JSON string from DB ---
def from_json(data):
    """Safely loads JSON string from DB into Python list."""
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return []
    return []


def initialize_global_state():
    """Initializes session state variables that are not user-specific."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.page = "login"
        st.session_state.current_user = None
        st.session_state.user_data_cache = None 
        
        # --- NEW: Set locale to Portuguese for weekdays ---
        try:
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        except locale.Error:
            try:
                locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil.1252') # Windows
            except locale.Error:
                locale.setlocale(locale.LC_TIME, '') # System default
        
        # --- NEW: Logical Verb Order (Grouped by Preposition and Meaning) ---
        LOGICAL_VERB_ORDER = [
            # Grupo 1: Foco/Emoção em Algo (Akk - an)
            "v1", "v2", "v3",
            # Grupo 2: Espera/Reação a Algo (Akk - auf)
            "v4", "v6", "v7", "v8", "v9", "v10", "v11",
            # Grupo 3: Motivação/Troca (Akk - für)
            "v12", "v13", "v14", "v15", "v16", "v17", "v18",
            # Grupo 4: Tópico/Assunto (Akk - über)
            "v5", "v23", "v24", "v25", "v26", "v27", "v28", "v29",
            # Grupo 5: Competição/Cuidado (Akk - um)
            "v19", "v20", "v21", "v22",
            # Grupo 6: Origem/Fonte de (Dat - von)
            "v30", "v31", "v32", "v33", "v34", "v35",
            # Grupo 7: Reação/Proteção de (Dat - vor)
            "v36", "v37", "v38",
            # Grupo 8: Relação/Destino (Dat - zu)
            "v39", "v40", "v41", "v42", "v43",
            # Grupo 9: Estado/Condição (Dat - an)
            "v44", "v45", "v46", "v47", "v48",
            # Grupo 10: Interação/Ferramenta (Dat - mit)
            "v49", "v50", "v51"
        ]
        
        if len(LOGICAL_VERB_ORDER) != len(VERB_DATA):
            st.error("Erro na lógica de ordenação: Nem todos os verbos foram incluídos.")
        
        st.session_state.all_verbs_ordered_ids = LOGICAL_VERB_ORDER
        
        # --- NEW: Add connection to session state ---
        st.session_state.db_conn = supabase

# --- NEW DB FUNCTION ---
def create_new_user_in_db(username, conn):
    """Creates a new user entry in the Supabase database."""
    all_ids = st.session_state.all_verbs_ordered_ids.copy()
    
    # Create initial verb stats dict
    verb_stats_init = {
        verb_id: {
            "streak": 0, "errors": 0, "preposition_errors": 0,
            "translation_errors": 0, "case_errors": 0
        } for verb_id in all_ids
    }
    
    # Add first batch to learning pool
    learning_pool_ids = []
    unseen_verb_ids = all_ids.copy() # Start with all
    for _ in range(NEW_VERB_BATCH_SIZE):
        if unseen_verb_ids:
            learning_pool_ids.append(unseen_verb_ids.pop(0))
    
    try:
        # Insert into users table
        conn.table("users").insert({
            "username": username,
            "unseen_verb_ids": to_json(unseen_verb_ids),
            "learning_pool_ids": to_json(learning_pool_ids),
            "learned_pool_ids": to_json([])
        }).execute()
        
        # Batch insert into verb_stats
        stats_data_to_insert = []
        for verb_id, stats in verb_stats_init.items():
            stats_data_to_insert.append({
                "username": username, 
                "verb_id": verb_id, 
                "streak": stats["streak"], 
                "errors": stats["errors"],
                "preposition_errors": stats["preposition_errors"], 
                "translation_errors": stats["translation_errors"], 
                "case_errors": stats["case_errors"]
            })
        
        conn.table("verb_stats").insert(stats_data_to_insert).execute()
        
    except Exception as e:
        st.error(f"Erro ao criar novo usuário no DB: {e}")

# --- NEW DB FUNCTION ---
def get_user_data():
    """Helper to get the data for the currently logged-in user from the cache."""
    return st.session_state.user_data_cache

# --- NEW DB FUNCTION ---
def save_user_data():
    """Saves the current user's data cache to the Supabase database."""
    user_data = st.session_state.user_data_cache
    username = st.session_state.current_user
    conn = st.session_state.db_conn
    
    if not user_data or not username or not conn:
        st.error("Erro: Não foi possível salvar. Sessão inválida.")
        return

    try:
        # 1. Update the 'users' table (the verb pools)
        conn.table("users").update({
            "unseen_verb_ids": to_json(user_data["unseen_verb_ids"]),
            "learning_pool_ids": to_json(user_data["learning_pool_ids"]),
            "learned_pool_ids": to_json(user_data["learned_pool_ids"])
        }).eq("username", username).execute()
        
        # 2. Update the 'verb_stats' table (UPSERT)
        stats_data_to_upsert = []
        for verb_id, stats in user_data["verb_stats"].items():
            stats_data_to_upsert.append({
                "username": username,
                "verb_id": verb_id,
                "streak": stats["streak"], 
                "errors": stats["errors"],
                "preposition_errors": stats["preposition_errors"], 
                "translation_errors": stats["translation_errors"], 
                "case_errors": stats["case_errors"]
            })
        
        conn.table("verb_stats").upsert(stats_data_to_upsert).execute()
        
        # 3. Add the *newest* history entry to 'daily_stats_history'
        if user_data.get("new_history_entry_to_save"):
            latest_entry = user_data["new_history_entry_to_save"]
            
            # Prepara a entrada para o Supabase (sem o ID, pois é SERIAL)
            entry_to_insert = {
                "username": username,
                "date": latest_entry["date"],
                "correct": latest_entry["correct"],
                "wrong": latest_entry["wrong"],
                "total": latest_entry["total"],
                "missed_verbs": to_json(latest_entry["missed_verbs"])
            }
            
            conn.table("daily_stats_history").insert(entry_to_insert).execute()
            
            # Reseta o flag
            user_data["new_history_entry_to_save"] = None
            
    except Exception as e:
        st.error(f"Erro ao salvar progresso: {e}")


def add_new_verbs_to_pool(user_data, num_to_add=NEW_VERB_BATCH_SIZE):
    """Adds a batch of new verbs from the unseen pile to the user's learning pool."""
    for _ in range(num_to_add):
        if user_data["unseen_verb_ids"]:
            new_verb_id = user_data["unseen_verb_ids"].pop(0) 
            user_data["learning_pool_ids"].append(new_verb_id)

def get_weighted_verbs(id_list, k, user_data):
    """Helper function to select verbs, weighted by their error count."""
    if not id_list:
        return []
    
    weights = [user_data["verb_stats"][vid]["errors"] + 1 for vid in id_list]
    chosen_verbs = random.choices(id_list, weights=weights, k=min(len(id_list), k))
    return list(set(chosen_verbs))


def generate_quiz_questions():
    """
    Generates the quiz session based on the new logic:
    - Day 1: 3 new verbs (9 questions total)
    - Day 2+: 3 new verbs (9 Qs) + 3 review verbs (3 Qs) [SPACED REPETITION]
    """
    user_data = get_user_data()
    if not user_data:
        return

    questions = []
    
    is_first_session = (len(user_data["daily_stats_history"]) == 0)
    
    # Ensure the learning pool has verbs
    if not user_data["learning_pool_ids"] and user_data["unseen_verb_ids"]:
        add_new_verbs_to_pool(user_data, num_to_add=NEW_VERB_BATCH_SIZE)
        
    learning_ids = user_data["learning_pool_ids"]
    learned_ids = user_data["learned_pool_ids"]
    
    # --- Part 1: Select "New" Verbs (Standard 3 questions) ---
    new_verbs_set = set()
    
    new_verbs_list_ordered = []
    
    if learning_ids:
        new_verbs_list_ordered = learning_ids[:min(len(learning_ids), NEW_VERBS_PER_SESSION)]
    
    remaining_new_slots = NEW_VERBS_PER_SESSION - len(new_verbs_list_ordered)
    if remaining_new_slots > 0 and user_data["unseen_verb_ids"]:
        add_new_verbs_to_pool(user_data, num_to_add=remaining_new_slots)
        
        learning_ids = user_data["learning_pool_ids"] 
        new_verbs_list_ordered = learning_ids[:min(len(learning_ids), NEW_VERBS_PER_SESSION)]
        
    new_verbs_set = set(new_verbs_list_ordered)
    
    learning_questions = []
    for verb_id in new_verbs_list_ordered: 
        verb = get_verb_by_id(verb_id)
        if not verb: continue 
        learning_questions.append(create_question(verb, "preposition"))
        learning_questions.append(create_question(verb, "case"))
        learning_questions.append(create_question(verb, "translation"))
        
    # --- Part 2: Select "Review" Verbs (SPACED REPETITION LOGIC) ---
    
    review_questions = []
    
    if is_first_session:
        questions = learning_questions
    else:
        verbs_to_review_set = set()
        history = user_data["daily_stats_history"]
        
        # 1. Get verb from 1 day ago (yesterday)
        if len(history) >= 1:
            verbs_missed_yesterday = history[-1].get("missed_verbs", [])
            if verbs_missed_yesterday:
                available = list(set(verbs_missed_yesterday) - new_verbs_set)
                if available:
                    verbs_to_review_set.add(random.choice(available))

        # 2. Get verb from 2 days ago
        if len(history) >= 2:
            verbs_missed_day_before = history[-2].get("missed_verbs", [])
            if verbs_missed_day_before:
                available = list(set(verbs_missed_day_before) - new_verbs_set - verbs_to_review_set)
                if available:
                    verbs_to_review_set.add(random.choice(available))

        # 3. Get verb from 3 days ago
        if len(history) >= 3:
            verbs_missed_day_before_that = history[-3].get("missed_verbs", [])
            if verbs_missed_day_before_that:
                available = list(set(verbs_missed_day_before_that) - new_verbs_set - verbs_to_review_set)
                if available:
                    verbs_to_review_set.add(random.choice(available))

        review_batch = list(verbs_to_review_set)

        # --- FALLBACK: Fill remaining slots ---
        num_needed = REVIEW_VERBS_PER_SESSION - len(review_batch)
        if num_needed > 0:
            
            fallback_pool_ids = list(
                (set(learned_ids) | set(learning_ids)) - new_verbs_set - set(review_batch)
            )
            
            if len(fallback_pool_ids) < num_needed:
                all_verb_ids = [v['id'] for v in VERB_DATA]
                fallback_pool_ids = list(
                    set(all_verb_ids) - new_verbs_set - set(review_batch)
                )

            fallback_selection = get_weighted_verbs(
                fallback_pool_ids, 
                k=num_needed,
                user_data=user_data
            )
            review_batch.extend(fallback_selection)
        
        num_needed_final = REVIEW_VERBS_PER_SESSION - len(review_batch)
        if num_needed_final > 0:
             all_verb_ids = [v['id'] for v in VERB_DATA]
             final_fallback_pool = list(
                 set(all_verb_ids) - new_verbs_set - set(review_batch)
             )
             if final_fallback_pool: 
                review_batch.extend(random.sample(final_fallback_pool, k=min(len(final_fallback_pool), num_needed_final)))

        # Create 3 review questions
        for verb_id in review_batch[:REVIEW_VERBS_PER_SESSION]: 
            verb = get_verb_by_id(verb_id)
            if not verb: continue
            review_questions.append(create_mega_review_question(verb))

        questions = learning_questions + review_questions

    # Store the generated quiz in the user's data (cache)
    user_data["current_quiz_session"] = {
        "questions": questions,
        "current_q_index": 0,
        "correct_count": 0,
        "wrong_count": 0,
        "num_questions": len(questions), 
        "verbs_missed": set() 
    }
    # Move to the pre-quiz review page
    st.session_state.page = "pre_quiz"

def create_question(verb, q_type):
    """Creates a *standard* (3-option) question object."""
    question = {"verb_id": verb["id"], "q_type": q_type, "verb": verb, "is_mega_review": False}
    
    if q_type == "translation":
        question["prompt"] = f"Qual o significado de: **{verb['verb']} {verb['preposition']}**?"
        correct = verb["translation"]
        distractors = random.sample([t for t in TRANSLATION_DISTRACTORS if t != correct], 2)
        options = distractors + [correct]
        
    elif q_type == "preposition":
        question["prompt"] = f"Complete a frase: **{verb['verb']} \_\_\_ + {verb['case']}**"
        correct = verb["preposition"]
        distractors = random.sample([p for p in PREPOSITION_DISTRACTORS if p != correct], 2)
        options = distractors + [correct]
        
    elif q_type == "case":
        question["prompt"] = f"Complete a frase: **{verb['verb']} {verb['preposition']} + \_\_\_**"
        correct = "Acusativo (Akk)" if verb["case"] == "Akk" else "Dativo (Dat)"
        distractor_pool = [c for c in CASE_DISTRACTORS if c != correct]
        distractors = random.sample(distractor_pool, min(len(distractor_pool), 2))
        options = distractors + [correct]
        while len(options) < 3: options.append("...") 
        
    random.shuffle(options)
    question["options"] = options
    question["correct"] = correct
    return question

# --- This is the 10-option "Mega-Review" function ---
def create_mega_review_question(verb):
    """Creates a *review* (10-option) question object based on user spec."""
    
    question = {"verb_id": verb["id"], "q_type": "mega_review", "verb": verb, "is_mega_review": True}
    
    correct_answer = f"{verb['verb']} - {verb['preposition']} - {verb['case']}"
    question["prompt"] = f"[REVISÃO] Qual a combinação correta para o significado: **'{verb['translation']}'**?"

    options_set = set()
    options_set.add(correct_answer)
    
    wrong_case = 'Dat' if verb['case'] == 'Akk' else 'Akk'
    options_set.add(f"{verb['verb']} - {verb['preposition']} - {wrong_case}")
    
    wrong_prep = random.choice([p for p in PREPOSITION_DISTRACTORS if p != verb['preposition']])
    options_set.add(f"{verb['verb']} - {wrong_prep} - {verb['case']}")
    options_set.add(f"{verb['verb']} - {wrong_prep} - {wrong_case}")

    distractor_verbs = random.sample(
        [v for v in VERB_DATA if v['id'] != verb['id']], 
        k=min(len(VERB_DATA) - 1, 7) 
    )
    
    for v in distractor_verbs:
        if len(options_set) >= 10:
            break
        options_set.add(f"{v['verb']} - {v['preposition']} - {v['case']}")
    
    final_options = list(options_set)
    while len(final_options) < 10:
        v = random.choice(VERB_DATA)
        opt = f"{v['verb']} - {v['preposition']} - {v['case']}"
        if opt not in final_options:
            final_options.append(opt)

    if len(final_options) > 10:
        final_options.remove(correct_answer)
        final_options = random.sample(final_options, 9) + [correct_answer]

    random.shuffle(final_options)
    
    question["options"] = final_options
    question["correct"] = correct_answer
    return question


def set_current_question(index):
    """Sets the current question in the user's session state cache."""
    user_data = get_user_data()
    if not user_data or not user_data.get("current_quiz_session"):
        return

    session = user_data["current_quiz_session"]
    if index < session["num_questions"]:
        user_data["current_question"] = session["questions"][index]
        user_data["show_answer"] = False
    else:
        # End of quiz
        end_quiz_session()

def handle_answer(chosen_answer):
    """Handles the user's answer, updates stats in cache, and moves verb between pools."""
    user_data = get_user_data() # This is the cache
    if not user_data: return
        
    session = user_data["current_quiz_session"]
    q = user_data["current_question"]
    verb_id = q["verb_id"]
    
    is_correct = (chosen_answer == q["correct"])
    
    if is_correct:
        session["correct_count"] += 1
        user_data["verb_stats"][verb_id]["streak"] += 1
        
        # Check for Mastery
        if (verb_id in user_data["learning_pool_ids"] and 
            user_data["verb_stats"][verb_id]["streak"] >= MASTERY_STREAK):
            
            user_data["learning_pool_ids"].remove(verb_id)
            user_data["learned_pool_ids"].append(verb_id)
            # We no longer auto-add 1. We add 3 in order.
                
    else:
        session["wrong_count"] += 1
        user_data["verb_stats"][verb_id]["streak"] = 0 
        user_data["verb_stats"][verb_id]["errors"] += 1 
        
        session["verbs_missed"].add(verb_id)
        
        q_type = q["q_type"]
        if q_type == "preposition":
            user_data["verb_stats"][verb_id]["preposition_errors"] += 1
        elif q_type == "translation":
            user_data["verb_stats"][verb_id]["translation_errors"] += 1
        elif q_type == "case":
            user_data["verb_stats"][verb_id]["case_errors"] += 1
        elif q_type == "mega_review":
            pass 
        
        # --- FIX: Removed the "Demotion" (rebaixamento) logic ---
            
    user_data["show_answer"] = True

# --- FIX: Added defensive check ---
def next_question():
    """Moves the quiz to the next question index for the user."""
    user_data = get_user_data()
    if not user_data: return
        
    session = user_data.get("current_quiz_session") # Use .get() for safety
    
    # --- FIX: Check if the session is already over ---
    # This prevents a crash if the button is double-clicked
    if not session:
        st.session_state.page = "results" # Ensure we are on results page
        # Use a flag to prevent multiple reruns
        if not st.session_state.get('rerun_requested', False):
             st.session_state.rerun_requested = True
             st.rerun()
        return 
    # --- END FIX ---

    next_index = session["current_q_index"] + 1 
    
    if next_index < session["num_questions"]:
        session["current_q_index"] = next_index
        set_current_question(next_index)
        st.session_state.rerun_requested = False # Reset flag
    else:
        end_quiz_session()
        # Rerun to go to results page
        if not st.session_state.get('rerun_requested', False):
             st.session_state.rerun_requested = True
             st.rerun()


def end_quiz_session():
    """Finalizes the quiz, saves stats to user's history, and saves to disk."""
    user_data = get_user_data()
    if not user_data: return
        
    session = user_data.get("current_quiz_session")
    if not session: 
        st.session_state.page = "home"
        return
    
    # Save stats to user's history (in cache)
    today = date.today().strftime("%Y-%m-%d")
    stats = {
        "date": today,
        "correct": session["correct_count"],
        "wrong": session["wrong_count"],
        "total": session["num_questions"],
        "missed_verbs": list(session.get("verbs_missed", set()))
    }
    # --- NEW DB LOGIC ---
    # Adiciona ao histórico do cache
    user_data["daily_stats_history"].append(stats)
    # Marca este novo registro para ser salvo no DB
    user_data["new_history_entry_to_save"] = stats
    
    # --- FIX: Clear the temporary session *before* saving ---
    user_data["current_quiz_session"] = None
    user_data["current_question"] = None
    
    # --- CRITICAL: Save progress to disk (DB) ---
    save_user_data()
    
    # Go to results page
    st.session_state.page = "results"
    
# --- NEW DB FUNCTION ---
def login_user(username):
    """Logs a user in, loading from DB or creating a new user in DB."""
    conn = st.session_state.db_conn 
    
    user_data = {}
    
    try:
        # Check if user exists
        user_response = conn.table("users").select("*").eq("username", username).execute()
        
        if not user_response.data:
            # User doesn't exist, create them
            create_new_user_in_db(username, conn)
            # Re-fetch the new user row
            user_response = conn.table("users").select("*").eq("username", username).execute()
    
        user_row = user_response.data[0]
        
        # Now, load all user data into the cache
        user_data["username"] = user_row["username"]
        user_data["unseen_verb_ids"] = from_json(user_row["unseen_verb_ids"])
        user_data["learning_pool_ids"] = from_json(user_row["learning_pool_ids"])
        user_data["learned_pool_ids"] = from_json(user_row["learned_pool_ids"])
        
        # Load verb_stats
        stats_response = conn.table("verb_stats").select("*").eq("username", username).execute()
        verb_stats = {}
        for row in stats_response.data:
            verb_id = row["verb_id"]
            verb_stats[verb_id] = {
                "streak": row["streak"], 
                "errors": row["errors"], 
                "preposition_errors": row["preposition_errors"],
                "translation_errors": row["translation_errors"], 
                "case_errors": row["case_errors"]
            }
        user_data["verb_stats"] = verb_stats
        
        # Load daily_stats_history
        history_response = conn.table("daily_stats_history").select("*").eq("username", username).order("id", desc=False).execute()
        daily_stats_history = []
        for row in history_response.data:
            daily_stats_history.append({
                "date": row["date"], 
                "correct": row["correct"], 
                "wrong": row["wrong"], 
                "total": row["total"],
                "missed_verbs": from_json(row["missed_verbs"])
            })
        user_data["daily_stats_history"] = daily_stats_history

        st.session_state.user_data_cache = user_data
        st.session_state.current_user = username
        st.session_state.page = "home"
        
    except Exception as e:
        st.error(f"Erro de conexão com o banco de dados: {e}")
        st.error("Verifique suas credenciais no .streamlit/secrets.toml e recarregue a página.")
        st.stop()


def logout_user():
    """Logs the current user out and returns to the login screen."""
    st.session_state.current_user = None
    st.session_state.user_data_cache = None
    st.session_state.page = "login"

# --- NEW DB FUNCTION ---
def delete_user(username):
    """Deletes a user's data from the Supabase database."""
    conn = st.session_state.db_conn
    if username:
        try:
            # ON DELETE CASCADE will handle other tables
            conn.table("users").delete().eq("username", username).execute()
            st.success(f"Usuário '{username}' deletado com sucesso.")
            st.session_state.login_selectbox = "Selecione um usuário..."
        except Exception as e:
            st.error(f"Erro ao deletar usuário: {e}")


def quit_quiz():
    """Quits the current quiz without saving and returns to home."""
    user_data = get_user_data()
    if user_data:
        user_data["current_quiz_session"] = None
        user_data["current_question"] = None
        user_data["show_answer"] = False
    st.session_state.page = "home"

# --- UI Rendering Functions ---

# --- NEW DB FUNCTION ---
def render_login_page():
    """Renders the login/user creation screen."""
    st.title("🧠 Verbos com Preposição")
    st.subheader("Bem-vindo!")
    
    st.info("Seu progresso será salvo na nuvem.")
    
    conn = st.session_state.db_conn # Get connection
    
    # Get user list from DB
    try:
        response = conn.table("users").select("username").order("username", desc=False).execute()
        existing_users = [row["username"] for row in response.data]
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        st.error("Verifique se suas chaves (secrets) estão corretas e recarregue a página.")
        st.stop()
    
    options = ["Selecione um usuário..."] + existing_users
    
    col1, col2 = st.columns(2)
    
    with col1:
        selected_user = st.selectbox(
            "Carregar progresso:", 
            options, 
            key="login_selectbox"
        )
        
        new_user = st.text_input(
            "Ou crie um novo usuário:",
            key="login_username"
        )
        
        if st.button("Entrar", type="primary", use_container_width=True):
            username_to_login = None
            
            if selected_user != "Selecione um usuário...":
                username_to_login = selected_user
            elif new_user:
                if new_user in existing_users:
                    st.error("Este usuário já existe. Selecione-o na lista.")
                    return
                if not new_user.isalnum():
                        st.error("Nome de usuário deve conter apenas letras e números.")
                        return
                username_to_login = new_user
            
            if username_to_login:
                login_user(username_to_login)
                st.rerun()
            else:
                st.error("Por favor, selecione um usuário ou crie um novo.")

    with col2:
        # --- NEW: Delete User Section ---
        if selected_user != "Selecione um usuário...":
            with st.expander("Deletar Usuário Selecionado"):
                st.warning(f"Isso irá deletar permanentemente todo o progresso do usuário **{selected_user}**.")
                confirm_delete = st.checkbox("Sim, tenho certeza que quero deletar este usuário.", key="delete_confirm")
                
                if st.button("Deletar Usuário", type="secondary", disabled=not confirm_delete, use_container_width=True):
                    delete_user(selected_user)
                    st.rerun() # Rerun to refresh the user list in the selectbox

def render_sidebar():
    """Renders the sidebar with user info and logout button."""
    if st.session_state.current_user:
        st.sidebar.title(f"Olá, {st.session_state.current_user}!")
        st.sidebar.button("Sair (Logout)", on_click=logout_user)
        
        # Add navigation
        st.sidebar.divider()
        if st.session_state.page != "home":
                st.sidebar.button("Início (Roadmap) 🚀", on_click=lambda: st.session_state.update(page="home"))
        if st.session_state.page != "report":
            st.sidebar.button("Relatório de Desempenho 📊", on_click=lambda: st.session_state.update(page="report"))

        # Add quit button in sidebar if in quiz
        if st.session_state.page == "quiz" or st.session_state.page == "pre_quiz":
            st.sidebar.divider()
            st.sidebar.button("Sair do Treino (Sem Salvar)", on_click=quit_quiz, type="secondary")

def render_home_page():
    """Renders the main dashboard/roadmap page for the logged-in user."""
    user_data = get_user_data()
    if not user_data:
        st.error("Erro ao carregar dados do usuário.")
        return

    render_sidebar()
    st.title("🚀 Meu Roadmap de Verbos em Alemão")
    st.divider()
    
    total_verbs = len(VERB_DATA)
    learned_count = len(user_data["learned_pool_ids"])
    learning_count = len(user_data["learning_pool_ids"])
    unseen_count = len(user_data["unseen_verb_ids"])
    
    st.subheader("Progresso Total")
    
    # --- NEW: Streak Calculation ---
    study_dates = set(entry["date"] for entry in user_data["daily_stats_history"])
    today = date.today()
    current_streak = 0
    check_date = today
    
    # If today is not in study_dates, start checking from yesterday
    if today.strftime("%Y-%m-%d") not in study_dates:
        check_date = today - timedelta(days=1)
        
    # Loop backwards to count consecutive days
    while check_date.strftime("%Y-%m-%d") in study_dates:
        current_streak += 1
        check_date -= timedelta(days=1)
    # --- END: Streak Calculation ---

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Verbos Aprendidos", f"{learned_count} / {total_verbs}")
    col2.metric("Em Aprendizado", f"{learning_count}")
    col3.metric("Não Vistos", f"{unseen_count}")
    col4.metric("Sequência Atual", f"🔥 {current_streak} Dias") # <-- NEW METRIC
    
    if total_verbs > 0:
        progress_percent = learned_count / total_verbs
        st.progress(progress_percent, text=f"{progress_percent:.0%} Dominado")
    
    st.divider()
    
    # --- NEW: 7-Day Streak Calendar ---
    st.subheader("🔥 Sequência (Últimos 7 Dias)")
    cols = st.columns(7)
    days_to_show = 7
    # Create list of dates from 6 days ago to today
    dates_list = [(today - timedelta(days=i)) for i in range(days_to_show - 1, -1, -1)] 

    for i, day in enumerate(dates_list):
        day_str = day.strftime("%Y-%m-%d")
        weekday_str = day.strftime("%a").capitalize().replace('.', '') # "Seg." -> "Seg"
        day_num_str = day.strftime("%d")
        
        with cols[i]:
            if day_str in study_dates:
                st.metric(label=f"{weekday_str} {day_num_str}", value="✅", help="Você treinou neste dia!")
            else:
                if day == today:
                    st.metric(label=f"{weekday_str} {day_num_str}", value="...", help="Treino de hoje pendente.")
                else:
                    st.metric(label=f"{weekday_str} {day_num_str}", value="❌", help="Você faltou neste dia.")
    # --- END: 7-Day Streak Calendar ---

    st.divider()
    
    # --- Dynamic Button Text ---
    is_first_session = (len(user_data["daily_stats_history"]) == 0)
    
    if is_first_session:
        button_text = f"Iniciar Treino do Dia (9 Questões)"
    else:
        # "FIXO" LOGIC
        button_text = f"Iniciar Treino do Dia (12 Questões)"
        
    # Check if there are verbs left to learn or review
    if learning_count > 0 or unseen_count > 0 or learned_count > 0:
        st.button(
            button_text,
            on_click=generate_quiz_questions, 
            type="primary",
            use_container_width=True
        )
    else:
        st.success("🎉 Parabéns! Você dominou todos os verbos do baralho!")

    # (Expander with memorization tips remains the same)
    with st.expander("Ver Táticas de Memorização Usadas"):
        st.markdown("""
        ### 1) Agrupe por "Emoção" (Lógica)
        As preposições seguem um sentido.
        
        **Quando algo envolve sentimento / foco / direção, quase sempre é Akkusativ:**
        - `sich freuen auf` (ansiar por)
        - `sich erinnern an` (lembrar de)
        - `warten auf` (esperar por)
        - `denken an` (pensar em)
        - `sich interessieren für` (interessar-se por)
        
        **📌 Dica mental: Se mexe com você → Akkusativ.**

        **Quando algo é origem / fundo / relação / estabilidade, geralmente é Dativ:**
        - `träumen von` (sonhar com - *origem do sonho*)
        - `erzählen von` (contar sobre - *origem da história*)
        - `Angst haben vor` (ter medo de - *reação a algo estável*)
        - `teilnehmen an` (participar de - *estar em um local*)
        - `passen zu` (combinar com - *relação*)

        **📌 Dica mental: Coisas calmas, estáveis → Dativ.**

        ### 2) Faça frases com sua vida real
        Nada de exemplo escolar. Quanto mais pessoal, mais a memória fixa.
        
        | Verbo | Sua frase (Exemplo) |
        |---|---|
        | `sich freuen auf` | `Ich freue mich auf das Wochenende.` |
        | `sich interessieren für` | `Ich interessiere mich für Daten & ML.` |
        | `warten auf` | `Ich warte auf den Kaffee.` |
        
        ### 3) Treino de Reconhecimento Ativo (Este App!)
        Este app força seu cérebro a *recuperar* a informação (Active Recall), que é a forma mais poderosa de estudo. A seleção de verbos é ponderada: **você revisa mais o que você mais erra.**
        """)
    
    st.divider()
    
    st.subheader("Últimas Sessões")
    if not user_data["daily_stats_history"]:
        st.caption("Nenhum treino concluído ainda. Vamos começar!")
    else:
        history_df = pd.DataFrame(user_data["daily_stats_history"])
        # Calculate % Correct, handling division by zero
        history_df["% Certo"] = history_df.apply(
            lambda row: (row["correct"] / row["total"] * 100) if row["total"] > 0 else 0, 
            axis=1
        ).map("{:.0f}%".format)
        
        history_df.rename(columns={
            "date": "Data", "correct": "Corretas", "wrong": "Erradas", "total": "Total"
        }, inplace=True)
        
        st.dataframe(
            history_df[["Data", "Corretas", "Erradas", "Total", "% Certo"]].tail(5),
            use_container_width=True,
            hide_index=True
        )

def render_pre_quiz_page():
    """Renders the new pre-quiz review screen."""
    user_data = get_user_data()
    render_sidebar()
    
    st.title("🎯 Preparação para o Treino")
    
    session_data = user_data.get("current_quiz_session")
    
    if not user_data or not session_data:
        st.error("Nenhuma sessão de quiz encontrada.")
        st.button("Voltar", on_click=lambda: st.session_state.update(page="home"))
        return

    questions = session_data["questions"]
    if not questions:
        st.error("Nenhum verbo selecionado para esta sessão. Tente adicionar mais verbos.")
        st.button("Voltar", on_click=lambda: st.session_state.update(page="home"))
        return
        
    # --- FIX: Reverted to show ALL verbs in the quiz (new + review) ---
    verb_ids_in_quiz = list(dict.fromkeys([q["verb_id"] for q in questions])) # Keep order
    verbs_to_review = [get_verb_by_id(vid) for vid in verb_ids_in_quiz if get_verb_by_id(vid)]
    
    num_verbs_found = len(verbs_to_review)
    
    st.subheader(f"Estes são os {num_verbs_found} verbos que aparecerão no treino de hoje:")
    st.caption("Reveja-os e clique em 'Começar!' quando estiver pronto.")
    st.divider()
    
    if not verbs_to_review:
        st.error("Nenhum verbo encontrado para esta sessão.")
        st.button("Voltar", on_click=lambda: st.session_state.update(page="home"))
        return
    
    # Display the verbs and their translations only
    # Use 3 columns, which works well for 3 (Day 1) or 6 (Day 2+) verbs
    cols = st.columns(3)
    col_index = 0
    for verb in verbs_to_review:
        cols[col_index].info(f"**{verb['verb']} {verb['preposition']} ({verb['case']})**\n- {verb['translation']}")
        col_index = (col_index + 1) % 3
        
    st.divider()
    if st.button("Começar o Questionário! ➔", type="primary", use_container_width=True):
        st.session_state.page = "quiz"
        # Set the first question
        set_current_question(0)
        st.rerun()

def render_quiz_page():
    """Renders the active quiz interface."""
    user_data = get_user_data()
    render_sidebar()

    if not user_data or not user_data.get("current_question"):
        st.warning("Erro: Nenhuma pergunta carregada.")
        st.button("Voltar ao Início", on_click=lambda: st.session_state.update(page="home"))
        return
        
    q = user_data["current_question"]
    session = user_data["current_quiz_session"]
    q_index = session["current_q_index"]
    total_q = session["num_questions"]
    
    st.title("🧠 Treino: Verbos com Preposição")
    
    if total_q > 0:
        st.progress((q_index + 1) / total_q, text=f"Pergunta {q_index + 1} de {total_q}")
    
    st.subheader(q["prompt"])
    st.divider()
    
    # --- Logic for 3-option vs 10-option questions ---
    radio_options = q["options"]
    if q["is_mega_review"]:
        # For 10 options, display in 2 columns to save space
        cols = st.columns(2)
        chosen = st.radio(
            "Selecione a resposta correta:",
            radio_options,
            key=f"q_{st.session_state.current_user}_{q_index}",
            disabled=user_data["show_answer"],
            label_visibility="collapsed",
            horizontal=False # This forces vertical layout *within* columns
        )
    else:
        # Standard 3-option layout
        chosen = st.radio(
            "Selecione a resposta correta:",
            radio_options,
            key=f"q_{st.session_state.current_user}_{q_index}",
            disabled=user_data["show_answer"],
            horizontal=True
        )
    
    st.divider()

    if user_data["show_answer"]:
        is_correct = (chosen == q["correct"])
        if is_correct:
            st.success(f"✅ Correto! **{q['correct']}**")
        else:
            st.error(f"❌ Errado. A resposta era: **{q['correct']}**")
        
        verb = q["verb"]
        st.info(f"**Verbo:** {verb['verb']} {verb['preposition']} ({verb['case']}) - {verb['translation']}")
        
        st.button("Próxima Pergunta ➔", on_click=next_question, use_container_width=True, type="primary")

    else:
        st.button(
            "Enviar Resposta", 
            on_click=handle_answer, 
            args=(chosen,), 
            use_container_width=True,
            type="primary"
        )

def render_results_page():
    """Renders the page shown after a quiz session."""
    user_data = get_user_data()
    render_sidebar()
    
    if not user_data or not user_data["daily_stats_history"]:
        st.error("Sessão não encontrada ou histórico vazio.")
        st.button("Voltar", on_click=lambda: st.session_state.update(page="home"))
        return
    
    session_stats = user_data["daily_stats_history"][-1]
    correct = session_stats["correct"]
    wrong = session_stats["wrong"]
    total = session_stats["total"]
    
    st.title("📊 Resultados do Treino")
    st.balloons()
    
    st.subheader("Resumo do dia:")
    
    col1, col2 = st.columns(2)
    col1.metric("Corretas", f"✅ {correct}")
    col2.metric("Erradas", f"❌ {wrong}")
    
    if total > 0:
        percent = (correct / total) * 100
        st.progress(percent / 100, text=f"{percent:.0f}% de acerto")

    st.divider()
    st.button(
        "Ver Relatório Detalhado 📊", 
        on_click=lambda: st.session_state.update(page="report"),
        use_container_width=True,
        type="secondary"
    )
    st.button(
        "Voltar ao Início (Roadmap) 🚀", 
        on_click=lambda: st.session_state.update(page="home"),
        use_container_width=True,
        type="primary"
    )
    # The quiz session is now cleared in end_quiz_session() before saving.

# --- --------------------------------- ---
# --- INÍCIO DA NOVA PÁGINA DE RELATÓRIO ---
# --- --------------------------------- ---

def render_report_page():
    """
    Renders the new, single-page, mobile-friendly report page.
    Replaces the old tabbed layout.
    """
    user_data = get_user_data()
    if not user_data:
        st.error("Erro ao carregar dados do usuário.")
        return

    render_sidebar()
    st.title("📊 Meu Desempenho")
    st.divider()

    # --- 1. Cálculos Iniciais ---
    total_verbs = len(VERB_DATA)
    learned_count = len(user_data["learned_pool_ids"])
    learning_count = len(user_data["learning_pool_ids"])
    unseen_count = len(user_data["unseen_verb_ids"])
    stats = user_data["verb_stats"]
    
    # Cálculo de Maestria
    maestria_percent = (learned_count / total_verbs) if total_verbs > 0 else 0
    
    # Cálculo de Erros Totais
    total_prep_errors = sum(data.get("preposition_errors", 0) for data in stats.values())
    total_trans_errors = sum(data.get("translation_errors", 0) for data in stats.values())
    total_case_errors = sum(data.get("case_errors", 0) for data in stats.values())
    total_errors = total_prep_errors + total_trans_errors + total_case_errors
    
    # Cálculo de Streak (copiado do render_home_page)
    study_dates = set(entry["date"] for entry in user_data["daily_stats_history"])
    today = date.today()
    current_streak = 0
    check_date = today
    if today.strftime("%Y-%m-%d") not in study_dates:
        check_date = today - timedelta(days=1)
    while check_date.strftime("%Y-%m-%d") in study_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # --- 2. Seção de Nível Atual ---
    st.subheader("🚀 Seu Nível Atual")
    
    st.progress(maestria_percent, text=f"Nível de Maestria: {maestria_percent:.0%}")

    # Métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("Dias de Treino", f"{len(user_data['daily_stats_history'])}")
    col2.metric("Sequência Atual", f"🔥 {current_streak} Dias")
    col3.metric("Total de Erros", f"❌ {total_errors}")

    # Gráfico de Donut (Visão Global)
    chart_data = pd.DataFrame([
        {"categoria": "Aprendidos", "valor": learned_count},
        {"categoria": "Em Aprendizado", "valor": learning_count},
        {"categoria": "Não Vistos", "valor": unseen_count},
    ])
    
    color_scale = alt.Scale(
        domain=["Aprendidos", "Em Aprendizado", "Não Vistos"],
        range=[heineken_colors["dark_green"], heineken_colors["lime_green"], heineken_colors["medium_gray"]]
    )
    
    base = alt.Chart(chart_data).encode(
        theta=alt.Theta("valor:Q", stack=True)
    )
    
    donut = base.mark_arc(outerRadius=120, innerRadius=80).encode(
        color=alt.Color("categoria:N", title="Categoria", scale=color_scale),
        order=alt.Order("valor", sort="descending"),
        tooltip=["categoria", "valor"]
    )
    
    text = base.mark_text(radius=140).encode(
        text=alt.Text("valor:Q"),
        order=alt.Order("valor", sort="descending"),
        color=alt.value("black")
    )
    
    st.altair_chart(donut + text, use_container_width=True)
    
    st.divider()

    # --- 3. Seção de Evolução ---
    st.subheader("📈 Sua Evolução")
    if not user_data["daily_stats_history"]:
        st.info("Você precisa completar pelo menos uma sessão para ver sua evolução.")
    else:
        history_df = pd.DataFrame(user_data["daily_stats_history"])
        history_df['Sessão #'] = range(1, len(history_df) + 1)
        history_df["% Certo"] = history_df.apply(
            lambda row: (row["correct"] / row["total"] * 100) if row["total"] > 0 else 0, 
            axis=1
        )
        # --- FIX: Adiciona as colunas 'correct' e 'wrong' que faltavam no DF ---
        history_df['correct'] = history_df['correct'].astype(int)
        history_df['wrong'] = history_df['wrong'].astype(int)
        # --- END FIX ---
        
        base = alt.Chart(history_df).encode(
            x=alt.X('Sessão #:Q', axis=alt.Axis(title='Sessão'))
        ).properties(
            title="Performance por Sessão"
        )
        
        # --- FIX: Corrigido o tooltip para usar os nomes de coluna corretos ---
        line = base.mark_line(color=heineken_colors["dark_green"], point=True).encode(
            y=alt.Y('% Certo:Q', axis=alt.Axis(title='% Corretas'), scale=alt.Scale(domain=[0, 100])),
            tooltip=[
                alt.Tooltip('Sessão #'),
                alt.Tooltip('% Certo', format='.0f', title='% Certo'),
                alt.Tooltip('correct', title='Corretas'), # Era 'Corretas'
                alt.Tooltip('wrong', title='Erradas')     # Era 'Erradas'
            ]
        )
        # --- END FIX ---
        
        st.altair_chart(line.interactive(), use_container_width=True)
        
    st.divider()

    # --- 4. Seção de Desafios ---
    st.subheader("🎯 Seus Desafios")
    st.caption("Onde você precisa focar para melhorar.")

    # Gráfico de Top 5 Erros
    error_verbs = []
    for vid, data in stats.items():
        if data["errors"] > 0:
            verb = get_verb_by_id(vid)
            if verb:
                error_verbs.append({
                    "Verbo": f"{verb['verb']} {verb['preposition']}",
                    "Tradução": verb["translation"],
                    "Erros": data["errors"]
                })
    
    if error_verbs:
        error_df = pd.DataFrame(error_verbs).sort_values(by="Erros", ascending=False).head(5)
        
        base = alt.Chart(error_df).encode(
            y=alt.Y('Verbo:N', sort=None, title='Verbo'),
            tooltip=['Verbo', 'Tradução', 'Erros']
        ).properties(
            title="Seus 5 Verbos Mais Difíceis"
        )
        
        bars = base.mark_bar(color=heineken_colors["red"]).encode(
            x=alt.X('Erros:Q', axis=alt.Axis(title='Total de Erros'))
        )
        
        text = bars.mark_text(
            align='left',
            baseline='middle',
            dx=3, # Desloca o texto 3 pixels à direita da barra
            color='black'
        ).encode(
            text=alt.Text('Erros:Q')
        )
        
        st.altair_chart(bars + text, use_container_width=True)

    else:
        st.info("Você ainda não errou nenhum verbo! 🎉")
    
    # Gráfico de Tipos de Erro
    if total_errors > 0:
        chart_data = pd.DataFrame([
            {"Tipo": "Preposição", "Total de Erros": total_prep_errors},
            {"Tipo": "Significado", "Total de Erros": total_trans_errors},
            {"Tipo": "Caso (Akk/Dat)", "Total de Erros": total_case_errors},
        ])
        
        bar_chart = alt.Chart(chart_data).mark_bar(color=heineken_colors["dark_green"]).encode(
            x=alt.X("Tipo:N", sort=None, title=None),
            y=alt.Y("Total de Erros:Q"),
            tooltip=["Tipo", "Total de Erros"]
        ).properties(
            title="Total de Erros por Tipo de Pergunta"
        )
        st.altair_chart(bar_chart, use_container_width=True)

    st.divider()

    # --- 5. Seção de Histórico Detalhado (Expander) ---
    st.subheader("📚 Histórico Completo de Sessões")
    with st.expander("Clique para ver todos os seus treinos"):
        if not user_data["daily_stats_history"]:
            st.info("Nenhum treino concluído ainda.")
        else:
            # Re-cria o history_df, mas desta vez com a coluna "Verbos Errados"
            history_df = pd.DataFrame(user_data["daily_stats_history"])
            history_df['Sessão #'] = range(1, len(history_df) + 1)
            history_df["% Certo"] = history_df.apply(
                lambda row: (row["correct"] / row["total"] * 100) if row["total"] > 0 else 0, 
                axis=1
            ).map("{:.0f}%".format)
            
            def format_missed_verbs(id_list):
                if not id_list or not isinstance(id_list, list):
                    return ""
                names = []
                for vid in id_list:
                    verb = get_verb_by_id(vid)
                    if verb:
                        names.append(f"{verb['verb']} {verb['preposition']}")
                return " - ".join(names)

            history_df["missed_verbs"] = history_df["missed_verbs"].apply(
                lambda x: from_json(x) # Use from_json helper
            )
            history_df["Verbos Errados"] = history_df["missed_verbs"].apply(format_missed_verbs)
            
            st.dataframe(
                history_df.rename(columns={
                    "date": "Data", "correct": "Corretas", "wrong": "Erradas", "total": "Total"
                })[
                    ["Sessão #", "Data", "Corretas", "Erradas", "Total", "% Certo", "Verbos Errados"]
                ].sort_values(by="Sessão #", ascending=False),
                use_container_width=True,
                hide_index=True
            )

# --- --------------------------------- ---
# --- FIM DA NOVA PÁGINA DE RELATÓRIO ---
# --- --------------------------------- ---


# --- Main App Logic ---

# Initialize global state once
initialize_global_state()

# Page router
if st.session_state.page == "login":
    render_login_page()
elif st.session_state.current_user:
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "report":
        render_report_page() # <-- CHAMA A NOVA FUNÇÃO
    elif st.session_state.page == "pre_quiz":
        render_pre_quiz_page()
    elif st.session_state.page == "quiz":
        render_quiz_page()
    elif st.session_state.page == "results":
        render_results_page()
else:
    # Fallback if user is not logged in but not on login page
    st.session_state.page = "login"
    st.rerun()