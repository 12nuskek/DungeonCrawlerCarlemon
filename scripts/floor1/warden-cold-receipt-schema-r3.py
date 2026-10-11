"""Explicit receipt Path schema. Importing this module performs no checks or IO."""
from pathlib import Path
import json
import math
import os
import hashlib
import stat

FILE_CAP = 8 * 1024**2
TOTAL_CAP = 64 * 1024**2


def require(value, reason):
    if not value:
        raise AssertionError(reason)


def matches(route, patterns):
    return any(len(route) == len(pattern) and
               all(expected == '*' or actual == expected
                   for actual, expected in zip(route, pattern)) for pattern in patterns)


def schema_value(value, path_key_maps=(), path_value_fields=()):
    """Only declared map keys/value fields permit Path -> str conversion."""
    visited = 0

    def convert(item, route):
        nonlocal visited
        visited += 1
        require(visited <= 100000 and len(route) <= 64, 'receipt structure bound')
        if isinstance(item, Path):
            require(matches(route, path_value_fields), 'Path value outside declared schema')
            return str(item)
        if type(item) is dict:
            converted = {}
            for key, child in item.items():
                if isinstance(key, Path):
                    require(matches(route, path_key_maps), 'Path key outside declared schema')
                    name = str(key)
                else:
                    require(type(key) is str, 'receipt keys must be strings or declared Paths')
                    name = key
                require(name not in converted, 'post-conversion receipt key collision')
                converted[name] = convert(child, route + (name,))
            return converted
        if type(item) is list:
            return [convert(child, route + (str(index),)) for index, child in enumerate(item)]
        if item is None or type(item) in (str, bool, int):
            return item
        if type(item) is float:
            require(math.isfinite(item), 'nonfinite receipt number')
            return item
        raise TypeError('unsupported receipt type at ' + repr(route) + ': ' + type(item).__name__)

    return convert(value, ())


def encode_receipt(value, *, path_key_maps=(), path_value_fields=(), validate):
    converted = schema_value(value, path_key_maps, path_value_fields)
    validate(converted)
    data = (json.dumps(converted, sort_keys=True, indent=2, allow_nan=False) + '\n').encode('utf-8')
    require(len(data) <= FILE_CAP, 'receipt file bound')
    decoded = json.loads(data)
    validate(decoded)
    require(decoded == converted, 'complete receipt round trip')
    return data


def prepare_bundle(payloads, *, path_key_maps=(), path_value_fields=(), validate):
    """Serialize and validate EVERY payload before the destination can exist."""
    require(type(payloads) is dict and 0 < len(payloads) <= 16, 'receipt bundle schema')
    result = {}
    for name, payload in payloads.items():
        require(type(name) is str and Path(name).name == name and name.endswith('.json'),
                'plain JSON receipt filename')
        result[name] = encode_receipt(payload, path_key_maps=path_key_maps,
                                      path_value_fields=path_value_fields, validate=validate)
    require(sum(len(data) + 4096 for data in result.values()) <= TOTAL_CAP, 'receipt bundle bound')
    return result


def write_bundle(destination, payloads, *, path_key_maps=(), path_value_fields=(), validate):
    prepared = prepare_bundle(payloads, path_key_maps=path_key_maps,
                              path_value_fields=path_value_fields, validate=validate)
    return write_prepared_bundle(destination, prepared, validate=validate)


def write_prepared_bundle(destination, prepared, *, validate):
    require(type(prepared) is dict and 0 < len(prepared) <= 16, 'complete prepared bundle')
    for name, data in prepared.items():
        require(type(name) is str and Path(name).name == name and name.endswith('.json') and
                type(data) is bytes and len(data) <= FILE_CAP, 'typed bounded prepared JSON payload')
        validate(json.loads(data))
    require(sum(len(data)+4096 for data in prepared.values()) <= TOTAL_CAP, 'prepared bundle bound')
    destination = Path(destination)
    require(destination.is_absolute() and not os.path.lexists(destination), 'fresh receipt destination')
    require(destination.parent.is_dir() and not destination.parent.is_symlink(), 'existing real parent')
    destination.mkdir(mode=0o700)
    for name, data in prepared.items():
        with (destination / name).open('xb') as file:
            os.fchmod(file.fileno(), 0o600)
            file.write(data)
            file.flush()
            os.fsync(file.fileno())
    for directory in (destination, destination.parent):
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    return prepared


def readback_prepared(destination, prepared, *, validate):
    result = {}
    for name, expected in prepared.items():
        require(type(name) is str and Path(name).name == name and name.endswith('.json') and
                type(expected) is bytes and len(expected) <= FILE_CAP, 'declared persisted receipt bytes')
        path = Path(destination)/name
        before = path.lstat()
        require(stat.S_ISREG(before.st_mode) and before.st_size == len(expected), 'exact-size real persisted receipt')
        fd = os.open(path, os.O_RDONLY|os.O_NOFOLLOW)
        stable = lambda s: (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink)
        try:
            require(stable(os.fstat(fd)) == stable(before), 'opened receipt identity')
            chunks, total = [], 0
            while total < len(expected):
                block = os.read(fd, min(65536, len(expected)-total))
                require(block, 'short persisted receipt')
                chunks.append(block); total += len(block)
            require(os.read(fd, 1) == b'' and stable(os.fstat(fd)) == stable(before), 'receipt exact EOF and stable metadata')
        finally:
            os.close(fd)
        actual = b''.join(chunks)
        require(stable(path.lstat()) == stable(before) and actual == expected and
                hashlib.sha256(actual).digest() == hashlib.sha256(expected).digest(), 'persisted receipt complete byte/hash identity')
        validate(json.loads(actual))
        result[name] = dict(bytes=total, SHA256=hashlib.sha256(actual).hexdigest(),
                            complete_schema_validated=True, exact_bytes=True, exact_EOF=True)
    return result
