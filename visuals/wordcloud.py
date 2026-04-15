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
            "pace",
        ]
    )  # Tagalog-specific common filler words

    wordcloud = WordCloud(
        width=150,
        height=150,
        background_color="#faf7f2",
        stopwords=stopwords,
        colormap="viridis",
    ).generate(filtered_text)

    fig, ax = plt.subplots(figsize=(2, 2))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")

    # Constrain within a narrow column
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(fig, use_container_width=True)


def generate_wordcloud_new(data):
    from wordcloud import WordCloud, STOPWORDS
    import matplotlib.pyplot as plt
    import re
    import streamlit as st

    # Combine all remarks into one string
    text = " ".join(str(remark) for remark in data["Remarks"].dropna())

    if not text.strip():
        st.info("No remarks available to generate word cloud")
        return

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
            "pace",
        ]
    )

    # Increase dimensions for better visibility
    wordcloud = WordCloud(
        width=800,  # Increased from 150
        height=600,  # Increased from 150
        background_color="#faf7f2",
        stopwords=stopwords,
        colormap="viridis",
        max_words=100,  # Limit words for cleaner look
        relative_scaling=0.5,
        prefer_horizontal=0.7,
    ).generate(filtered_text)

    # Create figure with larger size and no extra margins
    fig, ax = plt.subplots(figsize=(10, 8))  # Increased from (2,2)
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")

    # Remove padding around the image
    plt.tight_layout(pad=0)

    # Display with container width to fill the column
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)  # Free memory
