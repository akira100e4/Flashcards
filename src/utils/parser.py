"""
Modulo per il parsing del testo delle flashcards
"""
import re
from typing import List, Tuple
from src.models.flashcard import Flashcard


class FlashcardParser:
    """Parser per convertire testo formattato in flashcards"""
    
    @staticmethod
    def pulisci_linea(linea: str) -> str:
        """Rimuove bullet points, asterischi e spazi extra"""
        # Rimuove bullet points all'inizio
        linea = re.sub(r'^\s*[*\-•]\s*', '', linea)
        # Rimuove spazi multipli
        linea = re.sub(r'\s+', ' ', linea)
        return linea.strip()
    
    @staticmethod
    def ha_priorita(linea_originale: str) -> bool:
        """Verifica se la linea contiene asterischi (priorità)"""
        return '**' in linea_originale
    
    @staticmethod
    def estrai_categoria(linea: str) -> Tuple[str, str]:
        """
        Estrae la categoria se presente nel formato [Categoria]
        
        Returns:
            Tupla (categoria, linea_senza_categoria)
        """
        # Cerca pattern [Categoria] all'inizio
        match = re.match(r'^\[([^\]]+)\]\s*(.+)', linea)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return "Generale", linea
    
    @staticmethod
    def estrai_coppia(linea: str) -> Tuple[str, str, bool, str]:
        """
        Estrae la coppia tedesco-italiano da una linea
        
        Returns:
            Tupla (tedesco, italiano, ha_priorita, categoria)
        """
        linea_originale = linea
        
        # Estrae categoria
        categoria, linea = FlashcardParser.estrai_categoria(linea)
        
        linea_pulita = FlashcardParser.pulisci_linea(linea)
        
        # Rimuove gli asterischi per il parsing
        linea_pulita = linea_pulita.replace('**', '')
        
        # Cerca il separatore →
        if '→' not in linea_pulita:
            raise ValueError(f"Separatore '→' non trovato nella linea: {linea}")
        
        parti = linea_pulita.split('→')
        if len(parti) != 2:
            raise ValueError(f"Formato non valido nella linea: {linea}")
        
        tedesco = parti[0].strip()
        italiano = parti[1].strip()
        priorita = FlashcardParser.ha_priorita(linea_originale)
        
        if not tedesco or not italiano:
            raise ValueError(f"Parola tedesca o italiana vuota nella linea: {linea}")
        
        return tedesco, italiano, priorita, categoria
    
    @staticmethod
    def parse_testo(testo: str) -> List[Flashcard]:
        """
        Parse un testo con multiple flashcards
        
        Formato supportato:
        [Verbi] * **weit→ Lontano**
        [Sostantivi] * üben → esercitare
        Nachmittag → pomeriggio
        
        Returns:
            Lista di oggetti Flashcard
        """
        flashcards = []
        linee = testo.strip().split('\n')
        categoria_corrente = "Generale"
        
        for i, linea in enumerate(linee, 1):
            linea = linea.strip()
            
            # Salta linee vuote
            if not linea:
                continue
            
            # Controlla se è un'intestazione di categoria (es: "# Verbi" o "## Casa")
            if linea.startswith('#'):
                categoria_corrente = linea.lstrip('#').strip()
                continue
            
            # Salta linee che non contengono il separatore
            if '→' not in linea:
                continue
            
            try:
                tedesco, italiano, priorita, categoria = FlashcardParser.estrai_coppia(linea)
                
                # Se la categoria è "Generale" e abbiamo una categoria corrente, usa quella
                if categoria == "Generale" and categoria_corrente != "Generale":
                    categoria = categoria_corrente
                
                flashcard = Flashcard(
                    tedesco=tedesco,
                    italiano=italiano,
                    priorita=priorita,
                    categoria=categoria
                )
                flashcards.append(flashcard)
            except ValueError as e:
                print(f"Attenzione: errore alla riga {i}: {e}")
                continue
        
        return flashcards
    
    @staticmethod
    def flashcard_to_text(flashcard: Flashcard) -> str:
        """Converte una flashcard in formato testo"""
        asterischi = "**" if flashcard.priorita else ""
        categoria_str = f"[{flashcard.categoria}] " if flashcard.categoria != "Generale" else ""
        return f"{categoria_str}{asterischi}{flashcard.tedesco} → {flashcard.italiano}{asterischi}"
    
    @staticmethod
    def collezione_to_text(flashcards: List[Flashcard]) -> str:
        """Converte una lista di flashcards in testo formattato"""
        linee = []
        categoria_corrente = None
        
        # Ordina per categoria
        flashcards_ordinate = sorted(flashcards, key=lambda f: f.categoria)
        
        for flashcard in flashcards_ordinate:
            # Aggiungi intestazione categoria se cambiata
            if flashcard.categoria != categoria_corrente:
                if linee:  # Aggiungi linea vuota tra categorie
                    linee.append("")
                linee.append(f"# {flashcard.categoria}")
                categoria_corrente = flashcard.categoria
            
            testo = FlashcardParser.flashcard_to_text(flashcard)
            linee.append(f"* {testo}")
        
        return '\n'.join(linee)