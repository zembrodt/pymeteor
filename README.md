# PyMETEOR
Python implementation of METEOR.<br/>
This module is dependent on the following packages:
- nosetests (for testing only)

### References and credits
[METEOR: An Automatic Metric for MT Evaluation with
Improved Correlation with Human Judgments](https://www.cs.cmu.edu/~alavie/papers/BanerjeeLavie2005-final.pdf) by Satanjeev Banerjee and Alon Lavie.<br/>
[Wikipedia article](https://en.wikipedia.org/wiki/METEOR)

### Formulas
This program implements the formulas mentioned within the algorithm as separate functions.

Unigram precision *P* is calculated as:
>*P* = *m* / *w<sub>t</sub>*

Where *m* is the number of unigrams in the candidate string that are also found in the reference string, and *w<sub>t</sub>* is the number of unigrams in the candidate string.<br/>
In the program this is covered by `unigram_precision(reference, candidate)`

Unigram recall *R* is calculated as:
>*R* = *m* / *w<sub>r</sub>*

Where *m* is the same as above, and *w<sub>r</sub>* is the number of unigrams in the reference string.<br/>
In the program this is covered by `unigram_recall(reference, candidate)`<br/>

Unigram precision and recall are combined using the [harmonic mean](https://en.wikipedia.org/wiki/Harmonic_mean), with recall weighted 9 times more than precision, giving us *F<sub>mean</sub>* as follows:
>*F<sub>mean</sub>* = (10*P**R*) / (*R*+9*P*)

In the program this is covered by `harmonic_mean(P, R)`

The penalty *p* is calculated as:<br/>
>*p* = <sup>1</sup>&frasl;<sub>2</sub> (*c* / *u<sub>m</sub>*)<sup>3</sup>

Where *c* is the number of chunks, and *u<sub>m</sub>* is the number of unigrams that have been mapped.<br/>
In the program this is covered by `calculate_penalty(reference, candidate)`

The final score, *M*, is calculated as:
>*M* = *F<sub>mean</sub>* (1 - *p*)

In the program this is covered by `calculate_meteor(f_mean, penalty)`

### Mappings and chunks
The values for *c* and *u<sub>m</sub>*, used above in the penalty, are calculated in the function `calculate_chunks(reference, candidate)`

To do this, the program creates an alignment, or a set of mappings between unigrams within the two strings. *u<sub>m</sub>* is the length of this set of mappings. *c* is the amount of chunks in the alignment, where a chunk is a set of mappings where the unigrams are adjacent in both strings.<br/>
Below is an example of a reference and candidate string and their unigram's corresponding indices.

|  | 0 | 1 | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- | --- | --- |
| **reference** | the | cat | sat | on | the | mat | 
| **candidate** | on | the | mat | sat | the | cat |

Two possible alignments between these strings are:

<img src="https://upload.wikimedia.org/wikipedia/commons/2/27/METEOR-alignment-a.png" alt="Alignment A" height="87" />

<img src="https://upload.wikimedia.org/wikipedia/commons/7/78/METEOR-alignment-b.png" alt="Alignment B" height="87" /><br/>
*<sup>[Images linked from Wikipedia](https://en.wikipedia.org/wiki/METEOR)</sup>*

The difference between these examples are which "*the*" in the reference string is mapped with which "*the*" in the candidate string.

The METEOR algorithm calls for the alignment with the fewest amount of mappings to be chosen. Since both of these alignments have 6 mappings, we much choose the mapping that has the fewest amount of *intersections*. This is done by creating points on a graph for each word, with their X-value being their index in the string, and their Y-value corresponding with being in the reference or candidate string (0 or 1, for example). Illustrated above are the alignments with mappings drawn as lines. Calculating this, we can now count how many of these lines intersect.

In the above example, the first alignment will be chosen as it has 8 intersections, while the second alignment has 11 intersections. This gives us a final *c* value of 6, and a *u<sub>m</sub>* value of 6.

### License
This project is licensed under the MIT License, please see the [LICENSE](LICENSE) file for details.

### Author's note
Please feel free to notify me of any bugs in the code or improvements to be made. Thanks.
