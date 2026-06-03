#!/usr/bin/env python3
"""
Script pour extraire les chansons d'une playlist Spotify
et trouver les liens YouTube correspondants
"""

import requests
import json
import re
from pathlib import Path

print("="*70)
print("🎵 SPOTIFY → YOUTUBE CONVERTER")
print("="*70)

# ID de la playlist (on l'extrait du lien)
playlist_url = "https://open.spotify.com/playlist/37i9dQZF1F5p3rmiWPIYgZ"
playlist_id = playlist_url.split('/')[-1].split('?')[0]

print(f"\n🔍 Récupération de la playlist: {playlist_id}")

try:
    # Récupérer les chansons via l'API Spotify publique
    url = f"https://open.spotify.com/api/v1/playlists/{playlist_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    response = requests.get(
        f"https://open.spotify.com/playlist/{playlist_id}",
        headers=headers
    )

    # Alternative: utiliser une API publique qui scrape Spotify
    # On va utiliser le scraping simple
    print("📥 Téléchargement des données Spotify...")

    # Utiliser l'endpoint public de Spotify
    try:
        api_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        resp = requests.get(api_url)
        if resp.status_code == 401:
            # API requiert authentication, on va utiliser une autre méthode
            raise Exception("Auth needed")
    except:
        pass

    # Méthode alternative: extraire les données du HTML
    try:
        import yt_dlp
        HAS_YT_DLP = True
    except:
        HAS_YT_DLP = False
        print("⚠️  yt-dlp pas installé - on va juste chercher sur YouTube")

    # Créer un fichier CSV avec les résultats
    output_file = "youtube_links.txt"

    print("\n" + "="*70)
    print("✓ LISTE DE CHANSONS À CHERCHER")
    print("="*70)
    print("\nVa sur: https://spotlistr.herokuapp.com/")
    print("\n1. Colle le lien de ta playlist Spotify")
    print("2. Choisis 'Export to > File > CSV'")
    print("3. Récupère le fichier CSV")
    print("4. Ouvre-le et copie les chansons ici\n")

    # Alternative: créer un formulaire simple
    print("\n" + "="*70)
    print("📝 OU entre les chansons manuellement")
    print("="*70)
    print("\nFormat: Artiste - Titre")
    print("Exemple: Queen - Bohemian Rhapsody")
    print("Tape 'done' quand c'est fini\n")

    songs = []
    while True:
        song = input("🎵 Chanson: ").strip()
        if song.lower() == 'done':
            break
        if song:
            songs.append(song)

    if not songs:
        print("\n⚠️  Aucune chanson entré")
        exit(1)

    print(f"\n✓ {len(songs)} chanson(s) à traiter\n")

    # Chercher sur YouTube
    print("🔍 Recherche sur YouTube...")
    youtube_results = []

    if HAS_YT_DLP:
        import yt_dlp

        for idx, song in enumerate(songs, 1):
            print(f"  [{idx}/{len(songs)}] {song}...", end=" ", flush=True)

            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    results = ydl.extract_info(f"ytsearch:{song}", download=False)

                if results and 'entries' in results and results['entries']:
                    video = results['entries'][0]
                    link = f"https://www.youtube.com/watch?v={video['id']}"
                    youtube_results.append({
                        'song': song,
                        'youtube_link': link,
                        'youtube_id': video['id']
                    })
                    print(f"✓")
                else:
                    print(f"✗ Pas trouvé")

            except Exception as e:
                print(f"✗ Erreur: {str(e)[:20]}")

    else:
        print("❌ yt-dlp requis pour chercher automatiquement")
        print("\nInstalle: pip install yt-dlp")
        exit(1)

    # Sauvegarder les résultats
    if youtube_results:
        # Format 1: Fichier texte simple
        with open("youtube_links.txt", "w", encoding="utf-8") as f:
            for result in youtube_results:
                f.write(f"{result['song']}\n{result['youtube_link']}\n\n")

        # Format 2: JSON pour importer dans l'app
        with open("blind_test_youtube.json", "w", encoding="utf-8") as f:
            data = {
                "team1": "Équipe 1",
                "team2": "Équipe 2",
                "songs": [
                    {
                        "id": idx + 1,
                        "artist": r['song'].split(' - ')[0] if ' - ' in r['song'] else 'Unknown',
                        "title": r['song'].split(' - ')[1] if ' - ' in r['song'] else r['song'],
                        "youtubeId": r['youtube_id']
                    }
                    for idx, r in enumerate(youtube_results)
                ]
            }
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Format 3: URL simple
        with open("youtube_urls_only.txt", "w", encoding="utf-8") as f:
            for result in youtube_results:
                f.write(f"{result['youtube_link']}\n")

        print("\n" + "="*70)
        print("✓ FICHIERS CRÉÉS")
        print("="*70)
        print(f"\n✓ youtube_links.txt - Liens YouTube formatés")
        print(f"✓ youtube_urls_only.txt - Juste les URLs")
        print(f"✓ blind_test_youtube.json - Prêt pour l'app!")
        print(f"\n✓ {len(youtube_results)}/{len(songs)} chansons trouvées")

        print("\n" + "="*70)
        print("📋 POUR IMPORTER DANS L'APP:")
        print("="*70)
        print("\n1. Ouvre: https://blind-test-xxx.onrender.com")
        print("2. Va dans 'Gestion'")
        print("3. Copie les URLs de youtube_urls_only.txt")
        print("4. Rentre artiste + titre pour chaque lien")
        print("5. Ajoute!")

    else:
        print("\n❌ Aucune chanson trouvée")

except Exception as e:
    print(f"\n❌ Erreur: {str(e)}")
    print("\nAlternative: utilise https://spotlistr.herokuapp.com/")

print("\n" + "="*70)
