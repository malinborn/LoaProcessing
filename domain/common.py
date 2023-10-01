def shorten_text_repr(text: str, target_length: int) -> str:
    return ((text[0:target_length - 4] + '...').ljust(target_length)
            if len(text) > target_length - 5
            else text).ljust(target_length)
