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
        linea = re.sub(r'^\s*[*\-•]\s*', '', linea)
        linea = re.sub(r'\s+', ' ', linea)
        return linea.strip()
    
    @staticmethod
    def ha_priorita(linea_originale: str) -> bool:
        """Verifica se la linea contiene asterischi (priorità)"""
        return '**' in linea_originale
    
    @staticmethod
    def estrai_coppia(linea: str) -> Tuple[str, str, bool]:
        """
        Estrae la coppia tedesco-italiano da una linea
        
        Returns:
            Tupla (tedesco, italiano, ha_priorita)
        """
        linea_originale = linea
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
        
        return tedesco, italiano, priorita
    
    @staticmethod
    def parse_testo(testo: str, categoria: str = "Generale") -> List[Flashcard]:
        """
        Parse un testo con multiple flashcards
        
        Formato supportato:
        * **weit→ Lontano**
        * üben → esercitare
        Nachmittag → pomeriggio
        
        Args:
            testo: Il testo da parsare
            categoria: La categoria da assegnare a tutte le flashcards
        
        Returns:
            Lista di oggetti Flashcard
        """
        flashcards = []
        linee = testo.strip().split('\n')
        
        for i, linea in enumerate(linee, 1):
            linea = linea.strip()
            
            # Salta linee vuote
            if not linea:
                continue
            
            # Salta linee che non contengono il separatore
            if '→' not in linea:
                continue
            
            try:
                tedesco, italiano, priorita = FlashcardParser.estrai_coppia(linea)
                flashcard = Flashcard(
                    tedesco=tedesco,
                    italiano=italiano,
                    categoria=categoria,  # Usa la categoria passata come parametro
                    priorita=priorita
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
        return f"{asterischi}{flashcard.tedesco} → {flashcard.italiano}{asterischi}"
    
    @staticmethod
    def collezione_to_text(flashcards: List[Flashcard]) -> str:
        """Converte una lista di flashcards in testo formattato"""
        linee = []
        for flashcard in flashcards:
            testo = FlashcardParser.flashcard_to_text(flashcard)
            linee.append(f"* {testo}")
        return '\n'.join(linee)