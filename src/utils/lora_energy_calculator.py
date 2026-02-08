import numpy as np

def lora_toa(PL, SF=7, BW=500000, CR=3, IH=0, Npream=8, CRC=1) -> float:
    # CR input must be: 1->4/5, 2->4/6, 3->4/7, 4->4/8
    DE = 1 if (BW == 125000 and SF in [11,12]) else 0

    r_symbol = BW / 2**SF

    t_symbol = 1 / r_symbol
    t_preamble = (Npream + 4.25) * t_symbol

    numerator = 8*PL - 4*SF + 28 + 16*CRC - 20*IH
    denominator = 4 * (SF - 2*DE)

    n_payload = 8 + max(
        np.ceil(numerator / denominator) * (CR + 4), 0
    )

    t_payload = n_payload * t_symbol
    t_packet = t_preamble + t_payload

    return t_packet

def lora_tx_e_consumption(toa, voltage=3.3, current=29) -> float:
    return voltage * current * toa