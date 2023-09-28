import tlsh
import difflib
# import floret
import numpy as np
import random
from string import ascii_letters, digits


def tlsh_change_per_pos(sign, mod_sign):
    shash = tlsh.hash(bytes(sign, 'utf8'))
    mod_shash = tlsh.hash(bytes(mod_sign, 'utf8'))

    change_list = [li for li in difflib.ndiff(sign, mod_sign) if li[0] != ' ']
    diff = len(change_list)

    hash_change_list = [li for li in difflib.ndiff(
        shash, mod_shash) if li[0] != ' ']
    hash_diff = len(hash_change_list)

    ratio = (float)(hash_diff/(diff + 0.001))
    return ratio


# def ft_change_per_pos(sign, mod_sign):
    vec = model.get_word_vector(sign)
    mod_vec = model.get_word_vector(mod_sign)
    vec_diff1D = np.setdiff1d(vec, mod_vec)

    diff = (set(sign)).symmetric_difference(set(mod_sign))
    ratio = (float)(len(vec_diff1D)/len(diff))
    return ratio


def rand_change(sign):
    rlen = random.randrange(1, len(sign)-1)
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
# model = floret.train_unsupervised(
#    filename,
#    model="cbow",
#    mode="floret",
#    hashCount=2,
#    bucket=50000,
#    minn=3,
#    maxn=6,
# )

f = open(filename, '+r')
g = open("tlsh_log.txt", 'w+')
lines = f.readlines()

for line in lines:
    sign = line.strip()
    g.write("Current sign: " + sign + '\n')
    for _ in range(1, 20):
        mod_sign = rand_change(sign)
        change_ratio = tlsh_change_per_pos(sign, mod_sign)
        g.write(mod_sign + " Change ratio: " + str(change_ratio) + '\n')

f.close()
g.close()
