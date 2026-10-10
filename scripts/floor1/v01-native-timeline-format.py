"""Bounded streaming decoder; historical v1 and corrected v2 stay distinct.

This validates the sidecar format, never game equivalence or execution authority.
EOF after complete records is a partial trace unless a real terminal exists.
"""
import struct

WORDS = 46
RECORD = struct.Struct('<46I')
BUFFER_RECORDS = 4096
PREVISUAL_FRAMES = 2044
VISUAL_FRAMES = 36000
FRAME_CALLS = PREVISUAL_FRAMES + VISUAL_FRAMES
INSTRUCTION_RESERVE = 70
TERMINAL_RECORDS = 1
LIMIT = FRAME_CALLS * BUFFER_RECORDS + INSTRUCTION_RESERVE + TERMINAL_RECORDS
HEADERS = {b'BVTIME01': 1000000, b'BVTIME02': LIMIT}

def read_header(stream):
    raw = stream.read(16)
    if len(raw) != 16:
        raise ValueError('Incomplete timeline header')
    magic, words, limit = struct.unpack('<8sII', raw)
    if magic not in HEADERS or words != WORDS or limit != HEADERS[magic]:
        raise ValueError('Unrecognized timeline format or capacity')
    return {'magic': magic.decode('ascii'), 'words': words, 'limit': limit}

def records(stream, header):
    """Read at most one fixed record at a time, rejecting truncation and overflow."""
    if header not in [{'magic': m.decode('ascii'), 'words': WORDS, 'limit': n}
                      for m, n in HEADERS.items()]:
        raise ValueError('Unrecognized decoded header')
    total = batch = 0
    terminal = False
    while True:
        raw = stream.read(RECORD.size)
        if not raw:
            return
        if len(raw) != RECORD.size:
            raise ValueError('Incomplete timeline record')
        if terminal:
            raise ValueError('Records after terminal marker')
        total += 1
        batch += 1
        if total > header['limit'] or batch > BUFFER_RECORDS:
            raise ValueError('Timeline record capacity exceeded')
        row = RECORD.unpack(raw)
        event, phase = row[:2]
        if event not in range(1, 10) or phase != (1 if event in (1, 3) else 2):
            raise ValueError('Invalid timeline event or phase')
        if event in (6, 7, 8):
            batch = 0
            terminal = event in (7, 8)
        yield row
