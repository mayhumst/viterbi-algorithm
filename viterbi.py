
import os
import math
import pandas
from pandas import DataFrame
from pandas import ExcelWriter

# See README for complete explanation - basic logic: 

# go through traning corpus and development corpus TWICE
# FIRST TIME: gather each unique word and tag into arrays, sort and bin search as you go
# SECOND TIME: update transition and emission tables 
# Go through emission and transition tables and update percentages
# Go through TESTING corpus SENTENCE BY SENTENCE - apply dynamic programming implementation of Viterbi's Algorithm
# determine highest probability tag sequence, write sentence + tags to output file

"""         TRANSITION TABLE FORMAT                   EMISSION TABLE FORMAT

            tag1  tag2  tag3  *end*                   tag1  tag2  tag3  tag4
        tag1                                   word1
        tag2                                   word2
        tag3                                   word3
        *start*                                word4

"""

words = []
tags = []
emissionTable = []
transitionTable = []
paths = []


def my_bin_search(arr, item):
    # This is an implementation of binary search, used to quickly find the index of specific words or tags of interest
    # Returns -1 if the array does not contain the item of interest

    lower = 0
    upper = len(arr)-1
    ret = -1

    while upper >= lower:
        middle = math.floor((upper+lower)/2)
        if arr[middle] == item:
            ret = middle
            break
        elif item < arr[middle]:
            upper = middle -1
        else:
            lower = middle +1
    return ret

def parse_lines1(lines):
    ###### function that parses file and updates word and tag lists

    n = 0
    for line in lines: 
            
        line = line.rstrip('\n')
        # reading each word line: split into "words", which is word and tag     
        wordies = line.split()
        if len(wordies) == 0:
            continue

        ###### BINARY SEARCH FOR THE WORD: ADD IF NEW AND SORT
        if n == 0:
            words.append(wordies[0]) ## right here
            n = n+1
        else:
            find = my_bin_search(words, wordies[0])
            if find < 0:
                words.append(wordies[0])
                words.sort()
                n = n+1        

        ####### REGULAR LINEAR SEARCH FOR TAGS: ADD IF NEW 
        app = 0
        for thisTag in tags:
            if thisTag == wordies[1]:
                app = 1
                break
        if app == 0:
            tags.append(wordies[1])
    
    tags.sort()
    words.sort()  

def parse_lines2(lines):
    ###### function that parses file and updates emission and transition tables

    # first line
    line = lines[0].rstrip('\n')
    curr_token = line.split()
    
    if len(line) > 0:
        find_tag_index = my_bin_search(tags, curr_token[1])
        transitionTable[len(tags)][find_tag_index] = transitionTable[len(tags)][find_tag_index] +1
    # all lines
    for index in range(1, len(lines)):
        line = lines[index-1].rstrip('\n')
        nextline = lines[index].rstrip('\n')
        curr_token = line.split()
        next_token = nextline.split()
        
        # three cases: is blank line and has next, is real line and has next, is real line and does NOT have next
        if len(line) == 0:
            # just before first token in sentence: update transition table
            find_tag_index = my_bin_search(tags, next_token[1])
            transitionTable[len(tags)][find_tag_index] = transitionTable[len(tags)][find_tag_index] +1
        elif len(nextline) == 0:
            # last token in sentence: update emission and transition
            find_index_bin = my_bin_search(words, curr_token[0])
            find_tag_index = my_bin_search(tags, curr_token[1])
            emissionTable[find_index_bin][find_tag_index] = emissionTable[find_index_bin][find_tag_index] + 1
            transitionTable[find_tag_index][len(tags)] = transitionTable[find_tag_index][len(tags)] +1
        else:
            # middle token in sentence: update emission and transition tables
            find_index_bin = my_bin_search(words, curr_token[0])
            find_tag_index = my_bin_search(tags, curr_token[1])
            find_next_tag_index = my_bin_search(tags, next_token[1])
            emissionTable[find_index_bin][find_tag_index] = emissionTable[find_index_bin][find_tag_index] + 1
            transitionTable[find_tag_index][find_next_tag_index] = transitionTable[find_tag_index][find_next_tag_index] +1
    # last line
    line = lines[len(lines) - 1].rstrip('\n')
    curr_token = line.split()
    if len(line) > 0:
        find_index_bin = my_bin_search(words, curr_token[0])
        find_tag_index = my_bin_search(tags, curr_token[1])
        emissionTable[find_index_bin][find_tag_index] = emissionTable[find_index_bin][find_tag_index] + 1
        transitionTable[find_tag_index][len(tags)] = transitionTable[find_tag_index][len(tags)] +1

def calculate_probs(num, sentence):
    # RECURSIVE DYNAMIC ALGORITHM
    # given a sentence and number of words in a sentence, return the array of probabilities of each possible tag sequence 
    # see README for full description
    newprobs = []
    newpaths = []

    # base case: last word in sentence
    if num == 1:
        for i in range(0, len(tags)):
            paths.append([i])
        
        for tag_index in range(0, len(tags)):
            find_index_bin = my_bin_search(words, sentence[len(sentence)-num])
            if find_index_bin < 0:
                e_prob = 1
            else:
                e_prob = emissionTable[find_index_bin][tag_index]
            
            # Transition probability from this tag to <end> (end of sentence)
            t_prob = transitionTable[tag_index][len(tags)]
            
            newprobs.append( e_prob*t_prob ) 
        
        return newprobs
    
    # recursive call
    probs = calculate_probs(num-1, sentence)

    for tag_index in range(0, len(tags)):
        max_prob = 0
        max_prob_index = -1

        # calc emission prob
        find_index_bin = my_bin_search(words, sentence[len(sentence)-num])
        if find_index_bin < 0:
            e_prob = 1
        else:
            e_prob = emissionTable[find_index_bin][tag_index]

        # if emission prob is zero, don't bother looping, all probabilities will be zero
        if e_prob == 0:
            max_prob = 0
            max_prob_index = 0
            newprobs.append(max_prob)
            newpaths.append( [tag_index] + paths[max_prob_index] )
            continue
        
        for prob_index in range(0, len(probs)):
                            
            # calc transition prob
            t_prob = transitionTable[tag_index][prob_index]

            if probs[prob_index] * e_prob * t_prob > max_prob:
                max_prob = probs[prob_index] * e_prob * t_prob
                max_prob_index = prob_index # tag index of the most probable next tag
        newprobs.append(max_prob)
        newpaths.append( [tag_index] + paths[max_prob_index] )

    # update each stored path  
    for i in range(0, len(paths)):
        paths[i] = newpaths[i]
    
    return newprobs

def get_tag_sequence(sentence, probs):
    # given probability array, find the max (most probable path) and determine the corresponding tag sequence

    max = 0
    max_index = 0 # index of tag sequence with max probability

    # find largest probability and its index
    for i in range(0, len(probs)):
        if probs[i] > max:
            max = probs[i]
            max_index = i

    tag_seq_indices = paths[max_index]
    tag_seq = []
    for ind in tag_seq_indices:
        tag_seq.append(tags[ind])

    # return array of tag sequence
    return tag_seq


#######
# add each word and tag to initial arrays
######
        
f = open("training-files/WSJ_02-21.pos", 'r')
lines = f.readlines()
f.close()
parse_lines1(lines)
f = open("training-files/WSJ_24.pos", 'r')
lines = f.readlines()
f.close()
parse_lines1(lines)
    
# add empty arrays to emission table: number of arrays = number of words, size of arrays is number of tags
x = len(words)
y = len(tags)
while x > 0:
    emissionTable.append([0]*y)
    x = x-1
    
# add empty arrays to transition table: number of arrays = number of tags + 1, size of arrays is number of tags + 1
x = len(tags) + 1
y = len(tags) + 1
while x > 0:
    transitionTable.append([0]*y)
    x = x-1

######
###### FOR EACH WORD: update emission table and transition table 
######

f = open("training-files/WSJ_02-21.pos", 'r')
lines = f.readlines()
f.close()
parse_lines2(lines)
f = open("training-files/WSJ_24.pos", 'r')
lines = f.readlines()
f.close()
parse_lines2(lines)


###### EXCEL SHEETS

# visualize raw emission values 
todo = {}
row_tot = [0]*(len(tags)+1)
row_tot[len(tags)] = " "
for i in range(0, len(emissionTable)):
    tot = 0
    for j in range(0, len(emissionTable[i])):
        tot = tot + emissionTable[i][j]
        row_tot[j] = row_tot[j] + emissionTable[i][j]
    todo[words[i]] = emissionTable[i] + [tot]
todo["TOTAL"] = row_tot
df1 = DataFrame(todo, index=tags+["TOTAL"])

# visualize raw transition values 
todo = {}
modtags = tags + ["START"]
row_tot = [0]*(len(tags)+2)
row_tot[len(tags) + 1] = " "
for i in range(0, len(transitionTable)):
    tot = 0
    for j in range(0, len(transitionTable[i])):
        tot = tot + transitionTable[i][j]
        row_tot[j] = row_tot[j] + transitionTable[i][j]
    todo[modtags[i]] = transitionTable[i] + [tot]
todo["TOTAL"] = row_tot
df2 = DataFrame(todo, index=tags+["END", "TOTAL"])


######
# calculate probabilities of transition and emission tables
######

# emission: divide number by total in tag COL
for tagnum in range(0, len(tags)):
    col_tot = 0
    # iterate through each word arr to calculate column total
    for word in emissionTable:
        col_tot = col_tot + word[tagnum]
    # iterate again to calculate float probs
    for rownum in range(0, len(emissionTable)):
        emissionTable[rownum][tagnum] = emissionTable[rownum][tagnum] / col_tot


# transition: divide number by total in tag ROW
this_row = 0
for row in transitionTable:
    row_tot = 0
    for num in row:
        row_tot = row_tot + num
    for num in range(0, len(tags) + 1):
        transitionTable[this_row][num] = row[num] / row_tot
    this_row = this_row +1


###### EXCEL SHEETS


# visualize calculated transition values 
todo = {}
modtags = tags + ["START"]
row_tot = [0]*(len(tags)+2)
row_tot[len(tags) + 1] = " "
for i in range(0, len(transitionTable)):
    tot = 0
    for j in range(0, len(transitionTable[i])):
        tot = tot + transitionTable[i][j]
        row_tot[j] = row_tot[j] + transitionTable[i][j]
    todo[modtags[i]] = transitionTable[i] + [tot]
todo["TOTAL"] = row_tot
df4 = DataFrame(todo, index=tags+["END", "TOTAL"])

# visualize calculated emission values
todo = {}
row_tot = [0]*(len(tags)+1)
row_tot[len(tags)] = " "
for i in range(0, len(emissionTable)):
    tot = 0
    for j in range(0, len(emissionTable[i])):
        tot = tot + emissionTable[i][j]
        row_tot[j] = row_tot[j] + emissionTable[i][j]
    todo[words[i]] = emissionTable[i] + [tot]
todo["TOTAL"] = row_tot
df3 = DataFrame(todo, index=tags+["TOTAL"])

if os.path.exists("output/emission_transition_tables.xlsx"):
  os.remove("output/emission_transition_tables.xlsx")

with ExcelWriter("output/emission_transition_tables.xlsx") as writer:
    df1.transpose().to_excel(writer, sheet_name='emission_raw', index=True)
    df2.transpose().to_excel(writer, sheet_name='transition_raw', index=True)
    df3.transpose().to_excel(writer, sheet_name='emission_calc', index=True)
    df4.transpose().to_excel(writer, sheet_name='transition_calc', index=True)



###### 
# parse untagged testing file, output tagged results
######


# open development file, parse lines
f = open("untagged-files/WSJ_23.words", 'r')
lines = f.readlines()
f.close()
# open file for writing
if os.path.exists("output/output.pos"):
  os.remove("output/output.pos")

fwrite = open("output/output.pos", "w")

# for each sentence: turn sentence into an array and calculate the probabilities, then choose best path and write to file
this_sentence = []
for line in lines: 
    
    new_word = line.rstrip('\n')
    if (len(new_word) == 0 and len(this_sentence) > 0):
        # found end of sentence; apply algorithm calculation
        sentence_prob = calculate_probs(len(this_sentence), this_sentence)
        
        # one last multiplication: transition from <start> -> each first tag
        for prob_index in range(0, len(sentence_prob)):
            # calc transition prob
            t_prob = transitionTable[len(tags)][prob_index]
            sentence_prob[prob_index] = sentence_prob[prob_index] *t_prob

        these_tags = get_tag_sequence(this_sentence, sentence_prob)
        for i in range(0, len(this_sentence)):
            fwrite.write(this_sentence[i] + "\t" + these_tags[i] + "\n")
        fwrite.write("\n")
        
        # restart arrays for next sentence
        this_sentence = []
        paths = []
    elif len(new_word) > 0:
        this_sentence.append(new_word)


fwrite.close()
