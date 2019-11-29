def pre_traverse(root, callback=None):
    '''
    前序遍历
    '''
    if root is None:
        return
    callback and callback(root)
    pre_traverse(getattr(root, "l_value", None), callback)
    pre_traverse(getattr(root, "r_value", None), callback)


def mid_traverse(root, callback=None):
    '''
    中序遍历
    '''
    if root is None:
        return
    mid_traverse(getattr(root, "l_value", None), callback)
    callback and callback(root)
    mid_traverse(getattr(root, "r_value", None), callback)


def after_traverse(root, callback=None):
    '''
    后序遍历
    '''
    if root is None:
        return
    after_traverse(getattr(root, "l_value", None), callback)
    after_traverse(getattr(root, "r_value", None), callback)
    callback and callback(root)
