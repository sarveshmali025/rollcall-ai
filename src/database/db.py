from src.database.config import supabase
import bcrypt
from datetime import datetime


def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode() , bcrypt.gensalt()).decode()

def check_pass(pwd , hashed):
    return bcrypt.checkpw(pwd.encode() , hashed.encode())

def check_teacher_exists(username):
    response = supabase.table("teachers").select("username").eq("username" , username).execute()
    return len(response.data) > 0


def create_teacher(username , password , name):
    data = {"username" : username , "password" : hash_pass(password) , "name" : name}
    response = supabase.table("teachers").insert(data).execute()
    return response.data

def teacher_login(username , password):
    response = supabase.table("teachers").select("*").eq("username" , username).execute()
    if response.data:
        teacher = response.data[0]
        if check_pass(password, teacher['password']):
            return teacher
        return None


def get_all_students():
    response = supabase.table('students').select("*").execute()
    return response.data

def create_student(new_name , face_embedding = None , voice_embedding = None):
    data = {'name' : new_name , 'face_embedding' : face_embedding , 'voice_embedding' : voice_embedding}
    response = supabase.table('students').insert(data).execute()
    return response.data

def create_subject(subject_code, name, section, teacher_id):
    data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
    response = supabase.table("subjects").insert(data).execute()
    return response.data

def delete_subject(subject_id, teacher_id):
    """Delete a subject owned by the given teacher and its dependent records."""
    subject_res = (
        supabase.table('subjects')
        .select('subject_id')
        .eq('subject_id', subject_id)
        .eq('teacher_id', teacher_id)
        .execute()
    )

    if not subject_res.data:
        raise ValueError('Subject not found or you are not allowed to delete it.')

    # Remove dependent records first so deletion also works when the database
    # does not have ON DELETE CASCADE configured.
    supabase.table('attendance_corrections').delete().eq('subject_id', subject_id).execute()
    supabase.table('attendance_logs').delete().eq('subject_id', subject_id).execute()
    supabase.table('subject_students').delete().eq('subject_id', subject_id).execute()
    response = supabase.table('subjects').delete().eq('subject_id', subject_id).eq('teacher_id', teacher_id).execute()
    return response.data


def get_teacher_subjects(teacher_id):
    response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
    subjects = response.data


    for sub in subjects:
        sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
        attendance = sub.get('attendance_logs', [])
        unique_sessions = len(set(log['timestamp'] for log in attendance))
        sub['total_classes'] = unique_sessions


        sub.pop('subject_student', None)
        sub.pop('attendance_logs', None)

    return subjects

def  enroll_student_to_subject(student_id, subject_id):
    data = {'student_id': student_id, "subject_id": subject_id}
    response= supabase.table('subject_students').insert(data).execute()
    return response.data

def  unenroll_student_to_subject(student_id, subject_id):
    response= supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
    return response.data

def get_student_subjects(student_id):
    response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data


def get_student_attendance(student_id):
    response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
    return response.data

def create_attendance(log):
    response = supabase.table('attendance_logs').insert(log).execute()
    return response.data

# --- BATCH 2: Attendance Records + Manual Correction + Audit Trail ---

def get_subject_attendance_logs(subject_id):
    response = supabase.table('attendance_logs').select("*, students(name)").eq('subject_id', subject_id).order('timestamp', desc=True).execute()
    return response.data


def update_attendance_log(log_id, new_is_present, corrected_by, reason=None):
    current = supabase.table('attendance_logs').select("*").eq('id', log_id).execute()
    if not current.data:
        return None

    original = current.data[0]
    original_status = original.get('is_present')

    updated = supabase.table('attendance_logs').update(
        {'is_present': new_is_present}
    ).eq('id', log_id).execute()

    audit_entry = {
        'log_id': log_id,
        'student_id': original.get('student_id'),
        'subject_id': original.get('subject_id'),
        'corrected_by': corrected_by,
        'original_status': original_status,
        'new_status': new_is_present,
        'reason': reason,
        'corrected_at': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }

    supabase.table('attendance_corrections').insert(audit_entry).execute()

    return updated.data

def get_correction_audit_trail(subject_id):
    response = supabase.table('attendance_corrections').select("*, students(name)").eq('subject_id', subject_id).order('corrected_at', desc=True).execute()
    return response.data

# --- BATCH 4: Attendance Analytics ---

def get_teacher_attendance_logs(teacher_id):
    subjects_res = supabase.table('subjects').select('subject_id').eq('teacher_id', teacher_id).execute()
    subject_ids = [s['subject_id'] for s in subjects_res.data]

    if not subject_ids:
        return []

    response = supabase.table('attendance_logs').select("*, students(name), subjects(name)").in_('subject_id', subject_ids).execute()
    return response.data
