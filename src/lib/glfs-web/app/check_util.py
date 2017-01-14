def none(*values):
    for v in values:
        if v is None:
            return True
    return False


def empty(container):
    if hasattr(container, '__len__') and len(container) > 0:
        return False
    return True
