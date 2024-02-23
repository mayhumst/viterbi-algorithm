# viterbi-algorithm
My implementation of Viterbi algorithm for POS tagging in NLP


This is an implementation of a dynamic Viterbi algorithm to tag the part of speech of each word in a sentence. The algorithm follows these steps:

1. Parse the training/development file once, adding each unique word and tag to an array of words and tags, and sort each array 
every time a new word or tag is added. This allows for binary search to be used during and after the initial parsing steps. 

2. Create an emission table (a nested array of size len(words) x len(tags)) and a transition table (nested array of size 
len(tags)+1 x len(tags)+1; The extra index will be for the <start> "tag" in the rows and the <end> tag in the columns). Populate both arrays with zeros. 

3. Parse the training/development file again line by line, incrementing each correct emission/transition table entry by one. 

4. Go through the emission table, calculate each column total, and replace each raw value with the percentage of the column total. 
Repeat this for the transition table, but with row totals. 

5. [EXTRA] Export the tables to excel spreadsheets (currently commented out). This could make previously calculated data easier/faster
to import and add to. 

6. Open the untagged test file for parsing. Parse line by line until the end of a sentence is reached, then send that sentence to 
the recursive calculation function. 

7. Calculate the highest probability path (tag sequence) using a recursive, dynamic algorithm with input of the full sentence and 
number of words in the sentence (n). Get the path probabilities of the last n-1 words, then use those probabilities to calculate 
the path probabilities of the last n words in the sentence and return those values. 

The base case is n=1, where the algorithm calculates an array of initial probabilities of len(tags), where the each entry of probabilities[]
corresponds to the same index in tags[], and each probability entry is the emission probability of the last word in the sentence having
that tag muliplied by the transition probability from that tag to the <end> tag (end of sentence). 

For all cases where n>1: for each tag (t)-- multiply each of the previously calculated probabilities by the new emission probability for the 
current word with tag t and the correct transition probability. Take the max of these probabilities and add this to a new probability 
array at index t. Because we're only interested in bigrams, we only need the highest path that leads to the current tag. In other words,
the probability that the (n)th word has a specific tag is not dependent on the (n+2)th tag, so we can disregard all but the most 
probable path to the (n+1)th tag. 

As these probabilities are calculated and the max is chosen, store the path to that tag in a constantly updated array of paths. 

8. Once these final probabilities are recursively calculated, the result is an array of size len(tags) with the highest probable path 
that leads to each tag. The last step is to multiply each of these probabilities by the transition probability from <start> to each 
unique corresponding tag t. 

9. Iterate through the final probability array and find the index that contains the maximum probability value. That index is the index 
of the first tag of the sentence, or the tag of the first word. This also means that the path stored in the paths array at this index is 
the correct path. Iterate through the sentence and the path to write line by line to the output file. 

**Note: The algorithm may encounter words that were not present in the training files. This word would be considered Out Of Vocabulary (OOV). 
While there are many ways to handle this, the easiest is to give a constant value for the emission probability of every tag for this word. 
I used a value of 1 for simplicity. Other methods for OOV words may yield better results. 

**Note 2: When parsing the file originally and storing/checking each new word, I used the lowercase version of all words regardless 
of their position in a sentence. Theoretically, this will result in fewer OOV words; while the word "average" may be found in the 
training data many times, the word "Average", found at the beginning of a sentence, won't be. However, this may make the algorithm less 
accurate for words that are capitlized on purpose (acronyms, proper nouns). I tested both methods on the testing file, and preserving
the original capitalization of the words actually yielded better results. 
My original implementation (convert all to lowercase) yielded an accuracy score of 9.423647, with 53417 out of 56684 tags correct. 
The new implementation (maintain original capitalization) yielded an accuracy score of 9.534789, with 54047 out of 56684 tags correct.

**Note 3: Although dynamically programmed, this program is still relatively slow. I have made efforts to speed it up, including 
implementing binary search and skipping unnecessary calculations of previous probabilities and transition probabilities if the emission
probability for a potential tag is found to be 0. Both of these sped up the algorithm significantly. 

**Note 4: Although to my knowledge the testing file contained no sentences long enough to encounter this problem, some tests may 
yield probabilities small enough to go out of bounds of python's minimum float value. Ideally, the algorithm would constantly normalize 
the probabilities such that the largest probability is always greater than 1 and less than 10. Essentially, the algorithm would
periodically multiply all calculated probabilities in the array by ten (or some other constant) to keep the probabilities at reasonable 
values. My implementation does not yet do this. 