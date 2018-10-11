"""
PyMETEOR
Python implementation of METEOR.
"""

from numpy.linalg import det
import copy
import random

# Defines a Cartesian point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return '(%d, %d)'%(self.x, self.y)

# Defines a Cartesian line made of two Points.
class Line:
    def __init__(self, point1, point2):
        self.point1 = point1
        self.point2 = point2
    def __repr__(self):
        return '<%s, %s>'%(self.point1, self.point2)
    def intersects(self, line):
        p_num1 = [[self.point1.x, self.point1.y], [self.point2.x, self.point2.y]]
        px_num2 = [[self.point1.x, 1], [self.point2.x, 1]]
        p_num3 = [[line.point1.x, line.point1.y], [line.point2.x, line.point2.y]]
        px_num4 = [[line.point1.x, 1], [line.point2.x, 1]]

        py_num2 = [[self.point1.y, 1], [self.point2.y, 1]]
        py_num4 = [[line.point1.y, 1], [line.point2.y, 1]]

        p_det1 = px_num2
        p_det2 = py_num2
        p_det3 = px_num4
        p_det4 = py_num4

        px_num = [[det(p_num1), det(px_num2)], [det(p_num3), det(px_num4)]]
        py_num = [[det(p_num1), det(py_num2)], [det(p_num3), det(py_num4)]]
        p_det = det([[det(px_num2), det(py_num2)], [det(px_num4), det(py_num4)]])

        # Lines are parallel
        if p_det == 0:
            return False
			
        px = det(px_num) / float(p_det)
        py = det(py_num) / float(p_det)
		
        # Check intersection is within the two lines
        # Check that x1 <= px <= x2 or y1 <= py <= y2
        if not ((self.point1.x <= px and px <= self.point2.x) or\
                (self.point1.y <= py and py <= self.point2.y)) or not\
                ((line.point1.x <= px and px <= line.point2.x) or\
                 (line.point1.y <= py and py <= line.point2.y)):
            return False
        return True

# Find all alignments between two sentences
def count_intersections(lines):
    intersection_count = 0
    for i, line1 in enumerate(lines):
        j = i+1
        while j < len(lines):
            if line1.intersects(lines[j]):
                intersection_count += 1
            j += 1
    return intersection_count

# Iterate over each one, count number of assignments
def create_map(r, c):
    m = {}
    for i in range(len(r)):
        for j in range(len(c)):
            if r[i] == c[j]:
                if i in m:
                    m[i].append(j)
                else:
                    m[i] = [j]
    return m

def generate_alignments(m, keys):
    alignments = []
    curr_alignment = []
    # Used for if we are in a recursive call, we want to remove any duplicates of the inital value
    if len(keys) > 1 and len(m[keys[0]]) == 1:
        value = m[keys[0]][0]
        for key in keys[1:]:
            if value in m[key]:
                m[key].remove(value)
    for i, key in enumerate(keys):
        if len(m[key]) == 1:
            curr_alignment.append(Line(Point(key,0), Point(m[key][0],1)))
        elif len(m[key]) > 1:
            for v in m[key]:
                m_temp = copy.deepcopy(m)
                m_temp[key] = [v]
                temp_alignments = generate_alignments(m_temp, keys[i:])
                for alignment in temp_alignments:
                    alignments.append(curr_alignment + alignment)
            return alignments
    if len(curr_alignment) > 0:
        alignments.append(curr_alignment)
    return alignments

def create_alignments(reference, candidate):
    m = create_map(reference.split(), candidate.split())
    return generate_alignments(m, list(m.keys()))

# Input:  reference, candidate strings
# Output: chunks, mappings
def calculate_chunks(reference, candidate):
    alignments = create_alignments(reference, candidate)

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
            intersections = count_intersections(alignment)
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
def calculate_m(reference_unigrams, candidate_unigrams):
    m = 0
    for unigram in candidate_unigrams:
        if unigram in reference_unigrams:
            m += 1
    return m

# m: number of unigrams in the candidate translation also found in the reference translation
# wt: number of unigrams in the candidate translation
def unigram_precision(reference, candidate):
    candidate_unigrams = candidate.split()
    m = calculate_m(reference.split(), candidate_unigrams)
    wt = len(candidate_unigrams)
    
    return m / float(wt)

# m: number of unigrams in the candidate translation also found in the reference translation
# wr: number of unigrams in the reference translation
def unigram_recall(reference, candidate):
    reference_unigrams = reference.split()
    m = calculate_m(reference_unigrams, candidate.split())
    wr = len(reference_unigrams)

    return m / float(wr)

# F_mean
def harmonic_mean(p, r):
    if p == 0 and r == 0:
        return 0
    else:
        return (10*p*r) / float(r+9*p)

# c: number of chunks
# um: number of unigrams that have been mapped
def calculate_penalty(reference, candidate, ret_details=False):
    chunks, mappings = calculate_chunks(reference, candidate)
    penalty_val = 0.5 * pow((chunks/float(mappings)), 3)
    if not ret_details:
        return (penalty_val,)
    else:
        return penalty_val, chunks, mappings

def calculate_meteor(f_mean, penalty):
    return f_mean * (1 - penalty)

def meteor(reference, candidate, print_details=False):
    if print_details:
        print('Reference: "%s"' % reference)
        print('Candidate: "%s"' % candidate)
        
    reference_set = set(reference.split())
    candidate_set = set(candidate.split())
    if len(reference_set.intersection(candidate_set)) == 0:
        if print_details:
            print('Reference and candidate sentences have no matching words')
        return 0.0
    
    P = unigram_precision(reference, candidate)
    R = unigram_recall(reference, candidate)
    f_mean = harmonic_mean(P, R)
    penalty = calculate_penalty(reference, candidate, ret_details=print_details)
    penalty_val = penalty[0]
    M = calculate_meteor(f_mean, penalty_val)
    
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
