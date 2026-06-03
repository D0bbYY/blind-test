#!/usr/bin/env python3
"""
Serveur Blind Test - Flask (Render compatible)
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
import json
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'database'

# Créer le dossier database
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

DATABASE_FILE = Path(app.config['UPLOAD_FOLDER']) / 'songs.json'

def load_database():
    """Charge la base de données"""
    if DATABASE_FILE.exists():
        with open(DATABASE_FILE, 'r') as f:
            return json.load(f)
    return {
        "team1": "Équipe 1",
        "team2": "Équipe 2",
        "songs": []
    }

def save_database(data):
    """Sauvegarde la base de données"""
    with open(DATABASE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    """Sert la page principale"""
    return render_template('index.html')

@app.route('/api/songs', methods=['GET'])
def get_songs():
    """Récupère toutes les chansons"""
    data = load_database()
    return jsonify(data)

@app.route('/api/songs', methods=['POST'])
def add_song():
    """Ajoute une chanson (JSON ou FormData)"""
    try:
        data = load_database()

        # Si c'est du FormData (upload de fichier)
        if 'file' in request.files:
            file = request.files['file']
            artist = request.form.get('artist', 'Unknown')
            title = request.form.get('title', file.filename.replace('.mp3', ''))

            if not file or file.filename == '':
                return jsonify({"error": "Pas de fichier"}), 400

            # Lire le fichier MP3
            audio_data = list(file.read())

            new_song = {
                'id': len(data['songs']) + 1,
                'artist': artist.strip(),
                'title': title.strip(),
                'data': audio_data
            }

            data['songs'].append(new_song)
            save_database(data)

            return jsonify({"success": True, "id": new_song['id']})

        # Si c'est du JSON (ancien format)
        else:
            new_song = request.json

            if 'artist' not in new_song or 'title' not in new_song or 'data' not in new_song:
                return jsonify({"error": "Données manquantes"}), 400

            new_song['id'] = len(data['songs']) + 1
            data['songs'].append(new_song)
            save_database(data)

            return jsonify({"success": True, "id": new_song['id']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Supprime une chanson"""
    try:
        data = load_database()
        data['songs'] = [s for s in data['songs'] if s.get('id') != song_id]
        save_database(data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams', methods=['GET'])
def get_teams():
    """Récupère les noms des équipes"""
    data = load_database()
    return jsonify({
        "team1": data.get('team1', 'Équipe 1'),
        "team2": data.get('team2', 'Équipe 2')
    })

@app.route('/api/teams', methods=['POST'])
def set_teams():
    """Met à jour les noms des équipes"""
    try:
        data = load_database()
        data['team1'] = request.json.get('team1', 'Équipe 1')
        data['team2'] = request.json.get('team2', 'Équipe 2')
        save_database(data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_database():
    """Exporte la base de données"""
    data = load_database()
    return jsonify(data)

@app.route('/api/import', methods=['POST'])
def import_database():
    """Importe une base de données"""
    try:
        data = request.json
        save_database(data)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Pour Render: utiliser la variable d'environnement PORT
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
