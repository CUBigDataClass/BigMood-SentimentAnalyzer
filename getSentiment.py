class GetSentiment():
    def getSentiment(self,obj) :
        #to do
        print("From getSentiment")
        print(obj["location"])
        sentScore = ['happy','angry','sad','happy','happy']
        retRes = [{'location': obj['location'], 'timestamp': obj['timestamp'],'hashtags': obj['hashtags'],'sentiment':sentScore}]
        return retRes
        