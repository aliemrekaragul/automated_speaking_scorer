import pandas as pd
from typing import List
from models.score_models import SpeakingPerformance
import os
from datetime import datetime
import re

def _parse_file_name(file_name: str) -> tuple[str, str, str]:
    """Parse the file name to extract student ID, session ID, and task ID."""
    # Extract from format like 231101013-6-t2.mp3
    match = re.match(r'(\d+)-(\d+)-t(\d+)\.mp3$', file_name)
    if not match:
        return ('Unknown', 'Unknown', 'Unknown')
    return match.groups()  # Returns (student_id, session_id, task_number)

def save_scores_to_excel(performances: List[SpeakingPerformance], output_dir: str) -> str:
    """
    Save speaking performance scores to an Excel file.
    
    Args:
        performances: List of SpeakingPerformance objects
        output_dir: Directory to save the Excel file (same as audio files directory)
        
    Returns:
        str: Path to the saved Excel file
    """
    # Prepare data for DataFrame
    data = []
    for perf in performances:
        # Parse file name into components
        student_id, session_id, task_id = _parse_file_name(perf.file_name)
        
        row = {
            'File Name': perf.file_name,
            'Student ID': student_id,
            'Session ID': session_id,
            'Task ID': f't{task_id}',
            'Grammar': perf.analytic_scores.grammar if perf.analytic_scores else None,
            'Vocabulary': perf.analytic_scores.vocabulary if perf.analytic_scores else None,
            'Content': perf.analytic_scores.content if perf.analytic_scores else None,
            'Fluency': perf.analytic_scores.fluency if perf.analytic_scores else None,
            'Pronunciation': perf.analytic_scores.pronunciation if perf.analytic_scores else None,
            'Overall': perf.analytic_scores.overall if perf.analytic_scores else None,
            'Holistic Score': perf.holistic_score.overall_score if perf.holistic_score else None,
            'Analytic Score': perf.adjusted_score if perf.adjusted_score else None,
            'Off Topic': perf.off_topic_analysis.is_off_topic if perf.off_topic_analysis else None,
            'Off Topic Confidence': perf.off_topic_analysis.confidence if perf.off_topic_analysis else None,
            'Off Topic Explanation': perf.off_topic_analysis.explanation if perf.off_topic_analysis else None
        }
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Calculate student averages for Conversions sheet
    conversions_data = []
    for student_id in df['Student ID'].unique():
        student_df = df[df['Student ID'] == student_id]
        
        # Calculate averages
        avg_analytic = student_df['Analytic Score'].mean()
        avg_holistic = student_df['Holistic Score'].mean()
        
        # Count off-topic responses
        total_tasks = len(student_df)
        off_topic_count = student_df['Off Topic'].sum()  
        
        conversions_data.append({
            'Student ID': student_id,
            'Avg Analytic Score': avg_analytic,
            'Avg Holistic Score': avg_holistic,
            'Off Topic Task Count': off_topic_count
        })
    
    conversions_df = pd.DataFrame(conversions_data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'speaking_scores_{timestamp}.xlsx'
    filepath = os.path.join(output_dir, filename)
    
    # Create Excel writer with formatting
    with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
        # Write Scores sheet
        df.to_excel(writer, sheet_name='Scores', index=False)
        
        # Write Conversions sheet
        conversions_df.to_excel(writer, sheet_name='Conversions', index=False)
        
        # Get workbook and worksheet objects for formatting
        workbook = writer.book
        scores_worksheet = writer.sheets['Scores']
        conversions_worksheet = writer.sheets['Conversions']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        score_format = workbook.add_format({
            'num_format': '0.00',
            'border': 1
        })
        
        text_format = workbook.add_format({
            'text_wrap': True,
            'border': 1
        })
        
        # Format Scores sheet
        for col_num, value in enumerate(df.columns.values):
            scores_worksheet.write(0, col_num, value, header_format)
            
        # Set column widths for Scores sheet
        scores_worksheet.set_column('A:A', 20)  # File Name
        scores_worksheet.set_column('B:B', 15)  # Student ID
        scores_worksheet.set_column('C:C', 10)  # Session ID
        scores_worksheet.set_column('D:D', 8)   # Task ID
        scores_worksheet.set_column('E:K', 12)  # Score columns
        scores_worksheet.set_column('L:L', 15)  # Adjusted Score
        scores_worksheet.set_column('M:N', 12)  # Off Topic columns
        scores_worksheet.set_column('O:O', 40)  # Off Topic Explanation
        
        # Apply formats to Scores sheet
        score_cols = ['E:K', 'L:L', 'N:N']
        for col_range in score_cols:
            scores_worksheet.set_column(col_range, None, score_format)
            
        text_cols = ['A:D', 'O:O', 'M:M']
        for col_range in text_cols:
            scores_worksheet.set_column(col_range, None, text_format)
        
        # Format Conversions sheet
        for col_num, value in enumerate(conversions_df.columns.values):
            conversions_worksheet.write(0, col_num, value, header_format)
        
        # Set column widths for Conversions sheet
        conversions_worksheet.set_column('A:A', 15)  # Student ID
        conversions_worksheet.set_column('B:C', 18)  # Average scores
        conversions_worksheet.set_column('D:D', 15)  # Off Topic Task Count
        
        # Apply formats to Conversions sheet
        conversions_worksheet.set_column('B:C', None, score_format)  # Average scores
        conversions_worksheet.set_column('A:A', None, text_format)   # Student ID
        conversions_worksheet.set_column('D:D', None, text_format)   # Off Topic Count
    
    return filepath 