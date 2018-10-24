# PyMETEOR
# Python implementation of METEOR.

import collections
import copy
import itertools
import random

# Defines a Cartesian point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return '(%d, %d)'%(self.x, self.y)
    # Calculate the cross product with another point
    def cross_product(self, point):
        return self.x * point.y - self.y * point.x
    # Subtract a point from itself
    def subtract(self, point):
        return Point(self.x - point.x, self.y - point.y)
    # Check if two points have the same values
    def equals(self, point):
        return self.x == point.x and self.y == point.y

# Defines a Cartesian line segment made of two Points.
class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
    def __repr__(self):
        return '<%s, %s>'%(self.point1, self.point2)
    # Intersection of two line segments
    def intersects(self, line):
        # Get the difference between the points on each line
        r = self.point2.subtract(self.point1)
        s = line.point2.subtract(line.point1)

        numerator = line.point1.subtract(self.point1).cross_product(r)
        denominator = r.cross_product(s)

        # Check if lines are collinear
        if numerator == 0 and denominator == 0:
            # Check if any of the endpoints are equal
            if self.point1.equals(line.point1) or self.point1.equals(line.point2) or \
                    self.point2.equals(line.point1) or self.point2.equals(line.point2):
                return True
            x_check = [line.point1.x - self.point1.x < 0,
                       line.point1.x - self.point2.x < 0,
                       line.point2.x - self.point1.x < 0,
                       line.point2.x - self.point2.x < 0]
            y_check = [line.point1.y - self.point1.y < 0,
                       line.point1.y - self.point2.y < 0,
                       line.point2.y - self.point1.y < 0,
                       line.point2.y - self.point2.y < 0]

            return not (all(x_check) or all([not e for e in x_check])) or \
                    not (all(y_check) or all([not e for e in y_check]))
        # Check if lines are parallel
        elif denominator == 0:
            return False

        u = numerator / denominator
        t = line.point1.subtract(self.point1).cross_product(s) / denominator

        return t >= 0 and t <= 1 and u >= 0 and u <= 1
    
# Count the number of intersections between a list of Lines with each other
def _count_intersections(lines):
    return sum([1 for line1, line2 in itertools.combinations(lines, 2) if line1.intersects(line2)])

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
        alignments.append([Line(Point(item[0],0), Point(item[1],1)) for item in list(dict(zip(keys, v)).items())])
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
        if curr.point2.x != prev.point2.x + 1:
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
