import language_lists
import sys
import csv
import time
query = input("Search: ")
begin = time.time()
inverted_index = {}
dictionary = []
docid_doc_mapping = {}
with open('dictionary.csv', mode='r', encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        dictionary.append("".join(row))

with open('inverted_index.csv', mode='r', encoding="utf-8") as file:
    postings_list = [list(map(int, rec)) for rec in csv.reader(file, delimiter=',')]

i = 0
for w in dictionary:
    inverted_index[w] = postings_list[i]
    i += 1

with open('doc_id_mapping.csv', mode='r', encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        docid_doc_mapping[int(row[0])] = row[1:]

with open('other.csv', mode='r', encoding="utf-8") as file:
    reader = csv.reader(file)
    for r in reader:
        n_length = float(r[0])

# QUERY PROCESSING

for p in language_lists.punctuations:
    query = query.replace(p, " ")
for e in language_lists.escape:
    query = query.replace(e, '')
for n in language_lists.numbers:
    query = query.replace(n, '')
for e in language_lists.englsih_chars:
    query = query.replace(e, '')
    query = query.replace(e.capitalize(), '')
for en in language_lists.englsih_numbers:
    query = query.replace(en, '')

query = query.split(' ')
# remove post fix
for ch in language_lists.post_fix:
    for i in range(len(query)):
        if query[i].endswith(ch):
            if len(query[i][len(ch):]) >= n_length:
                query[i] = query[i][:(-1) * len(ch)]

# remove pre fix
for ch in language_lists.pre_fix:
    for i in range(len(query)):
        if query[i].startswith(ch):
            if len(query[i][len(ch):]) >= n_length:
                query[i] = query[i][len(ch):]

# verb stemming
for (past, present) in zip(language_lists.past_stem, language_lists.present_stem):
    for i in range(len(query)):
        if past in query[i]:
            for p in language_lists.past_pronoun:
                if query[i] == past + p or query[i] == 'می' + past + p or query[i] == past + 'ه' + 'بود' + p or query[
                    i] == 'خواه' + p + past:
                    query[i] = past
                    break
        if present in query[i]:
            for p in language_lists.present_pronoun:
                if query[i] == 'ب' + present + p or query[i] == present + p or query[i] == 'می' + present + p:
                    query[i] = present
                    break

# multi form words
for ch in language_lists.multi_form.keys():
    for i in range(len(query)):
        if query[i] == ch:
            query[i] = language_lists.multi_form.get(ch)

# arabic irregular
for ch in language_lists.arabic_irregular_plural.keys():
    for i in range(len(query)):
        if query[i] == ch:
            query[i] = language_lists.arabic_irregular_plural.get(ch)

match = []
finger = sys.maxsize
max_index = 0
for q in query:
    if q in inverted_index.keys():
        match.append(inverted_index.get(q))
        if inverted_index.get(q)[0] < finger:
            finger = inverted_index.get(q)[0]
        if inverted_index.get(q)[-1] > max_index:
            max_index = inverted_index.get(q)[-1]
result = {}
pointers = [0] * len(match)
while finger <= max_index:
    count = 0
    for i in range(len(match)):
        if pointers[i] < len(match[i]) and finger == match[i][pointers[i]]:
            pointers[i] += 1
            count += 1
    doc_id_list = result.get(count, [])
    result[count] = sorted(doc_id_list + [finger])
    min = max_index + 1
    for i in range(len(match)):
        if pointers[i] < len(match[i]) and match[i][pointers[i]] < min:
            min = match[i][pointers[i]]
    finger = min

result = {k: v for k, v in reversed(sorted(result.items(), key=lambda item: item[0]))}
end = time.time()
print(f"Time : {end - begin} sec")


for r in result:
    match_docs = result[r]
    if r > 1:
        s = "s"
    else:
        s = ""
    print(f"{len(match_docs)} records match {r} term{s}: ")
    for m in match_docs:
        print(f"Document {m}  : {docid_doc_mapping[m][0]}")

if len(result) == 0:
    print("No Results")
