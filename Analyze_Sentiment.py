import pandas as pd
from transformers import pipeline
import torch
from transformers import pipeline
import time
from utils import SENTIMENT_MAP, SENTIMENT_MAP_STARS, SENTIMENT_MAP_SCORE, SENTIMENT_MAP_STARS_SCORE, SENTIMENT_MODEL_NAMES

def analyze_sentiment(input_df, english_sentiment_pipeline, multilingual_sentiment_pipeline, verbose=False):
    """
    Load the comments' data and use designated Hugging Face model to perform sentimental analysis
    Then return a DataFrame with the results

    Args:
        input_df (pandas.DataFrame): the DataFrame for the original comment file
        english_sentiment_pipeline (transformers.pipeline): The pipeline for English comments
        multilingual_sentiment_pipeline (transformers.pipeline): The pipeline for multilingual comments
    
    Returns:
        pandas.DataFrame: The new DataFrame that contains the results of the sentimental analysis
        or None if errors occur
    """
    
    if 'clean_text' not in input_df.columns:
        print("Error: No clean_text column found in the dataframe")
        return None
    df = input_df.copy()
    df.dropna(subset=['clean_text'], inplace=True)
    df['clean_text'] = df['clean_text'].astype(str)
    df['language'] = df['language'].astype(str)
    

    # 1. Perform the sentiment analysis
    # def get_sentiment(text, language):
    #     if language == "en":
    #         try:
    #             result = english_sentiment_pipeline(text[:512])[0]
    #             return result['label'], result['score']
    #         except Exception as e:
    #             print(f"Error performing sentiment analysis for {text[:30]}...: {e}")
    #             return "Error", 0.0
    #     else:
    #         try:
    #             result = multilingual_sentiment_pipeline(text[:512])[0]
    #             return result['label'], result['score']
    #         except Exception as e:
    #             print(f"Error performing sentiment analysis for {text[:30]}...: {e}")
    #             return "Error", 0.0
    # Supposably the following is less efficient than the previous one but it is more readable
    # I experimented and found the time difference is negligible
    def get_sentiment_from_row(row):
        text = row['clean_text']
        if row['language'] == "en":
            try:
                result = english_sentiment_pipeline(text[:512])[0]
                standardized_label = SENTIMENT_MAP_SCORE.get(result['label'].lower(), 0)
                # standardized_label = SENTIMENT_MAP_SCORE.get(result['label'].lower(), 'Unknown')
                return standardized_label, result['label'], result['score']
            except Exception as e:
                print(f"Error performing sentiment analysis for {text[:30]}...: {e}")
                return "Error", "Error", 0.0
        else:
            try:
                result = multilingual_sentiment_pipeline(text[:512])[0]
                standardized_label = SENTIMENT_MAP_SCORE.get(result['label'].lower(), 0)
                # standardized_label = SENTIMENT_MAP_SCORE.get(result['label'].lower(), 'Unknown')
                return standardized_label, result['label'], result['score']
            except Exception as e:
                print(f"Error performing sentiment analysis for {text[:30]}...: {e}")
                return "Error", "Error", 0.0

    print("Performing sentiment analysis, it may take a while...")
    start_time = time.time()
    sentiment_results = df.apply(get_sentiment_from_row, axis=1)
    df[['sentiment_label', 'original_sentiment_label', 'sentiment_score']] = pd.DataFrame(sentiment_results.tolist(), index=input_df.index)
    # results = [get_sentiment(text, language) for text, language in zip(df['clean_text'], df['language'])]
    # df[['sentiment_label', 'sentiment_score']] = pd.DataFrame(results, index=df.index)
    end_time = time.time()
    print(f"Sentiment analysis completed in {end_time - start_time:.2f} seconds")
    return df

def main():
    search_query = "Mozart Violin Sonata in E minor"
    input_filename = f"{search_query.replace(' ', '_')}_comments_results.csv"
    output_filename = f"{search_query.replace(' ', '_')}_comments_results_with_sentiment.csv"
    english_sentiment_pipeline = pipeline("text-classification", model=SENTIMENT_MODEL_NAMES[2], device=0 if torch.cuda.is_available() else -1)
    multilingual_sentiment_pipeline = pipeline("text-classification", model=SENTIMENT_MODEL_NAMES[1], device=0 if torch.cuda.is_available() else -1)
    try:
        input_df = pd.read_csv(input_filename)
        print(f"Loaded {len(input_df)} comments from {input_filename} successfully")
    except FileNotFoundError:
        print(f"Error: No documents found in {input_filename}")
        return None
    df_results = analyze_sentiment(input_df, english_sentiment_pipeline=english_sentiment_pipeline, multilingual_sentiment_pipeline=multilingual_sentiment_pipeline)

    if df_results is not None:
        print("\nPreview of the results:")
        print(df_results[['text', 'sentiment_label', 'sentiment_score']].head())
        
        df_results.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\nResults saved to {output_filename}")

if __name__ == "__main__":
    main()
