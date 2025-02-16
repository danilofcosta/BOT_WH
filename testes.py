from moviepy import VideoFileClip

def video_to_gif(video_path, output_gif="output.gif", duration=5):
    # Carrega o vídeo
    clip = VideoFileClip(video_path)

    # Recorta os primeiros 5 segundos (ou até onde o vídeo permitir)
    clip = clip.subclipped(0, min(duration, clip.duration))

    # Salva como GIF
    clip.write_gif(output_gif, fps=10)  # Define FPS para otimizar tamanho

    print(f"GIF salvo como {output_gif}")

# Exemplo de uso
video_to_gif("Download.mp4", "meu_gif.gif")
