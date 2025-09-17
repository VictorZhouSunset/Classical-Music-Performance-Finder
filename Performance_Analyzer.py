import argparse
import os
import dotenv
import torch
from transformers import pipeline
import logging
import warnings
from bs4 import MarkupResemblesLocatorWarning

from utils import initialize_youtube_api, save_results_to_csv, SENTIMENT_MODEL_NAMES
from Search_Filter import search_and_filter
from Analyze_Sentiment import analyze_sentiment
from Calculate_Score import get_video_scores, get_recommendation

class PerformanceAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.youtube = initialize_youtube_api(api_key=self.api_key)
        self.verbose = False
        self._initialize_sentiment_analysis_models(english_model_name=SENTIMENT_MODEL_NAMES[2], multilingual_model_name=SENTIMENT_MODEL_NAMES[1])
    
    def _initialize_sentiment_analysis_models(self, english_model_name, multilingual_model_name):
        device = 0 if torch.cuda.is_available() else -1
        self.english_sentiment_pipeline = pipeline("text-classification", model=english_model_name, device=device)
        if self.verbose:
            print(f"Model {english_model_name} initialized successfully")
            print(f"Initializing the sentiment analysis model {multilingual_model_name} for multilingual comments")
        self.multilingual_sentiment_pipeline = pipeline("text-classification", model=multilingual_model_name, device=device)
        if self.verbose:
            print(f"Model {multilingual_model_name} initialized successfully")
        if not self.verbose:
            print(f"Sentiment analysis models initialized successfully")
        
    
    def get_recommendations(self, query, verbose=False):
        self.verbose = verbose
        # 1. Search and filter the videos
        video_general_results, video_comments_results, video_with_comments = search_and_filter(
            query,
            youtube=self.youtube,
            num_candidates=50,
            min_duration_in_seconds=65, 
            verbose=self.verbose
        )
        print(f"Total videos with comments: {video_with_comments}")
        if video_with_comments == 0:
            print("No videos with comments found.")
            return None, None, None, None, None
        if verbose:
            filename_general = f"{query.replace(' ', '_')}_general_results.csv"
            filename_comments = f"{query.replace(' ', '_')}_comments_results.csv"
            save_results_to_csv(video_general_results, filename_general)
            save_results_to_csv(video_comments_results, filename_comments)
            print(f"Results saved to: {filename_general} and {filename_comments}")
        
        # 2. Analyze the sentiment of the comments
        df_with_sentiment_results = analyze_sentiment(
            video_comments_results,
            english_sentiment_pipeline=self.english_sentiment_pipeline,
            multilingual_sentiment_pipeline=self.multilingual_sentiment_pipeline,
            verbose=self.verbose
        )
        if verbose:
            filename_with_sentiment = f"{query.replace(' ', '_')}_comments_results_with_sentiment.csv"
            save_results_to_csv(df_with_sentiment_results, filename_with_sentiment)
            print(f"Results saved to: {filename_with_sentiment}")
        
        # 3. Calculate the score of the videos
        df_video_scores_results = get_video_scores(df_with_sentiment_results)
        if verbose:
            print(f"Total videos with final scores: {len(df_video_scores_results)}")
            filename_video_scores = f"{query.replace(' ', '_')}_video_scores_results.csv"
            save_results_to_csv(df_video_scores_results, filename_video_scores)
            print(f"Results saved to: {filename_video_scores}")
        
        # 4. Get the recommendations
        best_video_id, best_score, most_polarized_video_id, most_polarized_polarization_score, most_polarized_std_deviation = get_recommendation(df_video_scores_results)
        if verbose:
            print(f"Best video ID: {best_video_id}, Best score: {best_score}, Most polarized video ID: {most_polarized_video_id}, Most polarized polarization score: {most_polarized_polarization_score}, Most polarized std deviation: {most_polarized_std_deviation}")
        
        return best_video_id, best_score, most_polarized_video_id, most_polarized_polarization_score, most_polarized_std_deviation

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Performance Analyzer, to find the best or the most polarized version of a piece according to the comments"
    )
    parser.add_argument(
        "query",
        type=str,
        help="The classical music piece you want to search for (e.g. Mozart Violin Sonata in E minor)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Start the program in verbose mode, will save the intermediate results to csv files"
    )
    args = parser.parse_args()

    logging.getLogger("transformers").setLevel(logging.ERROR)
    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
    dotenv.load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    analyzer = PerformanceAnalyzer(api_key)
    if args.verbose:
        print(f"Verbose mode enabled, will save the intermediate results to csv files")
    best_video_id, best_score, most_polarized_video_id, most_polarized_polarization_score, most_polarized_std_deviation = analyzer.get_recommendations(args.query, args.verbose)
    print("\n" + "="*20 + " Results " + "="*20)
    if best_video_id is None:
        print("No recommendations found, please try again with a different query or check the API quota.")
    else:
        print(f"Recommendations with the highest total score:")
        print(f"Video ID: {best_video_id}, Score: {best_score:.2f}")
        print(f"Video URL: https://www.youtube.com/watch?v={best_video_id}\n")
        print(f"Recommendations with the most polarized version:")
        print(f"Video ID: {most_polarized_video_id}, Polarization score: {most_polarized_polarization_score:.2f}, Std deviation: {most_polarized_std_deviation:.2f}")
        print(f"Video URL: https://www.youtube.com/watch?v={most_polarized_video_id}")
    print("\n" + "="*52)
