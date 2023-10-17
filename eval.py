import tlsh
import random
import subprocess
import os
import re
import sys
from simhash import Simhash
from string import ascii_letters, digits
from Levenshtein import distance
import numpy as np
import matplotlib.pyplot as plt

# Program computes locality of chosen hash function on p0f signature log file
# Currently supporting TLSH and simhash


# Choose required hash function and compute hash
# 'ch' keeps alive the possibility of adding more algorithms to this pipeline
def compute_hash(sign, ch):
    if ch == 1:
        sign_hash = compute_tlsh(sign)
    elif ch == 2:
        sign_hash = compute_simhash(sign)
    return sign_hash


# Compute hash when the chosen function is tlsh
def compute_tlsh(sign):
    return tlsh.hash(bytes(sign, 'utf8'))


# Compute hash when the chosen function is simhash
def compute_simhash(sign):
    width = 3
    sign = sign.lower()
    sign = re.sub(r'[^\w]+', '', sign)
    sign_features = [sign[i:i + width]
                     for i in range(max(len(sign) - width + 1, 1))]
    hash_str = str('%x' % Simhash(sign_features).value)
    return hash_str


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
    prev_i = -1
    i = 0
    j = 0
    gap_sum = 0
    gap_num = 0
    while i < len(sign_hash) and j < len(mod_sign_hash):
        if sign_hash[i] != mod_sign_hash[j]:
            if prev_i == -1:
                prev_i = i
            else:
                gap_sum += i - prev_i
                gap_num += 1
        else:
            i += 1
        j += 1
    if gap_num == 0:
        return (mean_gap, var_gap)
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


# Plotting the deltas in a scatter plot, where Y-axis represents change (delta) in input
# and X-axis represents delta in hash. Plotting the change ratio in the same plot
def get_plots(fname, crlist, delta_input_list, delta_hash_list, hash_alg):
    print("Plotting the data...")
    # X and Y axes values
    x1 = np.array(crlist)
    x2 = np.array(delta_hash_list)
    y = np.array(delta_input_list)

    # Scatter plots
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

    # First plot with the change ratio
    ax1.scatter(x1, y)
    ax1.set_xlabel("Change Ratio")
    ax1.set_ylabel("% Change in input")

    # Second plot with the % delta in hashes
    ax2.scatter(x2, y)
    ax2.set_xlabel("% Change in Hash")
    ax2.set_ylabel("% Change in input")

    # Making the plot square
    # lims = [
    #   np.min([ax.get_xlim(), ax.get_ylim()]),  # min of both axes
    #   np.max([ax.get_xlim(), ax.get_ylim()]),  # max of both axes
    # ]

    # now plot both limits against eachother
    # ax.plot(lims, lims, 'k-', alpha=0.75, zorder=0)
    # ax.set_aspect('equal')
    # ax.set_xlim(lims)
    # ax.set_ylim(lims)

    # Marking ranges of interest and drawing an x=y line for scale
    for ax in (ax1, ax2):
        ax.axline((0, 0), slope=1)
        ax.axhline(y=10, color='r', linestyle='dashed')
        ax.axhline(y=0, color='r', linestyle='dashed')
        ax.axvline(x=20, color='r', linestyle='dashed')
        ax.axvline(x=50, color='r', linestyle='dashed')

    fig.savefig("scatter_{ha}_{fn}.png".format(ha=hash_alg, fn=fname), dpi=100)
    plt.show()

    return


# Function to create an output log for the selected hashing scheme
def process_file(input_file, ch):
    input_file_path = ".\p0f signatures\{}.log".format(input_file)
    # Read signatures from the input file
    f = open(input_file_path, '+r')
    lines = f.readlines()
    f.close()

    # Getting the right output file
    if ch == 1:
        output_file = open("tlsh_log.txt", 'w+')
    elif ch == 2:
        output_file = open("simhash_log.txt", 'w+')
    else:
        print("Invalid input. Exiting.\n")
        sys.exit(0)

    # number of modified signatures on which gap stats have been calculated
    num = 0

    # initialize gap stats accumulators
    mean_gap = 0
    var_gap = 0

    # initialize a list of locality data per signature
    crlist = []

    # lists for plotting
    delta_input_list = []
    delta_hash_list = []

    print("Please wait for the computation to be over...")

    for line in lines:
        sign = line.strip()
        output_file.write("Current sign: " + sign + '\n')
        sign_hash = compute_hash(sign, ch)
        # print(f"Processing {sign_hash}\n")
        for i in range(1, 20):
            mod_sign = rand_change(sign)

            # Calculating modified hash
            mod_sign_hash = compute_hash(mod_sign, ch)

            # Calculating locality, gap data
            change_ratio = change_per_pos(
                sign, mod_sign, sign_hash, mod_sign_hash, delta_input_list, delta_hash_list)
            (mean_gap, var_gap) = calculate_gap_stats(
                mean_gap, var_gap, num, sign_hash, mod_sign_hash)

            # Writing computed stats to file
            output_file.write(
                f"Modified sign no.{i}: \n Change ratio: {str(change_ratio)}, Gap stats mean: {mean_gap}, variance: {var_gap}\n")
            crlist.append(change_ratio)
            num += 1

    # Write aggregate stats in the output log
    output_file.write("Mean change ratio:" +
                      str(np.mean(crlist)) + "\n")
    output_file.write("Input distribution mean: " + str(np.mean(delta_input_list)
                                                        ) + " variance: " + str(np.var(delta_input_list)) + "\n")
    output_file.write("Output distribution mean: " + str(np.mean(delta_hash_list)
                                                         ) + " variance: " + str(np.var(delta_hash_list)) + "\n")

    output_file.close()

    # Plot the data
    get_plots(input_file, crlist, delta_input_list, delta_hash_list, ch)
    return


# main function
def main():
    # Get the name of the p0f signature file from command line
    filename = sys.argv[1]

    print("Choose the hashing algorithm to run:\n ")
    print(" 1. TLSH \n 2. simhash\n")
    ch = int(input("Enter choice:"))

    process_file(filename, ch)
    return


if __name__ == "__main__":
    main()
