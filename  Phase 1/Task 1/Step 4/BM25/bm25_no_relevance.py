import pickle
import math
import collections
import os

# Access Encoded Data Structures
with open("../../Encoded Data Structures/Encoded-Inverted_List.txt", 'rb') as f:
    inverted_index = pickle.loads(f.read())

with open("../../Encoded Data Structures/Encoded-DocumentID_DocLen.txt", 'rb') as f:
    docID_documentLen = pickle.loads(f.read())

with open("../../Encoded Data Structures/Encoded-Cleaned_Queries.txt", 'rb') as f:
    query_dict = pickle.loads(f.read())

'''
with open("QueryID_RelevantDocs_encoded.txt", 'rb') as f:
    queryID_relevantDocs = pickle.loads(f.read())

x = 1
queryID_noofrelevantdocs = {}
for string in queryID_relevantDocs:
    queryID_noofrelevantdocs[x] = len(queryID_relevantDocs[string])
    x += 1

print(queryID_relevantDocs)
print(queryID_noofrelevantdocs)
'''
query_list = list(query_dict.values())    # Contains all the queries required

#BM25 FORMULA : ((k2 + 1)q)/((k2 + q)) * ((k1 + 1)f)/((K + f)) * log((r + 0.5)(N − n − R + r + 0.5))/((n − r + 0.5)(R − r + 0.5))
#where: K = k1(bL + (1 − b))

#f = term frequency in that document
#n = total number of documents in which the term appears,i.e., len(docIds)
#L = doc length / avg doc length

final_score = {}     # dictionary of docID, bm25-score
avg_doc_len = sum(docID_documentLen.values()) / len(docID_documentLen.keys())  # gives the average document length for the given corpus
i = 1                # counter for counting query ids
top_5 = {}


def bm25(f, n, L, R, r):

    k1 = 1.2
    k2 = 100
    b = 0.75
    N = len(docID_documentLen.keys())
    q = 1

    K = k1 * ((b * L) + (1 - b))
    a = (k2 + 1) * q / (k2 + q)
    b = (k1 + 1) * f / (K + f)
    c = (r + 0.5) * (N - n - R + r + 0.5)
    d = (n - r + 0.5) * (R - r + 0.5)
    score = a * b * math.log(c / d)

    return score
'''
def compute_r(term,id):
    r = 0
    print("id : %d" %id)
    doc_list = queryID_relevantDocs[str(id)]
    print(doc_list)
    for doc in doc_list:
        f = open('output/' + doc + '.txt', 'r')
        if term in f.read():
            r += 1
    return r
'''


def calc_score(q):
    final_score = {}
    terms = q.split()
    for term in terms:
        if term in inverted_index:
            for doc in inverted_index[term]:
                if doc[0] not in final_score.keys():
                    final_score[doc[0]] = bm25(doc[1], len(inverted_index[term]) , (docID_documentLen[doc[0]] / avg_doc_len), 0, 0)
                else:
                    final_score[doc[0]] += bm25(doc[1], len(inverted_index[term]) , (docID_documentLen[doc[0]] / avg_doc_len), 0, 0)

    return final_score


f = open('BM25_NonRelevance_Top100_Pages.txt', 'w')
for query in query_dict.values():
    c = 1                                      # the variable c denotes rank
    print("Calculating BM25 Score for query: " + query)
    bm25_score = calc_score(query)
    final_score1 = collections.OrderedDict(sorted(bm25_score.items(), key=lambda s: s[1], reverse=True))
    f.write('\nFor query : %s\n\n' % query)
    for quid in final_score1:
        if c < 100:
            # format-> query_id Q0 doc_id rank BM25_score system_name
            f.write('%d Q0 %s %d %s BM25_model\n' % (i, quid, c, final_score1[quid]))
        if c <= 5:
            if query not in top_5.keys():
                top_5[query] = [quid]
            else:
                top_5[query].append(quid)
        c += 1
    newpath = r'../../Encoded Data Structures/Encoded-BM25-NoRelevance-Top100Docs-perQuery/'
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    output = open(
        newpath + 'Encoded-Top100Docs-BM25-NoRelevance' + '_%d' % i + '.txt', 'wb')
    pickle.dump(final_score1, output)
    output.close()
    i += 1
f.close()

top_5_docs = list(top_5.values())
list_output = open('BM25_NoRelevance_Top5_Docs.txt', 'w')
for doc in top_5_docs:
    for i in doc:
        list_output.write(i + "\n")
list_output.close()

print("\n\nBM25 Scoring Process DONE")
output = open('BM25_NoRelevance_Top5_Query_Pages.txt', 'w')
output.write(str(top_5))
output.close()
encoded_output = open('../../Encoded Data Structures/Encoded-BM25_NoRelevance_Top5_Pages.txt', 'wb')
pickle.dump(top_5, encoded_output)
encoded_output.close()