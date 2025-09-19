import pandas as pd
import math

def calculate_total_and_divergence_score(group):
    """
    Calculate the total score, the standard deviation score, and the polarization score for a group of comments

    Args:
        group (pandas.DataFrame): A group of comments with the same video_id

    Returns:
        pandas.Series: A Series containing the total score, the standard deviation, and the polarization score
        total_score (float): The total score of the group
        std_deviation (float): The standard deviation of the group
        polarization_score_with_pseudo_count (float): The polarization score of the group (shrinkaged toward zero if the total count of the group is small)
    """
    video_title = group["video_title"].iloc[0] if "video_title" in group.columns else "N/A"
    total_score = group["sentiment_score"].sum()
    relevance_score = group["relevance_score"].mean()
    std_deviation = group["sentiment_score"].std()
    positive_sum = abs(group.loc[group["sentiment_label"] == 1, "weighted_sentiment_score"].sum())
    negative_sum = abs(group.loc[group["sentiment_label"] == -1, "weighted_sentiment_score"].sum())
    absolute_sum = positive_sum + negative_sum
    if absolute_sum == 0:
        polarization_score = 0
    else:
        polarization_score = 4 * (positive_sum / absolute_sum) * (negative_sum / absolute_sum)
    polarization_score_with_pseudo_count = len(group) / (len(group) + 5) * polarization_score
    return pd.Series({
        "video_title": video_title,
        "total_score": total_score * relevance_score,
        "relevance_score": relevance_score,
        "std_deviation": std_deviation * math.sqrt(relevance_score),
        "polarization_score_with_pseudo_count": polarization_score_with_pseudo_count * math.sqrt(relevance_score)
    })

def get_recommendation(df):
    """
    Get video recommendations based on highest total score and most polarized video with highest product score.
    
    Args:
        df (pandas.DataFrame): DataFrame containing video_id, total_score, relevance_score, polarization_score_with_pseudo_count, and std_deviation columns
        
    Returns:
        tuple: (best_video_id, best_score, most_polarized_video_id, most_polarized_polarization_score, most_polarized_std_deviation)
            - best_video_id: video_id with the highest total score
            - best_video_title: title of the best video
            - best_score: the highest total score value
            - best_polarization_score: polarization score of the best video
            - best_std_deviation: standard deviation of the best video
            - most_polarized_video_id: video_id from top 3 polarized videos with highest (polarization_score * total_score) product
            - most_polarized_video_title: title of the most polarized video
            - most_polarized_score: the highest total score value of the most polarized video
            - most_polarized_polarization_score: polarization score of the most polarized video
            - most_polarized_std_deviation: standard deviation of the most polarized video
    """
    if df.empty:
        return None, None, None, None, None, None, None, None, None, None
    
    max_score_idx = df["total_score"].idxmax()
    best_video_id = df.loc[max_score_idx, "video_id"]
    best_video_title = df.loc[max_score_idx, "video_title"]
    best_score = df.loc[max_score_idx, "total_score"]
    best_polarization_score = df.loc[max_score_idx, "polarization_score_with_pseudo_count"]
    best_std_deviation = df.loc[max_score_idx, "std_deviation"]

    max_polarization_3_idx = df.nlargest(3, "polarization_score_with_pseudo_count").index.tolist()
    # Calculate multiplication of polarization score and total score for top 3 polarized videos
    highest_product = 0
    highest_product_video_id = None
    for idx in max_polarization_3_idx:
        product = df.loc[idx, "polarization_score_with_pseudo_count"] * df.loc[idx, "total_score"]
        if product > highest_product:
            highest_product = product
            highest_product_video_idx = idx
    
    most_polarized_video_id = df.loc[highest_product_video_idx, "video_id"]
    most_polarized_video_title = df.loc[highest_product_video_idx, "video_title"]
    most_polarized_score = df.loc[highest_product_video_idx, "total_score"]
    most_polarized_polarization_score = df.loc[highest_product_video_idx, "polarization_score_with_pseudo_count"]
    most_polarized_std_deviation = df.loc[highest_product_video_idx, "std_deviation"]
    
    return best_video_id, best_video_title, best_score, best_polarization_score, best_std_deviation, most_polarized_video_id, most_polarized_video_title, most_polarized_score, most_polarized_polarization_score, most_polarized_std_deviation

def get_video_scores(df):
    """
    Get the scores of the videos
    """
    df["weighted_sentiment_score"] = df["sentiment_label"] * df["sentiment_score"] * df["like_count"]
    if not df.empty:
        df_results = df.groupby("video_id").apply(calculate_total_and_divergence_score).reset_index()
    else:
        print("No data to calculate scores.")
        return None
    return df_results

def main():
    search_query = "Mozart Violin Sonata in E minor"
    input_filename = f"{search_query.replace(' ', '_')}_comments_results_with_sentiment.csv"
    output_filename = f"{search_query.replace(' ', '_')}_comments_results_with_final_scores.csv"
    df = pd.read_csv(input_filename)
    df_results = get_video_scores(df)
    print("\nPreview of the results:")
    print(df_results.head())
    df_results.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print(f"Results saved to {output_filename}")
    best_video_id, best_video_title, best_score, best_polarization_score, best_std_deviation, most_polarized_video_id, most_polarized_video_title, most_polarized_score, most_polarized_polarization_score, most_polarized_std_deviation = get_recommendation(df_results)
    print(f"Best video ID: {best_video_id}, Best video title: {best_video_title}, Best score: {best_score}, Best polarization score: {best_polarization_score}, Best std deviation: {best_std_deviation}, Most polarized video ID: {most_polarized_video_id}, Most polarized video title: {most_polarized_video_title}, Most polarized video score: {most_polarized_score}, Most polarized polarization score: {most_polarized_polarization_score}, Most polarized std deviation: {most_polarized_std_deviation}")

if __name__ == "__main__":
    main()

    
