# src/locales/__init__.py
# Localization manager

import importlib
from typing import Dict, Any, Optional
from functools import lru_cache

class Localization:
    """Manages multi-language support for the bot."""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'am': 'አማርኛ'
    }
    
    DEFAULT_LANGUAGE = 'en'
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._load_all()
    
    def _load_all(self):
        """Pre-load all language modules."""
        for lang_code in self.SUPPORTED_LANGUAGES:
            try:
                module = importlib.import_module(f'src.locales.{lang_code}.messages')
                self._cache[lang_code] = module.Messages()
            except ImportError:
                pass
    
    @lru_cache(maxsize=128)
    def get(self, key: str, lang: str = None) -> str:
        """Get localized message by key."""
        lang = lang or self.DEFAULT_LANGUAGE
        if lang not in self._cache:
            lang = self.DEFAULT_LANGUAGE
        
        messages = self._cache.get(lang)
        if messages and hasattr(messages, key):
            return getattr(messages, key)
        
        # Fallback to English
        if lang != self.DEFAULT_LANGUAGE:
            messages = self._cache.get(self.DEFAULT_LANGUAGE)
            if messages and hasattr(messages, key):
                return getattr(messages, key)
        
        return key  # Return key as last resort
    
    def get_language_name(self, lang: str) -> str:
        """Get display name for language code."""
        return self.SUPPORTED_LANGUAGES.get(lang, lang)
    
    def is_supported(self, lang: str) -> bool:
        """Check if language is supported."""
        return lang in self.SUPPORTED_LANGUAGES


# Global instance
i18n = Localization()