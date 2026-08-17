import pandas as pd
from datetime import datetime


def _to_df(logs):
    """logs: list of dicts from get_teacher_attendance_logs / get_subject_attendance_logs.
    Each row expected to carry student_id, subject_id, timestamp, is_present,
    and optionally nested 'students': {'name': ...} / 'subjects': {'name': ...}.
    """
    if not logs:
        return pd.DataFrame(columns=['student_id', 'subject_id', 'timestamp', 'is_present', 'student_name', 'subject_name'])

    rows = []
    for log in logs:
        student_info = log.get('students') or {}
        subject_info = log.get('subjects') or {}
        rows.append({
            'student_id': log.get('student_id'),
            'subject_id': log.get('subject_id'),
            'timestamp': log.get('timestamp'),
            'is_present': bool(log.get('is_present')),
            'student_name': student_info.get('name', f"Student {log.get('student_id')}"),
            'subject_name': subject_info.get('name', f"Subject {log.get('subject_id')}"),
        })

    df = pd.DataFrame(rows)
    df['date'] = pd.to_datetime(df['timestamp'], errors='coerce')
    return df


def overall_stats(logs):
    df = _to_df(logs)
    if df.empty:
        return {
            'total_subjects': 0, 'total_students': 0, 'total_sessions': 0,
            'overall_attendance_pct': 0.0, 'total_records': 0,
        }

    total_sessions = df.groupby('subject_id')['timestamp'].nunique().sum()
    overall_pct = round(100 * df['is_present'].mean(), 1)

    return {
        'total_subjects': df['subject_id'].nunique(),
        'total_students': df['student_id'].nunique(),
        'total_sessions': int(total_sessions),
        'overall_attendance_pct': overall_pct,
        'total_records': len(df),
    }


def subject_wise_stats(logs):
    df = _to_df(logs)
    if df.empty:
        return pd.DataFrame(columns=['subject_id', 'subject_name', 'sessions', 'attendance_pct'])

    grouped = df.groupby(['subject_id', 'subject_name']).agg(
        sessions=('timestamp', 'nunique'),
        attendance_pct=('is_present', lambda x: round(100 * x.mean(), 1)),
        records=('is_present', 'count'),
    ).reset_index()

    return grouped.sort_values('attendance_pct', ascending=False)


def student_wise_stats(logs, subject_id=None):
    df = _to_df(logs)
    if subject_id is not None and not df.empty:
        df = df[df['subject_id'] == subject_id]

    if df.empty:
        return pd.DataFrame(columns=['student_id', 'student_name', 'sessions', 'attended', 'attendance_pct'])

    grouped = df.groupby(['student_id', 'student_name']).agg(
        sessions=('is_present', 'count'),
        attended=('is_present', 'sum'),
    ).reset_index()

    grouped['attendance_pct'] = round(100 * grouped['attended'] / grouped['sessions'], 1)
    grouped['attended'] = grouped['attended'].astype(int)

    return grouped.sort_values('attendance_pct', ascending=True)


def trend_over_time(logs, subject_id=None):
    df = _to_df(logs)
    if subject_id is not None and not df.empty:
        df = df[df['subject_id'] == subject_id]

    if df.empty or df['date'].isna().all():
        return pd.DataFrame(columns=['date', 'attendance_pct'])

    df = df.dropna(subset=['date'])
    df['day'] = df['date'].dt.date

    grouped = df.groupby('day').agg(
        attendance_pct=('is_present', lambda x: round(100 * x.mean(), 1))
    ).reset_index()

    grouped = grouped.sort_values('day')
    grouped = grouped.rename(columns={'day': 'date'})
    return grouped


def low_attendance_students(student_stats_df, threshold=75.0):
    if student_stats_df.empty:
        return student_stats_df
    return student_stats_df[student_stats_df['attendance_pct'] < threshold].sort_values('attendance_pct')


def generate_smart_insights(logs, subject_stats_df, student_stats_df, threshold=75.0):
    """Rule-based (not ML) insights derived directly from the aggregated data.
    Returns a list of short human-readable strings."""
    insights = []
    df = _to_df(logs)

    if df.empty:
        return ["No attendance data yet - insights will appear once you start taking attendance."]

    # Low attendance count
    low_df = low_attendance_students(student_stats_df, threshold)
    if len(low_df) > 0:
        insights.append(
            f"⚠️ {len(low_df)} student(s) are below {threshold:.0f}% attendance and may need a check-in."
        )
    else:
        insights.append(f"✅ No students are currently below {threshold:.0f}% attendance.")

    # Best / worst subject
    if not subject_stats_df.empty and len(subject_stats_df) > 1:
        best = subject_stats_df.iloc[0]
        worst = subject_stats_df.iloc[-1]
        if best['subject_name'] != worst['subject_name']:
            insights.append(
                f"📈 \"{best['subject_name']}\" has the highest attendance ({best['attendance_pct']}%), "
                f"while \"{worst['subject_name']}\" is lowest ({worst['attendance_pct']}%)."
            )

    # Trend direction: compare last 3 sessions vs prior sessions (all subjects combined)
    trend_df = trend_over_time(logs)
    if len(trend_df) >= 4:
        recent = trend_df.tail(3)['attendance_pct'].mean()
        prior = trend_df.iloc[:-3]['attendance_pct'].mean()
        diff = round(recent - prior, 1)
        if diff >= 3:
            insights.append(f"📈 Attendance is trending up: +{diff}% over the last few sessions.")
        elif diff <= -3:
            insights.append(f"📉 Attendance is trending down: {diff}% over the last few sessions.")

    # Most common absent day-of-week
    df_with_dates = df.dropna(subset=['date'])
    if not df_with_dates.empty:
        absents = df_with_dates[df_with_dates['is_present'] == False]
        if not absents.empty:
            absents = absents.copy()
            absents['weekday'] = absents['date'].dt.day_name()
            worst_day = absents['weekday'].value_counts().idxmax()
            insights.append(f"🗓️ Most absences tend to happen on {worst_day}s.")

    return insights
