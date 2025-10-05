"""
Modulo per la gestione delle flashcards e delle collezioni con categorie
"""
from datetime import datetime
from typing import List, Optional, Dict
import random


class Flashcard:
    """Rappresenta una singola flashcard con parola tedesca e traduzione italiana"""
    
    def __init__(
        self,
        tedesco: str,
        italiano: str,
        categoria: str = "Generale",
        priorita: bool = False,
        corrette: int = 0,
        sbagliate: int = 0,
        ultima_revisione: Optional[str] = None
    ):
        self.tedesco = tedesco.strip()
        self.italiano = italiano.strip()
        self.categoria = categoria.strip()
        self.priorita = priorita
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
            'categoria': self.categoria,
            'priorita': self.priorita,
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
            categoria=data.get('categoria', 'Generale'),
            priorita=data.get('priorita', False),
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
    
    def get_categorie(self) -> List[str]:
        """Ritorna la lista di tutte le categorie presenti"""
        categorie = set(card.categoria for card in self.flashcards)
        return sorted(list(categorie))
    
    def filtra_per_categoria(self, categoria: str) -> List[Flashcard]:
        """Ritorna le flashcards di una specifica categoria"""
        return [card for card in self.flashcards if card.categoria == categoria]
    
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
    
    def filtra_per_livello(self, livello: str) -> List[Flashcard]:
        """
        Filtra le flashcards per livello di difficoltà
        
        Args:
            livello: 'difficili', 'medie', 'facili', 'non-studiate'
        
        Returns:
            Lista di flashcards filtrate
        """
        if livello == 'difficili':
            return [c for c in self.flashcards if c.tentativi_totali > 0 and c.percentuale_successo < 50]
        elif livello == 'medie':
            return [c for c in self.flashcards if c.tentativi_totali > 0 and 50 <= c.percentuale_successo < 80]
        elif livello == 'facili':
            return [c for c in self.flashcards if c.tentativi_totali > 0 and c.percentuale_successo >= 80]
        elif livello == 'non-studiate':
            return [c for c in self.flashcards if c.tentativi_totali == 0]
        else:
            return list(self.flashcards)
    
    def get_flashcards_casuali(self, numero: Optional[int] = None) -> List[Flashcard]:
        """Ritorna le flashcards in ordine casuale"""
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
                'percentuale_media': 0.0
            }
        
        con_priorita = len(self.filtra_per_priorita())
        totale_tentativi = sum(card.tentativi_totali for card in self.flashcards)
        
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
            'percentuale_media': percentuale_media
        }
    
    def get_statistiche_per_categoria(self) -> Dict[str, dict]:
        """Calcola statistiche per ogni categoria"""
        categorie = self.get_categorie()
        stats_categorie = {}
        
        for categoria in categorie:
            cards = self.filtra_per_categoria(categoria)
            
            totale = len(cards)
            con_priorita = len([c for c in cards if c.priorita])
            totale_tentativi = sum(c.tentativi_totali for c in cards)
            
            cards_con_tentativi = [c for c in cards if c.tentativi_totali > 0]
            if cards_con_tentativi:
                percentuale_media = sum(
                    c.percentuale_successo for c in cards_con_tentativi
                ) / len(cards_con_tentativi)
                corrette_totali = sum(c.corrette for c in cards_con_tentativi)
                sbagliate_totali = sum(c.sbagliate for c in cards_con_tentativi)
            else:
                percentuale_media = 0.0
                corrette_totali = 0
                sbagliate_totali = 0
            
            stats_categorie[categoria] = {
                'totale_flashcards': totale,
                'con_priorita': con_priorita,
                'totale_tentativi': totale_tentativi,
                'percentuale_media': percentuale_media,
                'corrette_totali': corrette_totali,
                'sbagliate_totali': sbagliate_totali,
                'studiate': len(cards_con_tentativi),
                'non_studiate': totale - len(cards_con_tentativi)
            }
        
        return stats_categorie
    
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