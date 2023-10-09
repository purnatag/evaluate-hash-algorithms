import tlsh
import difflib
import random
import subprocess
import os
import sys
from string import ascii_letters, digits

# Program computes locality of chosen hash function on p0f signature log file

# Choose required hash function and compute hash


def compute_hash(sign, ch):
    if ch == 1:
        sign_hash = compute_tlsh(sign)
    elif ch == 2:
        sign_hash = compute_ssdeep(sign)
    else:
        sign_hash = compute_sdhash(sign)
    return sign_hash


# Compute hash when the chosen function is tlsh
def compute_tlsh(sign):
    return tlsh.hash(bytes(sign, 'utf8'))


# Compute hash when the chosen function is ssdeep
def compute_ssdeep(sign):
    f = open('single_sign.txt', 'w')
    f.write(sign)
    stdout = subprocess.run(
        ['..\ssdeep-2.14.1\ssdeep', '-l', 'single_sign.txt', '>', 'ssdeep_output'], check=True)
    ssdeep_result = (((open('ssdeep_output', 'r')).read()).splitlines())
    result = ssdeep_result[4].split(',')[0]
    print(stdout)

    f.close()
    # os.remove('output')
    os.remove('single_sign.txt')
    return result


# Compute hash when the chosen function is sdhash
def compute_sdhash(sign):
    f = open('single_sign.txt', 'w')
    f.write(sign)
    sdhash_result = subprocess.run(
        ['..\sdhash-3.4-win32\sdhash', 'single_sign.txt'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    f.close()
    os.remove('single_sign.txt')
    return sdhash_result


# Calculate locality as change in the hash of the randomly modified signature per
# position modified in the original signature to obtain the modified sign
def change_per_pos(sign, mod_sign, sign_hash, mod_sign_hash):
    change_list = [li for li in difflib.ndiff(sign, mod_sign) if li[0] != ' ']
    diff = len(change_list)
    diff_pc = (float)(diff/len(sign)) * 100

    hash_change_list = [li for li in difflib.ndiff(
        sign_hash, mod_sign_hash) if li[0] != ' ']
    hash_diff = len(hash_change_list)
    hash_diff_pc = (float)(hash_diff/len(sign_hash)) * 100

    ratio = hash_diff_pc/diff_pc
    return ratio


# Add random characters at random positions of the string.
# The string length at most doubles its original value
def rand_change(sign):
    rlen = random.randrange(1, len(sign)-1)
    mod_sign = sign
    for _ in range(rlen):
        pos = random.randrange(0, len(mod_sign))
        insert_char = random.choice(ascii_letters + digits)
        mod_sign = sign[:pos] + insert_char + sign[pos:]
    return mod_sign


# main function
def main():
    input_file = "p0f1.log"
    print("Choose the hashing algorithm to run:\n ")
    print(" 1. TLSH \n 2. ssdeep \n 3. sdhash\n")
    ch = int(input("Enter choice:"))

    f = open(input_file, '+r')
    if ch == 1:
        output_file = open("tlsh_log.txt", 'w+')
    elif ch == 2:
        output_file = open("ssdeep_log.txt", 'w+')
    elif ch == 3:
        output_file = open("sdhash_log.txt", 'w+')
    else:
        print("Invalid input. Exiting.\n")
        sys.exit(0)

    lines = f.readlines()
    f.close()

    for line in lines:
        sign = line.strip()
        output_file.write("Current sign: " + sign + '\n')
        sign_hash = compute_hash(sign, ch)
        print("Processing "+sign_hash+"\n")
        for _ in range(1, 20):
            mod_sign = rand_change(sign)
            # Calculating modified hash
            mod_sign_hash = compute_hash(mod_sign, ch)
            change_ratio = change_per_pos(
                sign, mod_sign, sign_hash, mod_sign_hash)
            output_file.write(mod_sign + " Change ratio: " +
                              str(change_ratio) + '\n')

    output_file.close()


if __name__ == "__main__":
    main()
