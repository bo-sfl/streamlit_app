
import base64
from pathlib import Path


def highlight_max_margin(data, color='yellow'):
    '''
    highlight the maximum in a currency string Series
    '''
    attr = 'background-color: {}'.format(color)
    is_max = data == data.max()
    return [attr if v else '' for v in is_max]


def int_to_currency(val):
    """
    Takes an int and cast to currency style
    """
    val = str(val)
    _start_pos = 0
    _end_pos = len(val)%3
    if _end_pos == 0:
        _end_pos = 3
    currency = ["$"]
    while _end_pos <= len(val): 
        currency.append(val[_start_pos:_end_pos] + ",")
        _start_pos = _end_pos
        _end_pos += 3
    
    return "".join(currency)[:-1]

def currency_to_int(val):
    """
    Convert an currency string to int
    """
    return int(val[1:].replace(",",""))



def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded