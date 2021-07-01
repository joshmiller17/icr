import csv
from statsmodels.stats import inter_rater
import matplotlib.pyplot as plt
import numpy as np

LIST_OF_CODES = [""]
with open("csg-codes.txt") as f:
    for line in f.readlines():
        LIST_OF_CODES.append(line.rstrip())
data_columns = [2, 3, 5, 7, 8]
codes = {} # {row num : {coder : codes}}

def check_valid_data(data):
    if type(data) is dict:
        for k,v in data.items():
            check_valid_data(v)
        return
    if isinstance(data,list):
        for d in data:
            check_valid_data(d)
        return
    elif data not in LIST_OF_CODES:
        print("Bad code:", data)

def unit_test(code = None):
    global codes, LIST_OF_CODES
    """Unit test for percent agreement"""
    codes = {}
    LIST_OF_CODES = ["A", "B", "C"]
    codes["0"] = {"C1":[["A","B"], ["B","A"]], "C2":[["B","A"], ["A","B"]]}
    codes["1"] = {"C1":[["A","B"], ["B","A"]], "C2":[["B","A"], ["B","C"]]}
    codes["2"] = {"C1":[["A","B"], ["B","A"]], "C2":[["B","A"], ["C","B"]]}
    codes["3"] = {"C1":[["A","C"], ["B","A"]], "C2":[["B","A"], ["A","B"]]}
    codes["4"] = {"C1":[["C","B"], ["C","A"]], "C2":[["C","A"], ["B","A"]]}
    
    print("Percent agreement")
    result = percent_agreement(code, debug=True)
    print(result)
    print("Passed!" if (result == .6) else "FAILED")
    
    print("Fleiss's Kappa")
    result = fleiss_kappa(debug=True)
    print(result) # should be -.21703 when all are uncommented
    print("Passed!" if (result < -.217 and result > -.2175) else "FAILED")

def read_codes(filename, coder):
    global codes
    with open(filename) as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader) # skip header
        row_count = 1
        for row in reader:
            data = []
            for i in range(len(row)):
                if i in data_columns:
                    row[i] = row[i].replace(' ', '')
                    row[i] = row[i].replace('/', '')
                    row[i] = row[i].upper()
                    row[i] = row[i].split(',')
                    if not isinstance(row[i], list):
                        row[i] = [row[i]]
                    data.append(row[i])
            if str(row_count) not in codes:
                codes[str(row_count)] = {}
            codes[str(row_count)][coder] = data
            row_count += 1
        
def count_data(data, code = None):
    """Helper function that counts the number of data points in an arbitrary list of lists"""
    if isinstance(data,list):
        sum = 0
        for d in data:
            sum += count_data(d, code=code)
        return sum
    if data != '' and data != 'NA':
        if code == None or data == code:
            return 1
    return 0
    
def confusion_matrix():
    # rows are codes, columns are codes
    # cells are a count of how many times both codes existed across all 3 coders
    # (for diagonals, count only if it occurs at least twice -- agreement)
    # only count one side of the symmetric matrix
    
    # init matrix
    matrix = []
    length = len(LIST_OF_CODES)
    for n in range(length):
        matrix.append([0] * length)
    
    for row_num, row_dict in codes.items():
        row = list(row_dict.values())
        num_coders = len(row)
        num_cols = len(row[0])
        
        for c in range(num_cols):
            
            all_codes_this_cell = []
            for coder in row:
                all_codes_this_cell += coder[c]
        
            for i in range(length):
                for j in range(length):
                    #if i >= j:
                    if i == j:
                        if count_data(all_codes_this_cell, code = LIST_OF_CODES[i]) >= 2:
                            matrix[i][j] += 1
                    else:
                        if LIST_OF_CODES[i] in all_codes_this_cell and LIST_OF_CODES[j] in all_codes_this_cell:
                            matrix[i][j] += 1
                                
    return matrix


def fleiss_kappa(debug = False):
    # each row is an entry in our data
    # each column is a code category
    # the number in each cell is how many raters put that code for that entry
    array_data = []
    
    for row_num, row_dict in codes.items():
        # row_dict = coder : code
        keys = row_dict.keys()
        num_rows = len(row_dict[list(row_dict.keys())[0]]) # dense, but this sizes the row properly using the first key as an example for how long each list is
        temp_array = []
        for n in range(num_rows):
            temp_array.append([0] * len(LIST_OF_CODES))
        for i in range(len(LIST_OF_CODES)):
            for key in keys:
                for col in range(len(row_dict[key])):
                    if LIST_OF_CODES[i] in row_dict[key][col]:
                        if debug:
                            print(key, col, row_dict[key][col], i, LIST_OF_CODES[i])
                        temp_array[col][i] += 1
        for n in range(num_rows):
            if debug:
                print(temp_array[n])
            array_data.append(temp_array[n])
        
    if debug:
        print(array_data)
        with open('fleiss.txt', 'w') as f:
            for row in array_data:
                f.write(str(row))
                f.write('\n')
        
    return inter_rater.cohens_kappa(array_data)
        
def percent_agreement(code = None, debug = False, summary = False):
    agreements = 0
    disagreements = 0
    for row_num, row_dict in codes.items():
        row = list(row_dict.values())
        num_coders = len(row)
        num_cols = len(row[0])
        agree_this_row = 0
        for c in range(num_cols):
            col = [r[c] for r in row]
            agree_set = set(col[0]).intersection(*col[1:])
            agree_set.discard('')
            agree_set.discard('NA')
            if code is not None:
                l = [s for s in agree_set]
                for s in l:
                    if s != code:
                        agree_set.discard(s)
            agree_this_col = len(agree_set)
            agree_this_row += agree_this_col
        agreements += agree_this_row
        disagree_this_row = count_data(row, code=code) - (num_coders * agree_this_row)
        disagreements += disagree_this_row
        if debug:
            print("Row is",row)
            print("Agree:", agree_this_row)
            print("Disagree:", disagree_this_row)
    if agreements + disagreements == 0:
        percent = 1
    else:
        percent = 1.0 * agreements / (agreements + disagreements)
    if debug or summary:
        print("Agreements", agreements)
        print("Disagreements", disagreements)
    return percent
    
def summary():
    print("Overall:" + str(percent_agreement(code = None, debug = False, summary = True)))

    for c in LIST_OF_CODES:
        print(c + ":" + str(percent_agreement(code = c, debug = False, summary = True)))


#unit_test()
read_codes('C1-v3.tsv', 'c1')
read_codes('C2-v3.tsv', 'c2')
read_codes('C3-v3.tsv', 'c3')
check_valid_data(codes)

code_length = 3
with open('confusion_matrix.txt', 'w') as f:
    matrix = confusion_matrix()
    matrix[len(matrix)-1][0] = 0 # TODO remove when we get to the end of coding
    matrix[0][len(matrix)-1] = 0 # TODO remove when we get to the end of coding
    f.write('\t')
    for r in range(len(matrix)):
        f.write(LIST_OF_CODES[r][:code_length] + '\t')
    f.write('\n')
    for r in range(len(matrix)):
        f.write(LIST_OF_CODES[r][:code_length] + '\t')
        for cell in matrix[r]:
            f.write(str(cell))
            f.write('\t')
        f.write('\n')
    plt.imshow(matrix, cmap='plasma')
    plt.xticks(range(len(matrix)), LIST_OF_CODES, rotation=75)
    plt.yticks(range(len(matrix)), LIST_OF_CODES)
    plt.show()

#print("Fleiss' Kappa: ", str(fleiss_kappa(debug = True)))

summary() # percent agreements
