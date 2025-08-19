from typing import Optional
from fastapi import Query, Header

DEFAULT_LANGUAGE = "en"

# 1. ?lang=az / ?lang=en
# 2. Use lang in header
# 3. if no lang provided it will be en by default

async def get_language(
    lang: Optional[str] = Query(default=None, description="Query param to override language"),
    accept_language: Optional[str] = Header(default=None, description="Accept-Language header")
) -> str:
    
    if lang and lang.strip():
        return lang.strip().lower()

    if accept_language:
        primary_lang = accept_language.split(",")[0].split("-")[0].strip().lower()
        if primary_lang:
            return primary_lang

    return DEFAULT_LANGUAGE