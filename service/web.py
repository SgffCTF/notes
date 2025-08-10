from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask import send_file
import sqlite3
import os
import hashlib
from pathlib import Path
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'nigga'
DATABASE = 'notes.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('init.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('public_notes'))

    db = get_db()
    notes = db.execute('''
        SELECT notes.*, users.username 
        FROM notes 
        LEFT JOIN users ON notes.user_id = users.id
        WHERE notes.user_id = ?
        ORDER BY notes.id DESC
    ''', (session['user_id'],)).fetchall()

    return render_template('index.html', notes=notes)


@app.route('/public')
def public_notes():
    db = get_db()
    notes = db.execute('''
        SELECT notes.*, users.username 
        FROM notes 
        LEFT JOIN users ON notes.user_id = users.id
        WHERE notes.is_public = 1
        ORDER BY notes.id DESC
    ''').fetchall()

    return render_template('public_notes.html', notes=notes)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        db = get_db()
        try:
            cursor = db.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, hashed_password))
            db.commit()
            user_id = cursor.lastrowid
            flash(f'Регистрация пользователя с id={user_id} прошла успешно! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Это имя пользователя уже занято!', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password(password)

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                          (username, hashed_password)).fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль!', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('login'))


@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.get_json()
        title = data["title"]
        content = data["content"]
        is_public = 1 if data["is_public"] == "true" else 0
        file_path = None
        if "file" in data:
            file_path = data["file"]
        print(data)

        if not title:
            flash('Требуется название!', 'error')
            return redirect(url_for('add_note'))

        db = get_db()
        try:
            if file_path:
                cursor = db.execute('''
                    INSERT INTO notes (title, content, file, user_id, is_public) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, content, file_path, session['user_id'], is_public))
            else:
                cursor = db.execute('''
                    INSERT INTO notes (title, content, user_id, is_public) 
                    VALUES (?, ?, ?, ?)
                ''', (title, content, session['user_id'], is_public))
            db.commit()
            note_id = cursor.lastrowid
            flash(f'Заметка с id={note_id} успешно создана!', 'success')
            return redirect(url_for('index'))
        except sqlite3.Error as e:
            db.rollback()
            flash(f'Ошибка при сохранении заметки: {str(e)}', 'error')
            return redirect(url_for('add_note'))

    return render_template('add_note.html')

@app.route("/load", methods=["POST"])
def load_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file = request.files["file"]
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return redirect(url_for('add_note'))
    else:
        flash('Недопустимый тип файла!', 'error')
        return redirect(url_for('add_note'))

@app.route('/download')
def download_file():
    filename = request.args.get('filename')
    if not filename:
        flash('Не указано имя файла', 'error')
        return redirect(url_for('index'))

    upload_dir = Path(app.config['UPLOAD_FOLDER'])
    requested_file = upload_dir / filename
    
    if '../' in str(requested_file):
        flash('malicious', 'error')
        return redirect(url_for('index'))

    if not requested_file.exists():
        flash('Файл не найден', 'error')
        return redirect(url_for('index'))

    return send_file(requested_file, as_attachment=True)


@app.route('/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    note = db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
    
    if note is None:
        flash('Заметка не найдена :(', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.get_json()
        content = data["content"]
        is_public = 1 if data["is_public"] == "true" else 0
        file_path = None
        if "file" in data:
            file_path = data["file"]

        if file_path:
            db.execute('''
                UPDATE notes 
                SET content = ?, is_public = ?, file = ?
                WHERE id = ?
            ''', (content, is_public, file_path, note_id))
        else:
            db.execute('''
                UPDATE notes 
                SET content = ?, is_public = ?
                WHERE id = ?
            ''', (content, is_public, note_id))
        db.commit()

        flash('Заметка обновлена!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_note.html', note=dict(note))


@app.route('/delete/<int:note_id>')
def delete_note(note_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    note = db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()

    if not note or note['user_id'] != session['user_id']:
        flash('Вы не можете удалить эту заметку', 'error')
        return redirect(url_for('index'))

    if note['file']:
        try:
            file_path = os.path.join('static', note['file'])
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            app.logger.error(f"Ошибка при удалении файла: {e}")

    db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    db.commit()
    flash('Заметка успешно удалена!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0")