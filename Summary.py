import re

####### MAGIC NUMBERS ########
numChars = 500
lengthWeight = 0.45837485736
freqWeights = 0.90918723647
fileName = "file4.txt"

stopwords = [
    'myself', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself',
    'yourselves', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself',
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what',
    'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'are', 'was',
    'were', 'been', 'being', 'have', 'has', 'had', 'having', 'does', 'did',
    'doing', 'the', 'and', 'but', 'because', 'until', 'while', 'for', 'with',
    'about', 'against', 'between', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'from', 'down', 'out', 'off', 'over', 'under',
    'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
    'some', 'such', 'nor', 'not', 'only', 'own', 'same', 'than', 'too', 'very',
    'can', 'will', 'just', 'don', 'should', 'now', "citigroup", "2018", "2017",
    "citi", "gps", "group", "figure"
]

alnumpattern = re.compile("[A-Z0-9a-z., '!?$%:-]")
moneypattern = re.compile("\$[0-9]+\.?[0-9]*|[0-9]+\.?[0-9]*[%]")
yearpattern = re.compile("[0-9]{4}")
splitpattern = '[.?!]'

# How many times exact instance of a sentence must appear to be removed
sentenceMutipleThreshold = 3


def freq(lst):
    dictionary = {}

    # We are just going to find DF here.
    # So essentially hash each "word" in the document.
    # A word is a space seperated token
    for sentence in lst:
        words = sentence.split(" ")
        for word in words:

            # If the word is too long we ignore it
            # If the word is too short, we also ignore it.
            # This means that small numbers also gets filtered, but they are small
            # Numbers are probably numbered points, so filtering them would be good too.
            if len(word) >= 16 or len(word) <= 2:
                continue

            # Work with lower case
            word = word.lower()

            # Check if the word is a trivial word. If it is, ignore it.
            # Trivial words cannot be a keyword
            if word in stopwords:
                continue

            # Populate the dictionary. EAFP style!
            try:
                dictionary[word] = dictionary[word] + 1
            except:
                dictionary[word] = 1
    return dictionary


# Implements a modified version of TF-IDF
def process(text, lenOutput):
    # Create the frequency map of the text
    frequency = freq(text)

    # Change some of the weights of certain keywords in the text
    # Essentially if it talks about money, it's probably important, so boost that
    # Then if it's some year, we don't really care about it so much
    for key in frequency:
        if re.match(moneypattern, key):
            frequency[key] = frequency[key] * 2
        elif re.match(yearpattern, key):
            frequency[key] = frequency[key] * 0.5

        # Then at the end, scale the frequencies by some factor
        frequency[key] = frequency[key]**freqWeights

    cost = []

    # Now, we want to see how heavy the weight of the sentence is
    # This is the TF-IDF part
    # Except we make 2 changes:

    # 1) Instead of taking log, we exponent the first part
    # This means TF contribution gets boosted

    # 2) We do not even consider the most common words that appear in english language
    # Words that are modality based etc are not counted.
    for index2, sentence in enumerate(text):
        pain = 0
        wordcount = 0
        for word in sentence.split(" "):
            wordcount += 1
            if word.lower() in frequency:
                pain += frequency[word.lower()]

        # Now, sometimes, we have empty string. We just ignore it here.
        if wordcount == 0:
            continue

        # We weight it by the length of the sentence as well.
        # This is modification #3.
        cost.append((pain / (wordcount**lengthWeight), index2))

    # Find the sentences with the highest cost (weights)
    cost.sort()
    cost.reverse()

    out = []
    size = 0
    index = 0

    # Concatenate the sentences together, in the order in which they appeared.
    while (index < index2):
        # Here, we dont want to break if we run out of room to write sentences.
        # So we keep filling up the space with shorter sentences, until the remaining
        # space left is a trivial amount.
        if (size > lenOutput - 20):
            break
        sentencenum = cost[index][1]

        # Some inputs will have double spaces...?
        toappend = text[sentencenum].replace("  ", " ")

        length = len(toappend) + 1

        # If we don't have space to append, don't bother appending
        if (size + length >= lenOutput):
            index += 1
            continue
        out.append((sentencenum, toappend))
        size += len(toappend)
        index += 1

    out.sort()
    text = ".".join([x[1] for x in out])[1:] + "."

    return text


def removeMultipleSentences(text):
    dictionary = {}

    for sentence in text:
        dictionary[sentence] = dictionary.get(sentence, 0) + 1

    result = []
    for sentence in text:
        if dictionary[sentence] < sentenceMutipleThreshold:
            result.append(sentence)

    return result


def main():
    file = open(fileName, "r", encoding="ISO-8859-1")
    text = file.readlines()
    file.close()

    # Most of the lines have trailing and ending white spaces
    text = [x.rstrip().lstrip() if x else "" for x in text]

    # Adding a couple of fullstops to the end of headers
    # So the headers are usually in a line of their own, seperated be the next with
    # an extra newline character below.
    for i in range(1, len(text)):
        if text[i] == "":
            text[i - 1] = text[i - 1] + "."

    # text is a list of sentences
    # filters and keeps alnum and these specific symbols:
    # ., '!?$%:-
    # But for some reason, ' and " are represented differently. No idea if that is so
    # for the final presentation.
    text = " ".join([
        "".join([x if alnumpattern.match(x) else " " for x in y]) for y in text
    ])
    text = re.split(splitpattern, text)

    # remove sentences that appear multiple times
    # Because usually they are headers/footers
    text = removeMultipleSentences(text)

    # return "-\n".join(text)

    return process(text, numChars)


if __name__ == "__main__":
    print(main())
