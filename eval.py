import tlsh
import random
import subprocess
import os
import sys
from string import ascii_letters, digits
from Levenshtein import distance
import numpy as np
import matplotlib.pyplot as plt

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
def change_per_pos(sign, mod_sign, sign_hash, mod_sign_hash, delta_input_list, delta_hash_list):
    diff = distance(sign, mod_sign)
    diff_pc = (float)(diff/len(sign)) * 100
    delta_input_list.append(diff_pc)

    hash_diff = distance(sign_hash, mod_sign_hash)
    hash_diff_pc = (float)(hash_diff/len(sign_hash)) * 100
    delta_hash_list.append(hash_diff_pc)

    ratio = hash_diff_pc/diff_pc
    return ratio


# Calculate mean gap between two changes in the hash, and variance
def calculate_gap_stats(mean_gap, var_gap, num, sign_hash, mod_sign_hash):
    len = min(len(sign_hash), len(mod_sign_hash))
    prev_i = -1
    gap_sum = 0
    gap_num = 0
    for i in range(len):
        if sign_hash[i] != mod_sign_hash[i]:
            if prev_i == -1:
                prev_i = i
            else:
                gap_sum += i - prev_i
                gap_num += 1
    curr_mean = (float)(gap_sum/gap_num)
    mean_gap += (curr_mean - mean_gap)/(num + 1)
    var_gap = compute_var_online(mean_gap, var_gap, num, curr_mean)
    return (mean_gap, var_gap)


# Calculate online variance
def compute_var_online(mean, var, num, curr):
    n = num + 1
    delta = curr - mean
    delta_n = (float)(delta / n)
    term1 = delta * delta_n * num
    var = (var + term1)/n
    return var


# Add random characters at random positions of the string.
# The string length at most doubles its original value
def rand_change(sign):
    rlen = random.randrange(1, len(sign))
    mod_sign = sign
    while rlen > 0:
        pos = random.randrange(0, len(mod_sign))
        insert_char = random.choice(ascii_letters + digits)
        mod_sign = mod_sign[:pos] + insert_char + mod_sign[pos:]
        rlen -= 1
    return mod_sign


# main function
def main():
    input_file = "..\p0f signatures\p0f1.log"
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

    # number of modified signatures on which gap stats have been calculated
    num = 0
    mean_gap = 0
    var_gap = 0

    # lists for plotting
    delta_input_list = []
    delta_hash_list = []

    for line in lines:
        sign = line.strip()
        output_file.write("Current sign: " + sign + '\n')
        sign_hash = compute_hash(sign, ch)
        print("Processing "+sign_hash+"\n")
        for _ in range(1, 20):
            mod_sign = rand_change(sign)
            # Calculating modified hash
            mod_sign_hash = compute_hash(mod_sign, ch)
            # Calculating locality
            change_ratio = change_per_pos(
                sign, mod_sign, sign_hash, mod_sign_hash, delta_input_list, delta_hash_list)
            output_file.write(mod_sign + " Change ratio: " +
                              str(change_ratio) + '\n')
            # (mean_gap, var_gap) = calculate_gap_stats(
            #    mean_gap, var_gap, num, sign_hash, mod_sign_hash)
            num += 1

    output_file.close()

    # Plot the deltas in a scatter plot, where Y-axis represents change (delta) in input
    # and X-axis represents delta in hash
    x = np.array(delta_hash_list)
    y = np.array(delta_input_list)
    plt.scatter(x, y)
    plt.show()
    # plt.savefig('scatter_tlsh.png')


if __name__ == "__main__":
    main()
