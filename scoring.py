import re

def calculate_relevance(row: dict, search_term: str) -> int:
    """Calcul relevance score

    Args:
        row (dict): row of the dataframe
        search_term (str): search term

    Returns:
        int: relevance score
    """
    terms = []
    score = 0

    parts = re.split(r'\s+(AND|OR)\s+', search_term, flags=re.IGNORECASE)
    for part in parts:
        if part.upper() not in ['AND', 'OR']:
            clean_term = part.strip().strip('"').strip("()")
            if clean_term:
                terms.append(clean_term)
                
    #print(terms)
    for term in terms:
        clean_term = term.replace('"', '')
        if clean_term.lower() in str(row['title']).lower():
            score += 4.5
        if clean_term.lower() in str(row['description']).lower():
            score += 4.5
        if ' ' in clean_term:
            hyphenated_term = clean_term.replace(' ', '-')
            if hyphenated_term.lower() in str(row['link']).lower():
                score += 1
            spaced_term = clean_term.replace(' ', '')
            if spaced_term.lower() in str(row['link']).lower():
                score += 1
        if clean_term.lower() in str(row['link']).lower():
            score += 1
    return score