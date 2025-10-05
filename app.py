"""
Flashcards Tedesco-Italiano - Versione Web
Server Flask per l'applicazione web
"""
from flask import Flask, render_template, request, jsonify, session
import sys
import os
import secrets
from pathlib import Path

# Aggiungi la directory root al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.flashcard import FlashcardCollection
from src.utils.parser import FlashcardParser
from src.utils.storage import Storage

app = Flask(__name__)

# FIX: Secret key persistente
secret_file = Path('data/secret.key')
if secret_file.exists():
    app.secret_key = secret_file.read_text()
else:
    secret_file.parent.mkdir(parents=True, exist_ok=True)
    new_secret = secrets.token_hex(32)  # 32 bytes = 256 bit
    secret_file.write_text(new_secret)
    app.secret_key = new_secret
    print("✅ Nuova secret key generata e salvata")

# Storage globale
storage = Storage()


def get_collection():
    """Ottiene la collezione di flashcards"""
    return storage.carica()


def save_collection(collection):
    """Salva la collezione"""
    return storage.salva(collection)


@app.route('/')
def index():
    """Pagina principale"""
    try:
        collection = get_collection()
        stats = collection.get_statistiche_generali()
        flashcards = list(collection)
        
        return render_template('index.html', 
                             flashcards=flashcards,
                             stats=stats)
    except Exception as e:
        print(f"❌ Errore nella pagina principale: {e}")
        return f"Errore: {e}", 500


@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    """API per ottenere tutte le flashcards"""
    try:
        collection = get_collection()
        flashcards = [
            {
                'tedesco': card.tedesco,
                'italiano': card.italiano,
                'priorita': card.priorita,
                'corrette': card.corrette,
                'sbagliate': card.sbagliate,
                'percentuale': card.percentuale_successo
            }
            for card in collection
        ]
        return jsonify(flashcards)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/flashcards/add', methods=['POST'])
def add_flashcards():
    """API per aggiungere flashcards"""
    try:
        data = request.get_json()
        testo = data.get('text', '')
        
        if not testo.strip():
            return jsonify({'error': 'Testo vuoto'}), 400
        
        nuove_cards = FlashcardParser.parse_testo(testo)
        
        if not nuove_cards:
            return jsonify({'error': 'Nessuna flashcard valida trovata'}), 400
        
        collection = get_collection()
        for card in nuove_cards:
            collection.aggiungi_flashcard(card)
        
        if save_collection(collection):
            return jsonify({
                'success': True,
                'count': len(nuove_cards),
                'message': f'Aggiunte {len(nuove_cards)} flashcard{"s" if len(nuove_cards) > 1 else ""}!'
            })
        else:
            return jsonify({'error': 'Errore nel salvataggio'}), 500
    
    except Exception as e:
        print(f"❌ Errore nell'aggiunta flashcards: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/flashcards/<int:index>/delete', methods=['DELETE'])
def delete_flashcard(index):
    """API per eliminare una flashcard"""
    try:
        collection = get_collection()
        
        if 0 <= index < len(collection):
            collection.rimuovi_flashcard(index)
            if save_collection(collection):
                return jsonify({'success': True})
            else:
                return jsonify({'error': 'Errore nel salvataggio'}), 500
        else:
            return jsonify({'error': 'Indice non valido'}), 400
    
    except Exception as e:
        print(f"❌ Errore nell'eliminazione: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/flashcards/<int:index>/toggle-priority', methods=['POST'])
def toggle_priority(index):
    """API per cambiare la priorità di una flashcard"""
    try:
        collection = get_collection()
        card = collection.get_flashcard(index)
        
        if card:
            card.priorita = not card.priorita
            if save_collection(collection):
                return jsonify({'success': True, 'priorita': card.priorita})
            else:
                return jsonify({'error': 'Errore nel salvataggio'}), 500
        else:
            return jsonify({'error': 'Flashcard non trovata'}), 404
    
    except Exception as e:
        print(f"❌ Errore nel cambio priorità: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/study/start', methods=['POST'])
def start_study():
    """API per iniziare una sessione di studio"""
    try:
        data = request.get_json()
        modalita = data.get('modalita', 'tedesco-italiano')
        
        collection = get_collection()
        
        if len(collection) == 0:
            return jsonify({'error': 'Nessuna flashcard disponibile'}), 400
        
        flashcards = collection.get_flashcards_casuali()
        
        # Salva la sessione
        session['flashcards'] = [
            {
                'tedesco': card.tedesco,
                'italiano': card.italiano,
                'priorita': card.priorita
            }
            for card in flashcards
        ]
        session['modalita'] = modalita
        session['indice'] = 0
        session['corrette'] = 0
        session['sbagliate'] = 0
        session.modified = True
        
        return jsonify({
            'success': True,
            'total': len(flashcards)
        })
    
    except Exception as e:
        print(f"❌ Errore nell'avvio studio: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/study/current', methods=['GET'])
def get_current_flashcard():
    """API per ottenere la flashcard corrente"""
    try:
        flashcards = session.get('flashcards', [])
        indice = session.get('indice', 0)
        modalita = session.get('modalita', 'tedesco-italiano')
        
        if not flashcards or indice >= len(flashcards):
            return jsonify({'completed': True})
        
        card = flashcards[indice]
        
        if modalita == 'tedesco-italiano':
            domanda = card['tedesco']
            risposta = card['italiano']
            lingua_domanda = 'de'
            lingua_risposta = 'it'
        else:
            domanda = card['italiano']
            risposta = card['tedesco']
            lingua_domanda = 'it'
            lingua_risposta = 'de'
        
        return jsonify({
            'domanda': domanda,
            'risposta': risposta,
            'priorita': card['priorita'],
            'indice': indice,
            'totale': len(flashcards),
            'corrette': session.get('corrette', 0),
            'sbagliate': session.get('sbagliate', 0),
            'lingua_domanda': lingua_domanda,
            'lingua_risposta': lingua_risposta
        })
    
    except Exception as e:
        print(f"❌ Errore nel recupero flashcard corrente: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/study/answer', methods=['POST'])
def register_answer():
    """API per registrare una risposta"""
    try:
        data = request.get_json()
        corretta = data.get('corretta', False)
        
        flashcards = session.get('flashcards', [])
        indice = session.get('indice', 0)
        
        if not flashcards or indice >= len(flashcards):
            return jsonify({'error': 'Sessione non valida'}), 400
        
        # Trova e aggiorna la flashcard nella collezione
        collection = get_collection()
        card_data = flashcards[indice]
        
        card_trovata = False
        for card in collection:
            if card.tedesco == card_data['tedesco'] and card.italiano == card_data['italiano']:
                card.registra_risposta(corretta)
                card_trovata = True
                break
        
        if card_trovata:
            save_collection(collection)
        else:
            print(f"⚠️ Attenzione: card non trovata nella collezione")
        
        # Aggiorna la sessione
        if corretta:
            session['corrette'] = session.get('corrette', 0) + 1
        else:
            session['sbagliate'] = session.get('sbagliate', 0) + 1
        
        session['indice'] = indice + 1
        session.modified = True
        
        # Controlla se è l'ultima
        if session['indice'] >= len(flashcards):
            return jsonify({
                'completed': True,
                'corrette': session['corrette'],
                'sbagliate': session['sbagliate'],
                'totale': len(flashcards)
            })
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"❌ Errore nella registrazione risposta: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/study')
def study():
    """Pagina di studio"""
    try:
        # Verifica che ci sia una sessione attiva
        if 'flashcards' not in session:
            return render_template('index.html', error='Inizia una sessione di studio dalla home'), 400
        
        return render_template('study.html')
    except Exception as e:
        print(f"❌ Errore nella pagina studio: {e}")
        return f"Errore: {e}", 500


@app.route('/stats')
def stats():
    """Pagina statistiche"""
    try:
        collection = get_collection()
        stats = collection.get_statistiche_generali()
        
        flashcards = [
            {
                'tedesco': card.tedesco,
                'italiano': card.italiano,
                'priorita': card.priorita,
                'corrette': card.corrette,
                'sbagliate': card.sbagliate,
                'totale': card.tentativi_totali,
                'percentuale': card.percentuale_successo
            }
            for card in collection
        ]
        
        # Ordina per difficoltà (più difficili prima)
        flashcards.sort(key=lambda x: (x['totale'] == 0, x['percentuale']))
        
        return render_template('stats.html', 
                             flashcards=flashcards,
                             stats=stats)
    except Exception as e:
        print(f"❌ Errore nella pagina statistiche: {e}")
        return f"Errore: {e}", 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Risorsa non trovata'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Errore interno del server'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Avvio Flashcards Tedesco-Italiano")
    print("="*60)
    print("📱 Apri il browser su: http://localhost:5003")
    print("📱 Oppure: http://127.0.0.1:5003")
    print("⌨️  Premi CTRL+C per fermare il server")
    print("="*60 + "\n")
    
    # Configurazione per sviluppo
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Avvia il server
    app.run(debug=True, host='0.0.0.0', port=5003)