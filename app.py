from flask import Flask, render_template, request, jsonify, url_for
from celery import Celery
import os
from dotenv import load_dotenv
from Performance_Analyzer import PerformanceAnalyzer
from bs4 import MarkupResemblesLocatorWarning
import warnings
import logging

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
logging.getLogger("transformers").setLevel(logging.ERROR)

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)

# 新建一个celery应用实例（可包含多个worker）
celery = Celery(
    app.name,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)
celery.conf.task_track_started = True

# 把 run_analysis_task 注册在这个应用示例下，每次调用这个函数.delay() 都会新建一条消息放进这个
# 应用实例的队列（这里是redis管理的）中，等待被worker处理
@celery.task
def run_analysis_task(query, num_candidates, min_duration_in_seconds, verbose=False):
    analyzer = PerformanceAnalyzer(API_KEY)
    results = analyzer.get_performance_recommendations(query, num_candidates=num_candidates, min_duration_in_seconds=min_duration_in_seconds, verbose=verbose)
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_query = request.form.get('query')
    num_candidates = request.form.get('num_candidates')
    min_duration_in_seconds = request.form.get('min_duration_in_seconds')
    if not search_query:
        return "Error: No search query provided", 400
    
    task = run_analysis_task.delay(search_query, num_candidates, min_duration_in_seconds, verbose=False)
    return render_template('result.html', task_id=task.id, query=search_query, num_candidates=num_candidates, min_duration_in_seconds=min_duration_in_seconds)
    # results = analyzer.get_performance_recommendations(search_query, num_candidates=num_candidates, min_duration_in_seconds=min_duration_in_seconds, verbose=False)
    # best_video_id, best_video_title, best_score, best_polarization_score, best_std_deviation, most_polarized_video_id, most_polarized_video_title, most_polarized_score, most_polarized_polarization_score, most_polarized_std_deviation = results
    # return render_template(
    #     'result.html',
    #     query=search_query,
    #     best_video_id=best_video_id,
    #     best_video_title=best_video_title,
    #     best_score=best_score,
    #     best_polarization_score=best_polarization_score,
    #     best_std_deviation=best_std_deviation,
    #     most_polarized_video_id=most_polarized_video_id,
    #     most_polarized_video_title=most_polarized_video_title,
    #     most_polarized_score=most_polarized_score,
    #     most_polarized_polarization_score=most_polarized_polarization_score,
    #     most_polarized_std_deviation=most_polarized_std_deviation
    # )

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = run_analysis_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Waiting for the task to start...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'status': 'Searching for the most recommended and most polarized videos...'}
        if task.state == 'SUCCESS':
            response['result'] = task.result
    else:
        response = {'state': task.state, 'status':str(task.info)}
    return jsonify(response)