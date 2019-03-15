from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#The compound score is computed by summing the valence scores of each word in the lexicon, adjusted according to the rules, 
#and then normalized to be between -1 (most extreme negative) and +1 (most extreme positive). This is the most useful metric 
#if you want a single unidimensional measure of sentiment for a given sentence. Calling it a 'normalized, weighted composite score' is accurate.

class SentimentAnalyzer:
        def sentimentAnalyzerScores(self,sentence):
                analyser = SentimentIntensityAnalyzer()
                score = analyser.polarity_scores(sentence)
                return score['compound']

        def computeSentiment(self,tweets):
                compoundSum = 0
                nTweets = 0
                for each in tweets:
                        nTweets += 1
                        compoundScore = self.sentimentAnalyzerScores(each)
                        compoundSum += compoundScore
                avgScore = compoundSum/nTweets
                return avgScore
