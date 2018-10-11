#import unittests
from pymeteor import pymeteor

# Assert two strings with 0 matching words give a value of 0
def test_meteor0():
    reference = 'this is a test'
    candidate = 'i also am one'

    meteor_score = pymeteor.meteor(reference, candidate)
    
    assert meteor_score == 0

# All testing data gathered from Wikipedia article on METEOR
# https://en.wikipedia.org/wiki/METEOR    
def test_meteor1():
    reference = 'the cat sat on  the mat'
    candidate = 'on  the mat sat the cat'

    meteor_score = pymeteor.meteor(reference, candidate)
    print('meteor_score: %.4f'%meteor_score)
    assert meteor_score == 0.5

def test_meteor2():
    reference = 'the cat sat on the mat'
    candidate = 'the cat sat on the mat'

    meteor_score = pymeteor.meteor(reference, candidate)
    print('meteor_score: %.4f'%meteor_score)
    assert round(meteor_score, 4) == 0.9977

def test_meteor3():
    reference = 'the cat     sat on the mat'
    candidate = 'the cat was sat on the mat'

    meteor_score = pymeteor.meteor(reference, candidate)
    print('meteor_score: %.4f'%meteor_score)
    assert round(meteor_score, 4) == 0.9654


