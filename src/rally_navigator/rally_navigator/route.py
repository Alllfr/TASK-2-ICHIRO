from collections import deque

from rally_interfaces.msg import Instruction
from rally_navigator.grid import Cell, DIRECTION_COL, DIRECTION_COUNT, DIRECTION_ROW, EAST

# Provided, do not modify
def trace_back(parent, finish):
    if finish not in parent:
        return []

    route = []
    cell = finish
    while cell is not None:
        route.append(cell)
        cell = parent[cell]
    route.reverse()
    return route

# TODO: TASK B
def find_route(grid):
    # Cari rute terpendek dari grid.start ke grid.finish dengan BFS, tetangga dicek berurutan
    # timur, utara, barat, selatan.
    # Return list kosong kalau tidak ada jalan.
    if not grid.inside(grid.start) or not grid.inside(grid.finish):
        return []

    # Ambil kotak dari pending. Untuk setiap tetangga yang di dalam grid yang bukan batu dan
    # belum dikunjungi, catat asalnya di parent lalu masukkan ke pending.
    parent = {grid.start: None}
    pending = deque([grid.start])
    # ... tulis pencariannya di sini ...
    while(pending):
        # Ambil cell pertama dari deque
        current_cell = pending.popleft()

        # Kalau sudah sampai finis, maka jalankan break
        if current_cell == grid.finish:
            break

        # Mengecek 4 arah
        for d in range(DIRECTION_COUNT):
            # Menghitung koordinat neighbor
            neighbor_col = current_cell.col + DIRECTION_COL[d]
            neighbor_row = current_cell.row + DIRECTION_ROW[d]
            neighbor = Cell(neighbor_col, neighbor_row)

            # Cek apakah neighbor ada di grid, dan apakah dia bukan batu serta neighbor tidak ada di parent
            if grid.inside(neighbor) and not grid.is_rock(neighbor) and neighbor not in parent:
                parent[neighbor] = current_cell # Catat asal neighbor
                pending.append(neighbor) # Masukan ke deque berikutnya

    return trace_back(parent, grid.finish)

# TODO: TASK C
def route_to_directions(route):
    # Ubah rute (daftar kotak) jadi daftar arah tiap langkah: 0 timur, 1 utara, 2 barat, 3 selatan.
    directions = []

    # Kalau route kosong atau cuma satu kotak saja, tidak ada langkah gerak
    if not route or len(route) < 2:
        return directions

    # Membandingkan cell saat ini dengan cell berikutnya
    for i in range(len(route) - 1):
        current_cell = route[i]
        next_cell = route[i + 1]
        delta_col = next_cell.col - current_cell.col
        delta_row = next_cell.row - current_cell.row

        # Mencocokan perubahan koordinat dengan nilai DIRECTION_COL dan DIRECTION_ROW
        for d in range(DIRECTION_COUNT):
            if DIRECTION_COL[d] == delta_col and DIRECTION_ROW[d] == delta_row:
                directions.append(d)
                break

    return directions

# TODO: TASK D
def directions_to_instructions(directions):
    # Gabungkan langkah lurus berturut-turut jadi satu instruksi, dan tutup tiap instruksi dengan belokannya.
    # Aturan khusus:
    # - Jika langkah pertama bukan ke timur, Miru harus belok dulu (instruksi pertama jaraknya 0).
    # - Putar balik ditulis dua belok kiri berturut-turut. 
    # - Instruksi terakhir tidak punya belokan (TURN_NONE).
    
    # Jika rute kosong, maka miru diam saja
    if not directions:
        return [Instruction(id=1, distance=0, turn=Instruction.TURN_NONE)]
    
    instructions = []
    # Miru selalu mulai dengan mengahadap timur
    current_facing = EAST
    current_distance = 0
    instruction_id = 1

    for d in directions:
        # Jika arah gerak sama, maka tambah jarak lurus
        if d == current_facing:
            current_distance += 1
        # Jika beda, tentukan arah beloknya
        else:
            diff = (d - current_facing) % 4

            # Putar balik
            if diff == 2:
                # Instruksi maju sejauh distance lalu belok kiri
                instructions.append(Instruction(id=instruction_id, distance=current_distance, turn=Instruction.TURN_LEFT))
                instruction_id += 1
                # Instruksi maju sejauh 0 lalu belok kiri
                instructions.append(Instruction(id=instruction_id, distance=0, turn=Instruction.TURN_LEFT))
                instruction_id += 1
            else:
                # diff == 1 itu kiri dan diff == 3 itu kanan
                turn_val = Instruction.TURN_LEFT if diff == 1 else Instruction.TURN_RIGHT
                instructions.append(Instruction(id=instruction_id, distance=current_distance, turn=turn_val))
                instruction_id += 1

            # Update facing ke arah baru
            current_facing = d
            current_distance = 1 # Karena sudah bergerak 1 cell ke arah baru
    instructions.append(Instruction(id=instruction_id, distance=current_distance, turn=Instruction.TURN_NONE))
    return instructions

# Provided, do not modify
def route_to_instructions(route):
    return directions_to_instructions(route_to_directions(route))
