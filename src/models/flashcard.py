"""
Modulo per la gestione delle flashcards e delle collezioni
"""
from datetime import datetime
from typing import List, Optional, Set
import random


class Flashcard:
    """Rappresenta una singola flashcard con parola tedesca e traduzione italiana"""
    
    def __init__(
        self,
        tedesco: str,
        italiano: str,
        priorita: bool = False,
        categoria: str = "Generale",
        corrette: int = 0,
        sbagliate: int = 0,
        ultima_revisione: Optional[str] = None
    ):
        self.tedesco = tedesco.strip()
        self.italiano = italiano.strip()
        self.priorita = priorita
        self.categoria = categoria.strip()
        self.corrette = corrette
        self.sbagliate = sbagliate
        self.ultima_revisione = ultima_revisione
    
    @property
    def tentativi_totali(self) -> int:
        """Ritorna il numero totale di tentativi"""
        return self.corrette + self.sbagliate
    
    @property
    def percentuale_successo(self) -> float:
        """Calcola la percentuale di successo"""
        if self.tentativi_totali == 0:
            return 0.0
        return (self.corrette / self.tentativi_totali) * 100
    
    def registra_risposta(self, corretta: bool):
        """Registra una risposta e aggiorna le statistiche"""
        if corretta:
            self.corrette += 1
        else:
            self.sbagliate += 1
        self.ultima_revisione = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Converte la flashcard in dizionario per il salvataggio"""
        return {
            'tedesco': self.tedesco,
            'italiano': self.italiano,
            'priorita': self.priorita,
            'categoria': self.categoria,
            'corrette': self.corrette,
            'sbagliate': self.sbagliate,
            'ultima_revisione': self.ultima_revisione
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Flashcard':
        """Crea una flashcard da un dizionario"""
        return cls(
            tedesco=data['tedesco'],
            italiano=data['italiano'],
            priorita=data.get('priorita', False),
            categoria=data.get('categoria', 'Generale'),
            corrette=data.get('corrette', 0),
            sbagliate=data.get('sbagliate', 0),
            ultima_revisione=data.get('ultima_revisione')
        )
    
    def __repr__(self) -> str:
        star = "⭐ " if self.priorita else ""
        return f"{star}[{self.categoria}] {self.tedesco} → {self.italiano}"


class FlashcardCollection:
    """Gestisce una collezione di flashcards"""
    
    def __init__(self):
        self.flashcards: List[Flashcard] = []
    
    def aggiungi_flashcard(self, flashcard: Flashcard):
        """Aggiunge una flashcard alla collezione"""
        self.flashcards.append(flashcard)
    
    def rimuovi_flashcard(self, indice: int):
        """Rimuove una flashcard dalla collezione"""
        if 0 <= indice < len(self.flashcards):
            self.flashcards.pop(indice)
    
    def get_flashcard(self, indice: int) -> Optional[Flashcard]:
        """Ottiene una flashcard per indice"""
        if 0 <= indice < len(self.flashcards):
            return self.flashcards[indice]
        return None
    
    def get_tutte_categorie(self) -> List[str]:
        """Ritorna tutte le categorie presenti, ordinate"""
        categorie = set(card.categoria for card in self.flashcards)
        return sorted(list(categorie))
    
    def filtra_per_categoria(self, categoria: str) -> List[Flashcard]:
        """Ritorna solo le flashcards di una categoria specifica"""
        return [card for card in self.flashcards if card.categoria == categoria]
    
    def filtra_per_categorie(self, categorie: List[str]) -> List[Flashcard]:
        """Ritorna le flashcards di più categorie"""
        return [card for card in self.flashcards if card.categoria in categorie]
    
    def cerca(self, termine: str) -> List[Flashcard]:
        """Cerca flashcards che contengono il termine"""
        termine = termine.lower()
        return [
            card for card in self.flashcards
            if termine in card.tedesco.lower() or termine in card.italiano.lower()
        ]
    
    def filtra_per_priorita(self) -> List[Flashcard]:
        """Ritorna solo le flashcards con priorità"""
        return [card for card in self.flashcards if card.priorita]
    
    def filtra_per_difficolta(self, soglia: float = 50.0) -> List[Flashcard]:
        """Ritorna le flashcards con percentuale di successo sotto la soglia"""
        return [
            card for card in self.flashcards
            if card.tentativi_totali > 0 and card.percentuale_successo < soglia
        ]
    
    def get_flashcards_casuali(self, numero: Optional[int] = None, categorie: Optional[List[str]] = None) -> List[Flashcard]:
        """Ritorna le flashcards in ordine casuale, opzionalmente filtrate per categorie"""
        if categorie:
            cards = self.filtra_per_categorie(categorie)
        else:
            cards = self.flashcards.copy()
        
        random.shuffle(cards)
        if numero:
            return cards[:numero]
        return cards
    
    def get_statistiche_generali(self) -> dict:
        """Calcola statistiche generali sulla collezione"""
        if not self.flashcards:
            return {
                'totale_flashcards': 0,
                'con_priorita': 0,
                'totale_tentativi': 0,
                'percentuale_media': 0.0,
                'num_categorie': 0
            }
        
        con_priorita = len(self.filtra_per_priorita())
        totale_tentativi = sum(card.tentativi_totali for card in self.flashcards)
        
        # Calcola percentuale media solo per card con tentativi
        cards_con_tentativi = [card for card in self.flashcards if card.tentativi_totali > 0]
        if cards_con_tentativi:
            percentuale_media = sum(
                card.percentuale_successo for card in cards_con_tentativi
            ) / len(cards_con_tentativi)
        else:
            percentuale_media = 0.0
        
        return {
            'totale_flashcards': len(self.flashcards),
            'con_priorita': con_priorita,
            'totale_tentativi': totale_tentativi,
            'percentuale_media': percentuale_media,
            'num_categorie': len(self.get_tutte_categorie())
        }
    
    def get_statistiche_per_categoria(self) -> dict:
        """Ritorna statistiche divise per categoria"""
        stats = {}
        for categoria in self.get_tutte_categorie():
            cards = self.filtra_per_categoria(categoria)
            totale = len(cards)
            con_priorita = len([c for c in cards if c.priorita])
            cards_studiate = [c for c in cards if c.tentativi_totali > 0]
            
            if cards_studiate:
                perc_media = sum(c.percentuale_successo for c in cards_studiate) / len(cards_studiate)
            else:
                perc_media = 0.0
            
            stats[categoria] = {
                'totale': totale,
                'con_priorita': con_priorita,
                'studiate': len(cards_studiate),
                'percentuale_media': perc_media
            }
        
        return stats
    
    def ordina_per_difficolta(self, crescente: bool = True):
        """Ordina le flashcards per percentuale di successo"""
        self.flashcards.sort(
            key=lambda card: card.percentuale_successo if card.tentativi_totali > 0 else 100,
            reverse=not crescente
        )
    
    def to_dict(self) -> dict:
        """Converte la collezione in dizionario per il salvataggio"""
        return {
            'flashcards': [card.to_dict() for card in self.flashcards]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FlashcardCollection':
        """Crea una collezione da un dizionario"""
        collection = cls()
        for card_data in data.get('flashcards', []):
            collection.aggiungi_flashcard(Flashcard.from_dict(card_data))
        return collection
    
    def __len__(self) -> int:
        return len(self.flashcards)
    
    def __iter__(self):
        return iter(self.flashcards)