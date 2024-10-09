blacklisted_tokens = set()

def add_token_to_blacklist(token_jwt: str):
    blacklisted_tokens.add(token_jti)

def is_token_blacklisted(token_jwt: str) -> bool:
    return token_jti in blacklisted_tokens
