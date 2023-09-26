import tlsh
import floret
import numpy as np
import random
from string import ascii_letters, digits


def tlsh_change_per_position(sign, mod_sign):
    hash = tlsh.hash(bytes(sign, 'utf8'))
    mod_hash = tlsh.hash(bytes(mod_sign, 'utf8'))

    A = set(sign)
    B = set(mod_sign)
    diff = A.symmetric_difference(B)

    hA = set(hash)
    hB = set(mod_hash)
    hash_diff = hA.symmetric_difference(hB)

    ratio = (float)(len(hash_diff)/len(diff))
    return ratio


def ft_change_per_pos(sign, mod_sign):
    vec = model.get_word_vector(sign)
    mod_vec = model.get_word_vector(mod_sign)
    vec_diff1D = np.setdiff1d(vec, mod_vec)

    diff = (set(sign)).symmetric_difference(set(mod_sign))
    ratio = (float)(len(vec_diff1D)/len(diff))
    return ratio


def rand_change(sign):
    rlen = random.randrange(0, len(sign)-1)
    mod_sign = sign
    for _ in range(rlen):
        pos = random.randrange(0, len(mod_sign))
        insert_char = random.choice(ascii_letters + digits)
        mod_sign = sign[:pos] + insert_char + sign[pos:]
    return mod_sign


# main function
if __name__ == "__main__":
    filename = "p0f1.log"
    # train vectors for floret
model = floret.train_unsupervised(
    filename,
    model="cbow",
    mode="floret",
    hashCount=2,
    bucket=50000,
    minn=3,
    maxn=6,
)

num_iterations = 50
