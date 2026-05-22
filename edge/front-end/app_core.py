import pygame
from UI.models import Song, LeaderboardEntry


def setup():
    The_Feels = Song.from_json("songs/json/the_feels.json")

    pygame.init()
    window = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("Kareoke + Dance")

    # constants
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    YELLOW = (255, 255, 0)
    LINE_WIDTH = 2
    MARGIN = 20
    GAP = 20
    LABEL_PADDING = 10
    LINE_OFFSET = 80

    # fonts
    small_font = pygame.font.SysFont("comicsansms", 24)
    big_font = pygame.font.SysFont("comicsansms", 36)
    label_font = pygame.font.SysFont(None, 26)

    left_label = label_font.render("POSE MODEL", True, WHITE)
    right_label = label_font.render("NEXT MOVE", True, WHITE)
    bottom_label = label_font.render("LYRICS", True, WHITE)

    window_width, window_height = window.get_size()

    top_height = (window_height - (2 * MARGIN) - GAP) // 2
    top_width = (window_width - (2 * MARGIN) - GAP) // 2

    left_rect = pygame.Rect(MARGIN, MARGIN, top_width, top_height)
    right_rect = pygame.Rect(MARGIN + top_width + GAP, MARGIN, top_width, top_height)
    bottom_rect = pygame.Rect(
        MARGIN,
        MARGIN + top_height + GAP,
        window_width - (2 * MARGIN),
        window_height - (2 * MARGIN) - top_height - GAP,
    )

    left_camera_rect = pygame.Rect(
        left_rect.x + LABEL_PADDING,
        left_rect.y + LABEL_PADDING + left_label.get_height() + LABEL_PADDING,
        left_rect.width - (2 * LABEL_PADDING),
        left_rect.height - (3 * LABEL_PADDING) - left_label.get_height(),
    )

    button_font = pygame.font.SysFont(None, 24)
    button_rect = pygame.Rect(window_width - MARGIN - 100, MARGIN, 100, 40)
    button_text = button_font.render("START", True, BLACK)
    game_state = "not_started"

    title_font = pygame.font.SysFont(None, 64)
    title_text = title_font.render("Dance Dance Karaoke", True, WHITE)

    menu_font = pygame.font.SysFont(None, 40)
    play_song_text = menu_font.render("1. PLAY SONG", True, WHITE)
    online_library_text = menu_font.render("2. ONLINE LIBRARY", True, WHITE)
    leaderboard_text = menu_font.render("3. LEADERBOARD", True, WHITE)

    end_title_font = pygame.font.SysFont(None, 64)
    end_score_font = pygame.font.SysFont(None, 80)
    end_hint_font = pygame.font.SysFont(None, 28)

    final_score = 100

    end_song_name_text = end_title_font.render(The_Feels.song_title, True, WHITE)
    end_score_text = end_score_font.render(f"Score: {final_score}", True, YELLOW)
    end_hint_text = end_hint_font.render("Press ENTER to return to menu", True, WHITE)

    leaderboard_title_font = pygame.font.SysFont(None, 64)
    leaderboard_entry_font = pygame.font.SysFont(None, 36)
    leaderboard_hint_font = pygame.font.SysFont(None, 28)

    leaderboard_entries = [
        LeaderboardEntry(player_name="HANSON", score=980, rank=1),
        LeaderboardEntry(player_name="Z", score=970, rank=2),
        LeaderboardEntry(player_name="ANDY", score=960, rank=3),
        LeaderboardEntry(player_name="EDWARD", score=950, rank=4),
        LeaderboardEntry(player_name="BOB", score=67, rank=5),
    ]

    leaderboard_title_text = leaderboard_title_font.render("LEADERBOARD", True, WHITE)
    leaderboard_hint_text = leaderboard_hint_font.render("Press ESC to return to menu", True, WHITE)

    SONG_DIR = "songs"
    pygame.mixer.music.load(f"{SONG_DIR}/cupid.mp3")

    # load poses
    pose_images = []
    for pose_moves in The_Feels.poses:
        image = pygame.image.load(pose_moves.image_path)
        image = pygame.transform.scale(image, (right_rect.width, right_rect.height))
        pose_images.append(image)

    state = {
        "window": window,
        "The_Feels": The_Feels,
        "WHITE": WHITE,
        "BLACK": BLACK,
        "YELLOW": YELLOW,
        "LINE_WIDTH": LINE_WIDTH,
        "MARGIN": MARGIN,
        "GAP": GAP,
        "LABEL_PADDING": LABEL_PADDING,
        "LINE_OFFSET": LINE_OFFSET,
        "small_font": small_font,
        "big_font": big_font,
        "label_font": label_font,
        "left_label": left_label,
        "right_label": right_label,
        "bottom_label": bottom_label,
        "window_width": window_width,
        "window_height": window_height,
        "left_rect": left_rect,
        "right_rect": right_rect,
        "bottom_rect": bottom_rect,
        "left_camera_rect": left_camera_rect,
        "button_font": button_font,
        "button_rect": button_rect,
        "button_text": button_text,
        "game_state": game_state,
        "title_text": title_text,
        "play_song_text": play_song_text,
        "online_library_text": online_library_text,
        "leaderboard_text": leaderboard_text,
        "end_song_name_text": end_song_name_text,
        "end_score_text": end_score_text,
        "end_hint_text": end_hint_text,
        "leaderboard_entries": leaderboard_entries,
        "leaderboard_title_text": leaderboard_title_text,
        "leaderboard_hint_text": leaderboard_hint_text,
        "pose_images": pose_images,
        "SONG_DIR": SONG_DIR,
        "current_lyrics_index": 1,
        "current_pose_index": 0,
        "current_display": "start_screen",
        "final_score": final_score,
        "run": True,
    }

    return state
