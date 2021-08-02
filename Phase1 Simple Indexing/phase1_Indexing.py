import openpyxl
from pathlib import Path
import itertools
import language_lists
import csv
import collections

xlsx_file = Path('../IR_Spring2021_ph12_7k.xlsx')
wb_obj = openpyxl.load_workbook(xlsx_file)
sheet = wb_obj.active

data_size = 0
inverted_index = {}
dictionary = {}
tokens = []
docid_doc_mapping = {}
n_length = 4
for row in sheet.iter_rows():

    if row[0].value == 'id':
        continue
    terms = []
    term_doc = []
    line = row[1].value
    data_size = int(row[0].value)
    docid_doc_mapping[row[0].value] = row[2].value
    # NORMALIZATION
    for p in language_lists.punctuations:
        line = line.replace(p, " ")
    for e in language_lists.escape:
        line = line.replace(e, '')
    for n in language_lists.numbers:
        line = line.replace(n, '')
    for e in language_lists.englsih_chars:
        line = line.replace(e, '')
        line = line.replace(e.capitalize(), '')
    for en in language_lists.englsih_numbers:
        line = line.replace(en, '')
    for w in line.split(' '):
        if w != '':
            terms.append(w)
    for i in range(len(terms)):
        t = terms[i]

        # NORMALIZATION: remove post fix
        for ch in language_lists.post_fix:
            if t.endswith(ch):
                normalized_term = t[:(-1) * len(ch)]
                if len(normalized_term) >= n_length:
                    terms[i] = normalized_term
                    break

        # NORMALIZATION: remove pre fix
        for ch in language_lists.pre_fix:
            if t.startswith(ch):
                normalized_term = t[len(ch):]
                if len(normalized_term) >= n_length:
                    terms[i] = normalized_term
                    break

        # NORMALIZATION: verb stemming
        for (past, present) in zip(language_lists.past_stem, language_lists.present_stem):
            if past in t:
                for p in language_lists.past_pronoun:
                    # IDEA: DO NOT REMOVE ANYTHING BUT VERBS
                    if t == past + p or t == 'می' + past + p or t == past + 'ه' + 'بود' + p or t == 'خواه' + p + past:
                        terms[i] = past
                        break
            if present in t:
                for p in language_lists.present_pronoun:
                    if t == 'ب' + present + p or t == present + p or t == 'می' + present + p:
                        terms[i] = present
                        break

        # NORMALIZATION: multi form words
        for ch in language_lists.multi_form.keys():
            if t == ch:
                normalized_term = language_lists.multi_form.get(ch)
                terms[i] = normalized_term
                break

        # NORMALIZATION: arabic irregular
        for ch in language_lists.arabic_irregular_plural.keys():
            if t in inverted_index and t == ch:
                normalized_term = language_lists.arabic_irregular_plural.get(ch)
                break


    for w in terms:
        term_doc.append({'term': w, 'doc_id': int(row[0].value)})
    tokens.extend(term_doc)

# print(len(tokens))
# tokens = list(dict.fromkeys(tokens))
# print(tokens)

for t in tokens:
    word = t['term']
    doc_id = t['doc_id']
    frq = dictionary.get(word, 0)
    dictionary[word] = frq + 1

    doc_list = inverted_index.get(word, [])

    doc_list.append(doc_id)
    inverted_index[word] = doc_list


for i in inverted_index:
    inverted_index[i] = list(dict.fromkeys(inverted_index[i]))

inverted_index = collections.OrderedDict(sorted(inverted_index.items()))
# remove stop words
frq_sorted_dic = {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1])}
stop_words = dict(itertools.islice(reversed(frq_sorted_dic.items()), 20))
for s in stop_words:
    dictionary.pop(s)
    inverted_index.pop(s)

with open('dictionary.csv', 'w', encoding="utf-8", newline='') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in inverted_index.items():
        writer.writerow(key)
with open('inverted_index.csv', 'w', encoding="utf-8", newline='') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in inverted_index.items():
        writer.writerow(value)
with open('doc_id_mapping.csv', 'w', encoding="utf-8", newline='') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in docid_doc_mapping.items():
        writer.writerow([key, value])

with open('other.csv', 'w', encoding="utf-8", newline='') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow([n_length])

print(inverted_index)