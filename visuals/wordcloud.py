def generate_wordcloud(data):
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    import re
    import streamlit as st

    # Combine all remarks into one string
    text = " ".join(str(remark) for remark in data["Remarks"].dropna())

    # Remove punctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Remove short words (3 letters or fewer)
    filtered_words = [word for word in text.split() if len(word) > 3]

    # Join back to single string
    filtered_text = " ".join(filtered_words)

    # Optional: add your own stopwords
    stopwords = set(STOPWORDS)
    stopwords.update(
        [
            "lang",
            "naman",
            "okay",
            "today",
            "medyo",
            "kasi",
            "still",
            "pero",
            "talaga",
            "tlaga",
            "mejo",
            "kaso",
            "baka",
            "yung",
            "tska",
            "nalang",
            "nung",
            "ayun",
            "kaya",
            "parang",
            "yoga",
            "buhat",
            "tempo",
            "lsd",
        ]
    )  # Tagalog-specific common filler words

    # Generate word cloud
    wordcloud = WordCloud(
        width=250,
        height=250,
        background_color="white",
        stopwords=stopwords,
        colormap="viridis",
    ).generate(filtered_text)

    # Display
    # st.subheader("📝 Word Cloud from Runner Remarks")
    fig, ax = plt.subplots(figsize=(1.5, 1.5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
