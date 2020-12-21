def get_val_by_keys_seq(struct, keys_seq):
    for key in keys_seq:
        struct = struct[key]
    return struct


def set_val_by_keys_seq(struct, keys_seq, val):
    for key in keys_seq[:-1]:
        struct = struct[key]
    struct[keys_seq[-1]] = val
