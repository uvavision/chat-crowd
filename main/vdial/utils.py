import hashlib
import random

# https://discuss.pytorch.org/t/adaptive-learning-rate/320/2
def adjust_lr(optimizer, epoch, initial_lr, decay_rate=0.8):
    """Sets the learning rate to the initial LR decayed by 10 every 30 epochs"""
    lr = initial_lr * (0.8 ** (epoch // 2))
    for param_group in optimizer.param_groups:
        param_group['lr'] = lr


def clip_gradient(optimizer, grad_clip):
    for group in optimizer.param_groups:
        for param in group['params']:
            param.grad.data.clamp_(-grad_clip, grad_clip)


def get_hashcode(o):
    return hashlib.md5((str(o)).encode()).hexdigest()


def alter(x, y):
    return random.choice(list(set(y) - set([x])))


def xs(o):
    if o is None:
        return ''
    return str(o)