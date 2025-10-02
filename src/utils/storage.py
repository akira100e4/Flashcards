"""
Modulo per il salvataggio e caricamento dei dati
"""
import json
import os
from pathlib import Path
from typing import Optional
from src.models.flashcard import FlashcardCollection


class Storage:
    """Gestisce il salvataggio e caricamento delle flashcards"""
    
    def __init__(self, file_path: str = "data/flashcards.json"):
        self.file_path = Path(file_path)
        self._assicura_directory()
    
    def _assicura_directory(self):
        """Crea la directory data/ se non esiste"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def salva(self, collection: FlashcardCollection) -> bool:
        """
        Salva la collezione di flashcards su file
        
        Returns:
            True se il salvataggio ha successo, False altrimenti
        """
        try:
            data = collection.to_dict()
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Errore durante il salvataggio: {e}")
            return False
    
    def carica(self) -> Optional[FlashcardCollection]:
        """
        Carica la collezione di flashcards dal file
        
        Returns:
            FlashcardCollection se il caricamento ha successo, None altrimenti
        """
        if not self.file_path.exists():
            print(f"File {self.file_path} non trovato, creazione nuova collezione")
            return FlashcardCollection()
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return FlashcardCollection.from_dict(data)
        except Exception as e:
            print(f"Errore durante il caricamento: {e}")
            return FlashcardCollection()
    
    def esporta_backup(self, collection: FlashcardCollection, backup_path: str) -> bool:
        """
        Esporta un backup della collezione
        
        Returns:
            True se l'esportazione ha successo, False altrimenti
        """
        try:
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = collection.to_dict()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Errore durante l'esportazione del backup: {e}")
            return False
    
    def importa_backup(self, backup_path: str) -> Optional[FlashcardCollection]:
        """
        Importa una collezione da un file di backup
        
        Returns:
            FlashcardCollection se l'importazione ha successo, None altrimenti
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            print(f"File di backup {backup_path} non trovato")
            return None
        
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return FlashcardCollection.from_dict(data)
        except Exception as e:
            print(f"Errore durante l'importazione del backup: {e}")
            return None
    
    def file_esiste(self) -> bool:
        """Verifica se il file di storage esiste"""
        return self.file_path.exists()
    
    def elimina_file(self) -> bool:
        """
        Elimina il file di storage
        
        Returns:
            True se l'eliminazione ha successo, False altrimenti
        """
        try:
            if self.file_path.exists():
                self.file_path.unlink()
            return True
        except Exception as e:
            print(f"Errore durante l'eliminazione del file: {e}")
            return False