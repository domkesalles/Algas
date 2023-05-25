import tweepy
from textblob import TextBlob

# Chaves de API do Twitter
consumer_key = "8CNb9XmJ7KrjOLp8UMNH9Fznh"
consumer_secret = "eGoW01Xjhg1rslbOk23UYIPBsItB6Qr0cOA4SDmiXGekWfPmDB"
access_token = "2973742181-XBE1qdfNncM8zrb5shvdKHLcJa1fvhvahPKQGjX"
access_token_secret = "qRGj0HK2MIKWZHlIuiZ2oConS7yNPIRQwrqgoP0sAyI10"

# Autenticação com a API do Twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Consulta de tweets
query = "juventus team" 
tweets = api.search_tweets(q=query, tweet_mode="extended", count=10)

# print(tweets)

# Análise de sentimento
for tweet in tweets:
    if hasattr(tweet, "retweeted_status"):
        cleaned_text = tweet.retweeted_status.full_text
    else:
        cleaned_text = tweet.full_text
    
    analysis = TextBlob(cleaned_text)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        sentiment = "positivo"
    elif polarity < 0:
        sentiment = "negativo"
    else:
        sentiment = "neutro"
        
    print(f"Tweet: {cleaned_text}")
    print(f"Sentimento: {sentiment}")
    print()