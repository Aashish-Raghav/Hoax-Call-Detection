from textblob import TextBlob

def analyze_sentiment(df):
    sentiments = []
    polarities = []
    caller_danger_map = {}

    for idx, row in df.iterrows():
        text = row["Call_Text"]
        caller = row["Caller_ID"]
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            sentiment = "Positive"
        elif polarity < -0.1:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        sentiments.append(sentiment)
        polarities.append(polarity)

        # Store only the most dangerous message per caller
        if caller not in caller_danger_map or polarity < caller_danger_map[caller][0]:
            caller_danger_map[caller] = (polarity, text)

    df["Sentiment"] = sentiments
    df["Polarity"] = polarities

    # Get top 10 most dangerous callers (lowest polarity)
    top_dangerous_nodes = sorted(
        [(polarity, caller, text) for caller, (polarity, text) in caller_danger_map.items()],
        key=lambda x: x[0]
    )[:20]

    return df, top_dangerous_nodes
