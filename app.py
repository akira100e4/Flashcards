"""
Flashcards Tedesco-Italiano - Versione Web
Server Flask per l'applicazione web
"""
from flask import Flask, render_template, request, jsonify, session
import sys
import os
import secrets

# Aggiungi la directory root al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.flashcard import FlashcardCollection
from src.utils.parser import FlashcardParser
from src.utils.storage import Storage

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Storage globale
storage = Storage()


def get_collection():
    """Ottiene la collezione di flashcards"""
    return storage.carica()


def save_collection(collection):
    """Salva la collezione"""
    storage.salva(collection)


@app.route('/')
def index():
    """Pagina principale"""
    collection = get_collection()
    stats = collection.get_statistiche_generali()
    flashcards = list(collection)
    
    return render_template('index.html', 
                         flashcards=flashcards,
                         stats=stats)


@app.route('/api/flashcards', methods=['GET'])
def get_flashcards():
    """API per ottenere tutte le flashcards"""
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


@app.route('/api/flashcards/add', methods=['POST'])
def add_flashcards():
    """API per aggiungere flashcards"""
    try:
        data = request.get_json()
        testo = data.get('text', '')
        
        nuove_cards = FlashcardParser.parse_testo(testo)
        
        if not nuove_cards:
            return jsonify({'error': 'Nessuna flashcard valida trovata'}), 400
        
        collection = get_collection()
        for card in nuove_cards:
            collection.aggiungi_flashcard(card)
        
        save_collection(collection)
        
        return jsonify({
            'success': True,
            'count': len(nuove_cards),
            'message': f'Aggiunte {len(nuove_cards)} flashcards!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/flashcards/<int:index>/delete', methods=['DELETE'])
def delete_flashcard(index):
    """API per eliminare una flashcard"""
    try:
        collection = get_collection()
        
        if 0 <= index < len(collection):
            collection.rimuovi_flashcard(index)
            save_collection(collection)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Indice non valido'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/flashcards/<int:index>/toggle-priority', methods=['POST'])
def toggle_priority(index):
    """API per cambiare la priorità di una flashcard"""
    try:
        collection = get_collection()
        card = collection.get_flashcard(index)
        
        if card:
            card.priorita = not card.priorita
            save_collection(collection)
            return jsonify({'success': True, 'priorita': card.priorita})
        else:
            return jsonify({'error': 'Flashcard non trovata'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/study/start', methods=['POST'])
def start_study():
    """API per iniziare una sessione di studio"""
    try:
        data = request.get_json()
        modalita = data.get('modalita', 'tedesco-italiano')
        
        collection = get_collection()
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
        
        return jsonify({
            'success': True,
            'total': len(flashcards)
        })
    
    except Exception as e:
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
            'lingua_domanda': lingua_domanda,
            'lingua_risposta': lingua_risposta
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/study/answer', methods=['POST'])
def register_answer():
    """API per registrare una risposta"""
    try:
        data = request.get_json()
        corretta = data.get('corretta', False)
        
        flashcards = session.get('flashcards', [])
        indice = session.get('indice', 0)
        modalita = session.get('modalita', 'tedesco-italiano')
        
        if not flashcards or indice >= len(flashcards):
            return jsonify({'error': 'Sessione non valida'}), 400
        
        # Trova e aggiorna la flashcard nella collezione
        collection = get_collection()
        card_data = flashcards[indice]
        
        for card in collection:
            if card.tedesco == card_data['tedesco'] and card.italiano == card_data['italiano']:
                card.registra_risposta(corretta)
                break
        
        save_collection(collection)
        
        # Aggiorna la sessione
        if corretta:
            session['corrette'] = session.get('corrette', 0) + 1
        
        session['indice'] = indice + 1
        
        # Controlla se è l'ultima
        if session['indice'] >= len(flashcards):
            return jsonify({
                'completed': True,
                'corrette': session['corrette'],
                'totale': len(flashcards)
            })
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/study')
def study():
    """Pagina di studio"""
    return render_template('study.html')


@app.route('/stats')
def stats():
    """Pagina statistiche"""
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


if __name__ == '__main__':
    print("🚀 Avvio server Flask...")
    print("📱 Apri il browser su: http://localhost:5001")
    print("⌨️  Premi CTRL+C per fermare il server\n")
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run(debug=True, host='0.0.0.0', port=5001)