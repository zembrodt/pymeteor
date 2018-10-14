# PyMETEOR
# Python implementation of METEOR.

import copy
import random
from numpy.linalg import det

# Defines a Cartesian point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return '(%d, %d)'%(self.x, self.y)

    def cross_product(self, point):
        return self.x * point.y - self.y * point.x
    def subtract(self, point):
        return Point(self.x - point.x, self.y - point.y)
    def equals(self, point):
        return self.x == point.x and self.y == point.y

# Defines a Cartesian line made of two Points.
class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
    def __repr__(self):
        return '<%s, %s>'%(self.point1, self.point2)

    def intersects(self, line):
        # Get the difference between the points on each line
        r = self.point2.subtract(self.point1)
        s = line.point2.subtract(line.point1)

        u_numerator = line.point1.subtract(self.point1).cross_product(r)
        denominator = r.cross_product(s)

        # Check if lines are collinear
        if u_numerator == 0 and denominator == 0:
            # Check if any of the endpoints are equal
            if self.point1.equals(line.point1) or self.point1.equals(line.point2) or self.point2.equals(line.point1) or self.point2.equals(line.point2):
                return True
            x_check = [line.point1.x - self.point1.x < 0, line.point1.x - self.point2.x < 0, line.point2.x - self.point1.x < 0, line.point2.x - self.point2.x < 0]
            y_check = [line.point1.y - self.point1.y < 0, line.point1.y - self.point2.y < 0, line.point2.y - self.point1.y < 0, line.point2.y - self.point2.y < 0]

            return not (all(x_check) or all([not e for e in x_check])) or not (all(y_check) or all([not e for e in y_check]))
        # Check if lines are parallel
        elif denominator == 0:
            return False

        u = u_numerator / denominator
        t = line.point1.subtract(self.point1).cross_product(s) / denominator

        return t >= 0 and t <= 1 and u >= 0 and u <= 1
    
# Find all alignments between two sentences
def _count_intersections(lines):
    intersection_count = 0
    for i, line1 in enumerate(lines):
        j = i+1
        while j < len(lines):
            if line1.intersects(lines[j]):
                intersection_count += 1
            j += 1
    return intersection_count

# Iterate over each one, count number of assignments
def _create_map(reference, candidate):
    _map = {}
    for i in range(len(reference)):
        for j in range(len(candidate)):
            if reference[i] == candidate[j]:
                if i in _map:
                    _map[i].append(j)
                else:
                    _map[i] = [j]
    return _map

# Recursive function
# Generates all possible alignments between the candidate and reference strings passed in _create_alignments
def _generate_alignments(_map, keys):
    alignments = []
    curr_alignment = []
    # Used for if we are in a recursive call, we want to remove any duplicates of the inital value
    if len(keys) > 1 and len(_map[keys[0]]) == 1:
        value = _map[keys[0]][0]
        for key in keys[1:]:
            if value in _map[key]:
                _map[key].remove(value)
    for i, key in enumerate(keys):
        if len(_map[key]) == 1:
            curr_alignment.append(Line(Point(key,0), Point(_map[key][0],1)))
        elif len(_map[key]) > 1:
            for v in _map[key]:
                map_temp = copy.deepcopy(_map)
                map_temp[key] = [v]
                temp_alignments = _generate_alignments(map_temp, keys[i:])
                for alignment in temp_alignments:
                    alignments.append(curr_alignment + alignment)
            return alignments
    if len(curr_alignment) > 0:
        alignments.append(curr_alignment)
    return alignments

# Starts initial call of _generate_alignments
# Maps the reference and candidate strings into indices and generates all their possible alignments
def _create_alignments(reference, candidate):
    _map = _create_map(reference.split(), candidate.split())
    return _generate_alignments(_map, list(_map))

# Input:  reference, candidate strings
# Output: chunks, mappings
def _calculate_chunks(reference, candidate):
    alignments = _create_alignments(reference, candidate)

    # Return the alignment with lowest assignment number
    min_alignments = []
    min_alignment = None
    min_len = None
    for alignment in alignments:
        length = len(alignment)
        if min_len is None or length < min_len:
            min_len = length
            min_alignments = [alignment]
        elif length == min_len:
            min_alignments.append(alignment)

    # If > 1 alignment, iterate over each, convert to lines on a graph, count intersections
    if len(min_alignments) > 1:
        min_intersections = None
        min_intersection_alignments = []
        for alignment in min_alignments:
            intersections = _count_intersections(alignment)
            if min_intersections is None or intersections < min_intersections:
                min_intersections = intersections
                min_intersection_alignments = [alignment]
            elif intersections == min_intersections:
                min_intersection_alignments.append(alignment)
        # Return alignment with lowest number of intersections
        if len(min_intersection_alignments) > 0:
            # If > 1 alignment, return one at random
            min_alignment = random.choice(min_intersection_alignments)
    elif len(min_alignments) == 1:
        min_alignment = min_alignments[0]

    # Calculate chunk count and mappings from the minimum alignment
    # Mappings is the number of lines within the alignment
    mappings = len(min_alignment)
    
    # Chunk count is the number of consecutive lines within the alignment
    chunks = 0
    prev_val = None
    for line in min_alignment:
        if prev_val is None or line.point2.x != prev_val + 1:
            chunks += 1
        prev_val = line.point2.x
    return chunks, mappings

# m: number of unigrams in the candidate translation also found in the reference translation
def _calculate_m(reference_unigrams, candidate_unigrams):
    m = 0
    for unigram in candidate_unigrams:
        if unigram in reference_unigrams:
            m += 1
    return m

# m: number of unigrams in the candidate translation also found in the reference translation
# wt: number of unigrams in the candidate translation
def _unigram_precision(reference, candidate):
    candidate_unigrams = candidate.split()
    m = _calculate_m(reference.split(), candidate_unigrams)
    wt = len(candidate_unigrams)
    
    return m / float(wt)

# m: number of unigrams in the candidate translation also found in the reference translation
# wr: number of unigrams in the reference translation
def _unigram_recall(reference, candidate):
    reference_unigrams = reference.split()
    m = _calculate_m(reference_unigrams, candidate.split())
    wr = len(reference_unigrams)

    return m / float(wr)


# P: Unigram precision
# R: Unigram recall
# Output: F_mean
def _harmonic_mean(P, R):
    if P == 0 and R == 0:
        return 0
    else:
        return (10*P*R) / float(R+9*P)

# c: number of chunks
# um: number of unigrams that have been mapped
def _calculate_penalty(reference, candidate, ret_details=False):
    chunks, mappings = _calculate_chunks(reference, candidate)
    penalty_val = 0.5 * pow((chunks/float(mappings)), 3)
    if not ret_details:
        return (penalty_val,)
    else:
        return penalty_val, chunks, mappings

# f_mean: the harmonic_mean
# penalty: the penalty calculated within calculate_penalty)
def _calculate_meteor(f_mean, penalty):
    return f_mean * (1 - penalty)

# reference: the reference string, with each unigram separated by white space
# candidate: the candidate string, with each unigram separated by white space
# print_details: if the user wishes to receive more information on the METEOR score as stdout (default is False)
# Output: the METEOR score as a float
#   Note: if neither reference or candidate strings have a matching unigram, the score is 0
def meteor(reference, candidate, print_details=False):
    if print_details:
        print('Reference: "%s"' % reference)
        print('Candidate: "%s"' % candidate)
        
    reference_set = set(reference.split())
    candidate_set = set(candidate.split())
    if len(reference_set.intersection(candidate_set)) == 0:
        if print_details:
            print('Reference and candidate sentences have no matching unigrams')
        return 0.0
    
    P = _unigram_precision(reference, candidate)
    R = _unigram_recall(reference, candidate)
    f_mean = _harmonic_mean(P, R)
    penalty = _calculate_penalty(reference, candidate, ret_details=print_details)
    penalty_val = penalty[0]
    M = _calculate_meteor(f_mean, penalty_val)
    
    if print_details:
        chunks = penalty[1]
        mappings = penalty[2]
        fragmentation = chunks/float(mappings)
        print('Score: %.4f = Fmean: %.4f * (1 - Penalty: %.4f)' % (M, f_mean, penalty_val))
        print('Fmean: %.4f = 10 * Precision: %.4f * Recall: %.4f / (Recall: %.4f + 9 * Precision: %.4f)' % (f_mean, P, R, R, P))
        print('Penalty: %.4f = 0.5 * (Fragmentation: %.4f ^3)' % (penalty_val, fragmentation))
        print('Fragmentation: %.4f = Chunks: %.4f / Matches: %.4f' % (fragmentation, chunks, mappings))
        print()
    return M
