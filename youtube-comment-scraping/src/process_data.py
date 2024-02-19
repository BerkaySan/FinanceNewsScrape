import re
from textblob import TextBlob

def calc_status(polarity):
    if polarity > 0.7:
        return 'Overly Positive'
    elif polarity > 0.4:
        return 'Positive'
    elif polarity > 0.1:
        return 'Partially Positive'
    elif polarity > -0.1:
        return 'Neutral'
    elif polarity > -0.4:
        return 'Partially Negative'
    elif polarity > -0.7:
        return 'Negative'
    else:
        return 'Overly Negative'



def analyze(comments):
    all_status=[]
    for comment in comments:
        status = TextBlob(str(comment))
        f_status = calc_status(status.sentiment.polarity)
        all_status.append(f_status)

    return all_status


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F1E0-\U0001F1FF"  # flags
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)



def remove_spaces(text):
    text = '\n'.join([line for line in text.split('\n') if line.strip() != ''])
    text = re.sub(r'\s+', ' ', text)
    return text


def remove_all(text):
    if not isinstance(text, str):
        return text
    
    text = remove_emojis(text)
    text = remove_spaces
    return text



def clean(text):
    text = remove_all(text)