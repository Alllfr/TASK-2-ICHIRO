from collections import deque
from typing import NamedTuple

class Instruction(NamedTuple):
    instruction_id: int
    distance: int  # jumlah kotak
    turn: int  # TURN_NONE, TURN_LEFT, atau TURN_RIGHT

# TODO: TASK A
class InstructionQueue:
    def __init__(self):
        self.last_id = 0
        self.ready = deque()

    def add(self, instruction):
        # Masukkan instruksi ke antrean, tapi abaikan jika id-nya tidak lebih besar dari self.last_id
        # Return True jika diterima, False jika diabaikan
        return False

    def pop(self):
        # Ambil instruksi paling lama di antrean, atau return None jika kosong
        return None

    def __len__(self):
        # Jumlah instruksi di antrean
        return 0
