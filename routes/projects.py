import fitz
import json
import os
import re
import time
import uuid

from extensions import db, cipher
from flask import Blueprint, flash, redirect, render_template, request, send_file, url_for, jsonify, g, current_app
from google import genai
from google.genai import types
from models import Document, login_required
from werkzeug.utils import secure_filename

projects_bp = Blueprint('projects', __name__)

def parse_pdf_with_gemini(filepath):
    """
    Takes a path to a saved PDF file, uploads it to 
    Gemini, and returns a parsed list of form fields 
    as Python data (dictionaries/lists).
    """

    max_retries = 3
    delay = 2 

    client = genai.Client()
    
    uploaded_file = client.files.upload(file=filepath)
    
    prompt = """
    You are an expert document parser. Scan and analyze this form
    from top to bottom and extract EVERY single fillable field, 
    label, checkbox, and table row (including repeating structures
    like Dependents, W-2 lines, or itemized lists).

    Return a JSON array of objects, where each object has:
    1. "field_label": The question or prompt text (e.g., 'First 
    Name', 'Date of Birth')
    2. "field_type": The type of input required ('text', 'date', 
    'checkbox', 'signature', 'numeric', etc.)
    3. "field_options": For checkboxes or multiple-choice fields,
    an array of options; otherwise null.
    4. "is_required": A boolean indicating if the field is 
    required or optional.
    5. "page": The 0-indexed page number where the field appears
    (e.g., 0 for page 1).
    6. "box_2d": The exact normalized 2D bounding box coordinates 
    [ymin, xmin, ymax, xmax] on a scale of 0 to 1000 representing 
    the exact input line or box area.
    """

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to parse PDF with Gemini API...")
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            parsed_data = json.loads(response.text)
            return parsed_data

        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  
                    continue
            raise e

def field_labels_with_gemini(filepath, field_list):
    """
    Takes a path to a saved PDF file, uploads it to 
    Gemini, and returns a JSON of the questions with  
    field labels as Python data (dictionaries/lists).
    """

    max_retries = 3
    delay = 2 

    client = genai.Client()
    
    uploaded_file = client.files.upload(file=filepath)

    field_string = json.dumps(field_list)

    prompt = f"""
    Here is the JSON list of fields to relabel: {field_string}

    You are an expert document parser. You are given a PDF form 
    and a list of field objects extracted from it. 

    Your task is to analyze the visual layout of the PDF and 
    provide a concise, human-readable label for every field in 
    the provided list based on its surrounding text and visual 
    context (e.g., 'First Name', 'Date of Birth', 'Filing Status 
    - Single').

    CRITICAL RULES:
    1. Return ONLY a JSON array containing the exact same 
    objects provided, with an updated "field_label" attribute 
    for each item.
    2. Keep all existing field "id", "field_type", "page", and 
    other attributes unchanged.
    3. Do NOT omit any fields or change the original order of 
    the array.
    4. Output strict JSON with no extra conversational text or 
    Markdown code block wrapping if possible.
    """

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} to parse PDF with Gemini API...")
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents=[uploaded_file, field_string, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            parsed_data = json.loads(response.text)
            return parsed_data

        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    delay *= 2  
                    continue
            raise e

def extract_acroform_fields(filepath):
    questions = []
    doc = fitz.open(filepath)
    
    for page_num, page in enumerate(doc):
        for widget in page.widgets():
            display_label = widget.field_name

            w_type = widget.field_type_string.lower()
            if "checkbox" in w_type:
                normalized_type = "checkbox"
            elif "radio" in w_type:
                normalized_type = "radio"
            elif "combo" in w_type or "list" in w_type:
                normalized_type = "select"
            else:
                normalized_type = "text"

            questions.append({
                "id": widget.field_name,
                "field_label": display_label,
                "field_type": normalized_type,
                "field_options": widget.choice_values or [],
                "field_required": bool(widget.field_flags & 2),
                "page": page_num,
                "field_answer": widget.field_value or ""
            })

    doc.close()

    updated_questions = field_labels_with_gemini(filepath, questions)

    return updated_questions

@projects_bp.route('/save', methods=['POST'])
def save_answers(original_file_path, completed_file_path, user_answers, form_type="acroform", items_list=None):
    if not os.path.exists(original_file_path):
        raise FileNotFoundError(f"Cannot find original PDF at {original_file_path}")

    doc = fitz.open(original_file_path)
    
    if form_type == "acroform":
        for page in doc:
            for widget in page.widgets():
                if widget.field_name in user_answers:
                    user_val = user_answers[widget.field_name]
                    
                    if widget.field_type_string in ["CheckBox", "RadioButton"]:
                        if user_val and user_val not in [False, "False", "Off", ""]:
                            on_val = widget.on_state() or "Yes"
                            widget.field_value = on_val
                        else:
                            widget.field_value = "Off"
                    else:
                        widget.field_value = str(user_val or "")
                        
                    widget.update()
                    
    else:
        items_list = items_list or []
        for item in items_list:
            page_num = item.get("page", 0)
            if page_num < 0 or page_num >= len(doc):
                page_num = 0
                
            page = doc[page_num]
            page_w = page.rect.width
            page_h = page.rect.height

            field_id = item.get("id") or item.get("field_label")
            user_val = user_answers.get(field_id)

            if item.get("field_type") == "checkbox":
                text_to_print = "X" if user_val else ""
            else:
                text_to_print = str(user_val or "")

            if re.match(r"^\d{4}-\d{2}-\d{2}$", text_to_print):
                parts = text_to_print.split("-")
                text_to_print = f"{parts[1]}/{parts[2]}/{parts[0]}"
    
            if not text_to_print:
                continue
    
            box = item.get("box_2d") or item.get("bbox")
            
            if box and len(box) == 4:
                ymin, xmin, ymax, xmax = box
                
                rect_xmin = (xmin / 1000.0) * page_w
                rect_ymin = (ymin / 1000.0) * page_h
                rect_xmax = (xmax / 1000.0) * page_w
                rect_ymax = (ymax / 1000.0) * page_h
                
                if item.get("field_type") == "checkbox":
                    fit_x = rect_xmin + ((rect_xmax - rect_xmin) / 4)
                    fit_y = rect_ymax - ((rect_ymax - rect_ymin) / 4)
                    page.insert_text(fitz.Point(fit_x, fit_y), "X", fontsize=10, color=(0, 0, 0))
                else:
                    fit_x = rect_xmin + 4
                    fit_y = rect_ymax - 3
                    page.insert_text(fitz.Point(fit_x, fit_y), text_to_print, fontsize=8.5, color=(0, 0, 0))
            else:
                raw_x = item.get("x", 0)
                raw_y = item.get("y", 0)
                
                fit_x = (raw_x / 1000.0) * page_w if raw_x > page_w else raw_x
                fit_y = (raw_y / 1000.0) * page_h if raw_y > page_h else raw_y
                
                page.insert_text(fitz.Point(fit_x + 5, fit_y + 10), text_to_print, fontsize=8.5, color=(0, 0, 0))
        
    doc.save(completed_file_path)
    doc.close()
            
    return jsonify({"status": "success"})

@projects_bp.route('/workspace/<int:doc_id>')
@login_required
def workspace(doc_id):
    current_user = g.current_user

    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not doc:
        flash("Document not found or access denied.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    parsed_fields = json.loads(raw_json)

    return render_template('workspace.html', 
                           user=current_user, 
                           document=doc,
                           fields=parsed_fields)

@projects_bp.route('/review-doc/<int:doc_id>')
@login_required
def review_doc(doc_id):
    current_user = g.current_user

    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first()

    if not doc:
        flash("Document not found or access denied.", "danger")
        return redirect(url_for('dashboard.dashboard'))

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    parsed_fields = json.loads(raw_json)

    return render_template('review_doc.html', 
                           user=current_user, 
                           document=doc,
                           fields=parsed_fields)

@projects_bp.route('/upload-endpoint', methods=['POST'])
@login_required
def upload(): 
    current_user = g.current_user

    pdf_check = request.files.get("pdf_file")
    pdf = ''

    total_active_docs = Document.query.filter_by(user_id=current_user.id).count()

    if total_active_docs >= 5:
        flash("You have reached your limit of 5 stored documents! Please delete an existing project to free up a slot.", "warning")
        return redirect(url_for('dashboard.dashboard'))

    if pdf_check and pdf_check.filename != "":        
        first_bytes = pdf_check.read(4)
        pdf_check.seek(0)

        is_valid_ext = pdf_check.filename.lower().endswith('.pdf')
        is_valid_mime = pdf_check.content_type == 'application/pdf'
        is_valid_bytes = first_bytes == b'%PDF' 

        if is_valid_ext and is_valid_mime and is_valid_bytes:
            pdf = pdf_check

            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            safe_name = secure_filename(pdf.filename)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

            pdf.save(file_path)

            doc_check = fitz.open(file_path)
            is_acroform = any(len(list(page.widgets())) > 0 for page in doc_check)
            doc_check.close()

            if is_acroform:
                try:
                    parsed_fields = extract_acroform_fields(file_path)
                except Exception as e:
                    print(f"Error parsing AcroForm fields: {e}")
                    flash("There was an error processing your document. Please try again in a moment!", "warning")
                    return redirect(url_for('dashboard.dashboard'))
            else:
                try:
                    parsed_fields = parse_pdf_with_gemini(file_path)
                except Exception as e:
                    print(f"Error parsing PDF with Gemini: {e}")
                    flash("Gemini API is temporarily experiencing high demand. Please try again in a moment!", "warning")
                    return redirect(url_for('dashboard.dashboard'))

            json_string = json.dumps(parsed_fields)
            encrypted_bytes = cipher.encrypt(json_string.encode())
            encrypted_string = encrypted_bytes.decode()

            new_doc = Document(
                user_id=current_user.id,
                filename=unique_filename,
                status='draft',
                data_json=encrypted_string,
                original_file_path = file_path
            )

            db.session.add(new_doc)
            db.session.commit()

            flash("PDF uploaded and parsed successfully!", "success")
            return redirect(url_for('projects.workspace', doc_id=new_doc.id))
            
        else:
            flash("Upload is not a valid PDF. Please try again.", "danger")
            return redirect(url_for('dashboard.dashboard'))
    else:
        flash("No file was selected.", "danger")
        return redirect(url_for('dashboard.dashboard'))

@projects_bp.route('/project/<int:doc_id>/submit', methods=['POST'])
@login_required
def submit(doc_id):
    current_user = g.current_user
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()

    original_path = doc.original_file_path
    completed_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"filled_{doc.id}.pdf")
    doc.completed_file_path = completed_path

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    fields = json.loads(raw_json)

    user_answers = {}
    for i, field in enumerate(fields, start=1):
        key = f"answer-{i}"
        
        if field.get('field_type') == 'checkbox':
            ans = True if request.form.get(key) else False
        else:
            ans = request.form.get(key, '')

        field['field_answer'] = ans
        
        field_name = field.get('id') or field.get('field_label')
        user_answers[field_name] = ans

    save_answers(original_path, completed_path, user_answers, form_type="acroform")

    doc.status = 'under_review'
    updated_json = json.dumps(fields)
    doc.data_json = cipher.encrypt(updated_json.encode()).decode()
    db.session.commit()

    return render_template('review_doc.html', 
                           user=current_user, 
                           document=doc, 
                           fields=fields)

@projects_bp.route('/project/<int:doc_id>/submit/view-pdf', methods=['GET', 'POST'])
@login_required
def view_pdf(doc_id):
    print(f"Made it to view_pdf route for doc_id: {doc_id}")

    current_user = g.current_user
    
    doc = Document.query.filter_by(id=doc_id, user_id=current_user.id).first_or_404()

    raw_json = cipher.decrypt(doc.data_json.encode()).decode()
    fields = json.loads(raw_json)

    return render_template(
        'view_pdf.html', 
        user=current_user, 
        document=doc, 
        fields=fields
    )

@projects_bp.route('/project/<int:doc_id>/pdf-file')
@login_required
def serve_pdf(doc_id):
    doc = Document.query.get_or_404(doc_id)
        
    return send_file(doc.completed_file_path, mimetype='application/pdf')

@projects_bp.route('/project/<int:doc_id>')
@login_required
def open_project(doc_id):
    doc = Document.query.filter_by(id=doc_id, user_id=g.current_user.id).first_or_404()
    
    if doc.status == 'under_review':
        return redirect(url_for('projects.review_doc', doc_id=doc.id))
    elif doc.status == 'completed':
        return redirect(url_for('projects.view_pdf', doc_id=doc.id))
    else:
        return redirect(url_for('projects.workspace', doc_id=doc.id))

@projects_bp.route('/project/<int:doc_id>/complete')
@login_required
def complete_project(doc_id):
    doc = Document.query.get_or_404(doc_id)
        
    if doc.status != 'completed':
            doc.status = 'completed'
            db.session.commit()

    return send_file(doc.completed_file_path, mimetype='application/pdf', as_attachment=True, download_name=doc.filename)