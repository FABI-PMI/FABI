import argparse
import sys
import time
import webbrowser
from typing import Optional

# --- Dependencias opcionales ---
try:
    import vlc  # type: ignore
    _VLC_OK = True
except Exception:
    _VLC_OK = False

try:
    import speech_recognition as sr  # type: ignore
    _SR_OK = True
except Exception:
    _SR_OK = False

from yt_dlp import YoutubeDL  # type: ignore

def search_youtube(query: str) -> dict:
    """Busca en YouTube y devuelve el dict del primer resultado.
    Retorna claves útiles: title, webpage_url, url (stream del mejor audio), duration, uploader.
    """
    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "default_search": "ytsearch",
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if not info:
            raise RuntimeError("No se obtuvo respuesta de YouTube.")
        if "entries" in info and info["entries"]:
            entry = info["entries"][0]
        else:
            entry = info
        required = {k: entry.get(k) for k in ("title", "webpage_url", "url", "duration", "uploader")}
        if not required.get("webpage_url"):
            raise RuntimeError("No encontré resultados para esa búsqueda.")
        return required

def play_with_vlc(stream_url: str, title: str) -> None:
    if not _VLC_OK:
        raise RuntimeError("python-vlc no está disponible.")
    print("▶️ Reproduciendo en VLC… (Ctrl+C para salir)")
    inst = vlc.Instance()
    player = inst.media_player_new()
    media = inst.media_new(stream_url)
    media.get_mrl()
    player.set_media(media)
    player.play()
    # Espera a que comience
    start = time.time()
    while time.time() - start < 5 and player.get_state() in (vlc.State.Opening, vlc.State.NothingSpecial):
        time.sleep(0.1)
    if player.get_state() == vlc.State.Error:
        raise RuntimeError("VLC no logró reproducir el stream.")
    # Mantener el script vivo mientras reproduce
    try:
        while True:
            state = player.get_state()
            if state in (vlc.State.Ended, vlc.State.Stopped, vlc.State.Error):
                break
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n⏹️ Detenido por el usuario.")
        player.stop()

def open_in_browser(url: str, title: str) -> None:
    print("🌐 Abriendo en tu navegador por defecto…")
    webbrowser.open(url)

def main():
    parser = argparse.ArgumentParser(description="Reproduce de YouTube por voz o por texto.")
    parser.add_argument("query", nargs="*", help="Lo que quieres escuchar (si lo omites, usa --voice o te preguntaré)")
    parser.add_argument("--voice", action="store_true", help="Usar el micrófono para dictar lo que quieres escuchar")
    parser.add_argument("--lang", default="es-CR", help="Código de idioma para el reconocimiento de voz (por defecto es-CR)")
    parser.add_argument("--browser", action="store_true", help="Forzar abrir en el navegador en vez de VLC")
    args = parser.parse_args()

    # Obtener consulta
    query_text: Optional[str] = " ".join(args.query).strip() if args.query else None

    if not query_text:
        try:
            query_text = input("¿Qué quieres escuchar en YouTube?: ").strip()
        except EOFError:
            print("No se recibió entrada.")
            sys.exit(1)

    if not query_text:
        print("No se proporcionó una consulta.")
        sys.exit(1)

    # Buscar y reproducir
    try:
        info = search_youtube(query_text)
        title = info.get("title", "(sin título)")
        page_url = info.get("webpage_url")
        stream_url = info.get("url")  # url directa del mejor audio
        print(f"Encontrado: {title} — {info.get('uploader', 'YouTube')}\n{page_url}")

        if args.browser or not _VLC_OK or not stream_url:
            open_in_browser(page_url, title)
        else:
            play_with_vlc(stream_url, title)

    except KeyboardInterrupt:
        print("\nCancelado.")
    except Exception as e:
        print(f"⚠️ Error: {e}\nAbriré el resultado en el navegador como alternativa…")
        try:
            # Fallback a navegador con lo que tengamos
            if 'page_url' in locals() and page_url:
                open_in_browser(page_url, title if 'title' in locals() else "YouTube")
            else:
                # Último recurso: buscar directamente en YouTube
                webbrowser.open(f"https://www.youtube.com/results?search_query={query_text.replace(' ', '+')}")
        except Exception:
            pass


if __name__ == "__main__":
    main()
