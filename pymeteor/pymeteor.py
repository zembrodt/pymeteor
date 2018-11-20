# PyMETEOR
# Python implementation of METEOR.

import collections
import copy
import itertools
import random
from collections import namedtuple
import time

# Constant indexes for accessing points and lines
X = 0
Y = 1
POINT1 = 0
POINT2 = 1

# Defines a cartesian point
def Point(x, y):
    return (x, y)
# Defines a cartesian line segment
def Line(line1, line2):
    return (line1, line2)

# Point methods
def cross_product(point1, point2):
    return point1[X] * point2[Y] - point1[Y] * point2[X]
# Subtract a point from itself
def subtract(point1, point2):
    return Point(point1[X] - point2[X], point1[Y] - point2[Y])
# Check if two points have the same values
def equals(point1, point2):
    return point1[X] == point2[X] and point1[Y] == point2[Y]

# Line methods
def parallel(line1, line2):
    # Return false if line1 == line2:
    if equals(line1[POINT1], line2[POINT1]) and equals(line1[POINT2], line2[POINT2]):
        return False

    r = subtract(line1[POINT2], line1[POINT1])
    s = subtract(line2[POINT2], line2[POINT1])

    return cross_product(r, s) == 0

# Intersection of two line segments
def intersects(line1, line2):
    # Get the difference between the points on each line
    r = subtract(line1[POINT2], line1[POINT1])
    s = subtract(line2[POINT2], line2[POINT1])

    numerator = cross_product(subtract(line2[POINT1], line1[POINT1]), r)
    denominator = cross_product(r, s)

    # Check if lines are collinear
    if numerator == 0 and denominator == 0:
        # Check if any of the endpoints are equal
        if equals(line1[POINT1], line2[POINT1]) or equals(line1[POINT1], line2[POINT2]) or \
                equals(line1[POINT2], line2[POINT1]) or equals(line1[POINT2], line2[POINT2]):
            return True
        x_check = [line2[POINT1][X] - line1[POINT1][X] < 0,
                    line2[POINT1][X] - line1[POINT2][X] < 0,
                    line2[POINT2][X] - line1[POINT1][X] < 0,
                    line2[POINT2][X] - line1[POINT2][X] < 0]
        y_check = [line2[POINT1][Y] - line1[POINT1][Y] < 0,
                    line2[POINT1][Y] - line1[POINT2][Y] < 0,
                    line2[POINT2][Y] - line1[POINT1][Y] < 0,
                    line2[POINT2][Y] - line1[POINT2][Y] < 0]

        return not (all(x_check) or all([not e for e in x_check])) or \
                not (all(y_check) or all([not e for e in y_check]))
    # Check if lines are parallel
    elif denominator == 0:
        return False

    u = numerator / denominator
    t = cross_product(subtract(line2[POINT1], line1[POINT1]), s) / denominator

    return t >= 0 and t <= 1 and u >= 0 and u <= 1
 
# Count the number of intersections between a list of Lines with each other
def _count_intersections(lines):
    return sum([1 for line1, line2 in itertools.combinations(lines, 2) if intersects(line1,line2)])

# Maps the reference and candidate strings into indices and generates all their possible alignments
def _get_alignments(reference_unigrams, candidate_unigrams):
    # Create all mappings between unigrams in the reference string and the candidate string
    mapping = collections.defaultdict(list)
    for r, c in itertools.product(range(len(reference_unigrams)), range(len(candidate_unigrams))):
        if reference_unigrams[r] == candidate_unigrams[c]:
            mapping[r].append(c)
    # Convert the mapping into a list of all possible (key,value) pairs (where a value is one element within the mapping's values list)
    alignments = []
    keys, values = zip(*mapping.items())
    for v in itertools.product(*values):
        t=[Line(Point(item[0],0), Point(item[1],1)) for item in list(dict(zip(keys, v)).items())]
        alignments.append(t)
    return alignments

# Calculate how many chunks (as defined by METEOR) between the reference and candidate unigrams
def _calculate_chunks(reference_unigrams, candidate_unigrams):
    # Get all alignments between the unigrams
    alignments = _get_alignments(reference_unigrams, candidate_unigrams)
    # Find the alignment(s) with the minimum length
    min_alignment = None
    min_len = min(map(len, alignments))
    min_alignments = [alignment for alignment in alignments if len(alignment) == min_len]

    # If > 1 alignment, get the alignment with the fewest number of intersections
    if len(min_alignments) > 1:
        print('num of min_alignments: {}'.format(len(min_alignments)))
        # O(2^n) min_alignments...
        # THOUGHTS TO FIX
        # While initially counting the number of intersections, we can keep a tally of the current min intersection
        # count, and if the count goes above it, break from processing
            # Could still potentially not speed things up if every node has equal number of intersections
        # TODO: We will likely have to find a rough max estimate on this project being efficient
        # If the comparison will be greater than this limit, have a variable override to let users attempt to calculate
            # May run out of memory, TODO: figure out how to do alignment/intersection calculations with limited memory footprint?
        min_alignment = min(min_alignments, key=_count_intersections)
    elif len(min_alignments) == 1:
        min_alignment = min_alignments[0]
    else:
        return 0, 0

    # The number of unigrams that have been mapped
    mappings = len(min_alignment)
    
    # Chunk count is the number of consecutive lines within the alignment
    chunks = 1 # Default to 1 as the first line will always be a chunk
    alignment_iter = iter(min_alignment)
    next(alignment_iter)
    # Compare each line with the previous
    for prev, curr in zip(min_alignment, alignment_iter):
        if curr[POINT2][X] != prev[POINT2][X] + 1:
            chunks += 1
    return chunks, mappings

# Calculate the number of unigrams in the candidate translation also found in the reference translation
def _calculate_m(reference_unigrams, candidate_unigrams):
    return sum(1 for c_unigram in candidate_unigrams if c_unigram in reference_unigrams)

# Calculate unigram precision and unigram recall
def _unigram_precision_and_recall(reference_unigrams, candidate_unigrams):
    # m is the intersection of unigrams in candidate and reference (but not via sets?)
    m = _calculate_m(reference_unigrams, candidate_unigrams)
    # Calculate unigram precision:
    wt = len(candidate_unigrams) # number of unigrams in candidate
    precision = m / float(wt)
    # Calculate unigram recall
    wr = len(reference_unigrams) # number of unigrams in reference
    recall = m / float(wr)
    return precision, recall

# P: Unigram precision
# R: Unigram recall
# Output: F_mean
def _harmonic_mean(P, R):
    if P == 0 and R == 0:
        return 0
    else:
        return (10*P*R) / float(R+9*P)

# Calculates the penalty for the METEOR score
# ret_details=true returns the values for chunks and mappings as well
def _calculate_penalty(reference_unigrams, candidate_unigrams, ret_details=False):
    # Get the number of chunks and number of unigrams that have been mapped
    chunks, mappings = _calculate_chunks(reference_unigrams, candidate_unigrams)
    penalty_val = 0.5 * pow((chunks/float(mappings)), 3)
    if not ret_details:
        return (penalty_val,)
    else:
        return penalty_val, chunks, mappings

# Calculate METEOR score given f_mean and penalty values
def _calculate_meteor(f_mean, penalty):
    return f_mean * (1 - penalty)

# reference: the reference string, with each unigram separated by white space
# candidate: the candidate string, with each unigram separated by white space
# print_details: if the user wishes to receive more information on the METEOR score as stdout (default is False)
# Output: the METEOR score as a float
#   Note: if neither reference or candidate strings have a matching unigram, the score is 0
def meteor(reference, candidate, print_details=False):
    if print_details:
        print('Reference: "{}"'.format(reference))
        print('Candidate: "{}"'.format(candidate))
    
    reference_unigrams = reference.split()
    candidate_unigrams = candidate.split()
    reference_set = set(reference_unigrams)
    candidate_set = set(candidate_unigrams)
    if len(reference_set.intersection(candidate_set)) == 0:
        if print_details:   
            print('Reference and candidate sentences have no matching unigrams.')
        return 0.0
    P, R = _unigram_precision_and_recall(reference_unigrams, candidate_unigrams)
    f_mean = _harmonic_mean(P, R)
    penalty = _calculate_penalty(reference_unigrams, candidate_unigrams, ret_details=print_details)
    penalty_val = penalty[0]
    M = _calculate_meteor(f_mean, penalty_val)
    
    if print_details:
        chunks = penalty[1]
        mappings = penalty[2]
        fragmentation = chunks/float(mappings)
        print('Score: {:.4f} = Fmean: {:.4f} * (1 - Penalty: {:.4f})'.format(M, f_mean, penalty_val))
        print('Fmean: {0:.4f} = 10 * Precision: {1:.4f} * Recall: {2:.4f} / (Recall: {2:.4f} + 9 * Precision: {1:.4f})'.format(f_mean, P, R))
        print('Penalty: {:.4f} = 0.5 * (Fragmentation: {:.4f} ^3)'.format(penalty_val, fragmentation))
        print('Fragmentation: {:.4f} = Chunks: {:.4f} / Matches: {:.4f}'.format(fragmentation, chunks, mappings))
    return M

def main():
    # Current tests on limit for O(2^n) alignments
    r = 'he '
    c = "he a a"
    for i in range(200):
        if i%10 == 0:
            r+=('a '*10)
            print('i={}\nr={}\nc={}'.format(i,r,c))
            start = time.time()
            m = meteor(r, c, print_details=True)
            end = time.time()
            print('Execution time={:.4f}'.format(end-start))
    exit()
    # Old tests
    r += ('a '*200)
    r_old = "he 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd a 'd"
    c_old = "he gives us all a bad name and you know he 's not really even a ghost i say what are you all doing here ?"
    print('r={}\nc={}'.format(r,c))
    start = time.time()
    m = meteor(r, c, print_details=True)
    end = time.time()
    print('meteor={:.4f}'.format(m))
    print('Execution time={:.4f}'.format(end-start))
    exit()
    r = ''
    c = ''
    with open('pymeteor/test_data.txt') as f:
        i = 0
        for line in f.readlines():
            if i == 0:
                r = line.strip()
            elif i == 1:
                c = line.strip()
            i += 1
    print('r={}\nc={}'.format(r,c))
    m = meteor(r, c, print_details=True)
    print('meteor={:.4f}'.format(m))
    print('Execution time={:.4f}'.format(end-start))

if __name__ == '__main__':
    main()